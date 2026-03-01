# AI SaaS Podcastr

A production-grade AI Podcast Generator built with Python (FastAPI), Jinja2, OpenAI, and Coqui TTS.

## Features
- **AI Script Generation**: Powered by Google Gemini API
- **Text-to-Speech**: Server-side audio generation using Coqui TTS
- **Authentication**: Secure Login/Register (Email/Password)
- **Payments**: Razorpay Subscription (Pro Plan)
- **Deployment Ready**: Using SQLite/PostgreSQL and FastAPI

## Prerequisites
- Python 3.9+
- Google Cloud API Key (Gemini)
- Razorpay API Keys (for payments)
- C++ Build Tools (for Coqui TTS compilation)

## Setup

1. **Clone & Install Dependencies**
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   
   pip install -r requirements.txt
   ```

2. **Environment Variables**
   Rename `.env.example` to `.env` and fill in your keys:
   ```
   OPENAI_API_KEY=sk-...
   RAZORPAY_KEY_ID=...
   RAZORPAY_KEY_SECRET=...
   ```

3. **Initialize Database**
   The application creates tables automatically on first run.

4. **Run the Server**
   ```bash
   uvicorn app.main:app --reload
   ```

5. **Access the App**
   Open http://localhost:8000

## Architecture
- `app/main.py`: Entry point
- `app/auth/`: User authentication
- `app/podcasts/`: Podcast logic & TTS integration
- `app/payments/`: Razorpay payment handling
- `templates/`: Jinja2 UI templates
- `static/`: CSS and generated audio files

## Notes
- **First Run**: The first time you generate audio, Coqui TTS will download the model (~1GB). Please be patient.
- **Audio**: Generated audio is saved in `static/uploads/`.

## Deployment (Render.com)
This project is configured for deployment on Render.

1.  Push this code to a GitHub repository.
2.  Log in to [Render.com](https://render.com).
3.  Click **New +** -> **Blueprint**.
4.  Connect your repository.
5.  Render will auto-detect `render.yaml` and prompt you for Environment Variables (`GOOGLE_API_KEY`, etc.).
6.  Click **Apply**.

> **Note**: This setup uses a Persistent Disk to save your database and audio files so they survive restarts.
