# app/main.py
from fastapi import FastAPI, Depends, HTTPException, status, Response
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from .Paymentdb import engine, SessionLocal
from .Paymentmodels import Base, Payment as PaymentModel, PaymentRefund
from .Paymentschemas import PaymentStatus, PaymentProvider, Currency, PaymentBase,PaymentUpdateStatus,PaymentRefundCreate, Payment as PaymentSchema, PaymentCreate

app = FastAPI(title="Payment Processor Microservice")

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def commit_or_rollback(db: Session, error_msg: str):
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail=error_msg)
    
@app.post("/payments", response_model=PaymentSchema, status_code=status.HTTP_201_CREATED)
def create_payment(
    payload: PaymentCreate,
    db: Session = Depends(get_db)
):

    db_payment = PaymentModel(
        amount=payload.amount,
        currency= payload.currency,
        description= payload.description,
        user_id= payload.user_id,
        order_id= payload.order_id,
        provider= payload.provider,
        provider_payment_id= payload.provider_payment_id,
    )

    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment

@app.get("/payment/{payment_id}", response_model=PaymentSchema)
def get_payment(payment_id: str, db: Session = Depends(get_db),):
    #get single payment by id
    payment = db.query(PaymentModel).filter(PaymentModel.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="payment not found",)
    return payment

@app.get("/payments", response_model=List[PaymentSchema],)
def list_payments(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    
    payments = (
        db.query(PaymentModel)
        .order_by(PaymentModel.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return payments

@app.patch("/payment/{payment_id}/status", response_model= PaymentSchema)
def update_payment_status(
    payment_id: str,
    payload: PaymentUpdateStatus,
    db: Session = Depends(get_db),
):
    
    payment = db.query(PaymentModel).filter(PaymentModel.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found",)
    payment.status = payload.status
    payment.failure_reason = payload.failure_reason

    db.commit()
    db.refresh(payment)
    return payment
