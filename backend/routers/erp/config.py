"""
ERP Premium Module - Core Configuration
Multi-currency, multi-region fiscal compliance
"""
from pydantic import BaseModel
from typing import Optional, Dict, List, Any
from decimal import Decimal
from datetime import datetime

# ==================== CURRENCY CONFIGURATION ====================
# Support for 50+ currencies worldwide

SUPPORTED_CURRENCIES = {
    # Major Currencies
    "USD": {"name": "US Dollar", "symbol": "$", "decimal_places": 2},
    "EUR": {"name": "Euro", "symbol": "€", "decimal_places": 2},
    "GBP": {"name": "British Pound", "symbol": "£", "decimal_places": 2},
    "JPY": {"name": "Japanese Yen", "symbol": "¥", "decimal_places": 0},
    "CNY": {"name": "Chinese Yuan", "symbol": "¥", "decimal_places": 2},
    "CHF": {"name": "Swiss Franc", "symbol": "CHF", "decimal_places": 2},
    "CAD": {"name": "Canadian Dollar", "symbol": "C$", "decimal_places": 2},
    "AUD": {"name": "Australian Dollar", "symbol": "A$", "decimal_places": 2},
    
    # Europe
    "SEK": {"name": "Swedish Krona", "symbol": "kr", "decimal_places": 2},
    "NOK": {"name": "Norwegian Krone", "symbol": "kr", "decimal_places": 2},
    "DKK": {"name": "Danish Krone", "symbol": "kr", "decimal_places": 2},
    "PLN": {"name": "Polish Zloty", "symbol": "zł", "decimal_places": 2},
    "CZK": {"name": "Czech Koruna", "symbol": "Kč", "decimal_places": 2},
    "HUF": {"name": "Hungarian Forint", "symbol": "Ft", "decimal_places": 0},
    "RON": {"name": "Romanian Leu", "symbol": "lei", "decimal_places": 2},
    "BGN": {"name": "Bulgarian Lev", "symbol": "лв", "decimal_places": 2},
    "HRK": {"name": "Croatian Kuna", "symbol": "kn", "decimal_places": 2},
    
    # Latin America
    "MXN": {"name": "Mexican Peso", "symbol": "$", "decimal_places": 2},
    "BRL": {"name": "Brazilian Real", "symbol": "R$", "decimal_places": 2},
    "ARS": {"name": "Argentine Peso", "symbol": "$", "decimal_places": 2},
    "CLP": {"name": "Chilean Peso", "symbol": "$", "decimal_places": 0},
    "COP": {"name": "Colombian Peso", "symbol": "$", "decimal_places": 0},
    "PEN": {"name": "Peruvian Sol", "symbol": "S/", "decimal_places": 2},
    
    # Asia
    "INR": {"name": "Indian Rupee", "symbol": "₹", "decimal_places": 2},
    "BDT": {"name": "Bangladeshi Taka", "symbol": "৳", "decimal_places": 2},
    "PKR": {"name": "Pakistani Rupee", "symbol": "₨", "decimal_places": 2},
    "LKR": {"name": "Sri Lankan Rupee", "symbol": "Rs", "decimal_places": 2},
    "NPR": {"name": "Nepalese Rupee", "symbol": "₨", "decimal_places": 2},
    "KRW": {"name": "South Korean Won", "symbol": "₩", "decimal_places": 0},
    "TWD": {"name": "Taiwan Dollar", "symbol": "NT$", "decimal_places": 2},
    "HKD": {"name": "Hong Kong Dollar", "symbol": "HK$", "decimal_places": 2},
    "SGD": {"name": "Singapore Dollar", "symbol": "S$", "decimal_places": 2},
    "MYR": {"name": "Malaysian Ringgit", "symbol": "RM", "decimal_places": 2},
    "THB": {"name": "Thai Baht", "symbol": "฿", "decimal_places": 2},
    "IDR": {"name": "Indonesian Rupiah", "symbol": "Rp", "decimal_places": 0},
    "PHP": {"name": "Philippine Peso", "symbol": "₱", "decimal_places": 2},
    "VND": {"name": "Vietnamese Dong", "symbol": "₫", "decimal_places": 0},
    
    # Middle East
    "AED": {"name": "UAE Dirham", "symbol": "د.إ", "decimal_places": 2},
    "SAR": {"name": "Saudi Riyal", "symbol": "﷼", "decimal_places": 2},
    "QAR": {"name": "Qatari Riyal", "symbol": "﷼", "decimal_places": 2},
    "KWD": {"name": "Kuwaiti Dinar", "symbol": "د.ك", "decimal_places": 3},
    "BHD": {"name": "Bahraini Dinar", "symbol": "BD", "decimal_places": 3},
    "OMR": {"name": "Omani Rial", "symbol": "﷼", "decimal_places": 3},
    "ILS": {"name": "Israeli Shekel", "symbol": "₪", "decimal_places": 2},
    "TRY": {"name": "Turkish Lira", "symbol": "₺", "decimal_places": 2},
    
    # Africa
    "ZAR": {"name": "South African Rand", "symbol": "R", "decimal_places": 2},
    "NGN": {"name": "Nigerian Naira", "symbol": "₦", "decimal_places": 2},
    "KES": {"name": "Kenyan Shilling", "symbol": "KSh", "decimal_places": 2},
    "EGP": {"name": "Egyptian Pound", "symbol": "E£", "decimal_places": 2},
    "MAD": {"name": "Moroccan Dirham", "symbol": "د.م.", "decimal_places": 2},
    "GHS": {"name": "Ghanaian Cedi", "symbol": "₵", "decimal_places": 2},
    "UGX": {"name": "Ugandan Shilling", "symbol": "USh", "decimal_places": 0},
    "TZS": {"name": "Tanzanian Shilling", "symbol": "TSh", "decimal_places": 0},
    
    # Oceania
    "NZD": {"name": "New Zealand Dollar", "symbol": "NZ$", "decimal_places": 2},
    "FJD": {"name": "Fijian Dollar", "symbol": "FJ$", "decimal_places": 2},
}

# ==================== TAX/FISCAL CONFIGURATION ====================
# Regional tax rules and compliance requirements

FISCAL_REGIONS = {
    # Europe - VAT
    "EU": {
        "name": "European Union",
        "tax_type": "VAT",
        "default_rate": 20.0,
        "reverse_charge": True,
        "invoice_requirements": ["VAT number", "Sequential numbering", "Issue date", "Due date"],
        "countries": {
            "ES": {"name": "Spain", "rate": 21.0, "reduced_rates": [10.0, 4.0], "requirements": ["NIF/CIF", "SII reporting"]},
            "DE": {"name": "Germany", "rate": 19.0, "reduced_rates": [7.0], "requirements": ["USt-IdNr"]},
            "FR": {"name": "France", "rate": 20.0, "reduced_rates": [10.0, 5.5, 2.1], "requirements": ["TVA intra"]},
            "IT": {"name": "Italy", "rate": 22.0, "reduced_rates": [10.0, 5.0, 4.0], "requirements": ["Partita IVA", "SDI"]},
            "PT": {"name": "Portugal", "rate": 23.0, "reduced_rates": [13.0, 6.0], "requirements": ["NIF"]},
            "NL": {"name": "Netherlands", "rate": 21.0, "reduced_rates": [9.0], "requirements": ["BTW-nummer"]},
            "BE": {"name": "Belgium", "rate": 21.0, "reduced_rates": [12.0, 6.0], "requirements": ["TVA/BTW"]},
            "AT": {"name": "Austria", "rate": 20.0, "reduced_rates": [13.0, 10.0], "requirements": ["UID"]},
            "PL": {"name": "Poland", "rate": 23.0, "reduced_rates": [8.0, 5.0], "requirements": ["NIP"]},
            "IE": {"name": "Ireland", "rate": 23.0, "reduced_rates": [13.5, 9.0, 4.8], "requirements": ["VAT number"]},
            "GR": {"name": "Greece", "rate": 24.0, "reduced_rates": [13.0, 6.0], "requirements": ["ΑΦΜ"]},
            "SE": {"name": "Sweden", "rate": 25.0, "reduced_rates": [12.0, 6.0], "requirements": ["Momsreg"]},
            "DK": {"name": "Denmark", "rate": 25.0, "reduced_rates": [], "requirements": ["CVR"]},
            "FI": {"name": "Finland", "rate": 24.0, "reduced_rates": [14.0, 10.0], "requirements": ["ALV-numero"]},
            "NO": {"name": "Norway", "rate": 25.0, "reduced_rates": [15.0, 12.0], "requirements": ["MVA-nummer"]},
        }
    },
    
    # UK
    "UK": {
        "name": "United Kingdom",
        "tax_type": "VAT",
        "default_rate": 20.0,
        "reverse_charge": True,
        "invoice_requirements": ["VAT number", "Sequential numbering", "MTD compliance"],
        "countries": {
            "GB": {"name": "United Kingdom", "rate": 20.0, "reduced_rates": [5.0, 0.0], "requirements": ["VAT number", "MTD"]}
        }
    },
    
    # United States
    "US": {
        "name": "United States",
        "tax_type": "Sales Tax",
        "default_rate": 0.0,  # Varies by state
        "reverse_charge": False,
        "invoice_requirements": ["Business ID", "State tax ID if applicable"],
        "states": {
            "CA": {"name": "California", "rate": 7.25},
            "NY": {"name": "New York", "rate": 8.0},
            "TX": {"name": "Texas", "rate": 6.25},
            "FL": {"name": "Florida", "rate": 6.0},
            "WA": {"name": "Washington", "rate": 6.5},
            "IL": {"name": "Illinois", "rate": 6.25},
            "PA": {"name": "Pennsylvania", "rate": 6.0},
            "OH": {"name": "Ohio", "rate": 5.75},
            "GA": {"name": "Georgia", "rate": 4.0},
            "NC": {"name": "North Carolina", "rate": 4.75},
            # Add more states as needed
        }
    },
    
    # Latin America
    "LATAM": {
        "name": "Latin America",
        "tax_type": "Various",
        "default_rate": 16.0,
        "reverse_charge": False,
        "countries": {
            "MX": {"name": "Mexico", "tax_type": "IVA", "rate": 16.0, "requirements": ["RFC", "CFDI"]},
            "BR": {"name": "Brazil", "tax_type": "Multiple", "rate": 17.0, "requirements": ["CNPJ", "NF-e"]},
            "AR": {"name": "Argentina", "tax_type": "IVA", "rate": 21.0, "requirements": ["CUIT"]},
            "CL": {"name": "Chile", "tax_type": "IVA", "rate": 19.0, "requirements": ["RUT"]},
            "CO": {"name": "Colombia", "tax_type": "IVA", "rate": 19.0, "requirements": ["NIT"]},
            "PE": {"name": "Peru", "tax_type": "IGV", "rate": 18.0, "requirements": ["RUC"]},
        }
    },
    
    # Asia Pacific
    "APAC": {
        "name": "Asia Pacific",
        "tax_type": "GST/VAT",
        "default_rate": 10.0,
        "countries": {
            "IN": {"name": "India", "tax_type": "GST", "rate": 18.0, "reduced_rates": [5.0, 12.0, 28.0], "requirements": ["GSTIN"]},
            "BD": {"name": "Bangladesh", "tax_type": "VAT", "rate": 15.0, "requirements": ["BIN"]},
            "JP": {"name": "Japan", "tax_type": "Consumption Tax", "rate": 10.0, "reduced_rates": [8.0], "requirements": ["Company number"]},
            "KR": {"name": "South Korea", "tax_type": "VAT", "rate": 10.0, "requirements": ["Business Registration"]},
            "AU": {"name": "Australia", "tax_type": "GST", "rate": 10.0, "requirements": ["ABN"]},
            "NZ": {"name": "New Zealand", "tax_type": "GST", "rate": 15.0, "requirements": ["IRD number"]},
            "SG": {"name": "Singapore", "tax_type": "GST", "rate": 9.0, "requirements": ["UEN"]},
            "MY": {"name": "Malaysia", "tax_type": "SST", "rate": 10.0, "requirements": ["MyCoID"]},
            "TH": {"name": "Thailand", "tax_type": "VAT", "rate": 7.0, "requirements": ["Tax ID"]},
            "PH": {"name": "Philippines", "tax_type": "VAT", "rate": 12.0, "requirements": ["TIN"]},
            "ID": {"name": "Indonesia", "tax_type": "PPN", "rate": 11.0, "requirements": ["NPWP"]},
            "VN": {"name": "Vietnam", "tax_type": "VAT", "rate": 10.0, "requirements": ["Tax code"]},
        }
    },
    
    # Africa
    "AFRICA": {
        "name": "Africa",
        "tax_type": "VAT",
        "default_rate": 15.0,
        "countries": {
            "NG": {"name": "Nigeria", "tax_type": "VAT", "rate": 7.5, "requirements": ["TIN"]},
            "ZA": {"name": "South Africa", "tax_type": "VAT", "rate": 15.0, "requirements": ["VAT number"]},
            "KE": {"name": "Kenya", "tax_type": "VAT", "rate": 16.0, "requirements": ["PIN"]},
            "EG": {"name": "Egypt", "tax_type": "VAT", "rate": 14.0, "requirements": ["Tax Registration"]},
            "MA": {"name": "Morocco", "tax_type": "TVA", "rate": 20.0, "requirements": ["ICE"]},
            "GH": {"name": "Ghana", "tax_type": "VAT", "rate": 15.0, "requirements": ["TIN"]},
        }
    },
    
    # Middle East
    "ME": {
        "name": "Middle East",
        "tax_type": "VAT",
        "default_rate": 5.0,
        "countries": {
            "AE": {"name": "UAE", "tax_type": "VAT", "rate": 5.0, "requirements": ["TRN"]},
            "SA": {"name": "Saudi Arabia", "tax_type": "VAT", "rate": 15.0, "requirements": ["VAT number"]},
            "IL": {"name": "Israel", "tax_type": "VAT", "rate": 17.0, "requirements": ["Company ID"]},
            "TR": {"name": "Turkey", "tax_type": "KDV", "rate": 18.0, "reduced_rates": [8.0, 1.0], "requirements": ["Vergi Kimlik"]},
        }
    }
}

# ==================== INVOICE NUMBER FORMATS ====================
# Regional invoice numbering requirements

INVOICE_FORMATS = {
    "default": "{prefix}{year}{sequence:06d}",
    "ES": "F{year}-{sequence:06d}",  # Spain
    "IT": "{year}/{sequence:08d}",   # Italy (SDI)
    "MX": "{prefix}-{uuid}",          # Mexico (CFDI)
    "BR": "NF-{series}-{sequence:09d}",  # Brazil (NF-e)
    "IN": "{prefix}/{year}-{month}/{sequence:05d}",  # India (GST)
}

# ==================== CHART OF ACCOUNTS ====================
# Standard chart of accounts structure

DEFAULT_CHART_OF_ACCOUNTS = {
    "1000": {"name": "Assets", "type": "asset", "children": {
        "1100": {"name": "Current Assets", "children": {
            "1110": {"name": "Cash and Cash Equivalents"},
            "1120": {"name": "Accounts Receivable"},
            "1130": {"name": "Prepaid Expenses"},
        }},
        "1200": {"name": "Fixed Assets", "children": {
            "1210": {"name": "Equipment"},
            "1220": {"name": "Accumulated Depreciation"},
        }},
    }},
    "2000": {"name": "Liabilities", "type": "liability", "children": {
        "2100": {"name": "Current Liabilities", "children": {
            "2110": {"name": "Accounts Payable"},
            "2120": {"name": "Accrued Expenses"},
            "2130": {"name": "VAT/Tax Payable"},
            "2140": {"name": "Deferred Revenue"},
        }},
        "2200": {"name": "Long-term Liabilities", "children": {
            "2210": {"name": "Long-term Debt"},
        }},
    }},
    "3000": {"name": "Equity", "type": "equity", "children": {
        "3100": {"name": "Capital Stock"},
        "3200": {"name": "Retained Earnings"},
    }},
    "4000": {"name": "Revenue", "type": "revenue", "children": {
        "4100": {"name": "Subscription Revenue"},
        "4200": {"name": "Credit Sales"},
        "4300": {"name": "Professional Services"},
        "4400": {"name": "Other Revenue"},
    }},
    "5000": {"name": "Expenses", "type": "expense", "children": {
        "5100": {"name": "Cost of Goods Sold", "children": {
            "5110": {"name": "AI Processing Costs"},
            "5120": {"name": "Infrastructure Costs"},
        }},
        "5200": {"name": "Operating Expenses", "children": {
            "5210": {"name": "Salaries and Wages"},
            "5220": {"name": "Marketing and Advertising"},
            "5230": {"name": "Software Subscriptions"},
            "5240": {"name": "Professional Fees"},
            "5250": {"name": "Office Expenses"},
        }},
    }},
}

# ==================== MODELS ====================

class CurrencyAmount(BaseModel):
    amount: float
    currency: str
    exchange_rate: Optional[float] = 1.0
    base_amount: Optional[float] = None  # Amount in base currency

class TaxLine(BaseModel):
    tax_code: str
    tax_name: str
    rate: float
    taxable_amount: float
    tax_amount: float
    is_reverse_charge: bool = False

class FiscalSettings(BaseModel):
    region: str
    country: str
    tax_id: Optional[str] = None
    tax_type: str
    default_tax_rate: float
    invoice_prefix: str = "INV"
    invoice_format: str = "default"
    fiscal_year_start: str = "01-01"  # MM-DD
    additional_requirements: List[str] = []
