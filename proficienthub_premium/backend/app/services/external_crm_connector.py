"""
External CRM Connector Service for ProficientHub B2B Platform.

Provides integration with popular CRM systems:
- Salesforce
- HubSpot
- Zoho CRM
- Pipedrive
- Microsoft Dynamics 365
- Custom Webhooks

Supports bidirectional sync of leads, contacts, deals, and activities.
"""

import uuid
import asyncio
import hashlib
import hmac
import json
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any, Type

import httpx
import structlog
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models_crm import (
    CRMLead, CRMContact, CRMDeal, CRMCommunication,
    ExternalCRMIntegration, ExternalCRMType,
    LeadSource, LeadStatus, DealStage
)

logger = structlog.get_logger()


# ===================== ABSTRACT BASE CONNECTOR =====================

class BaseCRMConnector(ABC):
    """Base class for all CRM connectors."""

    def __init__(self, integration: ExternalCRMIntegration):
        self.integration = integration
        self.client = httpx.AsyncClient(timeout=30.0)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    @abstractmethod
    async def test_connection(self) -> bool:
        """Test the CRM connection."""
        pass

    @abstractmethod
    async def sync_leads_to_external(self, leads: List[CRMLead]) -> Dict[str, Any]:
        """Sync leads to external CRM."""
        pass

    @abstractmethod
    async def sync_leads_from_external(self) -> List[Dict]:
        """Sync leads from external CRM."""
        pass

    @abstractmethod
    async def sync_contacts_to_external(self, contacts: List[CRMContact]) -> Dict[str, Any]:
        """Sync contacts to external CRM."""
        pass

    @abstractmethod
    async def sync_contacts_from_external(self) -> List[Dict]:
        """Sync contacts from external CRM."""
        pass

    @abstractmethod
    async def sync_deals_to_external(self, deals: List[CRMDeal]) -> Dict[str, Any]:
        """Sync deals to external CRM."""
        pass

    @abstractmethod
    async def sync_deals_from_external(self) -> List[Dict]:
        """Sync deals from external CRM."""
        pass

    @abstractmethod
    async def refresh_token(self) -> bool:
        """Refresh OAuth token if needed."""
        pass

    def _map_lead_status_to_external(self, status: LeadStatus) -> str:
        """Map internal lead status to external CRM status."""
        # Override in subclass for specific mappings
        return status.value

    def _map_lead_status_from_external(self, external_status: str) -> LeadStatus:
        """Map external CRM status to internal lead status."""
        # Override in subclass for specific mappings
        return LeadStatus.NEW

    def _map_deal_stage_to_external(self, stage: DealStage) -> str:
        """Map internal deal stage to external CRM stage."""
        return stage.value

    def _map_deal_stage_from_external(self, external_stage: str) -> DealStage:
        """Map external CRM stage to internal deal stage."""
        return DealStage.PROSPECTING


# ===================== SALESFORCE CONNECTOR =====================

class SalesforceConnector(BaseCRMConnector):
    """Salesforce CRM connector."""

    BASE_URL = "https://login.salesforce.com"

    async def test_connection(self) -> bool:
        """Test Salesforce connection."""
        try:
            await self._ensure_valid_token()
            response = await self.client.get(
                f"{self.integration.instance_url}/services/data/v57.0/",
                headers=self._get_headers()
            )
            return response.status_code == 200
        except Exception as e:
            logger.error("Salesforce connection test failed", error=str(e))
            return False

    async def refresh_token(self) -> bool:
        """Refresh Salesforce OAuth token."""
        try:
            response = await self.client.post(
                f"{self.BASE_URL}/services/oauth2/token",
                data={
                    "grant_type": "refresh_token",
                    "client_id": self.integration.api_key,
                    "client_secret": self.integration.api_secret,
                    "refresh_token": self.integration.refresh_token
                }
            )

            if response.status_code == 200:
                data = response.json()
                self.integration.access_token = data["access_token"]
                self.integration.token_expires_at = datetime.utcnow() + timedelta(hours=2)
                if "instance_url" in data:
                    self.integration.instance_url = data["instance_url"]
                return True
            return False
        except Exception as e:
            logger.error("Salesforce token refresh failed", error=str(e))
            return False

    async def _ensure_valid_token(self):
        """Ensure access token is valid."""
        if self.integration.token_expires_at and self.integration.token_expires_at <= datetime.utcnow():
            await self.refresh_token()

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers."""
        return {
            "Authorization": f"Bearer {self.integration.access_token}",
            "Content-Type": "application/json"
        }

    async def sync_leads_to_external(self, leads: List[CRMLead]) -> Dict[str, Any]:
        """Sync leads to Salesforce."""
        await self._ensure_valid_token()

        synced = 0
        errors = []

        for lead in leads:
            try:
                sf_lead = self._lead_to_salesforce(lead)

                if lead.external_crm_id:
                    # Update existing
                    response = await self.client.patch(
                        f"{self.integration.instance_url}/services/data/v57.0/sobjects/Lead/{lead.external_crm_id}",
                        headers=self._get_headers(),
                        json=sf_lead
                    )
                else:
                    # Create new
                    response = await self.client.post(
                        f"{self.integration.instance_url}/services/data/v57.0/sobjects/Lead",
                        headers=self._get_headers(),
                        json=sf_lead
                    )

                    if response.status_code == 201:
                        data = response.json()
                        lead.external_crm_id = data["id"]
                        lead.external_crm_type = ExternalCRMType.SALESFORCE

                if response.status_code in [200, 201, 204]:
                    synced += 1
                    lead.last_synced_at = datetime.utcnow()
                else:
                    errors.append({
                        "lead_id": str(lead.id),
                        "error": response.text
                    })

            except Exception as e:
                errors.append({
                    "lead_id": str(lead.id),
                    "error": str(e)
                })

        return {
            "synced": synced,
            "total": len(leads),
            "errors": errors
        }

    async def sync_leads_from_external(self) -> List[Dict]:
        """Sync leads from Salesforce."""
        await self._ensure_valid_token()

        # Query recently modified leads
        last_sync = self.integration.last_sync_at or datetime.utcnow() - timedelta(days=30)
        query = f"""
            SELECT Id, Company, FirstName, LastName, Email, Phone, Status, LeadSource,
                   NumberOfEmployees, AnnualRevenue, Description, Website,
                   LastModifiedDate
            FROM Lead
            WHERE LastModifiedDate > {last_sync.strftime('%Y-%m-%dT%H:%M:%SZ')}
            ORDER BY LastModifiedDate ASC
            LIMIT 200
        """

        response = await self.client.get(
            f"{self.integration.instance_url}/services/data/v57.0/query",
            headers=self._get_headers(),
            params={"q": query}
        )

        if response.status_code != 200:
            logger.error("Salesforce lead sync failed", error=response.text)
            return []

        data = response.json()
        leads = []

        for record in data.get("records", []):
            leads.append(self._salesforce_to_lead(record))

        return leads

    async def sync_contacts_to_external(self, contacts: List[CRMContact]) -> Dict[str, Any]:
        """Sync contacts to Salesforce."""
        await self._ensure_valid_token()

        synced = 0
        errors = []

        for contact in contacts:
            try:
                sf_contact = {
                    "FirstName": contact.first_name,
                    "LastName": contact.last_name,
                    "Email": contact.email,
                    "Phone": contact.phone,
                    "MobilePhone": contact.mobile,
                    "Title": contact.title,
                    "Department": contact.department
                }

                if contact.external_crm_id:
                    response = await self.client.patch(
                        f"{self.integration.instance_url}/services/data/v57.0/sobjects/Contact/{contact.external_crm_id}",
                        headers=self._get_headers(),
                        json=sf_contact
                    )
                else:
                    response = await self.client.post(
                        f"{self.integration.instance_url}/services/data/v57.0/sobjects/Contact",
                        headers=self._get_headers(),
                        json=sf_contact
                    )

                    if response.status_code == 201:
                        data = response.json()
                        contact.external_crm_id = data["id"]

                if response.status_code in [200, 201, 204]:
                    synced += 1
                else:
                    errors.append({
                        "contact_id": str(contact.id),
                        "error": response.text
                    })

            except Exception as e:
                errors.append({
                    "contact_id": str(contact.id),
                    "error": str(e)
                })

        return {"synced": synced, "total": len(contacts), "errors": errors}

    async def sync_contacts_from_external(self) -> List[Dict]:
        """Sync contacts from Salesforce."""
        await self._ensure_valid_token()

        last_sync = self.integration.last_sync_at or datetime.utcnow() - timedelta(days=30)
        query = f"""
            SELECT Id, FirstName, LastName, Email, Phone, MobilePhone, Title, Department,
                   AccountId, LastModifiedDate
            FROM Contact
            WHERE LastModifiedDate > {last_sync.strftime('%Y-%m-%dT%H:%M:%SZ')}
            ORDER BY LastModifiedDate ASC
            LIMIT 200
        """

        response = await self.client.get(
            f"{self.integration.instance_url}/services/data/v57.0/query",
            headers=self._get_headers(),
            params={"q": query}
        )

        if response.status_code != 200:
            return []

        data = response.json()
        return [self._salesforce_to_contact(r) for r in data.get("records", [])]

    async def sync_deals_to_external(self, deals: List[CRMDeal]) -> Dict[str, Any]:
        """Sync deals to Salesforce (as Opportunities)."""
        await self._ensure_valid_token()

        synced = 0
        errors = []

        for deal in deals:
            try:
                sf_opp = {
                    "Name": deal.name,
                    "Amount": float(deal.amount),
                    "StageName": self._map_deal_stage_to_salesforce(deal.stage),
                    "Probability": deal.probability,
                    "CloseDate": deal.expected_close_date.isoformat() if deal.expected_close_date else None,
                    "Description": deal.description
                }

                if deal.external_crm_id:
                    response = await self.client.patch(
                        f"{self.integration.instance_url}/services/data/v57.0/sobjects/Opportunity/{deal.external_crm_id}",
                        headers=self._get_headers(),
                        json=sf_opp
                    )
                else:
                    response = await self.client.post(
                        f"{self.integration.instance_url}/services/data/v57.0/sobjects/Opportunity",
                        headers=self._get_headers(),
                        json=sf_opp
                    )

                    if response.status_code == 201:
                        data = response.json()
                        deal.external_crm_id = data["id"]

                if response.status_code in [200, 201, 204]:
                    synced += 1
                else:
                    errors.append({
                        "deal_id": str(deal.id),
                        "error": response.text
                    })

            except Exception as e:
                errors.append({"deal_id": str(deal.id), "error": str(e)})

        return {"synced": synced, "total": len(deals), "errors": errors}

    async def sync_deals_from_external(self) -> List[Dict]:
        """Sync deals from Salesforce."""
        await self._ensure_valid_token()

        last_sync = self.integration.last_sync_at or datetime.utcnow() - timedelta(days=30)
        query = f"""
            SELECT Id, Name, Amount, StageName, Probability, CloseDate, Description,
                   AccountId, LastModifiedDate
            FROM Opportunity
            WHERE LastModifiedDate > {last_sync.strftime('%Y-%m-%dT%H:%M:%SZ')}
            ORDER BY LastModifiedDate ASC
            LIMIT 200
        """

        response = await self.client.get(
            f"{self.integration.instance_url}/services/data/v57.0/query",
            headers=self._get_headers(),
            params={"q": query}
        )

        if response.status_code != 200:
            return []

        data = response.json()
        return [self._salesforce_to_deal(r) for r in data.get("records", [])]

    def _lead_to_salesforce(self, lead: CRMLead) -> Dict:
        """Convert internal lead to Salesforce format."""
        return {
            "Company": lead.organization_name,
            "FirstName": lead.contact_name.split()[0] if lead.contact_name else "",
            "LastName": lead.contact_name.split()[-1] if lead.contact_name else "",
            "Email": lead.contact_email,
            "Phone": lead.contact_phone,
            "Status": self._map_lead_status_to_salesforce(lead.status),
            "LeadSource": self._map_lead_source_to_salesforce(lead.source),
            "NumberOfEmployees": lead.employee_count,
            "AnnualRevenue": float(lead.annual_revenue) if lead.annual_revenue else None,
            "Description": lead.qualification_notes,
            "Website": lead.website
        }

    def _salesforce_to_lead(self, sf_record: Dict) -> Dict:
        """Convert Salesforce lead to internal format."""
        return {
            "external_crm_id": sf_record.get("Id"),
            "organization_name": sf_record.get("Company", ""),
            "contact_name": f"{sf_record.get('FirstName', '')} {sf_record.get('LastName', '')}".strip(),
            "contact_email": sf_record.get("Email", ""),
            "contact_phone": sf_record.get("Phone"),
            "status": self._map_lead_status_from_salesforce(sf_record.get("Status", "")),
            "source": self._map_lead_source_from_salesforce(sf_record.get("LeadSource", "")),
            "employee_count": sf_record.get("NumberOfEmployees"),
            "annual_revenue": Decimal(str(sf_record.get("AnnualRevenue", 0))) if sf_record.get("AnnualRevenue") else None,
            "website": sf_record.get("Website"),
            "qualification_notes": sf_record.get("Description")
        }

    def _salesforce_to_contact(self, sf_record: Dict) -> Dict:
        """Convert Salesforce contact to internal format."""
        return {
            "external_crm_id": sf_record.get("Id"),
            "first_name": sf_record.get("FirstName", ""),
            "last_name": sf_record.get("LastName", ""),
            "email": sf_record.get("Email", ""),
            "phone": sf_record.get("Phone"),
            "mobile": sf_record.get("MobilePhone"),
            "title": sf_record.get("Title"),
            "department": sf_record.get("Department")
        }

    def _salesforce_to_deal(self, sf_record: Dict) -> Dict:
        """Convert Salesforce opportunity to internal format."""
        return {
            "external_crm_id": sf_record.get("Id"),
            "name": sf_record.get("Name", ""),
            "amount": Decimal(str(sf_record.get("Amount", 0))) if sf_record.get("Amount") else Decimal("0"),
            "stage": self._map_deal_stage_from_salesforce(sf_record.get("StageName", "")),
            "probability": sf_record.get("Probability", 0),
            "expected_close_date": sf_record.get("CloseDate"),
            "description": sf_record.get("Description")
        }

    def _map_lead_status_to_salesforce(self, status: LeadStatus) -> str:
        """Map lead status to Salesforce."""
        mapping = {
            LeadStatus.NEW: "New",
            LeadStatus.CONTACTED: "Working - Contacted",
            LeadStatus.QUALIFIED: "Qualified",
            LeadStatus.WON: "Converted",
            LeadStatus.LOST: "Unqualified"
        }
        return mapping.get(status, "New")

    def _map_lead_status_from_salesforce(self, sf_status: str) -> LeadStatus:
        """Map Salesforce status to lead status."""
        mapping = {
            "New": LeadStatus.NEW,
            "Working - Contacted": LeadStatus.CONTACTED,
            "Qualified": LeadStatus.QUALIFIED,
            "Converted": LeadStatus.WON,
            "Unqualified": LeadStatus.LOST
        }
        return mapping.get(sf_status, LeadStatus.NEW)

    def _map_lead_source_to_salesforce(self, source: LeadSource) -> str:
        """Map lead source to Salesforce."""
        mapping = {
            LeadSource.WEBSITE: "Web",
            LeadSource.REFERRAL: "Referral",
            LeadSource.ADVERTISEMENT: "Advertisement",
            LeadSource.EMAIL_CAMPAIGN: "Email",
            LeadSource.PARTNER: "Partner"
        }
        return mapping.get(source, "Other")

    def _map_lead_source_from_salesforce(self, sf_source: str) -> LeadSource:
        """Map Salesforce source to lead source."""
        mapping = {
            "Web": LeadSource.WEBSITE,
            "Referral": LeadSource.REFERRAL,
            "Advertisement": LeadSource.ADVERTISEMENT,
            "Email": LeadSource.EMAIL_CAMPAIGN,
            "Partner": LeadSource.PARTNER
        }
        return mapping.get(sf_source, LeadSource.MANUAL_ENTRY)

    def _map_deal_stage_to_salesforce(self, stage: DealStage) -> str:
        """Map deal stage to Salesforce opportunity stage."""
        mapping = {
            DealStage.PROSPECTING: "Prospecting",
            DealStage.QUALIFICATION: "Qualification",
            DealStage.NEEDS_ANALYSIS: "Needs Analysis",
            DealStage.VALUE_PROPOSITION: "Value Proposition",
            DealStage.PROPOSAL: "Proposal/Price Quote",
            DealStage.NEGOTIATION: "Negotiation/Review",
            DealStage.CLOSED_WON: "Closed Won",
            DealStage.CLOSED_LOST: "Closed Lost"
        }
        return mapping.get(stage, "Prospecting")

    def _map_deal_stage_from_salesforce(self, sf_stage: str) -> DealStage:
        """Map Salesforce stage to deal stage."""
        mapping = {
            "Prospecting": DealStage.PROSPECTING,
            "Qualification": DealStage.QUALIFICATION,
            "Needs Analysis": DealStage.NEEDS_ANALYSIS,
            "Value Proposition": DealStage.VALUE_PROPOSITION,
            "Proposal/Price Quote": DealStage.PROPOSAL,
            "Negotiation/Review": DealStage.NEGOTIATION,
            "Closed Won": DealStage.CLOSED_WON,
            "Closed Lost": DealStage.CLOSED_LOST
        }
        return mapping.get(sf_stage, DealStage.PROSPECTING)


# ===================== HUBSPOT CONNECTOR =====================

class HubSpotConnector(BaseCRMConnector):
    """HubSpot CRM connector."""

    BASE_URL = "https://api.hubapi.com"

    async def test_connection(self) -> bool:
        """Test HubSpot connection."""
        try:
            response = await self.client.get(
                f"{self.BASE_URL}/crm/v3/objects/contacts",
                headers=self._get_headers(),
                params={"limit": 1}
            )
            return response.status_code == 200
        except Exception as e:
            logger.error("HubSpot connection test failed", error=str(e))
            return False

    async def refresh_token(self) -> bool:
        """Refresh HubSpot OAuth token."""
        try:
            response = await self.client.post(
                f"{self.BASE_URL}/oauth/v1/token",
                data={
                    "grant_type": "refresh_token",
                    "client_id": self.integration.api_key,
                    "client_secret": self.integration.api_secret,
                    "refresh_token": self.integration.refresh_token
                }
            )

            if response.status_code == 200:
                data = response.json()
                self.integration.access_token = data["access_token"]
                self.integration.refresh_token = data.get("refresh_token", self.integration.refresh_token)
                self.integration.token_expires_at = datetime.utcnow() + timedelta(seconds=data.get("expires_in", 21600))
                return True
            return False
        except Exception as e:
            logger.error("HubSpot token refresh failed", error=str(e))
            return False

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers."""
        return {
            "Authorization": f"Bearer {self.integration.access_token}",
            "Content-Type": "application/json"
        }

    async def sync_leads_to_external(self, leads: List[CRMLead]) -> Dict[str, Any]:
        """Sync leads to HubSpot (as Contacts with company association)."""
        synced = 0
        errors = []

        for lead in leads:
            try:
                # Create or update company first
                company_data = {
                    "properties": {
                        "name": lead.organization_name,
                        "website": lead.website,
                        "numberofemployees": str(lead.employee_count) if lead.employee_count else "",
                        "annualrevenue": str(lead.annual_revenue) if lead.annual_revenue else ""
                    }
                }

                # Create or update contact
                contact_data = {
                    "properties": {
                        "firstname": lead.contact_name.split()[0] if lead.contact_name else "",
                        "lastname": lead.contact_name.split()[-1] if lead.contact_name else "",
                        "email": lead.contact_email,
                        "phone": lead.contact_phone or "",
                        "company": lead.organization_name,
                        "lifecyclestage": self._map_lead_status_to_hubspot(lead.status),
                        "hs_lead_status": self._map_lead_status_to_hubspot_detailed(lead.status)
                    }
                }

                if lead.external_crm_id:
                    response = await self.client.patch(
                        f"{self.BASE_URL}/crm/v3/objects/contacts/{lead.external_crm_id}",
                        headers=self._get_headers(),
                        json=contact_data
                    )
                else:
                    response = await self.client.post(
                        f"{self.BASE_URL}/crm/v3/objects/contacts",
                        headers=self._get_headers(),
                        json=contact_data
                    )

                    if response.status_code == 201:
                        data = response.json()
                        lead.external_crm_id = data["id"]
                        lead.external_crm_type = ExternalCRMType.HUBSPOT

                if response.status_code in [200, 201]:
                    synced += 1
                    lead.last_synced_at = datetime.utcnow()
                else:
                    errors.append({
                        "lead_id": str(lead.id),
                        "error": response.text
                    })

            except Exception as e:
                errors.append({"lead_id": str(lead.id), "error": str(e)})

        return {"synced": synced, "total": len(leads), "errors": errors}

    async def sync_leads_from_external(self) -> List[Dict]:
        """Sync leads from HubSpot."""
        last_sync = self.integration.last_sync_at or datetime.utcnow() - timedelta(days=30)

        response = await self.client.post(
            f"{self.BASE_URL}/crm/v3/objects/contacts/search",
            headers=self._get_headers(),
            json={
                "filterGroups": [{
                    "filters": [{
                        "propertyName": "lastmodifieddate",
                        "operator": "GTE",
                        "value": int(last_sync.timestamp() * 1000)
                    }]
                }],
                "properties": [
                    "firstname", "lastname", "email", "phone", "company",
                    "lifecyclestage", "hs_lead_status", "website"
                ],
                "limit": 100
            }
        )

        if response.status_code != 200:
            return []

        data = response.json()
        leads = []

        for record in data.get("results", []):
            props = record.get("properties", {})
            leads.append({
                "external_crm_id": record.get("id"),
                "organization_name": props.get("company", ""),
                "contact_name": f"{props.get('firstname', '')} {props.get('lastname', '')}".strip(),
                "contact_email": props.get("email", ""),
                "contact_phone": props.get("phone"),
                "status": self._map_lead_status_from_hubspot(props.get("lifecyclestage", "")),
                "website": props.get("website")
            })

        return leads

    async def sync_contacts_to_external(self, contacts: List[CRMContact]) -> Dict[str, Any]:
        """Sync contacts to HubSpot."""
        synced = 0
        errors = []

        for contact in contacts:
            try:
                contact_data = {
                    "properties": {
                        "firstname": contact.first_name,
                        "lastname": contact.last_name,
                        "email": contact.email,
                        "phone": contact.phone or "",
                        "mobilephone": contact.mobile or "",
                        "jobtitle": contact.title or ""
                    }
                }

                if contact.external_crm_id:
                    response = await self.client.patch(
                        f"{self.BASE_URL}/crm/v3/objects/contacts/{contact.external_crm_id}",
                        headers=self._get_headers(),
                        json=contact_data
                    )
                else:
                    response = await self.client.post(
                        f"{self.BASE_URL}/crm/v3/objects/contacts",
                        headers=self._get_headers(),
                        json=contact_data
                    )

                    if response.status_code == 201:
                        data = response.json()
                        contact.external_crm_id = data["id"]

                if response.status_code in [200, 201]:
                    synced += 1
                else:
                    errors.append({"contact_id": str(contact.id), "error": response.text})

            except Exception as e:
                errors.append({"contact_id": str(contact.id), "error": str(e)})

        return {"synced": synced, "total": len(contacts), "errors": errors}

    async def sync_contacts_from_external(self) -> List[Dict]:
        """Sync contacts from HubSpot."""
        response = await self.client.get(
            f"{self.BASE_URL}/crm/v3/objects/contacts",
            headers=self._get_headers(),
            params={
                "limit": 100,
                "properties": "firstname,lastname,email,phone,mobilephone,jobtitle"
            }
        )

        if response.status_code != 200:
            return []

        data = response.json()
        return [
            {
                "external_crm_id": r.get("id"),
                "first_name": r.get("properties", {}).get("firstname", ""),
                "last_name": r.get("properties", {}).get("lastname", ""),
                "email": r.get("properties", {}).get("email", ""),
                "phone": r.get("properties", {}).get("phone"),
                "mobile": r.get("properties", {}).get("mobilephone"),
                "title": r.get("properties", {}).get("jobtitle")
            }
            for r in data.get("results", [])
        ]

    async def sync_deals_to_external(self, deals: List[CRMDeal]) -> Dict[str, Any]:
        """Sync deals to HubSpot."""
        synced = 0
        errors = []

        for deal in deals:
            try:
                deal_data = {
                    "properties": {
                        "dealname": deal.name,
                        "amount": str(deal.amount),
                        "dealstage": self._map_deal_stage_to_hubspot(deal.stage),
                        "closedate": deal.expected_close_date.isoformat() if deal.expected_close_date else "",
                        "description": deal.description or ""
                    }
                }

                if deal.external_crm_id:
                    response = await self.client.patch(
                        f"{self.BASE_URL}/crm/v3/objects/deals/{deal.external_crm_id}",
                        headers=self._get_headers(),
                        json=deal_data
                    )
                else:
                    response = await self.client.post(
                        f"{self.BASE_URL}/crm/v3/objects/deals",
                        headers=self._get_headers(),
                        json=deal_data
                    )

                    if response.status_code == 201:
                        data = response.json()
                        deal.external_crm_id = data["id"]

                if response.status_code in [200, 201]:
                    synced += 1
                else:
                    errors.append({"deal_id": str(deal.id), "error": response.text})

            except Exception as e:
                errors.append({"deal_id": str(deal.id), "error": str(e)})

        return {"synced": synced, "total": len(deals), "errors": errors}

    async def sync_deals_from_external(self) -> List[Dict]:
        """Sync deals from HubSpot."""
        response = await self.client.get(
            f"{self.BASE_URL}/crm/v3/objects/deals",
            headers=self._get_headers(),
            params={
                "limit": 100,
                "properties": "dealname,amount,dealstage,closedate,description"
            }
        )

        if response.status_code != 200:
            return []

        data = response.json()
        return [
            {
                "external_crm_id": r.get("id"),
                "name": r.get("properties", {}).get("dealname", ""),
                "amount": Decimal(str(r.get("properties", {}).get("amount", 0) or 0)),
                "stage": self._map_deal_stage_from_hubspot(r.get("properties", {}).get("dealstage", "")),
                "expected_close_date": r.get("properties", {}).get("closedate"),
                "description": r.get("properties", {}).get("description")
            }
            for r in data.get("results", [])
        ]

    def _map_lead_status_to_hubspot(self, status: LeadStatus) -> str:
        """Map lead status to HubSpot lifecycle stage."""
        mapping = {
            LeadStatus.NEW: "lead",
            LeadStatus.CONTACTED: "lead",
            LeadStatus.QUALIFIED: "marketingqualifiedlead",
            LeadStatus.PROPOSAL_SENT: "salesqualifiedlead",
            LeadStatus.NEGOTIATION: "opportunity",
            LeadStatus.WON: "customer",
            LeadStatus.LOST: "other"
        }
        return mapping.get(status, "lead")

    def _map_lead_status_to_hubspot_detailed(self, status: LeadStatus) -> str:
        """Map lead status to HubSpot detailed lead status."""
        mapping = {
            LeadStatus.NEW: "NEW",
            LeadStatus.CONTACTED: "CONNECTED",
            LeadStatus.QUALIFIED: "QUALIFIED",
            LeadStatus.PROPOSAL_SENT: "PRESENTATION_SCHEDULED",
            LeadStatus.NEGOTIATION: "DECISION_MAKER_BOUGHT_IN",
            LeadStatus.WON: "CLOSED",
            LeadStatus.LOST: "CLOSED_LOST"
        }
        return mapping.get(status, "NEW")

    def _map_lead_status_from_hubspot(self, hs_stage: str) -> LeadStatus:
        """Map HubSpot lifecycle stage to lead status."""
        mapping = {
            "lead": LeadStatus.NEW,
            "marketingqualifiedlead": LeadStatus.QUALIFIED,
            "salesqualifiedlead": LeadStatus.PROPOSAL_SENT,
            "opportunity": LeadStatus.NEGOTIATION,
            "customer": LeadStatus.WON
        }
        return mapping.get(hs_stage, LeadStatus.NEW)

    def _map_deal_stage_to_hubspot(self, stage: DealStage) -> str:
        """Map deal stage to HubSpot deal stage."""
        # These are default HubSpot pipeline stages
        mapping = {
            DealStage.PROSPECTING: "appointmentscheduled",
            DealStage.QUALIFICATION: "qualifiedtobuy",
            DealStage.NEEDS_ANALYSIS: "presentationscheduled",
            DealStage.VALUE_PROPOSITION: "presentationscheduled",
            DealStage.PROPOSAL: "decisionmakerboughtin",
            DealStage.NEGOTIATION: "contractsent",
            DealStage.CLOSED_WON: "closedwon",
            DealStage.CLOSED_LOST: "closedlost"
        }
        return mapping.get(stage, "appointmentscheduled")

    def _map_deal_stage_from_hubspot(self, hs_stage: str) -> DealStage:
        """Map HubSpot deal stage to deal stage."""
        mapping = {
            "appointmentscheduled": DealStage.PROSPECTING,
            "qualifiedtobuy": DealStage.QUALIFICATION,
            "presentationscheduled": DealStage.NEEDS_ANALYSIS,
            "decisionmakerboughtin": DealStage.PROPOSAL,
            "contractsent": DealStage.NEGOTIATION,
            "closedwon": DealStage.CLOSED_WON,
            "closedlost": DealStage.CLOSED_LOST
        }
        return mapping.get(hs_stage, DealStage.PROSPECTING)


# ===================== ZOHO CRM CONNECTOR =====================

class ZohoCRMConnector(BaseCRMConnector):
    """Zoho CRM connector."""

    BASE_URL = "https://www.zohoapis.com/crm/v3"
    AUTH_URL = "https://accounts.zoho.com/oauth/v2/token"

    async def test_connection(self) -> bool:
        """Test Zoho CRM connection."""
        try:
            await self._ensure_valid_token()
            response = await self.client.get(
                f"{self.BASE_URL}/Leads",
                headers=self._get_headers(),
                params={"per_page": 1}
            )
            return response.status_code == 200
        except Exception as e:
            logger.error("Zoho CRM connection test failed", error=str(e))
            return False

    async def refresh_token(self) -> bool:
        """Refresh Zoho OAuth token."""
        try:
            response = await self.client.post(
                self.AUTH_URL,
                params={
                    "grant_type": "refresh_token",
                    "client_id": self.integration.api_key,
                    "client_secret": self.integration.api_secret,
                    "refresh_token": self.integration.refresh_token
                }
            )

            if response.status_code == 200:
                data = response.json()
                self.integration.access_token = data["access_token"]
                self.integration.token_expires_at = datetime.utcnow() + timedelta(seconds=data.get("expires_in", 3600))
                return True
            return False
        except Exception as e:
            logger.error("Zoho token refresh failed", error=str(e))
            return False

    async def _ensure_valid_token(self):
        """Ensure access token is valid."""
        if self.integration.token_expires_at and self.integration.token_expires_at <= datetime.utcnow():
            await self.refresh_token()

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers."""
        return {
            "Authorization": f"Zoho-oauthtoken {self.integration.access_token}",
            "Content-Type": "application/json"
        }

    async def sync_leads_to_external(self, leads: List[CRMLead]) -> Dict[str, Any]:
        """Sync leads to Zoho CRM."""
        await self._ensure_valid_token()

        synced = 0
        errors = []

        for lead in leads:
            try:
                zoho_lead = {
                    "Company": lead.organization_name,
                    "First_Name": lead.contact_name.split()[0] if lead.contact_name else "",
                    "Last_Name": lead.contact_name.split()[-1] if lead.contact_name else "",
                    "Email": lead.contact_email,
                    "Phone": lead.contact_phone,
                    "Website": lead.website,
                    "No_of_Employees": lead.employee_count,
                    "Annual_Revenue": float(lead.annual_revenue) if lead.annual_revenue else None,
                    "Lead_Status": self._map_lead_status_to_zoho(lead.status),
                    "Lead_Source": self._map_lead_source_to_zoho(lead.source)
                }

                if lead.external_crm_id:
                    response = await self.client.put(
                        f"{self.BASE_URL}/Leads",
                        headers=self._get_headers(),
                        json={"data": [{**zoho_lead, "id": lead.external_crm_id}]}
                    )
                else:
                    response = await self.client.post(
                        f"{self.BASE_URL}/Leads",
                        headers=self._get_headers(),
                        json={"data": [zoho_lead]}
                    )

                    if response.status_code in [200, 201]:
                        data = response.json()
                        if data.get("data") and len(data["data"]) > 0:
                            lead.external_crm_id = data["data"][0]["details"]["id"]
                            lead.external_crm_type = ExternalCRMType.ZOHO

                if response.status_code in [200, 201]:
                    synced += 1
                    lead.last_synced_at = datetime.utcnow()
                else:
                    errors.append({"lead_id": str(lead.id), "error": response.text})

            except Exception as e:
                errors.append({"lead_id": str(lead.id), "error": str(e)})

        return {"synced": synced, "total": len(leads), "errors": errors}

    async def sync_leads_from_external(self) -> List[Dict]:
        """Sync leads from Zoho CRM."""
        await self._ensure_valid_token()

        last_sync = self.integration.last_sync_at or datetime.utcnow() - timedelta(days=30)

        response = await self.client.get(
            f"{self.BASE_URL}/Leads",
            headers=self._get_headers(),
            params={
                "per_page": 200,
                "modified_since": last_sync.strftime("%Y-%m-%dT%H:%M:%S+00:00")
            }
        )

        if response.status_code != 200:
            return []

        data = response.json()
        leads = []

        for record in data.get("data", []):
            leads.append({
                "external_crm_id": record.get("id"),
                "organization_name": record.get("Company", ""),
                "contact_name": f"{record.get('First_Name', '')} {record.get('Last_Name', '')}".strip(),
                "contact_email": record.get("Email", ""),
                "contact_phone": record.get("Phone"),
                "status": self._map_lead_status_from_zoho(record.get("Lead_Status", "")),
                "source": self._map_lead_source_from_zoho(record.get("Lead_Source", "")),
                "website": record.get("Website"),
                "employee_count": record.get("No_of_Employees"),
                "annual_revenue": Decimal(str(record.get("Annual_Revenue", 0))) if record.get("Annual_Revenue") else None
            })

        return leads

    async def sync_contacts_to_external(self, contacts: List[CRMContact]) -> Dict[str, Any]:
        """Sync contacts to Zoho CRM."""
        await self._ensure_valid_token()

        synced = 0
        errors = []

        for contact in contacts:
            try:
                zoho_contact = {
                    "First_Name": contact.first_name,
                    "Last_Name": contact.last_name,
                    "Email": contact.email,
                    "Phone": contact.phone,
                    "Mobile": contact.mobile,
                    "Title": contact.title,
                    "Department": contact.department
                }

                if contact.external_crm_id:
                    response = await self.client.put(
                        f"{self.BASE_URL}/Contacts",
                        headers=self._get_headers(),
                        json={"data": [{**zoho_contact, "id": contact.external_crm_id}]}
                    )
                else:
                    response = await self.client.post(
                        f"{self.BASE_URL}/Contacts",
                        headers=self._get_headers(),
                        json={"data": [zoho_contact]}
                    )

                    if response.status_code in [200, 201]:
                        data = response.json()
                        if data.get("data") and len(data["data"]) > 0:
                            contact.external_crm_id = data["data"][0]["details"]["id"]

                if response.status_code in [200, 201]:
                    synced += 1
                else:
                    errors.append({"contact_id": str(contact.id), "error": response.text})

            except Exception as e:
                errors.append({"contact_id": str(contact.id), "error": str(e)})

        return {"synced": synced, "total": len(contacts), "errors": errors}

    async def sync_contacts_from_external(self) -> List[Dict]:
        """Sync contacts from Zoho CRM."""
        await self._ensure_valid_token()

        response = await self.client.get(
            f"{self.BASE_URL}/Contacts",
            headers=self._get_headers(),
            params={"per_page": 200}
        )

        if response.status_code != 200:
            return []

        data = response.json()
        return [
            {
                "external_crm_id": r.get("id"),
                "first_name": r.get("First_Name", ""),
                "last_name": r.get("Last_Name", ""),
                "email": r.get("Email", ""),
                "phone": r.get("Phone"),
                "mobile": r.get("Mobile"),
                "title": r.get("Title"),
                "department": r.get("Department")
            }
            for r in data.get("data", [])
        ]

    async def sync_deals_to_external(self, deals: List[CRMDeal]) -> Dict[str, Any]:
        """Sync deals to Zoho CRM."""
        await self._ensure_valid_token()

        synced = 0
        errors = []

        for deal in deals:
            try:
                zoho_deal = {
                    "Deal_Name": deal.name,
                    "Amount": float(deal.amount),
                    "Stage": self._map_deal_stage_to_zoho(deal.stage),
                    "Probability": deal.probability,
                    "Closing_Date": deal.expected_close_date.isoformat() if deal.expected_close_date else None,
                    "Description": deal.description
                }

                if deal.external_crm_id:
                    response = await self.client.put(
                        f"{self.BASE_URL}/Deals",
                        headers=self._get_headers(),
                        json={"data": [{**zoho_deal, "id": deal.external_crm_id}]}
                    )
                else:
                    response = await self.client.post(
                        f"{self.BASE_URL}/Deals",
                        headers=self._get_headers(),
                        json={"data": [zoho_deal]}
                    )

                    if response.status_code in [200, 201]:
                        data = response.json()
                        if data.get("data") and len(data["data"]) > 0:
                            deal.external_crm_id = data["data"][0]["details"]["id"]

                if response.status_code in [200, 201]:
                    synced += 1
                else:
                    errors.append({"deal_id": str(deal.id), "error": response.text})

            except Exception as e:
                errors.append({"deal_id": str(deal.id), "error": str(e)})

        return {"synced": synced, "total": len(deals), "errors": errors}

    async def sync_deals_from_external(self) -> List[Dict]:
        """Sync deals from Zoho CRM."""
        await self._ensure_valid_token()

        response = await self.client.get(
            f"{self.BASE_URL}/Deals",
            headers=self._get_headers(),
            params={"per_page": 200}
        )

        if response.status_code != 200:
            return []

        data = response.json()
        return [
            {
                "external_crm_id": r.get("id"),
                "name": r.get("Deal_Name", ""),
                "amount": Decimal(str(r.get("Amount", 0) or 0)),
                "stage": self._map_deal_stage_from_zoho(r.get("Stage", "")),
                "probability": r.get("Probability", 0),
                "expected_close_date": r.get("Closing_Date"),
                "description": r.get("Description")
            }
            for r in data.get("data", [])
        ]

    def _map_lead_status_to_zoho(self, status: LeadStatus) -> str:
        """Map lead status to Zoho."""
        mapping = {
            LeadStatus.NEW: "Not Contacted",
            LeadStatus.CONTACTED: "Contacted",
            LeadStatus.QUALIFIED: "Contact in Future",
            LeadStatus.PROPOSAL_SENT: "Junk Lead",
            LeadStatus.WON: "Converted",
            LeadStatus.LOST: "Lost Lead"
        }
        return mapping.get(status, "Not Contacted")

    def _map_lead_status_from_zoho(self, zoho_status: str) -> LeadStatus:
        """Map Zoho status to lead status."""
        mapping = {
            "Not Contacted": LeadStatus.NEW,
            "Contacted": LeadStatus.CONTACTED,
            "Contact in Future": LeadStatus.QUALIFIED,
            "Converted": LeadStatus.WON,
            "Lost Lead": LeadStatus.LOST
        }
        return mapping.get(zoho_status, LeadStatus.NEW)

    def _map_lead_source_to_zoho(self, source: LeadSource) -> str:
        """Map lead source to Zoho."""
        mapping = {
            LeadSource.WEBSITE: "Web Download",
            LeadSource.REFERRAL: "Employee Referral",
            LeadSource.ADVERTISEMENT: "Advertisement",
            LeadSource.EMAIL_CAMPAIGN: "Email",
            LeadSource.PARTNER: "Partner"
        }
        return mapping.get(source, "None")

    def _map_lead_source_from_zoho(self, zoho_source: str) -> LeadSource:
        """Map Zoho source to lead source."""
        mapping = {
            "Web Download": LeadSource.WEBSITE,
            "Employee Referral": LeadSource.REFERRAL,
            "Advertisement": LeadSource.ADVERTISEMENT,
            "Email": LeadSource.EMAIL_CAMPAIGN,
            "Partner": LeadSource.PARTNER
        }
        return mapping.get(zoho_source, LeadSource.MANUAL_ENTRY)

    def _map_deal_stage_to_zoho(self, stage: DealStage) -> str:
        """Map deal stage to Zoho."""
        mapping = {
            DealStage.PROSPECTING: "Qualification",
            DealStage.QUALIFICATION: "Needs Analysis",
            DealStage.NEEDS_ANALYSIS: "Value Proposition",
            DealStage.VALUE_PROPOSITION: "Id. Decision Makers",
            DealStage.PROPOSAL: "Proposal/Price Quote",
            DealStage.NEGOTIATION: "Negotiation/Review",
            DealStage.CLOSED_WON: "Closed Won",
            DealStage.CLOSED_LOST: "Closed Lost"
        }
        return mapping.get(stage, "Qualification")

    def _map_deal_stage_from_zoho(self, zoho_stage: str) -> DealStage:
        """Map Zoho stage to deal stage."""
        mapping = {
            "Qualification": DealStage.PROSPECTING,
            "Needs Analysis": DealStage.QUALIFICATION,
            "Value Proposition": DealStage.NEEDS_ANALYSIS,
            "Id. Decision Makers": DealStage.VALUE_PROPOSITION,
            "Proposal/Price Quote": DealStage.PROPOSAL,
            "Negotiation/Review": DealStage.NEGOTIATION,
            "Closed Won": DealStage.CLOSED_WON,
            "Closed Lost": DealStage.CLOSED_LOST
        }
        return mapping.get(zoho_stage, DealStage.PROSPECTING)


# ===================== WEBHOOK CONNECTOR =====================

class WebhookConnector(BaseCRMConnector):
    """Custom webhook connector for any CRM."""

    async def test_connection(self) -> bool:
        """Test webhook connection."""
        try:
            response = await self.client.post(
                self.integration.webhook_url,
                headers=self._get_headers(),
                json={"event": "test", "timestamp": datetime.utcnow().isoformat()}
            )
            return response.status_code in [200, 201, 202, 204]
        except Exception as e:
            logger.error("Webhook connection test failed", error=str(e))
            return False

    async def refresh_token(self) -> bool:
        """Not needed for webhooks."""
        return True

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with signature."""
        headers = {"Content-Type": "application/json"}

        if self.integration.webhook_secret:
            # Add signature header
            timestamp = str(int(datetime.utcnow().timestamp()))
            headers["X-Webhook-Timestamp"] = timestamp

        if self.integration.api_key:
            headers["Authorization"] = f"Bearer {self.integration.api_key}"

        return headers

    def _sign_payload(self, payload: Dict) -> str:
        """Sign webhook payload."""
        if not self.integration.webhook_secret:
            return ""

        payload_str = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            self.integration.webhook_secret.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature

    async def sync_leads_to_external(self, leads: List[CRMLead]) -> Dict[str, Any]:
        """Send leads to webhook."""
        synced = 0
        errors = []

        for lead in leads:
            try:
                payload = {
                    "event": "lead.sync",
                    "timestamp": datetime.utcnow().isoformat(),
                    "data": {
                        "id": str(lead.id),
                        "organization_name": lead.organization_name,
                        "contact_name": lead.contact_name,
                        "contact_email": lead.contact_email,
                        "contact_phone": lead.contact_phone,
                        "status": lead.status.value,
                        "source": lead.source.value,
                        "lead_score": lead.lead_score,
                        "estimated_students": lead.estimated_students,
                        "interested_exams": lead.interested_exams,
                        "created_at": lead.created_at.isoformat() if lead.created_at else None
                    }
                }

                headers = self._get_headers()
                headers["X-Webhook-Signature"] = self._sign_payload(payload)

                response = await self.client.post(
                    self.integration.webhook_url,
                    headers=headers,
                    json=payload
                )

                if response.status_code in [200, 201, 202, 204]:
                    synced += 1
                    lead.last_synced_at = datetime.utcnow()

                    # Try to get external ID from response
                    try:
                        resp_data = response.json()
                        if "id" in resp_data:
                            lead.external_crm_id = str(resp_data["id"])
                            lead.external_crm_type = ExternalCRMType.CUSTOM_WEBHOOK
                    except Exception:
                        pass
                else:
                    errors.append({"lead_id": str(lead.id), "error": response.text})

            except Exception as e:
                errors.append({"lead_id": str(lead.id), "error": str(e)})

        return {"synced": synced, "total": len(leads), "errors": errors}

    async def sync_leads_from_external(self) -> List[Dict]:
        """Webhooks are push-based, no pull sync."""
        return []

    async def sync_contacts_to_external(self, contacts: List[CRMContact]) -> Dict[str, Any]:
        """Send contacts to webhook."""
        synced = 0
        errors = []

        for contact in contacts:
            try:
                payload = {
                    "event": "contact.sync",
                    "timestamp": datetime.utcnow().isoformat(),
                    "data": {
                        "id": str(contact.id),
                        "first_name": contact.first_name,
                        "last_name": contact.last_name,
                        "email": contact.email,
                        "phone": contact.phone,
                        "title": contact.title,
                        "contact_type": contact.contact_type.value
                    }
                }

                headers = self._get_headers()
                headers["X-Webhook-Signature"] = self._sign_payload(payload)

                response = await self.client.post(
                    self.integration.webhook_url,
                    headers=headers,
                    json=payload
                )

                if response.status_code in [200, 201, 202, 204]:
                    synced += 1
                else:
                    errors.append({"contact_id": str(contact.id), "error": response.text})

            except Exception as e:
                errors.append({"contact_id": str(contact.id), "error": str(e)})

        return {"synced": synced, "total": len(contacts), "errors": errors}

    async def sync_contacts_from_external(self) -> List[Dict]:
        """Webhooks are push-based, no pull sync."""
        return []

    async def sync_deals_to_external(self, deals: List[CRMDeal]) -> Dict[str, Any]:
        """Send deals to webhook."""
        synced = 0
        errors = []

        for deal in deals:
            try:
                payload = {
                    "event": "deal.sync",
                    "timestamp": datetime.utcnow().isoformat(),
                    "data": {
                        "id": str(deal.id),
                        "name": deal.name,
                        "amount": str(deal.amount),
                        "currency": deal.currency,
                        "stage": deal.stage.value,
                        "probability": deal.probability,
                        "expected_close_date": deal.expected_close_date.isoformat() if deal.expected_close_date else None
                    }
                }

                headers = self._get_headers()
                headers["X-Webhook-Signature"] = self._sign_payload(payload)

                response = await self.client.post(
                    self.integration.webhook_url,
                    headers=headers,
                    json=payload
                )

                if response.status_code in [200, 201, 202, 204]:
                    synced += 1
                else:
                    errors.append({"deal_id": str(deal.id), "error": response.text})

            except Exception as e:
                errors.append({"deal_id": str(deal.id), "error": str(e)})

        return {"synced": synced, "total": len(deals), "errors": errors}

    async def sync_deals_from_external(self) -> List[Dict]:
        """Webhooks are push-based, no pull sync."""
        return []


# ===================== CONNECTOR FACTORY =====================

class CRMConnectorFactory:
    """Factory for creating CRM connectors."""

    CONNECTORS: Dict[ExternalCRMType, Type[BaseCRMConnector]] = {
        ExternalCRMType.SALESFORCE: SalesforceConnector,
        ExternalCRMType.HUBSPOT: HubSpotConnector,
        ExternalCRMType.ZOHO: ZohoCRMConnector,
        ExternalCRMType.CUSTOM_WEBHOOK: WebhookConnector
    }

    @classmethod
    def create(cls, integration: ExternalCRMIntegration) -> BaseCRMConnector:
        """Create a connector for the integration type."""
        connector_class = cls.CONNECTORS.get(integration.crm_type)
        if not connector_class:
            raise ValueError(f"Unsupported CRM type: {integration.crm_type}")
        return connector_class(integration)


# ===================== SYNC SERVICE =====================

class CRMSyncService:
    """Service for managing CRM synchronization."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_integration(
        self,
        academy_id: uuid.UUID,
        crm_type: Optional[ExternalCRMType] = None
    ) -> Optional[ExternalCRMIntegration]:
        """Get CRM integration for an academy."""
        query = select(ExternalCRMIntegration).where(
            ExternalCRMIntegration.academy_id == academy_id,
            ExternalCRMIntegration.is_active == True,
            ExternalCRMIntegration.deleted_at.is_(None)
        )

        if crm_type:
            query = query.where(ExternalCRMIntegration.crm_type == crm_type)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def setup_integration(
        self,
        academy_id: uuid.UUID,
        crm_type: ExternalCRMType,
        credentials: Dict[str, Any],
        sync_settings: Optional[Dict] = None
    ) -> ExternalCRMIntegration:
        """Set up a new CRM integration."""
        integration = ExternalCRMIntegration(
            academy_id=academy_id,
            crm_type=crm_type,
            access_token=credentials.get("access_token"),
            refresh_token=credentials.get("refresh_token"),
            api_key=credentials.get("api_key"),
            api_secret=credentials.get("api_secret"),
            instance_url=credentials.get("instance_url"),
            webhook_url=credentials.get("webhook_url"),
            webhook_secret=credentials.get("webhook_secret"),
            is_active=True,
            **(sync_settings or {})
        )

        self.session.add(integration)
        await self.session.commit()
        await self.session.refresh(integration)

        # Test connection
        connector = CRMConnectorFactory.create(integration)
        try:
            if not await connector.test_connection():
                integration.is_active = False
                integration.last_sync_error = "Connection test failed"
                await self.session.commit()
        finally:
            await connector.close()

        return integration

    async def run_sync(
        self,
        academy_id: uuid.UUID,
        crm_type: Optional[ExternalCRMType] = None
    ) -> Dict[str, Any]:
        """Run CRM synchronization for an academy."""
        integration = await self.get_integration(academy_id, crm_type)
        if not integration:
            raise ValueError("No active CRM integration found")

        connector = CRMConnectorFactory.create(integration)

        try:
            results = {
                "leads": {"to_external": {}, "from_external": []},
                "contacts": {"to_external": {}, "from_external": []},
                "deals": {"to_external": {}, "from_external": []}
            }

            # Sync based on direction
            if integration.sync_direction in ["to_external", "bidirectional"]:
                # Get data to sync
                if integration.sync_leads:
                    leads = await self._get_leads_to_sync(academy_id, integration)
                    results["leads"]["to_external"] = await connector.sync_leads_to_external(leads)

                if integration.sync_contacts:
                    contacts = await self._get_contacts_to_sync(academy_id, integration)
                    results["contacts"]["to_external"] = await connector.sync_contacts_to_external(contacts)

                if integration.sync_deals:
                    deals = await self._get_deals_to_sync(academy_id, integration)
                    results["deals"]["to_external"] = await connector.sync_deals_to_external(deals)

            if integration.sync_direction in ["from_external", "bidirectional"]:
                if integration.sync_leads:
                    results["leads"]["from_external"] = await connector.sync_leads_from_external()
                    await self._import_leads(academy_id, results["leads"]["from_external"])

                if integration.sync_contacts:
                    results["contacts"]["from_external"] = await connector.sync_contacts_from_external()
                    await self._import_contacts(academy_id, results["contacts"]["from_external"])

                if integration.sync_deals:
                    results["deals"]["from_external"] = await connector.sync_deals_from_external()
                    await self._import_deals(academy_id, results["deals"]["from_external"])

            # Update integration status
            integration.last_sync_at = datetime.utcnow()
            integration.last_sync_status = "success"
            integration.last_sync_error = None

            total_synced = sum(
                r.get("synced", 0)
                for entity in results.values()
                for r in [entity.get("to_external", {})]
                if isinstance(r, dict)
            )
            integration.records_synced += total_synced

            await self.session.commit()

            return results

        except Exception as e:
            integration.last_sync_at = datetime.utcnow()
            integration.last_sync_status = "failed"
            integration.last_sync_error = str(e)
            await self.session.commit()
            raise

        finally:
            await connector.close()

    async def _get_leads_to_sync(
        self,
        academy_id: uuid.UUID,
        integration: ExternalCRMIntegration
    ) -> List[CRMLead]:
        """Get leads that need to be synced."""
        query = select(CRMLead).where(
            CRMLead.deleted_at.is_(None),
            or_(
                CRMLead.last_synced_at.is_(None),
                CRMLead.updated_at > CRMLead.last_synced_at
            )
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def _get_contacts_to_sync(
        self,
        academy_id: uuid.UUID,
        integration: ExternalCRMIntegration
    ) -> List[CRMContact]:
        """Get contacts that need to be synced."""
        query = select(CRMContact).where(
            CRMContact.academy_id == academy_id,
            CRMContact.deleted_at.is_(None)
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def _get_deals_to_sync(
        self,
        academy_id: uuid.UUID,
        integration: ExternalCRMIntegration
    ) -> List[CRMDeal]:
        """Get deals that need to be synced."""
        query = select(CRMDeal).where(
            CRMDeal.academy_id == academy_id,
            CRMDeal.deleted_at.is_(None)
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def _import_leads(self, academy_id: uuid.UUID, leads_data: List[Dict]):
        """Import leads from external CRM."""
        for lead_data in leads_data:
            external_id = lead_data.get("external_crm_id")
            if not external_id:
                continue

            # Check if lead exists
            existing = await self.session.execute(
                select(CRMLead).where(CRMLead.external_crm_id == external_id)
            )
            lead = existing.scalar_one_or_none()

            if lead:
                # Update existing
                for key, value in lead_data.items():
                    if key != "external_crm_id" and hasattr(lead, key):
                        setattr(lead, key, value)
            else:
                # Create new
                lead = CRMLead(**lead_data)
                self.session.add(lead)

        await self.session.commit()

    async def _import_contacts(self, academy_id: uuid.UUID, contacts_data: List[Dict]):
        """Import contacts from external CRM."""
        for contact_data in contacts_data:
            external_id = contact_data.get("external_crm_id")
            if not external_id:
                continue

            existing = await self.session.execute(
                select(CRMContact).where(CRMContact.external_crm_id == external_id)
            )
            contact = existing.scalar_one_or_none()

            if contact:
                for key, value in contact_data.items():
                    if key != "external_crm_id" and hasattr(contact, key):
                        setattr(contact, key, value)
            else:
                contact_data["academy_id"] = academy_id
                contact = CRMContact(**contact_data)
                self.session.add(contact)

        await self.session.commit()

    async def _import_deals(self, academy_id: uuid.UUID, deals_data: List[Dict]):
        """Import deals from external CRM."""
        for deal_data in deals_data:
            external_id = deal_data.get("external_crm_id")
            if not external_id:
                continue

            existing = await self.session.execute(
                select(CRMDeal).where(CRMDeal.external_crm_id == external_id)
            )
            deal = existing.scalar_one_or_none()

            if deal:
                for key, value in deal_data.items():
                    if key != "external_crm_id" and hasattr(deal, key):
                        setattr(deal, key, value)
            else:
                deal_data["academy_id"] = academy_id
                deal = CRMDeal(**deal_data)
                self.session.add(deal)

        await self.session.commit()
