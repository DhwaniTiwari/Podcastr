from fastapi import APIRouter, Depends, HTTPException, status, Request, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import models, utils
from app.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="templates")

@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request})

@router.post("/register")
def register(
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == email).first()
    if user:
        return templates.TemplateResponse("auth/register.html", {"request": request, "error": "Email already registered"})
    
    hashed_password = utils.get_password_hash(password)
    new_user = models.User(email=email, hashed_password=hashed_password, full_name=full_name)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})

@router.post("/login")
def login(
    request: Request,
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not utils.verify_password(password, user.hashed_password):
        return templates.TemplateResponse("auth/login.html", {"request": request, "error": "Invalid credentials"})
    
    access_token = utils.create_access_token(data={"sub": user.email})
    
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True, path="/")
    return response

@router.get("/logout")
def logout(response: Response):
    response = RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("access_token")
    return response
