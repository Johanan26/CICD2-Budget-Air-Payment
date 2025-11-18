# app/schemas.py
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field

#Enum
class PaymentStatus(str, Enum):
    PENDING = "pending"
    AUTHORIZED = "authorized"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELED = "cancled"
    REFUNDED = "refunded"

class PaymentProvider(str, Enum):
    STRIPE = "stripe"
    PAYPAL = "paypal"
    ADYEN = "adyen"
    INTERNAL = "internal"

class Currency(str, Enum):
    EUR = "EUR"
    USD = "USD"
    GBP = "GBP"

class PaymentBase(BaseModel):
    amount: Decimal = Field(..., gt=0, description="Amount to charge in major units") 
    current: Currency = Field(..., description="Currency of the payment")
    description: Optional[str] = Field(None, description="Human readable description")
    user_id: Optional[str] = Field(None, description="ID of the user making the payment")
    order_id: Optional[str] = Field(None, description="ID of the related order in your system")
    provider: PaymentProvider = Field(default=PaymentProvider.INTERNAL)
    provider_payment_id: Optional[str] = Field(None, description="ID of payment in the PSP")

class PaymentCreate(PaymentBase):
    ...

#Input models
class PaymentUpdateStatus(BaseModel):
    status: PaymentStatus
    failure_reason: Optional[str] = Field(None, description="Reason for failure / cancel if application(from provider or internal)")

class PaymentRefundCreate(BaseModel):
    payment_id: str
    amount: Optional[Decimal] = Field(None, gt=0, description="Ifomitted, refund full remaining amount")
    reason: Optional[str] = None

#Output model
class Payment(PaymentBase):
    id:str
    status: PaymentStatus = PaymentStatus.PENDING
    failure_reason: Optional[str] = None
    created_at: datetime
    update_at: datetime

    class Config:
        from_attributes = True