"""
ProficientHub - Marketplace & Commerce Models

Sistema completo para:
1. Catálogo de productos (Mock Exams, Writing, Speaking)
2. Precios mayorista para instituciones
3. Precios de reventa personalizables por institución
4. Marketplace B2B entre instituciones
5. Sistema de comisiones

FLUJO DE NEGOCIO:
1. ProficientHub vende productos a instituciones (precio mayorista)
2. Instituciones revenden a estudiantes (precio personalizado)
3. Instituciones pueden ofrecer servicios en Marketplace
4. ProficientHub cobra comisión por transacciones de Marketplace
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import uuid4
import enum
from decimal import Decimal

from sqlalchemy import (
    String, Text, Integer, Float, Boolean, DateTime, Numeric,
    ForeignKey, Enum, JSON, Index, CheckConstraint,
    UniqueConstraint, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY

from app.db.database import Base
from app.db.models import TimestampMixin, SoftDeleteMixin


# =============================================================================
# ENUMS
# =============================================================================

class ProductType(str, enum.Enum):
    """Tipos de productos que vendemos"""
    MOCK_EXAM = "mock_exam"           # Examen simulacro completo
    WRITING_PRACTICE = "writing"       # Práctica de writing individual
    SPEAKING_PRACTICE = "speaking"     # Práctica de speaking con AI
    READING_PRACTICE = "reading"       # Práctica de reading individual
    LISTENING_PRACTICE = "listening"   # Práctica de listening individual
    BUNDLE = "bundle"                  # Paquete combinado
    COURSE = "course"                  # Curso completo
    TUTORING = "tutoring"              # Sesión de tutoría


class ProductStatus(str, enum.Enum):
    """Estado del producto"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    DISCONTINUED = "discontinued"


class OrderStatus(str, enum.Enum):
    """Estado de una orden"""
    PENDING = "pending"
    PAID = "paid"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentStatus(str, enum.Enum):
    """Estado del pago"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class MarketplaceListingStatus(str, enum.Enum):
    """Estado de un listing en el marketplace"""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    ACTIVE = "active"
    PAUSED = "paused"
    REJECTED = "rejected"
    EXPIRED = "expired"


class CommissionType(str, enum.Enum):
    """Tipo de comisión"""
    PLATFORM_FEE = "platform_fee"         # Comisión base de plataforma
    MARKETPLACE_SALE = "marketplace_sale"  # Venta en marketplace
    REFERRAL = "referral"                  # Referido
    RESALE = "resale"                      # Reventa de productos


# =============================================================================
# PRODUCT CATALOG
# =============================================================================

class Product(Base, TimestampMixin, SoftDeleteMixin):
    """
    Catálogo de productos de ProficientHub

    Los productos se venden a instituciones (B2B) con precio mayorista,
    y las instituciones los revenden a estudiantes con su precio personalizado.
    """
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4())
    )

    # Información básica
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    short_description: Mapped[str] = mapped_column(String(500), nullable=True)

    # Tipo y categoría
    product_type: Mapped[ProductType] = mapped_column(
        Enum(ProductType),
        nullable=False,
        index=True
    )
    exam_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # ielts_academic, etc.

    # Estado
    status: Mapped[ProductStatus] = mapped_column(
        Enum(ProductStatus),
        default=ProductStatus.DRAFT,
        nullable=False
    )

    # Precio mayorista (lo que paga la institución)
    wholesale_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )
    currency: Mapped[str] = mapped_column(String(3), default="EUR")

    # Precio sugerido de venta al público (MSRP)
    suggested_retail_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=True
    )

    # Precio mínimo de reventa (para proteger el mercado)
    minimum_resale_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        nullable=True
    )

    # Contenido incluido
    credits_included: Mapped[int] = mapped_column(Integer, default=1)  # Créditos de examen
    features: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)

    # Media
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # SEO
    meta_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    meta_description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Analytics
    total_sales: Mapped[int] = mapped_column(Integer, default=0)
    average_rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Relationships
    variants: Mapped[List["ProductVariant"]] = relationship(
        "ProductVariant",
        back_populates="product",
        lazy="dynamic"
    )
    academy_prices: Mapped[List["AcademyProductPrice"]] = relationship(
        "AcademyProductPrice",
        back_populates="product",
        lazy="dynamic"
    )

    __table_args__ = (
        Index("idx_products_type_status", "product_type", "status"),
        Index("idx_products_exam_type", "exam_type"),
        CheckConstraint("wholesale_price >= 0", name="check_wholesale_positive"),
    )


class ProductVariant(Base, TimestampMixin):
    """
    Variantes de un producto (ej: 5 exámenes, 10 exámenes, 20 exámenes)
    """
    __tablename__ = "product_variants"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4())
    )
    product_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)  # "5 Mock Exams"
    sku: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    # Cantidad incluida
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)  # 5, 10, 20, etc.
    credits_included: Mapped[int] = mapped_column(Integer, nullable=False)

    # Precios (sobrescribe los del producto si se especifican)
    wholesale_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    suggested_retail_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)

    # Descuento por volumen (%)
    volume_discount_percent: Mapped[float] = mapped_column(Float, default=0.0)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="variants")

    __table_args__ = (
        Index("idx_variants_product", "product_id"),
        CheckConstraint("quantity > 0", name="check_quantity_positive"),
    )


# =============================================================================
# ACADEMY PRICING (Precios personalizados por institución)
# =============================================================================

class AcademyProductPrice(Base, TimestampMixin):
    """
    Precio personalizado que una institución pone a un producto para sus estudiantes

    FLUJO:
    1. ProficientHub vende a Academia a 10€ (wholesale_price)
    2. Academia decide vender a estudiantes a 15€ (retail_price)
    3. Academia se queda con 5€ de margen
    """
    __tablename__ = "academy_product_prices"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4())
    )
    academy_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("academies.id", ondelete="CASCADE"),
        nullable=False
    )
    product_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False
    )
    variant_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("product_variants.id", ondelete="SET NULL"),
        nullable=True
    )

    # Precio que la academia cobra a sus estudiantes
    retail_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )
    currency: Mapped[str] = mapped_column(String(3), default="EUR")

    # Configuración
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True)  # Mostrar en catálogo
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)  # Destacado
    custom_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Nombre personalizado
    custom_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Promociones
    promo_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    promo_starts_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    promo_ends_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    academy: Mapped["Academy"] = relationship("Academy")
    product: Mapped["Product"] = relationship("Product", back_populates="academy_prices")

    __table_args__ = (
        UniqueConstraint("academy_id", "product_id", "variant_id", name="uq_academy_product_variant"),
        Index("idx_academy_prices", "academy_id", "is_visible"),
        CheckConstraint("retail_price >= 0", name="check_retail_positive"),
    )

    @property
    def current_price(self) -> Decimal:
        """Retorna el precio actual (promoción si aplica)"""
        now = datetime.utcnow()
        if (self.promo_price and
            self.promo_starts_at and self.promo_ends_at and
            self.promo_starts_at <= now <= self.promo_ends_at):
            return self.promo_price
        return self.retail_price


# =============================================================================
# ORDERS & PAYMENTS
# =============================================================================

class Order(Base, TimestampMixin):
    """
    Orden de compra (puede ser de institución o de estudiante)
    """
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4())
    )
    order_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    # Comprador
    buyer_type: Mapped[str] = mapped_column(String(20), nullable=False)  # "academy" or "student"
    buyer_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    buyer_academy_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("academies.id"),
        nullable=True
    )  # Si es estudiante, de qué academia

    # Vendedor (si es marketplace)
    seller_academy_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("academies.id"),
        nullable=True
    )
    is_marketplace_order: Mapped[bool] = mapped_column(Boolean, default=False)

    # Estado
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus),
        default=OrderStatus.PENDING,
        nullable=False
    )

    # Totales
    subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="EUR")

    # Comisión (si aplica)
    commission_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    commission_rate: Mapped[float] = mapped_column(Float, default=0.0)

    # Metadata
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)

    # Timestamps
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    items: Mapped[List["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="order",
        lazy="selectin"
    )
    payments: Mapped[List["Payment"]] = relationship(
        "Payment",
        back_populates="order",
        lazy="dynamic"
    )

    __table_args__ = (
        Index("idx_orders_buyer", "buyer_type", "buyer_id"),
        Index("idx_orders_status", "status"),
        Index("idx_orders_marketplace", "is_marketplace_order", "seller_academy_id"),
    )


class OrderItem(Base, TimestampMixin):
    """Item individual dentro de una orden"""
    __tablename__ = "order_items"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4())
    )
    order_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False
    )
    product_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("products.id"),
        nullable=False
    )
    variant_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("product_variants.id"),
        nullable=True
    )

    # Cantidad y precio
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    # Créditos otorgados
    credits_granted: Mapped[int] = mapped_column(Integer, default=0)

    # Snapshot del producto al momento de compra
    product_snapshot: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)

    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="items")

    __table_args__ = (
        Index("idx_order_items_order", "order_id"),
    )


class Payment(Base, TimestampMixin):
    """Registro de pago"""
    __tablename__ = "payments"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4())
    )
    order_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False
    )

    # Monto
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="EUR")

    # Método de pago
    payment_method: Mapped[str] = mapped_column(String(50), nullable=False)  # stripe, paypal, transfer
    payment_provider: Mapped[str] = mapped_column(String(50), nullable=True)

    # Estado
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus),
        default=PaymentStatus.PENDING,
        nullable=False
    )

    # IDs externos
    external_payment_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    external_transaction_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Metadata
    metadata: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamps
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="payments")

    __table_args__ = (
        Index("idx_payments_order", "order_id"),
        Index("idx_payments_status", "status"),
        Index("idx_payments_external", "external_payment_id"),
    )


# =============================================================================
# MARKETPLACE B2B
# =============================================================================

class MarketplaceListing(Base, TimestampMixin, SoftDeleteMixin):
    """
    Listing de una institución en el marketplace B2B

    Las instituciones pueden ofrecer:
    - Tutorías
    - Cursos presenciales
    - Material adicional
    - Servicios de preparación
    """
    __tablename__ = "marketplace_listings"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4())
    )
    seller_academy_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("academies.id", ondelete="CASCADE"),
        nullable=False
    )

    # Información del listing
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    short_description: Mapped[str] = mapped_column(String(500), nullable=True)

    # Categorización
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    subcategory: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tags: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)

    # Tipo de servicio
    service_type: Mapped[str] = mapped_column(String(50), nullable=False)  # tutoring, course, material
    delivery_method: Mapped[str] = mapped_column(String(50), nullable=False)  # online, presencial, hybrid

    # Estado
    status: Mapped[MarketplaceListingStatus] = mapped_column(
        Enum(MarketplaceListingStatus),
        default=MarketplaceListingStatus.DRAFT,
        nullable=False
    )

    # Precio
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    price_type: Mapped[str] = mapped_column(String(20), default="fixed")  # fixed, hourly, per_session

    # Ubicación (para servicios presenciales)
    location_city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    location_country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_remote_available: Mapped[bool] = mapped_column(Boolean, default=True)

    # Media
    images: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    video_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Disponibilidad
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    availability_schedule: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    max_bookings_per_week: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Analytics
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    inquiry_count: Mapped[int] = mapped_column(Integer, default=0)
    booking_count: Mapped[int] = mapped_column(Integer, default=0)
    average_rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Comisión específica (puede sobrescribir la default)
    custom_commission_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Fechas
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    seller_academy: Mapped["Academy"] = relationship("Academy")
    bookings: Mapped[List["MarketplaceBooking"]] = relationship(
        "MarketplaceBooking",
        back_populates="listing",
        lazy="dynamic"
    )
    reviews: Mapped[List["MarketplaceReview"]] = relationship(
        "MarketplaceReview",
        back_populates="listing",
        lazy="dynamic"
    )

    __table_args__ = (
        UniqueConstraint("seller_academy_id", "slug", name="uq_listing_slug"),
        Index("idx_listings_seller", "seller_academy_id"),
        Index("idx_listings_category", "category", "status"),
        Index("idx_listings_location", "location_city", "location_country"),
    )


class MarketplaceBooking(Base, TimestampMixin):
    """Reserva/compra de un servicio del marketplace"""
    __tablename__ = "marketplace_bookings"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4())
    )
    listing_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("marketplace_listings.id", ondelete="CASCADE"),
        nullable=False
    )

    # Comprador
    buyer_academy_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("academies.id"),
        nullable=True
    )
    buyer_user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id"),
        nullable=False
    )

    # Estado
    status: Mapped[str] = mapped_column(String(50), default="pending")

    # Detalles de la reserva
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Precio y comisión
    price_paid: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    commission_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    seller_receives: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    # Order asociada
    order_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("orders.id"),
        nullable=True
    )

    # Relationships
    listing: Mapped["MarketplaceListing"] = relationship("MarketplaceListing", back_populates="bookings")

    __table_args__ = (
        Index("idx_bookings_listing", "listing_id"),
        Index("idx_bookings_buyer", "buyer_user_id"),
    )


class MarketplaceReview(Base, TimestampMixin):
    """Review de un servicio del marketplace"""
    __tablename__ = "marketplace_reviews"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4())
    )
    listing_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("marketplace_listings.id", ondelete="CASCADE"),
        nullable=False
    )
    booking_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("marketplace_bookings.id"),
        nullable=False
    )
    reviewer_user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id"),
        nullable=False
    )

    # Rating
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Respuesta del vendedor
    seller_response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    seller_responded_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Moderación
    is_approved: Mapped[bool] = mapped_column(Boolean, default=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    listing: Mapped["MarketplaceListing"] = relationship("MarketplaceListing", back_populates="reviews")

    __table_args__ = (
        Index("idx_reviews_listing", "listing_id"),
        CheckConstraint("rating >= 1 AND rating <= 5", name="check_rating_range"),
    )


# =============================================================================
# COMMISSION SYSTEM
# =============================================================================

class CommissionConfig(Base, TimestampMixin):
    """Configuración de comisiones de la plataforma"""
    __tablename__ = "commission_configs"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4())
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    commission_type: Mapped[CommissionType] = mapped_column(
        Enum(CommissionType),
        nullable=False
    )

    # Tasas
    rate_percent: Mapped[float] = mapped_column(Float, nullable=False)  # Ej: 10.0 = 10%
    fixed_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)  # Cantidad fija adicional
    minimum_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)  # Comisión mínima

    # Aplicabilidad
    applies_to_category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    applies_to_tier: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # academy tier

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    valid_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    valid_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("idx_commission_config_type", "commission_type", "is_active"),
    )


class CommissionRecord(Base, TimestampMixin):
    """Registro de comisiones cobradas"""
    __tablename__ = "commission_records"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4())
    )

    # Origen de la comisión
    commission_type: Mapped[CommissionType] = mapped_column(Enum(CommissionType), nullable=False)
    order_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("orders.id"),
        nullable=True
    )
    booking_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("marketplace_bookings.id"),
        nullable=True
    )

    # Partes involucradas
    seller_academy_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("academies.id"),
        nullable=True
    )
    buyer_academy_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("academies.id"),
        nullable=True
    )

    # Montos
    transaction_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    commission_rate: Mapped[float] = mapped_column(Float, nullable=False)
    commission_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="EUR")

    # Estado
    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending, collected, paid_out
    collected_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    paid_out_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Metadata
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    metadata: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)

    __table_args__ = (
        Index("idx_commission_records_type", "commission_type", "status"),
        Index("idx_commission_records_seller", "seller_academy_id"),
    )


# =============================================================================
# ACADEMY WALLET (Para payouts)
# =============================================================================

class AcademyWallet(Base, TimestampMixin):
    """Balance de una academia (para recibir pagos del marketplace)"""
    __tablename__ = "academy_wallets"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4())
    )
    academy_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("academies.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    # Balances
    available_balance: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    pending_balance: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    total_earned: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    total_withdrawn: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    currency: Mapped[str] = mapped_column(String(3), default="EUR")

    # Configuración de payout
    payout_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # bank_transfer, paypal
    payout_details: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    minimum_payout: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=50)
    auto_payout: Mapped[bool] = mapped_column(Boolean, default=False)
    auto_payout_threshold: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=100)

    # Relationships
    academy: Mapped["Academy"] = relationship("Academy")
    transactions: Mapped[List["WalletTransaction"]] = relationship(
        "WalletTransaction",
        back_populates="wallet",
        lazy="dynamic"
    )


class WalletTransaction(Base, TimestampMixin):
    """Transacción en el wallet de una academia"""
    __tablename__ = "wallet_transactions"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4())
    )
    wallet_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("academy_wallets.id", ondelete="CASCADE"),
        nullable=False
    )

    # Tipo y monto
    transaction_type: Mapped[str] = mapped_column(String(50), nullable=False)  # credit, debit, payout
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    balance_after: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    # Referencia
    reference_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # order, booking, payout
    reference_id: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False), nullable=True)

    # Descripción
    description: Mapped[str] = mapped_column(String(500), nullable=False)

    # Relationships
    wallet: Mapped["AcademyWallet"] = relationship("AcademyWallet", back_populates="transactions")

    __table_args__ = (
        Index("idx_wallet_transactions", "wallet_id", "created_at"),
    )


# =============================================================================
# DEFAULT COMMISSION RATES
# =============================================================================

DEFAULT_COMMISSION_RATES = {
    CommissionType.PLATFORM_FEE: {
        "rate_percent": 3.0,  # 3% por uso de la plataforma
        "description": "Comisión base por uso de la plataforma"
    },
    CommissionType.MARKETPLACE_SALE: {
        "rate_percent": 15.0,  # 15% por ventas en marketplace
        "description": "Comisión por ventas en el marketplace B2B"
    },
    CommissionType.REFERRAL: {
        "rate_percent": 5.0,  # 5% por referidos
        "description": "Comisión por traer nuevas instituciones"
    },
    CommissionType.RESALE: {
        "rate_percent": 0.0,  # Sin comisión por reventa de productos ProficientHub
        "description": "Las instituciones se quedan con el 100% del margen de reventa"
    }
}
