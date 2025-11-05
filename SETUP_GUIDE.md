# 🚀 MindMirror AI - Complete Setup Guide

This guide will walk you through setting up MindMirror AI from scratch, including all required accounts and configurations.

---

## 📋 Prerequisites

Before you begin, ensure you have:
- **Node.js 18+** and npm installed
- **Python 3.9+** installed
- A **Google Account** for OAuth and Drive API
- A **Hugging Face account** (free) for AI models

---

## 🔧 Step 1: Google Cloud Setup

### 1.1 Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Create Project"**
3. Name it **"MindMirror AI"**
4. Click **"Create"**

### 1.2 Enable Required APIs

1. In your project, go to **"APIs & Services" > "Library"**
2. Search and enable:
   - **Google Drive API**
   - **Google+ API** (for OAuth)

### 1.3 Create OAuth 2.0 Credentials

1. Go to **"APIs & Services" > "Credentials"**
2. Click **"Create Credentials" > "OAuth client ID"**
3. Configure consent screen if prompted:
   - User Type: **External**
   - App name: **MindMirror AI**
   - User support email: Your email
   - Developer contact: Your email
   - Scopes: Add `openid`, `profile`, `email`, and `https://www.googleapis.com/auth/drive.file`
4. Create OAuth client ID:
   - Application type: **Web application**
   - Name: **MindMirror AI Web Client**
   - Authorized JavaScript origins:
     - `http://localhost:3000`
     - `https://your-production-domain.com` (add later)
   - Authorized redirect URIs:
     - `http://localhost:8000/auth/callback`
     - `https://your-api-domain.com/auth/callback` (add later)
5. Click **"Create"**
6. **Save your Client ID and Client Secret** - you'll need these!

---

## 🤖 Step 2: Hugging Face Setup

### 2.1 Create Account and Get API Token

1. Go to [Hugging Face](https://huggingface.co/)
2. Sign up for a free account
3. Go to **Settings > Access Tokens**
4. Click **"New token"**
5. Name it **"MindMirror AI"**
6. Select **"Read"** permission
7. Click **"Generate"**
8. **Copy and save your token** securely

---

## 💻 Step 3: Backend Setup

### 3.1 Navigate to Backend Directory

```bash
cd backend
```

### 3.2 Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3.3 Install Dependencies

```bash
pip install -r requirements.txt
```

### 3.4 Configure Environment Variables

1. Copy the example environment file:
```bash
copy .env.example .env  # Windows
cp .env.example .env    # macOS/Linux
```

2. Edit `.env` file with your actual values:
```env
SECRET_KEY=your-generated-secret-key-here
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback
FRONTEND_URL=http://localhost:3000
HUGGINGFACE_API_TOKEN=your-huggingface-token
```

**Generate a secure SECRET_KEY:**
```bash
# Python
python -c "import secrets; print(secrets.token_hex(32))"

# Or OpenSSL
openssl rand -hex 32
```

### 3.5 Test Backend

```bash
uvicorn main:app --reload --port 8000
```

Visit `http://localhost:8000` - you should see:
```json
{
  "message": "🧠 Welcome to MindMirror AI",
  "status": "healthy",
  "version": "1.0.0"
}
```

---

## 🎨 Step 4: Frontend Setup

### 4.1 Navigate to Frontend Directory

Open a **new terminal** and:
```bash
cd frontend
```

### 4.2 Install Dependencies

```bash
npm install
```

### 4.3 Configure Environment Variables

1. Copy the example environment file:
```bash
copy .env.example .env  # Windows
cp .env.example .env    # macOS/Linux
```

2. Edit `.env` file:
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
```

**Important:** Use the **same Google Client ID** as in the backend!

### 4.4 Start Frontend

```bash
npm start
```

The app will open at `http://localhost:3000`

---

## ✅ Step 5: Test the Application

### 5.1 Sign In

1. Click **"Continue with Google"**
2. Select your Google account
3. Grant permissions for:
   - View your email and profile
   - Access Google Drive files

### 5.2 Test Multi-Modal Input

Try each input type:

**Text:**
- Write: "I'm feeling happy today because I accomplished my goals!"
- Click "Generate Reflection"

**Voice:**
- Click "Start Recording"
- Speak for a few seconds
- Click "Stop Recording"
- Submit for reflection

**Image:**
- Upload a photo or drawing
- Add an optional caption
- Generate reflection

**Video:**
- Upload a short video clip
- Generate reflection

### 5.3 Explore Features

- **Timeline:** View your mood history
- **Gallery:** Browse your uploaded content
- **Stats:** Check your emotional wellness statistics

---

## 🚀 Step 6: Deployment (Optional)

### 6.1 Deploy Backend to Render

1. Create account at [Render.com](https://render.com/)
2. Click **"New +"** > **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - Name: `mindmirror-ai-backend`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables (same as local `.env`)
6. Click **"Create Web Service"**
7. Copy your deployment URL (e.g., `https://mindmirror-ai-backend.onrender.com`)

### 6.2 Deploy Frontend to Vercel

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Deploy:
```bash
cd frontend
vercel --prod
```

3. Follow prompts and set environment variables:
   - `REACT_APP_API_URL`: Your Render backend URL
   - `REACT_APP_GOOGLE_CLIENT_ID`: Your Google Client ID

### 6.3 Update Google OAuth Settings

1. Go back to Google Cloud Console
2. Add your production URLs to OAuth credentials:
   - Authorized JavaScript origins: `https://your-vercel-domain.vercel.app`
   - Authorized redirect URIs: `https://your-render-backend.onrender.com/auth/callback`

---

## 🔍 Troubleshooting

### Backend Issues

**Port already in use:**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:8000 | xargs kill -9
```

**Module not found:**
```bash
pip install -r requirements.txt --force-reinstall
```

**Google Drive API errors:**
- Ensure Drive API is enabled in Google Cloud Console
- Check that OAuth scopes include `https://www.googleapis.com/auth/drive.file`

### Frontend Issues

**React not starting:**
```bash
rm -rf node_modules package-lock.json
npm install
npm start
```

**Google Sign-In not working:**
- Verify `REACT_APP_GOOGLE_CLIENT_ID` matches backend
- Check browser console for errors
- Ensure localhost:3000 is in authorized origins

**CORS errors:**
- Verify `FRONTEND_URL` in backend `.env` is correct
- Check backend is running on correct port

### AI Model Issues

**Hugging Face API rate limits:**
- Free tier has rate limits
- Wait a few minutes between requests
- Consider upgrading to Pro tier for production

**Model loading errors:**
- Verify `HUGGINGFACE_API_TOKEN` is correct
- Check token has "Read" permission
- Try alternative models in `config.py`

---

## 📚 Additional Resources

- [Google Drive API Documentation](https://developers.google.com/drive/api/guides/about-sdk)
- [Hugging Face Inference API](https://huggingface.co/docs/api-inference/index)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)

---

## 🆘 Getting Help

If you encounter issues:

1. Check the [GitHub Issues](https://github.com/yourusername/mindmirror-ai/issues)
2. Review error logs in terminal
3. Verify all environment variables are set correctly
4. Ensure all APIs are enabled in Google Cloud Console

---

## 🎉 Success!

You now have MindMirror AI running! Start your emotional wellness journey by expressing yourself through text, voice, images, or videos.

**Remember:** All your data is stored privately in YOUR Google Drive. No one else has access to your reflections.

---

**Built with ❤️ for Gen Z mental wellness**
