from fastapi import APIRouter, Depends, Form, Request, BackgroundTasks, status, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from app.database import get_db
from app.podcasts import models, services
from app.dependencies import get_current_user
from app.auth.models import User
import uuid
import os
import shutil

router = APIRouter(prefix="", tags=["podcasts"]) 
templates = Jinja2Templates(directory="templates")

# --- Dashboard & Home ---
@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # User's own podcasts
    podcasts = db.query(models.Podcast).filter(models.Podcast.user_id == current_user.id).order_by(models.Podcast.created_at.desc()).all()
    # Top podcasts (Trending)
    top_podcasts = db.query(models.Podcast).order_by(models.Podcast.views.desc()).limit(4).all()
    
    # Top Podcasters (Users with most podcasts)
    top_users = db.query(User).join(models.Podcast).group_by(User.id).order_by(func.count(models.Podcast.id).desc()).limit(5).all()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "user": current_user, 
        "podcasts": podcasts,
        "top_podcasts": top_podcasts,
        "top_users": top_users
    })

# --- Discover ---
@router.get("/discover", response_class=HTMLResponse)
def discover_page(request: Request, q: str = "", db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(models.Podcast)
    
    if q:
        search = f"%{q}%"
        query = query.filter(models.Podcast.title.ilike(search) | models.Podcast.description.ilike(search))
    
    # Sort by views/trending
    podcasts = query.order_by(models.Podcast.views.desc()).limit(20).all()
    
    return templates.TemplateResponse("discover.html", {
        "request": request,
        "user": current_user,
        "podcasts": podcasts,
        "q": q
    })

# --- Create Flow ---

@router.get("/create", response_class=HTMLResponse)
def create_podcast_page(request: Request, current_user: User = Depends(get_current_user)):
    return templates.TemplateResponse("create_podcast.html", {"request": request, "user": current_user})

from fastapi import APIRouter, Depends, Form, Request, BackgroundTasks, status, UploadFile, File, HTTPException
# ... imports ...

# ... routes ...

@router.post("/create/generate")
def generate_script(
    request: Request,
    topic: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db) # Need DB to check/update
):
    print(f"DEBUG: Generating script for topic: {topic}", flush=True)
    # ENFORCE LIMITS
    LIMITS = {"free": 3, "pro": 30}
    user_plan = current_user.subscription_plan or "free"
    limit = LIMITS.get(user_plan, 3)

    if current_user.podcasts_used >= limit:
         print(f"DEBUG: Limit reached for user {current_user.id}", flush=True)
         return templates.TemplateResponse("create_podcast.html", {
             "request": request, 
             "user": current_user, 
             "error": f"You have reached your monthly limit of {limit} podcasts. Please upgrade to Pro.",
             "topic": topic
         })

    # Step 1: Generate Script only
    script = services.generate_script_content(topic)
    
    # ... rest ...
    print(f"DEBUG: Script generated (len: {len(script)}). Rendering create_preview.html")
    return templates.TemplateResponse("create_preview.html", {
        "request": request, 
        "user": current_user, 
        "script": script,
        "topic": topic
    })

@router.post("/create/publish")
def publish_podcast(
    request: Request,
    title: str = Form(...),
    script: str = Form(...),
    description: str = Form(""),
    thumbnail: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Step 2: Generate Audio & Save
    
    # 1. Save Thumbnail (if any)
    image_url = None
    if thumbnail and thumbnail.filename:
        os.makedirs("static/uploads", exist_ok=True)
        img_name = f"{uuid.uuid4()}_{thumbnail.filename}"
        img_path = f"static/uploads/{img_name}"
        with open(img_path, "wb") as buffer:
             shutil.copyfileobj(thumbnail.file, buffer)
        image_url = f"/static/uploads/{img_name}"

    # 2. Generate Audio
    filename = f"{uuid.uuid4()}.mp3"
    os.makedirs("static/uploads", exist_ok=True)
    filepath = f"static/uploads/{filename}"
    
    services.generate_audio_content(script, filepath)

    # 3. Save to DB
    new_podcast = models.Podcast(
        title=title, 
        description=description,
        script=script, 
        voice="default", 
        audio_path=f"/static/uploads/{filename}",
        image_path=image_url,
        user_id=current_user.id
    )
    db.add(new_podcast)
    
    # Increment Usage
    current_user.podcasts_used += 1
    db.add(current_user)
    
    db.commit()
    
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)

from pydantic import BaseModel

class TranslateRequest(BaseModel):
    target_language: str

@router.post("/podcasts/{podcast_id}/translate")
def translate_podcast_script(
    podcast_id: int,
    request: TranslateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from fastapi.responses import JSONResponse
    import uuid
    import os
    podcast = db.query(models.Podcast).filter(models.Podcast.id == podcast_id).first()
    if not podcast:
        return JSONResponse(status_code=404, content={"error": "Podcast not found"})
        
    try:
        translated_text = services.translate_text_service(podcast.script, request.target_language)
        
        # Generate translated audio
        filename = f"translated_{uuid.uuid4()}.mp3"
        os.makedirs("static/uploads", exist_ok=True)
        filepath = f"static/uploads/{filename}"
        
        services.generate_audio_content(translated_text, filepath, language=request.target_language)
        audio_url = f"/static/uploads/{filename}"
        
        return {"translated_text": translated_text, "audio_url": audio_url}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.get("/podcasts/{podcast_id}", response_class=HTMLResponse)
def podcast_detail(
    request: Request, 
    podcast_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    podcast = db.query(models.Podcast).filter(models.Podcast.id == podcast_id).first()
    if not podcast:
        raise HTTPException(status_code=404, detail="Podcast not found")
    
    # Recommendations: Fetch 3 other random/latest podcasts
    recommendations = db.query(models.Podcast).filter(models.Podcast.id != podcast_id).order_by(func.random()).limit(3).all()

    # SELF-HEALING: Check if audio file exists and is valid (>1KB)
    if podcast.audio_path:
        local_path = podcast.audio_path.lstrip("/")
        if not os.path.exists(local_path) or os.path.getsize(local_path) < 1024:
            print(f"DEBUG: Audio missing/corrupt for Podcast {podcast.id}. ABANDONING old file.", flush=True)
            
            # Generate NEW filename to avoid locks
            new_filename = f"{uuid.uuid4()}_healed.mp3"
            new_path_rel = f"static/uploads/{new_filename}"
            
            try:
                # Ensure directory exists
                os.makedirs("static/uploads", exist_ok=True)
                
                print(f"DEBUG: Regenerating to NEW path: {new_path_rel}", flush=True)
                services.generate_audio_content(podcast.script, new_path_rel)
                
                # Update DB with new path
                podcast.audio_path = f"/{new_path_rel}"
                db.commit()
                db.refresh(podcast) # <--- CRITICAL: Ensure template sees new path
                print(f"DEBUG: Database updated with new audio path: {podcast.audio_path}", flush=True)
                
            except Exception as e:
                print(f"ERROR: Failed to regenerate audio: {e}", flush=True)

    # Playlists: Fetch user's playlists for the 'Save to' modal
    my_playlists = db.query(models.Playlist).filter(models.Playlist.user_id == current_user.id).all()
        
    return templates.TemplateResponse("podcasts/detail.html", {
        "request": request, 
        "podcast": podcast,
        "user": current_user,
        "recommendations": recommendations,
        "playlists": my_playlists
    })
