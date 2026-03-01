from fastapi import APIRouter, Depends, HTTPException, status, Request, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.models import User
from app.podcasts.models import Podcast, Playlist
from app.dependencies import get_current_user

router = APIRouter(prefix="/profile", tags=["profile"])
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def profile_page(request: Request, response: Response, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Fetch user's podcasts
    my_podcasts = db.query(Podcast).filter(Podcast.user_id == current_user.id).order_by(Podcast.created_at.desc()).all()
    # Fetch user's playlists
    my_playlists = db.query(Playlist).filter(Playlist.user_id == current_user.id).order_by(Playlist.created_at.desc()).all()
    
    # Prevent Caching
    response = templates.TemplateResponse("profile/index.html", {
        "request": request,
        "user": current_user,
        "podcasts": my_podcasts,
        "playlists": my_playlists
    })
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response

@router.get("/{user_id}", response_class=HTMLResponse)
async def public_profile(
    request: Request, 
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Fetch Target User
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Fetch user's podcasts
    podcasts = db.query(Podcast).filter(Podcast.user_id == user_id).order_by(Podcast.created_at.desc()).all()
    
    # Fetch user's playlists (public?) - For now show all
    playlists = db.query(Playlist).filter(Playlist.user_id == user_id).order_by(Playlist.created_at.desc()).all()
    
    # If viewing own profile, redirect to private view
    if current_user.id == user_id:
        return RedirectResponse(url="/profile", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse("profile/public.html", {
        "request": request,
        "user": current_user, # The viewer
        "target_user": target_user, # The profile owner
        "podcasts": podcasts,
        "playlists": playlists
    })

@router.post("/update")
async def update_profile(
    request: Request,
    full_name: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    current_user.full_name = full_name
    db.commit()
    return RedirectResponse(url="/profile", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/delete-podcast/{podcast_id}")
async def delete_podcast(
    podcast_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    print(f"Attempting to delete podcast {podcast_id} for user {current_user.id}")
    podcast = db.query(Podcast).filter(Podcast.id == podcast_id).first()
    
    if not podcast:
        raise HTTPException(status_code=404, detail="Podcast not found")
        
    # STRICT OWNERSHIP CHECK
    if podcast.user_id != current_user.id:
        print(f"Unauthorized delete attempt: User {current_user.id} tried to delete Podcast {podcast.id} (Owner: {podcast.user_id})")
        raise HTTPException(status_code=403, detail="Not authorized to delete this podcast")
        
    db.delete(podcast)
    db.commit()
    print(f"Podcast {podcast_id} deleted successfully.")
    
    return RedirectResponse(url="/profile", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/playlists/create")
async def create_playlist(
    title: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_playlist = Playlist(title=title, user_id=current_user.id)
    db.add(new_playlist)
    db.commit()
    return RedirectResponse(url="/profile", status_code=status.HTTP_302_FOUND)

@router.post("/playlists/{playlist_id}/add/{podcast_id}")
async def add_to_playlist(
    playlist_id: int,
    podcast_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id, Playlist.user_id == current_user.id).first()
    podcast = db.query(Podcast).filter(Podcast.id == podcast_id).first()
    
    if not playlist or not podcast:
        return JSONResponse({"error": "Not found"}, status_code=404)
        
    if podcast not in playlist.podcasts:
        playlist.podcasts.append(podcast)
        db.commit()
        
    return JSONResponse({"status": "success"})


@router.get("/playlists/{playlist_id}", response_class=HTMLResponse)
async def playlist_detail(
    request: Request,
    playlist_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    if not playlist:
         raise HTTPException(status_code=404, detail="Playlist not found")

    return templates.TemplateResponse("profile/playlist_detail.html", {
        "request": request,
        "user": current_user,
        "playlist": playlist
    })
