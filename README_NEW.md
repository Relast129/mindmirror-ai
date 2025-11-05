# 🧠 MindMirror AI - Privacy-First Emotional Reflection Dashboard

**CLOSED SOURCE - PROPRIETARY SOFTWARE**

> Multi-modal emotional journaling with AI-powered insights, deployed on Hugging Face Spaces + Vercel (100% free hosting)

---

## 🎯 Overview

MindMirror AI is a privacy-first emotional wellness platform that allows users to express their feelings through text, voice, images, and video. AI analyzes emotions and generates personalized reflections, poetry, and mood-based art—all stored privately in the user's own Google Drive.

### Key Features

- **🔐 Privacy-First**: All data stored in user's Google Drive only
- **🎤 Multi-Modal Input**: Text, voice, images, video
- **🤖 AI-Powered**: Emotion detection, reflection generation, mood art
- **💰 Free Hosting**: Hugging Face Spaces (backend) + Vercel (frontend)
- **🚀 No API Keys Required**: Works with free public model endpoints

---

## 🏗️ Architecture

### Backend: Gradio on Hugging Face Spaces
- **Framework**: Gradio with `api=True` for REST endpoints
- **AI Models**: Hugging Face Inference API (free tier)
- **Storage**: Google Drive API (user's account)
- **Session Management**: In-memory with TTL (ephemeral)

### Frontend: React on Vercel
- **Framework**: React 18 + Tailwind CSS
- **Deployment**: Vercel (free tier)
- **API Client**: Axios calling Gradio REST endpoints

### Data Flow
```
User → React Frontend (Vercel)
  ↓
Gradio Backend (HF Spaces)
  ↓
AI Models (HF Inference API) + Google Drive (User's Account)
```

---

## 📂 Project Structure

```
MindMirror AI/
├── backend/                    # Gradio backend
│   ├── app.py                 # Main Gradio app with API endpoints
│   ├── ai/
│   │   ├── model_registry.py  # Model configurations & fallbacks
│   │   ├── orchestrator.py    # AI pipeline coordinator
│   │   ├── emotion.py         # Emotion detection
│   │   ├── reflection.py      # Reflection & poetry generation
│   │   ├── art.py             # Mood-based art generation
│   │   └── speech.py          # Speech-to-text & TTS
│   ├── utils/
│   │   ├── google_oauth.py    # OAuth2 flow handler
│   │   ├── drive_manager.py   # Google Drive operations
│   │   ├── session_store.py   # In-memory session management
│   │   └── file_helpers.py    # File utilities
│   ├── tests/
│   │   ├── test_orchestrator.py
│   │   └── test_drive_integration.py
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── AuthButton.js
│   │   │   ├── VoiceRecorder.js
│   │   │   ├── DrawingCanvas.js
│   │   │   ├── ReflectionPanel.js
│   │   │   ├── Gallery.js
│   │   │   └── Header.js
│   │   ├── pages/
│   │   │   ├── Home.jsx
│   │   │   ├── Journal.jsx
│   │   │   └── Settings.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   └── index.jsx
│   ├── package.json
│   ├── tailwind.config.js
│   └── .env.example
│
├── Dockerfile
├── run_local.sh
├── .gitignore
├── LICENSE                     # Proprietary/Closed-source
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

1. **Google Cloud Account** (free)
2. **Hugging Face Account** (free)
3. **Vercel Account** (free)
4. **Node.js 18+** and **Python 3.10+**

### Step 1: Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project: "MindMirror AI"
3. Enable APIs:
   - Google Drive API
   - Google+ API (for OAuth)
4. Create OAuth 2.0 credentials:
   - Application type: Web application
   - Authorized JavaScript origins:
     - `http://localhost:3000` (development)
     - `https://your-app.vercel.app` (production)
   - Authorized redirect URIs:
     - `http://localhost:7860/callback` (development)
     - `https://your-username-mindmirror-ai.hf.space/callback` (production)
5. Save **Client ID** and **Client Secret**

### Step 2: Local Development

```bash
# Clone repository (private)
git clone [your-private-repo-url]
cd MindMirror-AI

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Google OAuth credentials

# Run backend
python app.py
# Backend runs on http://localhost:7860

# Frontend setup (new terminal)
cd frontend
npm install

# Configure environment
cp .env.example .env
# Edit .env:
# REACT_APP_API_URL=http://localhost:7860
# REACT_APP_GOOGLE_CLIENT_ID=your-client-id

# Run frontend
npm start
# Frontend runs on http://localhost:3000
```

### Step 3: Test Locally

1. Open `http://localhost:3000`
2. Click "Sign in with Google"
3. Authorize the app
4. Try journaling with text, voice, or images
5. View AI-generated reflections and art

---

## 🌐 Production Deployment

### Deploy Backend to Hugging Face Spaces

1. Create new Space at [huggingface.co/spaces](https://huggingface.co/spaces)
   - Name: `mindmirror-ai`
   - SDK: **Gradio**
   - Hardware: **CPU Basic** (free)

2. Push code to Space:
```bash
# Add HF Space as remote
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/mindmirror-ai
git subtree push --prefix backend hf main
```

3. Configure Space secrets (Settings → Repository secrets):
   - `GOOGLE_CLIENT_ID`: Your Google OAuth client ID
   - `GOOGLE_CLIENT_SECRET`: Your Google OAuth client secret
   - `REDIRECT_URI`: `https://YOUR_USERNAME-mindmirror-ai.hf.space/callback`
   - `FRONTEND_URL`: `https://your-app.vercel.app`
   - `HUGGINGFACE_HUB_TOKEN`: (optional, for higher rate limits)

4. Space will auto-deploy. Note your Space URL.

### Deploy Frontend to Vercel

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Deploy:
```bash
cd frontend
vercel
```

3. Configure environment variables in Vercel dashboard:
   - `REACT_APP_API_URL`: Your HF Space URL (e.g., `https://your-username-mindmirror-ai.hf.space`)
   - `REACT_APP_GOOGLE_CLIENT_ID`: Your Google OAuth client ID

4. Deploy to production:
```bash
vercel --prod
```

### Update Google OAuth

Go back to Google Cloud Console and add production URLs:
- Authorized origins: `https://your-app.vercel.app`
- Redirect URIs: `https://your-username-mindmirror-ai.hf.space/callback`

---

## 🔒 Privacy & Security

### Data Storage
- **User files**: Stored ONLY in user's Google Drive
- **No server storage**: Backend does not persist any user data
- **Session tokens**: Ephemeral, in-memory only (lost on restart)
- **Metadata**: Stored in `log.json` in user's Drive folder

### Security Considerations

⚠️ **Important Limitations on HF Spaces:**
- Sessions are in-memory and lost on container restart
- No persistent secure storage for tokens
- For production, consider:
  - Redis for session storage
  - Encrypted database for metadata
  - Always-on hosting (not serverless)

### Keeping Repository Private

**This is CLOSED SOURCE software. To keep it private:**

1. **GitHub**: Set repository to Private
2. **Never commit** `.env` files or credentials
3. **HF Spaces**: Keep Space private or use access tokens
4. **Vercel**: Projects are private by default
5. **Share access**: Only invite trusted collaborators

```bash
# Verify repository is private
git remote -v
# Should show your private repo URL

# Never push to public repos
git remote remove origin  # if accidentally added public remote
```

---

## 🧪 Testing

### Run Unit Tests

```bash
cd backend
pytest tests/test_orchestrator.py -v
```

### Run Integration Tests

Requires test Google account:

```bash
# Set test token
export GOOGLE_TEST_ACCESS_TOKEN="your_test_token"

# Run tests
pytest tests/test_drive_integration.py -v
```

### Manual Testing Checklist

- [ ] Google OAuth login flow
- [ ] Text journal entry + AI reflection
- [ ] Voice recording + transcription
- [ ] Image upload + emotion analysis
- [ ] Video upload (if implemented)
- [ ] Gallery view
- [ ] History retrieval
- [ ] Mobile responsiveness

---

## 🤖 AI Models & Fallbacks

### Model Registry

The app uses a prioritized list of free models with automatic fallbacks:

**Emotion Detection:**
1. `j-hartmann/emotion-english-distilroberta-base`
2. `nateraw/bert-base-uncased-emotion`
3. Fallback: Template-based keyword matching

**Reflection Generation:**
1. `HuggingFaceH4/zephyr-7b-beta`
2. `mistralai/Mistral-7B-Instruct-v0.1`
3. Fallback: Template-based reflections

**Art Generation:**
1. `stabilityai/stable-diffusion-2-1-base`
2. `CompVis/stable-diffusion-v1-4`
3. Fallback: Procedural SVG art

**Speech-to-Text:**
1. `openai/whisper-tiny`
2. `openai/whisper-base`
3. Fallback: Local speech_recognition (requires setup)

**Text-to-Speech:**
1. HF TTS models
2. Fallback: gTTS (Google Text-to-Speech)

### Handling Rate Limits

Free tier limitations:
- **HF Inference API**: Rate limited, may have cold starts
- **Timeouts**: 12-45s depending on model
- **Retries**: 2 retries with exponential backoff
- **Caching**: 5-minute in-memory cache for identical requests

To improve performance:
- Get HF API token (free) for higher rate limits
- Upgrade to HF Pro ($9/mo) for faster inference
- Self-host models (requires GPU)

---

## 📊 API Endpoints

### Authentication
- `POST /api/login` - Start OAuth or exchange code
- Returns: `{session_token, profile, drive_folder_id}`

### Journal Operations
- `POST /api/submit` - Submit entry (text/voice/image/video)
- Returns: `{id, timestamp, emotions, ai_reflection, poem, art_urls}`

### History
- `GET /api/history` - Get user's journal entries
- Returns: `{entries: [...], total: N}`

### Files
- `GET /api/download?file_id=...` - Download file from Drive

### Feedback
- `POST /api/feedback` - Add feedback to entry

See `backend/app.py` for full API documentation.

---

## 🐛 Troubleshooting

### Backend Issues

**"Model loading" errors:**
- First request may take 30-60s (cold start)
- Retry after a few seconds
- Check HF model status: https://status.huggingface.co/

**OAuth errors:**
- Verify redirect URI matches exactly
- Check Google Cloud Console credentials
- Ensure APIs are enabled

**Session expired:**
- Sessions last 1 hour by default
- Lost on HF Space restart
- User must re-authenticate

### Frontend Issues

**CORS errors:**
- Verify `FRONTEND_URL` in backend `.env`
- Check Vercel deployment URL matches

**"Failed to fetch" errors:**
- Backend may be cold-starting (wait 30s)
- Check backend logs in HF Space

### Performance Issues

**Slow AI generation:**
- Free tier has rate limits
- Consider HF Pro subscription
- Use caching (already implemented)

**Space keeps sleeping:**
- Free HF Spaces sleep after 48h inactivity
- Upgrade to persistent hardware ($0.60/day)
- Or accept cold starts

---

## 💡 Future Enhancements

### Short-term
- [ ] Improve video processing (ffmpeg integration)
- [ ] Add more emotion categories
- [ ] Implement mood prediction
- [ ] Export journal as PDF

### Medium-term
- [ ] Redis session storage
- [ ] Persistent metadata database
- [ ] Mobile app (React Native)
- [ ] Multi-language support

### Long-term
- [ ] Custom fine-tuned models
- [ ] Community features (opt-in)
- [ ] Therapist integration
- [ ] Enterprise version

---

## 📝 Development Notes

### Cold Start Mitigation
- HF Spaces may sleep after inactivity
- First request can take 30-60s
- Consider keep-alive pings or paid tier

### Session Management
- Current: In-memory (lost on restart)
- Production: Use Redis or encrypted DB
- Tokens expire after 1 hour

### Model Fallbacks
- Always provide template fallbacks
- Test with HF API down
- Cache successful model responses

### Cost Optimization
- Free tier sufficient for <100 users
- Monitor HF Space usage
- Upgrade selectively (backend vs frontend)

---

## 📞 Support & Contact

**This is proprietary software. For access or licensing:**
- Email: [your-email@example.com]
- Do NOT share code publicly
- Do NOT fork to public repositories

---

## 📄 License

**PROPRIETARY - ALL RIGHTS RESERVED**

This software is closed-source and private. See `LICENSE` file for details.

Copyright © 2023-2024 MindMirror AI

---

## 🙏 Acknowledgments

- Hugging Face for free model hosting
- Google for Drive API and OAuth
- Vercel for free frontend hosting
- Gradio for easy API creation

---

**Built with ❤️ for mental wellness**

*Keep this repository private. Do not share publicly.*
