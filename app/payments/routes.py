from fastapi import APIRouter, Depends, Request, status, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.auth.models import User
from app.payments import razorpay
from app.config import settings
from pydantic import BaseModel

router = APIRouter(prefix="/payment", tags=["payment"])
templates = Jinja2Templates(directory="templates")

class OrderRequest(BaseModel):
    plan: str

class VerifyRequest(BaseModel):
    razorpay_payment_id: str
    razorpay_order_id: str
    razorpay_signature: str

@router.get("/upgrade", response_class=HTMLResponse)
def upgrade_page(request: Request, current_user: User = Depends(get_current_user)):
    return templates.TemplateResponse("payment/upgrade.html", {
        "request": request,
        "user": current_user,
        "plan": current_user.subscription_plan,
        "razorpay_key_id": settings.RAZORPAY_KEY_ID
    })

@router.post("/create-order")
def create_order_endpoint(
    request: OrderRequest, 
    current_user: User = Depends(get_current_user)
):
    amount = 399 # Fixed for Pro Plan
    
    try:
        order = razorpay.create_order(amount=amount, notes={"user_email": current_user.email})
        return JSONResponse(content={
            "order_id": order["id"],
            "amount": order["amount"],
            "key": settings.RAZORPAY_KEY_ID,
            "currency": order["currency"],
            "name": "Podcastr Pro",
            "description": "Unlock Pro Features",
            "prefill": {
                "name": current_user.email.split("@")[0],
                "email": current_user.email
            }
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/verify")
def verify_payment_endpoint(
    data: VerifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # Verify signature
        params_dict = {
            'razorpay_payment_id': data.razorpay_payment_id,
            'razorpay_order_id': data.razorpay_order_id,
            'razorpay_signature': data.razorpay_signature
        }
        
        # Verify will raise error if invalid
        razorpay.verify_payment_signature(params_dict)
        
        # Update User Plan
        current_user.subscription_plan = "pro"
        db.commit()
        
        return JSONResponse(content={"status": "success", "new_plan": "pro"})
        
    except Exception as e:
        raise HTTPException(status_code=400, detail="Payment verification failed")
