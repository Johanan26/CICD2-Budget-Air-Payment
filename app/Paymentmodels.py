from datetime import datetime
from decimal import Decimal
import uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Enum as SqlEnum, Numeric, DateTime, JSON, ForeignKey
from .Paymentschemas import PaymentStatus, PaymentProvider, Currency

class Base(DeclarativeBase):
 pass

class Payment(Base):
    __tablename__ = "payments"
    id: Mapped[str] = mapped_column(String, primary_key=True, idex=True, default=lambda: str(uuid.uuid4()))
    amount: Mapped[Decimal] = mapped_column(Numeric(10,2), nullable=False)
    currency: Mapped[Currency] = mapped_column(SqlEnum(Currency), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    user_id: Mapped[str] = mapped_column(String, index=True, nullable=True)
    order_id: Mapped[str]= mapped_column(String, index=True, nullable=True)
    provider: Mapped[PaymentProvider] = mapped_column(SqlEnum(PaymentProvider), default= PaymentStatus.PENDING, nullable=False,)
    failure_reason: Mapped[str] = mapped_column(String, nullable=True)

    create_at:Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False,)
    update_at:Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False,)
    refunds: Mapped[list["PaymentRefund"]] = relationship(back_populates="payment", cascade="all, delete-orphan",)

class PaymentRefund(Base):
    __tablename__="payment_refunds"

    id: Mapped[str] = mapped_column(String, primary_key = True, index=True, default= lambda: str(uuid.uuid4()),)
    payment_id: Mapped[str] = mapped_column(String, ForeignKey("payments.id", ondelete="CASCADE"), index=True,nullable=False,)
    amount: Mapped[Decimal] = mapped_column(Numeric(10,2), nullable=True)
    reason: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime]= mapped_column(DateTime, default=datetime.utcnow,nullable=False,)
    payment: Mapped["Payment"] = relationship(back_populates="refunds")