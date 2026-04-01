from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from app.config import settings
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure required directories exist at startup
    os.makedirs("static/uploads", exist_ok=True)
    # Create all DB tables (idempotent)
    from app.database import engine, Base
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="AI SaaS Podcastr", lifespan=lifespan)

# Ensure static and templates directories exist
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


from app.auth import routes as auth_routes
from app.database import engine, Base
from app.auth import models as auth_models
from app.podcasts import models as podcast_models

from app.podcasts import routes as podcast_routes
from app.payments import routes as payment_routes
from app.profile import routes as profile_routes

app.include_router(auth_routes.router)
app.include_router(podcast_routes.router)
app.include_router(payment_routes.router)
app.include_router(profile_routes.router)

from fastapi import HTTPException
from fastapi.responses import RedirectResponse
from fastapi.responses import PlainTextResponse
import traceback

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 401:
        response = RedirectResponse(url="/auth/login")
        response.delete_cookie("access_token") 
        return response
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    tb = traceback.format_exc()
    print(f"UNHANDLED EXCEPTION: {tb}")
    return PlainTextResponse(f"Internal Server Error:\n\n{tb}", status_code=500)



@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

