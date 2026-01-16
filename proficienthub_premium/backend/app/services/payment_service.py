"""
ProficientHub - Payment Service

Enterprise payment processing with Stripe integration.
Handles purchases, subscriptions, payouts, and refunds.
"""

import hashlib
import hmac
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import os

# Stripe SDK would be imported in production
# import stripe


class PaymentStatus(str, Enum):
    """Payment status states."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"


class PaymentMethod(str, Enum):
    """Supported payment methods."""
    CARD = "card"
    BANK_TRANSFER = "bank_transfer"
    WALLET = "wallet"
    INVOICE = "invoice"
    PAYPAL = "paypal"


class SubscriptionStatus(str, Enum):
    """Subscription status states."""
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
    UNPAID = "unpaid"
    TRIALING = "trialing"
    PAUSED = "paused"


@dataclass
class PaymentResult:
    """Result of a payment operation."""
    success: bool
    payment_id: str
    status: PaymentStatus
    amount: Decimal
    currency: str
    method: PaymentMethod
    metadata: Dict[str, Any]
    error_message: Optional[str] = None
    stripe_payment_intent_id: Optional[str] = None
    receipt_url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "payment_id": self.payment_id,
            "status": self.status.value,
            "amount": float(self.amount),
            "currency": self.currency,
            "method": self.method.value,
            "metadata": self.metadata,
            "error_message": self.error_message,
            "stripe_payment_intent_id": self.stripe_payment_intent_id,
            "receipt_url": self.receipt_url,
        }


@dataclass
class SubscriptionResult:
    """Result of a subscription operation."""
    success: bool
    subscription_id: str
    status: SubscriptionStatus
    plan_id: str
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool
    metadata: Dict[str, Any]
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "subscription_id": self.subscription_id,
            "status": self.status.value,
            "plan_id": self.plan_id,
            "current_period_start": self.current_period_start.isoformat(),
            "current_period_end": self.current_period_end.isoformat(),
            "cancel_at_period_end": self.cancel_at_period_end,
            "metadata": self.metadata,
            "error_message": self.error_message,
        }


# ============================================================================
# PRICING PLANS
# ============================================================================

SUBSCRIPTION_PLANS = {
    "academy_starter": {
        "name": "Academy Starter",
        "description": "Perfect for small academies just getting started",
        "price_monthly": Decimal("49.00"),
        "price_yearly": Decimal("490.00"),  # ~17% discount
        "credits_monthly": 20,
        "features": [
            "20 Mock Exam Credits/month",
            "Up to 50 students",
            "Basic analytics",
            "Email support",
            "IELTS & TOEFL exams",
        ],
        "limits": {
            "max_students": 50,
            "max_teachers": 3,
            "exam_types": ["ielts_academic", "ielts_general", "toefl_ibt"],
        },
        "stripe_price_id_monthly": "price_academy_starter_monthly",
        "stripe_price_id_yearly": "price_academy_starter_yearly",
    },
    "academy_professional": {
        "name": "Academy Professional",
        "description": "For growing academies with multiple programs",
        "price_monthly": Decimal("149.00"),
        "price_yearly": Decimal("1490.00"),  # ~17% discount
        "credits_monthly": 100,
        "features": [
            "100 Mock Exam Credits/month",
            "Up to 200 students",
            "Advanced analytics",
            "Priority support",
            "All exam types",
            "Writing review credits (10/month)",
            "Custom branding",
            "API access",
        ],
        "limits": {
            "max_students": 200,
            "max_teachers": 10,
            "exam_types": "all",
            "writing_reviews_monthly": 10,
        },
        "stripe_price_id_monthly": "price_academy_pro_monthly",
        "stripe_price_id_yearly": "price_academy_pro_yearly",
    },
    "academy_enterprise": {
        "name": "Academy Enterprise",
        "description": "For large institutions and exam centers",
        "price_monthly": Decimal("449.00"),
        "price_yearly": Decimal("4490.00"),  # ~17% discount
        "credits_monthly": 500,
        "features": [
            "500 Mock Exam Credits/month",
            "Unlimited students",
            "Real-time analytics dashboard",
            "Dedicated account manager",
            "All exam types",
            "Unlimited writing reviews",
            "White-label solution",
            "Full API access",
            "SLA guarantee",
            "Marketplace access",
            "Commission-free reselling",
        ],
        "limits": {
            "max_students": -1,  # Unlimited
            "max_teachers": -1,  # Unlimited
            "exam_types": "all",
            "writing_reviews_monthly": -1,  # Unlimited
        },
        "stripe_price_id_monthly": "price_academy_enterprise_monthly",
        "stripe_price_id_yearly": "price_academy_enterprise_yearly",
    },
}

CREDIT_PACKAGES = {
    "credits_10": {
        "name": "10 Credits",
        "credits": 10,
        "price": Decimal("50.00"),
        "price_per_credit": Decimal("5.00"),
        "stripe_price_id": "price_credits_10",
    },
    "credits_25": {
        "name": "25 Credits",
        "credits": 25,
        "price": Decimal("112.50"),  # 10% discount
        "price_per_credit": Decimal("4.50"),
        "savings_percent": 10,
        "stripe_price_id": "price_credits_25",
    },
    "credits_50": {
        "name": "50 Credits",
        "credits": 50,
        "price": Decimal("200.00"),  # 20% discount
        "price_per_credit": Decimal("4.00"),
        "savings_percent": 20,
        "stripe_price_id": "price_credits_50",
    },
    "credits_100": {
        "name": "100 Credits",
        "credits": 100,
        "price": Decimal("350.00"),  # 30% discount
        "price_per_credit": Decimal("3.50"),
        "savings_percent": 30,
        "stripe_price_id": "price_credits_100",
    },
    "credits_250": {
        "name": "250 Credits",
        "credits": 250,
        "price": Decimal("750.00"),  # 40% discount
        "price_per_credit": Decimal("3.00"),
        "savings_percent": 40,
        "stripe_price_id": "price_credits_250",
    },
    "credits_500": {
        "name": "500 Credits",
        "credits": 500,
        "price": Decimal("1250.00"),  # 50% discount
        "price_per_credit": Decimal("2.50"),
        "savings_percent": 50,
        "stripe_price_id": "price_credits_500",
    },
}


# ============================================================================
# STRIPE CONFIGURATION (Mock for development)
# ============================================================================

class StripeConfig:
    """Stripe configuration and API key management."""

    def __init__(self):
        self.api_key = os.environ.get("STRIPE_API_KEY", "sk_test_mock")
        self.webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET", "whsec_mock")
        self.publishable_key = os.environ.get("STRIPE_PUBLISHABLE_KEY", "pk_test_mock")

    @property
    def is_live(self) -> bool:
        return self.api_key.startswith("sk_live_")

    def initialize(self):
        """Initialize Stripe SDK with API key."""
        # In production:
        # stripe.api_key = self.api_key
        pass


# ============================================================================
# PAYMENT SERVICE
# ============================================================================

class PaymentService:
    """
    Main payment service for processing all payment operations.
    Integrates with Stripe for card payments and handles internal wallet transactions.
    """

    def __init__(self, db_session=None):
        self.config = StripeConfig()
        self.config.initialize()
        self.db = db_session

    # ========================================================================
    # ONE-TIME PAYMENTS
    # ========================================================================

    async def create_payment_intent(
        self,
        amount: Decimal,
        currency: str = "usd",
        customer_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a Stripe payment intent for one-time payments.
        """
        # In production with Stripe:
        # intent = stripe.PaymentIntent.create(
        #     amount=int(amount * 100),  # Convert to cents
        #     currency=currency,
        #     customer=customer_id,
        #     metadata=metadata or {},
        #     automatic_payment_methods={"enabled": True},
        # )
        # return {
        #     "client_secret": intent.client_secret,
        #     "payment_intent_id": intent.id,
        # }

        # Mock response for development
        timestamp = datetime.now(timezone.utc).timestamp()
        return {
            "client_secret": f"pi_secret_{hashlib.md5(str(timestamp).encode()).hexdigest()[:24]}",
            "payment_intent_id": f"pi_{hashlib.md5(str(timestamp).encode()).hexdigest()[:24]}",
            "amount": float(amount),
            "currency": currency,
            "status": "requires_payment_method",
        }

    async def confirm_payment(
        self,
        payment_intent_id: str,
        payment_method_id: Optional[str] = None,
    ) -> PaymentResult:
        """
        Confirm a payment intent after customer provides payment method.
        """
        # In production with Stripe:
        # intent = stripe.PaymentIntent.confirm(
        #     payment_intent_id,
        #     payment_method=payment_method_id,
        # )

        # Mock successful payment
        return PaymentResult(
            success=True,
            payment_id=f"pay_{payment_intent_id[3:]}",
            status=PaymentStatus.COMPLETED,
            amount=Decimal("0"),  # Would come from Stripe
            currency="usd",
            method=PaymentMethod.CARD,
            metadata={"payment_intent_id": payment_intent_id},
            stripe_payment_intent_id=payment_intent_id,
            receipt_url=f"https://pay.stripe.com/receipts/{payment_intent_id}",
        )

    async def process_credit_purchase(
        self,
        academy_id: str,
        package_id: str,
        payment_method_id: str,
    ) -> PaymentResult:
        """
        Process a credit package purchase.
        """
        package = CREDIT_PACKAGES.get(package_id)
        if not package:
            return PaymentResult(
                success=False,
                payment_id="",
                status=PaymentStatus.FAILED,
                amount=Decimal("0"),
                currency="usd",
                method=PaymentMethod.CARD,
                metadata={},
                error_message=f"Invalid package ID: {package_id}",
            )

        # Create payment intent
        intent_data = await self.create_payment_intent(
            amount=package["price"],
            metadata={
                "type": "credit_purchase",
                "academy_id": academy_id,
                "package_id": package_id,
                "credits": package["credits"],
            },
        )

        # Confirm payment
        result = await self.confirm_payment(
            intent_data["payment_intent_id"],
            payment_method_id,
        )

        if result.success:
            # Add credits to academy account
            # In production: update database
            result.metadata["credits_added"] = package["credits"]

        return result

    # ========================================================================
    # SUBSCRIPTIONS
    # ========================================================================

    async def create_subscription(
        self,
        academy_id: str,
        plan_id: str,
        billing_cycle: str = "monthly",  # monthly or yearly
        payment_method_id: Optional[str] = None,
        trial_days: int = 0,
    ) -> SubscriptionResult:
        """
        Create a new subscription for an academy.
        """
        plan = SUBSCRIPTION_PLANS.get(plan_id)
        if not plan:
            return SubscriptionResult(
                success=False,
                subscription_id="",
                status=SubscriptionStatus.CANCELLED,
                plan_id=plan_id,
                current_period_start=datetime.now(timezone.utc),
                current_period_end=datetime.now(timezone.utc),
                cancel_at_period_end=False,
                metadata={},
                error_message=f"Invalid plan ID: {plan_id}",
            )

        # Get price ID based on billing cycle
        if billing_cycle == "yearly":
            stripe_price_id = plan["stripe_price_id_yearly"]
            price = plan["price_yearly"]
        else:
            stripe_price_id = plan["stripe_price_id_monthly"]
            price = plan["price_monthly"]

        # In production with Stripe:
        # customer = self._get_or_create_customer(academy_id)
        # subscription = stripe.Subscription.create(
        #     customer=customer.id,
        #     items=[{"price": stripe_price_id}],
        #     payment_behavior="default_incomplete",
        #     payment_settings={"payment_method_types": ["card"]},
        #     expand=["latest_invoice.payment_intent"],
        #     trial_period_days=trial_days if trial_days > 0 else None,
        #     metadata={"academy_id": academy_id, "plan_id": plan_id},
        # )

        # Mock response
        from datetime import timedelta
        now = datetime.now(timezone.utc)
        period_end = now + (timedelta(days=365) if billing_cycle == "yearly" else timedelta(days=30))

        if trial_days > 0:
            status = SubscriptionStatus.TRIALING
            period_end = now + timedelta(days=trial_days)
        else:
            status = SubscriptionStatus.ACTIVE

        return SubscriptionResult(
            success=True,
            subscription_id=f"sub_{hashlib.md5(f'{academy_id}{plan_id}'.encode()).hexdigest()[:24]}",
            status=status,
            plan_id=plan_id,
            current_period_start=now,
            current_period_end=period_end,
            cancel_at_period_end=False,
            metadata={
                "plan_name": plan["name"],
                "price": float(price),
                "billing_cycle": billing_cycle,
                "credits_monthly": plan["credits_monthly"],
            },
        )

    async def cancel_subscription(
        self,
        subscription_id: str,
        cancel_immediately: bool = False,
    ) -> SubscriptionResult:
        """
        Cancel a subscription.
        By default, cancels at period end. Set cancel_immediately=True to cancel now.
        """
        # In production with Stripe:
        # if cancel_immediately:
        #     subscription = stripe.Subscription.delete(subscription_id)
        # else:
        #     subscription = stripe.Subscription.modify(
        #         subscription_id,
        #         cancel_at_period_end=True,
        #     )

        return SubscriptionResult(
            success=True,
            subscription_id=subscription_id,
            status=SubscriptionStatus.CANCELLED if cancel_immediately else SubscriptionStatus.ACTIVE,
            plan_id="",
            current_period_start=datetime.now(timezone.utc),
            current_period_end=datetime.now(timezone.utc),
            cancel_at_period_end=not cancel_immediately,
            metadata={"cancelled_at": datetime.now(timezone.utc).isoformat()},
        )

    async def update_subscription(
        self,
        subscription_id: str,
        new_plan_id: str,
        prorate: bool = True,
    ) -> SubscriptionResult:
        """
        Upgrade or downgrade a subscription to a new plan.
        """
        plan = SUBSCRIPTION_PLANS.get(new_plan_id)
        if not plan:
            return SubscriptionResult(
                success=False,
                subscription_id=subscription_id,
                status=SubscriptionStatus.ACTIVE,
                plan_id="",
                current_period_start=datetime.now(timezone.utc),
                current_period_end=datetime.now(timezone.utc),
                cancel_at_period_end=False,
                metadata={},
                error_message=f"Invalid plan ID: {new_plan_id}",
            )

        # In production with Stripe:
        # subscription = stripe.Subscription.retrieve(subscription_id)
        # stripe.Subscription.modify(
        #     subscription_id,
        #     items=[{
        #         "id": subscription["items"]["data"][0].id,
        #         "price": plan["stripe_price_id_monthly"],
        #     }],
        #     proration_behavior="create_prorations" if prorate else "none",
        # )

        now = datetime.now(timezone.utc)
        return SubscriptionResult(
            success=True,
            subscription_id=subscription_id,
            status=SubscriptionStatus.ACTIVE,
            plan_id=new_plan_id,
            current_period_start=now,
            current_period_end=now + __import__('datetime').timedelta(days=30),
            cancel_at_period_end=False,
            metadata={
                "plan_name": plan["name"],
                "upgraded_at": now.isoformat(),
                "prorated": prorate,
            },
        )

    # ========================================================================
    # REFUNDS
    # ========================================================================

    async def create_refund(
        self,
        payment_id: str,
        amount: Optional[Decimal] = None,
        reason: str = "requested_by_customer",
    ) -> PaymentResult:
        """
        Create a refund for a payment.
        If amount is None, refunds the full amount.
        """
        # In production with Stripe:
        # refund = stripe.Refund.create(
        #     payment_intent=payment_id,
        #     amount=int(amount * 100) if amount else None,
        #     reason=reason,
        # )

        return PaymentResult(
            success=True,
            payment_id=f"re_{payment_id[3:]}",
            status=PaymentStatus.REFUNDED if amount is None else PaymentStatus.PARTIALLY_REFUNDED,
            amount=amount or Decimal("0"),
            currency="usd",
            method=PaymentMethod.CARD,
            metadata={
                "original_payment_id": payment_id,
                "reason": reason,
                "refunded_at": datetime.now(timezone.utc).isoformat(),
            },
        )

    # ========================================================================
    # PAYOUTS (for marketplace sellers)
    # ========================================================================

    async def create_payout(
        self,
        academy_id: str,
        amount: Decimal,
        destination_account: str,
        currency: str = "usd",
    ) -> Dict[str, Any]:
        """
        Create a payout to an academy's connected Stripe account.
        Used for marketplace commission payouts.
        """
        # In production with Stripe Connect:
        # payout = stripe.Payout.create(
        #     amount=int(amount * 100),
        #     currency=currency,
        #     destination=destination_account,
        #     metadata={"academy_id": academy_id},
        # )

        return {
            "success": True,
            "payout_id": f"po_{hashlib.md5(f'{academy_id}{amount}'.encode()).hexdigest()[:24]}",
            "amount": float(amount),
            "currency": currency,
            "status": "pending",
            "arrival_date": (datetime.now(timezone.utc) +
                           __import__('datetime').timedelta(days=2)).isoformat(),
        }

    async def get_academy_balance(
        self,
        academy_id: str,
    ) -> Dict[str, Any]:
        """
        Get the available and pending balance for an academy.
        """
        # In production: query from database and Stripe
        return {
            "available": {
                "amount": 0.0,
                "currency": "usd",
            },
            "pending": {
                "amount": 0.0,
                "currency": "usd",
            },
            "instant_available": {
                "amount": 0.0,
                "currency": "usd",
            },
        }

    # ========================================================================
    # WEBHOOK HANDLING
    # ========================================================================

    def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str,
    ) -> bool:
        """
        Verify Stripe webhook signature.
        """
        # In production with Stripe:
        # try:
        #     stripe.Webhook.construct_event(
        #         payload, signature, self.config.webhook_secret
        #     )
        #     return True
        # except ValueError:
        #     return False

        # Mock verification
        expected = hmac.new(
            self.config.webhook_secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(f"sha256={expected}", signature)

    async def handle_webhook_event(
        self,
        event_type: str,
        event_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Handle Stripe webhook events.
        """
        handlers = {
            "payment_intent.succeeded": self._handle_payment_succeeded,
            "payment_intent.failed": self._handle_payment_failed,
            "customer.subscription.created": self._handle_subscription_created,
            "customer.subscription.updated": self._handle_subscription_updated,
            "customer.subscription.deleted": self._handle_subscription_deleted,
            "invoice.paid": self._handle_invoice_paid,
            "invoice.payment_failed": self._handle_invoice_payment_failed,
            "payout.paid": self._handle_payout_paid,
            "payout.failed": self._handle_payout_failed,
        }

        handler = handlers.get(event_type)
        if handler:
            return await handler(event_data)

        return {"handled": False, "event_type": event_type}

    async def _handle_payment_succeeded(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle successful payment."""
        payment_intent = data.get("object", {})
        metadata = payment_intent.get("metadata", {})

        if metadata.get("type") == "credit_purchase":
            # Add credits to academy
            academy_id = metadata.get("academy_id")
            credits = int(metadata.get("credits", 0))
            # In production: update database
            return {
                "handled": True,
                "action": "credits_added",
                "academy_id": academy_id,
                "credits": credits,
            }

        return {"handled": True, "action": "payment_recorded"}

    async def _handle_payment_failed(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle failed payment."""
        payment_intent = data.get("object", {})
        # In production: notify customer, retry logic
        return {"handled": True, "action": "payment_failed_recorded"}

    async def _handle_subscription_created(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle new subscription."""
        subscription = data.get("object", {})
        metadata = subscription.get("metadata", {})
        academy_id = metadata.get("academy_id")
        plan_id = metadata.get("plan_id")

        # In production: activate academy features, add monthly credits
        return {
            "handled": True,
            "action": "subscription_activated",
            "academy_id": academy_id,
            "plan_id": plan_id,
        }

    async def _handle_subscription_updated(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription update (upgrade/downgrade)."""
        return {"handled": True, "action": "subscription_updated"}

    async def _handle_subscription_deleted(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription cancellation."""
        subscription = data.get("object", {})
        metadata = subscription.get("metadata", {})
        academy_id = metadata.get("academy_id")

        # In production: downgrade academy features
        return {
            "handled": True,
            "action": "subscription_cancelled",
            "academy_id": academy_id,
        }

    async def _handle_invoice_paid(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle paid invoice (subscription renewal)."""
        invoice = data.get("object", {})
        subscription_id = invoice.get("subscription")

        # In production: add monthly credits for subscription
        return {
            "handled": True,
            "action": "subscription_renewed",
            "subscription_id": subscription_id,
        }

    async def _handle_invoice_payment_failed(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle failed invoice payment."""
        invoice = data.get("object", {})
        # In production: notify customer, retry, eventually suspend
        return {"handled": True, "action": "invoice_failed_recorded"}

    async def _handle_payout_paid(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle successful payout."""
        payout = data.get("object", {})
        # In production: update commission records
        return {"handled": True, "action": "payout_completed"}

    async def _handle_payout_failed(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle failed payout."""
        payout = data.get("object", {})
        # In production: notify academy, update records
        return {"handled": True, "action": "payout_failed_recorded"}

    # ========================================================================
    # CHECKOUT SESSION (for complex purchases)
    # ========================================================================

    async def create_checkout_session(
        self,
        academy_id: str,
        line_items: List[Dict[str, Any]],
        success_url: str,
        cancel_url: str,
        mode: str = "payment",  # payment, subscription, setup
    ) -> Dict[str, Any]:
        """
        Create a Stripe Checkout session for complex purchases.
        """
        # In production with Stripe:
        # session = stripe.checkout.Session.create(
        #     customer=customer_id,
        #     line_items=line_items,
        #     mode=mode,
        #     success_url=success_url,
        #     cancel_url=cancel_url,
        #     metadata={"academy_id": academy_id},
        # )

        session_id = f"cs_{hashlib.md5(f'{academy_id}{datetime.now(timezone.utc)}'.encode()).hexdigest()[:24]}"

        return {
            "session_id": session_id,
            "url": f"https://checkout.stripe.com/pay/{session_id}",
            "expires_at": (datetime.now(timezone.utc) +
                         __import__('datetime').timedelta(hours=24)).isoformat(),
        }

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def get_subscription_plans(self) -> Dict[str, Any]:
        """Get all available subscription plans."""
        return {
            plan_id: {
                "id": plan_id,
                "name": plan["name"],
                "description": plan["description"],
                "price_monthly": float(plan["price_monthly"]),
                "price_yearly": float(plan["price_yearly"]),
                "credits_monthly": plan["credits_monthly"],
                "features": plan["features"],
            }
            for plan_id, plan in SUBSCRIPTION_PLANS.items()
        }

    def get_credit_packages(self) -> Dict[str, Any]:
        """Get all available credit packages."""
        return {
            package_id: {
                "id": package_id,
                "name": package["name"],
                "credits": package["credits"],
                "price": float(package["price"]),
                "price_per_credit": float(package["price_per_credit"]),
                "savings_percent": package.get("savings_percent", 0),
            }
            for package_id, package in CREDIT_PACKAGES.items()
        }

    def calculate_proration(
        self,
        current_plan_id: str,
        new_plan_id: str,
        days_remaining: int,
    ) -> Dict[str, Any]:
        """
        Calculate proration for plan change.
        """
        current_plan = SUBSCRIPTION_PLANS.get(current_plan_id)
        new_plan = SUBSCRIPTION_PLANS.get(new_plan_id)

        if not current_plan or not new_plan:
            return {"error": "Invalid plan IDs"}

        current_daily = current_plan["price_monthly"] / Decimal("30")
        new_daily = new_plan["price_monthly"] / Decimal("30")

        credit = current_daily * days_remaining
        charge = new_daily * days_remaining
        net = charge - credit

        return {
            "credit": float(credit),
            "charge": float(charge),
            "net_amount": float(net),
            "is_upgrade": net > 0,
            "days_remaining": days_remaining,
        }


# ============================================================================
# INVOICE SERVICE
# ============================================================================

class InvoiceService:
    """
    Service for managing invoices for enterprise customers.
    """

    async def create_invoice(
        self,
        academy_id: str,
        items: List[Dict[str, Any]],
        due_days: int = 30,
    ) -> Dict[str, Any]:
        """
        Create an invoice for enterprise customers who pay by invoice.
        """
        subtotal = sum(Decimal(str(item["amount"])) for item in items)
        tax_rate = Decimal("0.0")  # Configure based on jurisdiction
        tax_amount = subtotal * tax_rate
        total = subtotal + tax_amount

        invoice_number = f"INV-{academy_id[:8].upper()}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M')}"
        due_date = datetime.now(timezone.utc) + __import__('datetime').timedelta(days=due_days)

        return {
            "invoice_number": invoice_number,
            "academy_id": academy_id,
            "items": items,
            "subtotal": float(subtotal),
            "tax_rate": float(tax_rate),
            "tax_amount": float(tax_amount),
            "total": float(total),
            "currency": "USD",
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "due_date": due_date.isoformat(),
            "payment_instructions": {
                "bank_name": "ProficientHub Bank",
                "account_number": "****1234",
                "routing_number": "****5678",
                "reference": invoice_number,
            },
        }

    async def mark_invoice_paid(
        self,
        invoice_number: str,
        payment_method: str = "bank_transfer",
        payment_reference: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Mark an invoice as paid.
        """
        return {
            "invoice_number": invoice_number,
            "status": "paid",
            "paid_at": datetime.now(timezone.utc).isoformat(),
            "payment_method": payment_method,
            "payment_reference": payment_reference,
        }


# ============================================================================
# FACTORY FUNCTION
# ============================================================================

def create_payment_service(db_session=None) -> PaymentService:
    """Factory function to create a payment service instance."""
    return PaymentService(db_session=db_session)


def create_invoice_service() -> InvoiceService:
    """Factory function to create an invoice service instance."""
    return InvoiceService()
