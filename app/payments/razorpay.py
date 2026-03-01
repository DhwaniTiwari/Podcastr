import razorpay
from app.config import settings

if settings.RAZORPAY_KEY_ID:
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
else:
    client = None

def create_order(amount: int, notes: dict = None, currency: str = "INR"):
    if not client:
        # Mock for dev/test if no keys
        return {"id": "order_mock_123", "amount": amount * 100, "currency": currency}
        
    data = {
        "amount": amount * 100, # Razorpay expects amount in paise
        "currency": currency,
        "payment_capture": 1,
        "notes": notes or {}
    }
    order = client.order.create(data=data)
    return order

def verify_payment_signature(params_dict):
    if not client:
        return True
    client.utility.verify_payment_signature(params_dict)
