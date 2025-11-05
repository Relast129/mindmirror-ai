# ⚡ MindMirror AI - Quick Start Guide

Get MindMirror AI running in **under 15 minutes**!

---

## 🎯 Prerequisites

- [ ] Node.js 18+ installed ([Download](https://nodejs.org/))
- [ ] Python 3.9+ installed ([Download](https://python.org/))
- [ ] Google account
- [ ] Hugging Face account ([Sign up](https://huggingface.co/))

---

## 🚀 5-Minute Setup

### Step 1: Get API Keys (5 minutes)

#### Google OAuth (3 minutes)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project → "MindMirror AI"
3. Enable APIs: **Google Drive API** + **Google+ API**
4. Create OAuth credentials:
   - Type: Web application
   - Origins: `http://localhost:3000`
   - Redirect: `http://localhost:8000/auth/callback`
5. **Copy Client ID and Secret**

#### Hugging Face Token (2 minutes)
1. Go to [Hugging Face](https://huggingface.co/)
2. Settings → Access Tokens
3. Create new token (Read permission)
4. **Copy token**

---

### Step 2: Backend Setup (3 minutes)

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# OR (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
copy .env.example .env  # Windows
cp .env.example .env    # Mac/Linux
```

**Edit `.env` file:**
```env
SECRET_KEY=your-secret-key-here
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback
FRONTEND_URL=http://localhost:3000
HUGGINGFACE_API_TOKEN=your-hf-token
```

**Generate SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

### Step 3: Frontend Setup (2 minutes)

**Open NEW terminal:**
```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Create .env file
copy .env.example .env  # Windows
cp .env.example .env    # Mac/Linux
```

**Edit `.env` file:**
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_GOOGLE_CLIENT_ID=your-google-client-id
```

---

### Step 4: Launch! (1 minute)

**Terminal 1 (Backend):**
```bash
cd backend
uvicorn main:app --reload --port 8000
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm start
```

**Open browser:** `http://localhost:3000`

---

## ✅ Quick Test

1. **Sign In** with Google
2. **Write** a text entry: "I'm feeling great today!"
3. **Click** "Generate Reflection"
4. **View** your AI-powered reflection with poetry and art!

---

## 🎨 Try All Features

### Text Input
```
"I accomplished all my goals today and feel proud!"
```

### Voice Input
1. Click "Start Recording"
2. Speak: "I'm feeling a bit anxious about tomorrow"
3. Click "Stop" → "Generate Reflection"

### Image Upload
- Upload a photo that represents your mood
- Add caption: "Sunset that made me feel peaceful"

### Video Upload
- Upload a short video clip
- AI will transcribe audio and analyze emotions

---

## 📊 Explore Dashboard

- **Timeline:** View mood trends over time
- **Gallery:** Browse your emotional journey
- **Stats:** Check streaks and insights

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000  # Windows
lsof -ti:8000  # Mac/Linux

# Kill process if needed
taskkill /PID <PID> /F  # Windows
kill -9 <PID>  # Mac/Linux
```

### Frontend won't start
```bash
# Clear and reinstall
rm -rf node_modules package-lock.json
npm install
npm start
```

### Google Sign-In not working
- Verify Client ID matches in both `.env` files
- Check `http://localhost:3000` is in authorized origins
- Clear browser cache and cookies

### AI models slow
- First request may take 30-60 seconds (model loading)
- Subsequent requests will be faster
- Free tier has rate limits

---

## 📚 Next Steps

- **Read:** [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed setup
- **Deploy:** [DEPLOYMENT.md](DEPLOYMENT.md) for production
- **API:** [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for endpoints
- **Contribute:** [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines

---

## 🎉 You're Ready!

Start your emotional wellness journey with MindMirror AI!

**Remember:** All your data is private and stored only in YOUR Google Drive.

---

## 💡 Pro Tips

1. **Journal Daily** - Build a streak for better insights
2. **Try All Modes** - Different expressions reveal different emotions
3. **Review Timeline** - See your emotional growth over time
4. **Save AI Art** - Download your favorite mood visualizations
5. **Be Honest** - The more authentic, the better the insights

---

## 📞 Need Help?

- **Issues:** [GitHub Issues](https://github.com/yourusername/mindmirror-ai/issues)
- **Email:** support@mindmirror.ai
- **Docs:** Check the comprehensive guides in the repo

---

**Built with ❤️ for Gen Z mental wellness**

*Happy reflecting! 🧠✨*
