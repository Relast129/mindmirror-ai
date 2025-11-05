# 🧠 MindMirror AI

**A Privacy-First, Multi-Modal Emotional Reflection Dashboard for Youth & Gen Z**

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![React](https://img.shields.io/badge/React-18.x-61DAFB?logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python)

---

## 🌟 Overview

MindMirror AI is a revolutionary mental health platform that helps youth express emotions safely through **text, voice, images, videos, or drawings**. It provides AI-generated emotional reflections, poetic insights, and mood-based abstract art—all while keeping your data 100% private in your own Google Drive.

### 🎯 Key Features

- 🔐 **Privacy-First**: All data stored in YOUR Google Drive
- 🎨 **Multi-Modal Input**: Text, voice, images, videos, drawings
- 🤖 **AI-Powered Reflections**: Emotional analysis, poetry, and personalized insights
- 🖼️ **Mood-Based Art**: AI-generated abstract visualizations
- 📊 **Mood Tracking**: Visualize emotional trends over time
- 🎮 **Gamification**: Streaks and rewards for consistent journaling
- 📱 **Responsive Design**: Works beautifully on mobile and desktop

---

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.9+
- Google Cloud Project with OAuth2 credentials
- Hugging Face API token (free tier)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/mindmirror-ai.git
cd mindmirror-ai
```

2. **Set up the backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure environment variables**

Create `backend/.env`:
```env
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback
HUGGINGFACE_API_TOKEN=your_hf_token
SECRET_KEY=your_secret_key_here
FRONTEND_URL=http://localhost:3000
```

4. **Set up the frontend**
```bash
cd ../frontend
npm install
```

Create `frontend/.env`:
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_GOOGLE_CLIENT_ID=your_google_client_id
```

5. **Run the application**

Terminal 1 (Backend):
```bash
cd backend
uvicorn main:app --reload --port 8000
```

Terminal 2 (Frontend):
```bash
cd frontend
npm start
```

Visit `http://localhost:3000` 🎉

---

## 🏗️ Project Structure

```
mindmirror-ai/
├── frontend/                 # React + Tailwind CSS
│   ├── public/
│   ├── src/
│   │   ├── components/      # UI components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API services
│   │   ├── utils/           # Utility functions
│   │   ├── App.js
│   │   └── index.js
│   ├── package.json
│   └── tailwind.config.js
│
├── backend/                  # FastAPI backend
│   ├── ai/                  # AI processing modules
│   │   ├── emotion_detector.py
│   │   ├── poetry_generator.py
│   │   ├── art_generator.py
│   │   └── voice_processor.py
│   ├── utils/               # Utilities
│   │   ├── google_drive.py
│   │   ├── auth.py
│   │   └── file_handler.py
│   ├── routers/             # API routes
│   │   ├── auth.py
│   │   ├── upload.py
│   │   ├── reflect.py
│   │   └── history.py
│   ├── main.py
│   └── requirements.txt
│
├── README.md
└── .gitignore
```

---

## 🔧 Technology Stack

### Frontend
- **React 18** - Component-based UI
- **Tailwind CSS** - Modern, responsive styling
- **Framer Motion** - Smooth animations
- **Recharts** - Data visualization
- **Lucide React** - Beautiful icons

### Backend
- **FastAPI** - High-performance Python API
- **Google Drive API** - Privacy-first storage
- **Google OAuth2** - Secure authentication

### AI/ML
- **Hugging Face Transformers** - Emotion detection
- **Stable Diffusion** - AI art generation
- **Whisper** - Speech-to-text
- **gTTS** - Text-to-speech
- **OpenAI GPT** (via Hugging Face) - Poetic reflections

---

## 📡 API Endpoints

### Authentication
- `POST /auth/google` - Initiate Google OAuth
- `GET /auth/callback` - OAuth callback
- `POST /auth/logout` - Logout user

### Upload
- `POST /upload/text` - Submit text journal
- `POST /upload/voice` - Upload voice recording
- `POST /upload/image` - Upload image/drawing
- `POST /upload/video` - Upload video clip

### Reflection
- `POST /reflect` - Generate AI reflection
- `GET /reflect/{reflection_id}` - Get specific reflection

### History
- `GET /history/moods` - Get mood timeline
- `GET /history/gallery` - Get emotional gallery
- `GET /history/stats` - Get user statistics

---

## 🎨 Features in Detail

### 1. Multi-Modal Input
Express yourself however feels natural:
- **Text Journaling**: Write your thoughts freely
- **Voice Notes**: Record your feelings (auto-transcribed)
- **Drawings**: Upload sketches or doodles
- **Photos**: Share visual moments
- **Videos**: Short clips for deeper context

### 2. AI Emotional Reflection
- **Sentiment Analysis**: Detect emotions from your input
- **Personalized Poetry**: AI-generated poems reflecting your mood
- **Empathetic Advice**: Supportive, personalized guidance
- **Mood Art**: Abstract visualizations of your emotions
- **Voice Feedback**: Optional audio reflections

### 3. Privacy & Security
- **Zero Database Storage**: All data in YOUR Google Drive
- **End-to-End Control**: You own your data completely
- **Secure OAuth**: Industry-standard authentication
- **No Third-Party Access**: Your reflections stay private

### 4. Mood Tracking
- **Timeline Visualization**: See emotional trends over time
- **Color-Coded Moods**: Intuitive visual feedback
- **Streak Tracking**: Gamified journaling consistency
- **Gallery View**: Browse your emotional journey

---

## 🚢 Deployment

### Frontend (Vercel)
```bash
cd frontend
vercel --prod
```

### Backend (Render)
1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables

### Environment Variables (Production)
Update redirect URIs and URLs to production domains.

---

## 🔑 Google Cloud Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Google Drive API and Google+ API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URIs:
   - `http://localhost:8000/auth/callback` (development)
   - `https://your-domain.com/auth/callback` (production)
6. Download credentials and add to `.env`

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md).

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Hugging Face for free AI model inference
- Google Drive API for privacy-first storage
- The open-source community

---

## 📞 Support

- 📧 Email: support@mindmirror.ai
- 💬 Discord: [Join our community](https://discord.gg/mindmirror)
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/mindmirror-ai/issues)

---

**Built with ❤️ for Gen Z mental wellness**
