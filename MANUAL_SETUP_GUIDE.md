# 🛠️ Complete Manual Setup Guide - MindMirror AI

**Step-by-step instructions to make your app production-ready and deployable.**

---

## ✅ **WHAT I'VE ALREADY DONE FOR YOU**

I've completed the backend conversion and updated key frontend files:

✅ **Backend (100% Complete)**:
- Gradio app with REST API endpoints
- AI modules with fallback strategies
- Google OAuth & Drive integration
- Session management
- Tests
- Docker & deployment configs

✅ **Frontend (Partially Updated)**:
- `App.js` - OAuth callback handling
- `LoginPage.js` - Gradio OAuth flow
- `gradio-api.js` - New API service created

---

## 📋 **WHAT YOU NEED TO DO MANUALLY**

### **TASK 1: Update Frontend Components (30-45 minutes)**

You need to update these component files to use the new `gradio-api.js` service:

#### **File 1: `frontend/src/components/TextInput.js`**

**Location**: Open this file in your editor

**What to change**: Replace the import and API calls

**Find this line** (around line 2-4):
```javascript
import { uploadAPI } from '../services/api';
```

**Replace with**:
```javascript
import { journalAPI } from '../services/gradio-api';
```

**Find this code** (around line 20-30):
```javascript
const result = await uploadAPI.uploadText(content, title, tags, googleToken);
```

**Replace with**:
```javascript
const result = await journalAPI.submitText(content);
```

---

#### **File 2: `frontend/src/components/VoiceInput.js`**

**Location**: Open this file

**Find**:
```javascript
import { uploadAPI } from '../services/api';
```

**Replace with**:
```javascript
import { journalAPI } from '../services/gradio-api';
```

**Find**:
```javascript
const result = await uploadAPI.uploadVoice(audioBlob, googleToken);
```

**Replace with**:
```javascript
const result = await journalAPI.submitVoice(audioBlob);
```

---

#### **File 3: `frontend/src/components/ImageInput.js`**

**Find**:
```javascript
import { uploadAPI } from '../services/api';
```

**Replace with**:
```javascript
import { journalAPI } from '../services/gradio-api';
```

**Find**:
```javascript
const result = await uploadAPI.uploadImage(file, caption, googleToken);
```

**Replace with**:
```javascript
const result = await journalAPI.submitImage(file);
```

---

#### **File 4: `frontend/src/components/VideoInput.js`**

**Find**:
```javascript
import { uploadAPI } from '../services/api';
```

**Replace with**:
```javascript
import { journalAPI } from '../services/gradio-api';
```

**Find**:
```javascript
const result = await uploadAPI.uploadVideo(file, caption, googleToken);
```

**Replace with**:
```javascript
const result = await journalAPI.submitVideo(file);
```

---

#### **File 5: `frontend/src/components/Gallery.js`**

**Find**:
```javascript
import { reflectionAPI } from '../services/api';
```

**Replace with**:
```javascript
import { historyAPI } from '../services/gradio-api';
```

**Find**:
```javascript
const data = await reflectionAPI.getHistory(googleToken);
```

**Replace with**:
```javascript
const data = await historyAPI.getHistory(50);
```

---

#### **File 6: `frontend/src/pages/Dashboard.js`**

**Find** (around line 3-5):
```javascript
import { authAPI } from '../services/api';
```

**Replace with**:
```javascript
import { authAPI } from '../services/gradio-api';
```

**Find** (in logout function):
```javascript
await authAPI.logout();
```

**Replace with**:
```javascript
authAPI.logout();
```

---

### **TASK 2: Update Frontend Environment File (2 minutes)**

**File**: `frontend/.env.example`

**Action**: Open and update it to:

```env
# MindMirror AI Frontend - Gradio Backend
REACT_APP_API_URL=http://localhost:7860
REACT_APP_GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
```

**Then create your actual `.env` file**:

```bash
cd frontend
copy .env.example .env
```

Edit `frontend/.env` and put your real values (you'll get these in Task 3).

---

### **TASK 3: Update package.json (Remove Unused Dependency) (1 minute)**

**File**: `frontend/package.json`

**Find** (in dependencies):
```json
"@react-oauth/google": "^0.11.1",
```

**Remove this line** (we're not using it anymore)

**Save the file**

---

### **TASK 4: Remove Old GoogleOAuthProvider from index.js (2 minutes)**

**File**: `frontend/src/index.js`

**Find**:
```javascript
import { GoogleOAuthProvider } from '@react-oauth/google';
```

**Remove this line**

**Find**:
```javascript
<GoogleOAuthProvider clientId={process.env.REACT_APP_GOOGLE_CLIENT_ID}>
  <App />
</GoogleOAuthProvider>
```

**Replace with**:
```javascript
<App />
```

**Final `index.js` should look like**:
```javascript
import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

---

### **TASK 5: Test Backend Locally (5 minutes)**

Open PowerShell/Terminal:

```powershell
# Navigate to backend
cd "C:\Users\ramzy\Downloads\MindMirror AI\backend"

# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
copy .env.example .env
```

**Edit `backend/.env`** with a text editor and add:
```env
GOOGLE_CLIENT_ID=your-client-id-here
GOOGLE_CLIENT_SECRET=your-client-secret-here
REDIRECT_URI=http://localhost:7860/callback
FRONTEND_URL=http://localhost:3000
PORT=7860
```

(Leave GOOGLE_CLIENT_ID empty for now, we'll get it in Task 6)

**Start the backend**:
```powershell
python app.py
```

You should see:
```
Running on local URL:  http://127.0.0.1:7860
```

**Keep this terminal open!**

---

### **TASK 6: Set Up Google Cloud OAuth (15 minutes)**

#### **Step 6.1: Create Google Cloud Project**

1. Go to: https://console.cloud.google.com/
2. Click **"Select a project"** dropdown (top bar)
3. Click **"NEW PROJECT"**
4. Project name: `MindMirror-AI`
5. Click **"CREATE"**
6. Wait 10-20 seconds, then select the project

#### **Step 6.2: Enable APIs**

1. In left menu: **"APIs & Services"** → **"Library"**
2. Search: `Google Drive API`
3. Click it → Click **"ENABLE"**
4. Go back to Library
5. Search: `Google People API`
6. Click it → Click **"ENABLE"**

#### **Step 6.3: Configure OAuth Consent Screen**

1. Left menu: **"APIs & Services"** → **"OAuth consent screen"**
2. Select: **"External"**
3. Click **"CREATE"**
4. Fill in:
   - **App name**: `MindMirror AI`
   - **User support email**: (select your email)
   - **Developer contact**: (type your email)
5. Click **"SAVE AND CONTINUE"**
6. **Scopes page**: Click **"ADD OR REMOVE SCOPES"**
7. In the filter box, search and check these:
   - `userinfo.email`
   - `userinfo.profile`
   - `drive.file`
8. Click **"UPDATE"** → **"SAVE AND CONTINUE"**
9. **Test users**: Click **"+ ADD USERS"**
10. Enter your email address
11. Click **"ADD"** → **"SAVE AND CONTINUE"**
12. Click **"BACK TO DASHBOARD"**

#### **Step 6.4: Create OAuth Credentials**

1. Left menu: **"APIs & Services"** → **"Credentials"**
2. Click **"+ CREATE CREDENTIALS"** → **"OAuth client ID"**
3. Application type: **"Web application"**
4. Name: `MindMirror Web Client`
5. **Authorized redirect URIs**: Click **"+ ADD URI"**
6. Add: `http://localhost:7860/callback`
7. Click **"+ ADD URI"** again
8. Add: `http://localhost:3000/callback`
9. Click **"CREATE"**
10. **IMPORTANT**: A popup appears with your credentials

**COPY THESE NOW**:
- ✅ **Client ID**: (looks like `123456789-abc123.apps.googleusercontent.com`)
- ✅ **Client Secret**: (looks like `GOCSPX-abc123xyz`)

11. Click **"OK"**

#### **Step 6.5: Update Backend .env**

Open `backend/.env` and update:
```env
GOOGLE_CLIENT_ID=paste-your-client-id-here
GOOGLE_CLIENT_SECRET=paste-your-client-secret-here
REDIRECT_URI=http://localhost:7860/callback
FRONTEND_URL=http://localhost:3000
PORT=7860
```

**Restart your backend** (Ctrl+C in the terminal, then `python app.py` again)

#### **Step 6.6: Update Frontend .env**

Open `frontend/.env` and update:
```env
REACT_APP_API_URL=http://localhost:7860
REACT_APP_GOOGLE_CLIENT_ID=paste-your-client-id-here
```

---

### **TASK 7: Test Frontend Locally (5 minutes)**

Open a **NEW** PowerShell/Terminal (keep backend running):

```powershell
# Navigate to frontend
cd "C:\Users\ramzy\Downloads\MindMirror AI\frontend"

# Install dependencies
npm install

# Start frontend
npm start
```

Browser should open to `http://localhost:3000`

**Test the flow**:
1. Click **"Sign in with Google"**
2. You'll be redirected to Google
3. Sign in and authorize
4. You'll be redirected back to your app
5. You should see the Dashboard

**If it works** ✅ - Great! Move to deployment.

**If it doesn't work** ❌ - Check:
- Backend is running on port 7860
- Frontend is running on port 3000
- Google OAuth redirect URIs are correct
- Check browser console for errors

---

### **TASK 8: Deploy Backend to Hugging Face Spaces (15 minutes)**

#### **Step 8.1: Create HF Account & Space**

1. Go to: https://huggingface.co/join
2. Sign up (if you don't have an account)
3. Verify your email
4. Go to: https://huggingface.co/spaces
5. Click **"Create new Space"**
6. Fill in:
   - **Owner**: (your username)
   - **Space name**: `mindmirror-ai`
   - **License**: **"other"** (closed-source)
   - **SDK**: **"Gradio"**
   - **Hardware**: **"CPU basic - Free"**
   - **Space visibility**: **"Private"** ✅
7. Click **"Create Space"**

#### **Step 8.2: Upload Backend Files**

**Your Space URL**: `https://huggingface.co/spaces/YOUR_USERNAME/mindmirror-ai`

**Option A: Via Web Interface (Easier)**

1. In your Space, click **"Files"** tab
2. Click **"Add file"** → **"Upload files"**
3. From `backend/` folder, upload:
   - `app.py`
   - `requirements.txt`
4. Click **"Commit changes to main"**
5. Click **"Add file"** → **"Create a new folder"**
6. Name: `ai`
7. Upload all files from `backend/ai/`:
   - `__init__.py`
   - `model_registry.py`
   - `orchestrator.py`
   - `emotion.py`
   - `reflection.py`
   - `art.py`
   - `speech.py`
8. Repeat for `utils/` folder (upload all files from `backend/utils/`)
9. Click **"Commit changes to main"**

**Option B: Via Git (Advanced)**

```powershell
cd "C:\Users\ramzy\Downloads\MindMirror AI\backend"
git init
git add app.py requirements.txt ai/ utils/
git commit -m "Initial backend"
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/mindmirror-ai
git push hf main
```

#### **Step 8.3: Configure Space Secrets**

1. In your Space, click **"Settings"** tab
2. Scroll to **"Repository secrets"**
3. Click **"New secret"**

**Add these secrets one by one**:

**Secret 1**:
- Name: `GOOGLE_CLIENT_ID`
- Value: (paste your Google Client ID)
- Click **"Add"**

**Secret 2**:
- Name: `GOOGLE_CLIENT_SECRET`
- Value: (paste your Google Client Secret)
- Click **"Add"**

**Secret 3**:
- Name: `REDIRECT_URI`
- Value: `https://YOUR_USERNAME-mindmirror-ai.hf.space/callback`
  (Replace YOUR_USERNAME with your actual HF username)
- Click **"Add"**

**Secret 4**:
- Name: `FRONTEND_URL`
- Value: `http://localhost:3000` (we'll update this after Vercel)
- Click **"Add"**

**Secret 5**:
- Name: `PORT`
- Value: `7860`
- Click **"Add"**

#### **Step 8.4: Wait for Build**

1. Go to **"App"** tab
2. You'll see "Building..." (takes 2-5 minutes)
3. Once done, you'll see the Gradio interface
4. **Copy your Space URL**: `https://YOUR_USERNAME-mindmirror-ai.hf.space`

#### **Step 8.5: Update Google OAuth**

1. Go back to Google Cloud Console
2. **"APIs & Services"** → **"Credentials"**
3. Click your OAuth client ID
4. Under **"Authorized redirect URIs"**, click **"+ ADD URI"**
5. Add: `https://YOUR_USERNAME-mindmirror-ai.hf.space/callback`
6. Click **"SAVE"**

---

### **TASK 9: Deploy Frontend to Vercel (10 minutes)**

#### **Step 9.1: Install Vercel CLI**

```powershell
npm install -g vercel
```

#### **Step 9.2: Login to Vercel**

```powershell
vercel login
```

Follow the prompts (opens browser to authenticate).

#### **Step 9.3: Deploy**

```powershell
cd "C:\Users\ramzy\Downloads\MindMirror AI\frontend"
vercel
```

**Answer the prompts**:
- Set up and deploy: **Y**
- Which scope: (select your account)
- Link to existing project: **N**
- Project name: **mindmirror-ai**
- In which directory: **./** (press Enter)
- Override settings: **N**

Wait 1-2 minutes for deployment.

You'll get a URL like: `https://mindmirror-ai-abc123.vercel.app`

#### **Step 9.4: Set Environment Variables**

```powershell
# Set API URL
vercel env add REACT_APP_API_URL
```
When prompted:
- Value: `https://YOUR_USERNAME-mindmirror-ai.hf.space`
- Environments: Select **all three** (Production, Preview, Development)

```powershell
# Set Google Client ID
vercel env add REACT_APP_GOOGLE_CLIENT_ID
```
When prompted:
- Value: (paste your Google Client ID)
- Environments: Select **all three**

#### **Step 9.5: Deploy to Production**

```powershell
vercel --prod
```

You'll get your production URL: `https://mindmirror-ai.vercel.app`

**COPY THIS URL** ✅

#### **Step 9.6: Update Backend with Frontend URL**

1. Go to your HF Space settings
2. Find `FRONTEND_URL` secret
3. Click **"Edit"**
4. Change to: `https://mindmirror-ai.vercel.app`
5. Click **"Save"**
6. Space will rebuild (wait 2-3 minutes)

#### **Step 9.7: Update Google OAuth (Final)**

1. Google Cloud Console → Credentials
2. Click your OAuth client ID
3. **Authorized JavaScript origins**: Click **"+ ADD URI"**
4. Add: `https://mindmirror-ai.vercel.app`
5. **Authorized redirect URIs**: Click **"+ ADD URI"**
6. Add: `https://mindmirror-ai.vercel.app/callback`
7. Click **"SAVE"**

---

### **TASK 10: Final Testing (10 minutes)**

#### **Test Production App**:

1. Open: `https://mindmirror-ai.vercel.app`
2. Click **"Sign in with Google"**
3. Authorize the app
4. Create a journal entry:
   - Type: "I'm feeling happy today!"
   - Click submit
   - Wait 10-30 seconds (first request is slow)
5. You should see:
   - ✅ Detected emotions
   - ✅ AI reflection
   - ✅ Generated poem
   - ✅ Mood art

#### **Verify Google Drive**:

1. Go to: https://drive.google.com/
2. Look for folder: `MindMirrorAI/YourName_123/`
3. Check:
   - `raw/` folder has your entry
   - `outputs/` folder has AI content
   - `log.json` file exists

#### **Test on Mobile**:

1. Open your Vercel URL on your phone
2. Test the same flow
3. Verify responsive design

---

## ✅ **COMPLETION CHECKLIST**

Before considering your app production-ready, verify:

- [ ] All frontend components updated to use `gradio-api.js`
- [ ] `package.json` cleaned (removed @react-oauth/google)
- [ ] `index.js` updated (removed GoogleOAuthProvider)
- [ ] Backend tested locally
- [ ] Google Cloud OAuth configured
- [ ] Backend deployed to HF Spaces
- [ ] Frontend deployed to Vercel
- [ ] Environment variables set correctly
- [ ] Google OAuth redirect URIs updated
- [ ] Production app tested end-to-end
- [ ] Google Drive storage verified
- [ ] Mobile testing done

---

## 🐛 **TROUBLESHOOTING**

### **Issue: "Redirect URI mismatch"**
**Solution**: Go to Google Cloud Console → Credentials → verify all URIs match exactly (no trailing slashes).

### **Issue: "Failed to fetch" on frontend**
**Solution**: 
- Check HF Space is running (not sleeping)
- Verify `REACT_APP_API_URL` in Vercel
- First request may take 30-60 seconds

### **Issue: "Session expired" immediately**
**Solution**:
- Clear browser cache
- Check HF Space didn't restart
- Verify session token is in sessionStorage (not localStorage)

### **Issue: Backend build fails on HF Spaces**
**Solution**:
- Check `requirements.txt` syntax
- View build logs in HF Space
- Verify all files uploaded correctly

### **Issue: AI generation fails**
**Solution**:
- Check HF Space logs
- Models may be cold-starting (wait 30s and retry)
- Template fallbacks should still work

---

## 📊 **TIME ESTIMATE**

- **Task 1-4** (Frontend updates): 30-45 minutes
- **Task 5** (Local backend test): 5 minutes
- **Task 6** (Google OAuth): 15 minutes
- **Task 7** (Local frontend test): 5 minutes
- **Task 8** (HF Spaces deploy): 15 minutes
- **Task 9** (Vercel deploy): 10 minutes
- **Task 10** (Final testing): 10 minutes

**Total: 90-120 minutes (1.5-2 hours)**

---

## 🎉 **AFTER COMPLETION**

Your app will be:
- ✅ Live at your Vercel URL
- ✅ Backend on HF Spaces (free)
- ✅ Frontend on Vercel (free)
- ✅ All data in user's Google Drive
- ✅ Privacy-first and secure
- ✅ Production-ready

---

## 📞 **NEED HELP?**

If you get stuck on any step:
1. Check the error message carefully
2. Review the troubleshooting section
3. Check browser console (F12)
4. Check HF Space logs
5. Verify all environment variables

---

**Good luck! You're almost there! 🚀**
