# ✅ Quick Deployment Checklist

**Use this as a quick reference while following MANUAL_SETUP_GUIDE.md**

---

## 📝 **FRONTEND CODE UPDATES**

### Files to Update (Find & Replace):

1. **`frontend/src/components/TextInput.js`**
   - [ ] Change import: `api` → `gradio-api`
   - [ ] Change call: `uploadAPI.uploadText()` → `journalAPI.submitText()`

2. **`frontend/src/components/VoiceInput.js`**
   - [ ] Change import: `api` → `gradio-api`
   - [ ] Change call: `uploadAPI.uploadVoice()` → `journalAPI.submitVoice()`

3. **`frontend/src/components/ImageInput.js`**
   - [ ] Change import: `api` → `gradio-api`
   - [ ] Change call: `uploadAPI.uploadImage()` → `journalAPI.submitImage()`

4. **`frontend/src/components/VideoInput.js`**
   - [ ] Change import: `api` → `gradio-api`
   - [ ] Change call: `uploadAPI.uploadVideo()` → `journalAPI.submitVideo()`

5. **`frontend/src/components/Gallery.js`**
   - [ ] Change import: `api` → `gradio-api`
   - [ ] Change call: `reflectionAPI.getHistory()` → `historyAPI.getHistory()`

6. **`frontend/src/pages/Dashboard.js`**
   - [ ] Change import: `api` → `gradio-api`
   - [ ] Change call: `await authAPI.logout()` → `authAPI.logout()`

7. **`frontend/src/index.js`**
   - [ ] Remove: `import { GoogleOAuthProvider }`
   - [ ] Remove: `<GoogleOAuthProvider>` wrapper

8. **`frontend/package.json`**
   - [ ] Remove: `"@react-oauth/google": "^0.11.1",`

---

## 🔧 **CONFIGURATION FILES**

### Backend `.env`:
```
- [ ] GOOGLE_CLIENT_ID=_______________
- [ ] GOOGLE_CLIENT_SECRET=_______________
- [ ] REDIRECT_URI=http://localhost:7860/callback
- [ ] FRONTEND_URL=http://localhost:3000
- [ ] PORT=7860
```

### Frontend `.env`:
```
- [ ] REACT_APP_API_URL=http://localhost:7860
- [ ] REACT_APP_GOOGLE_CLIENT_ID=_______________
```

---

## ☁️ **GOOGLE CLOUD SETUP**

- [ ] Create project: `MindMirror-AI`
- [ ] Enable Google Drive API
- [ ] Enable Google People API
- [ ] Configure OAuth consent screen (External)
- [ ] Add scopes: `userinfo.email`, `userinfo.profile`, `drive.file`
- [ ] Add test user (your email)
- [ ] Create OAuth credentials (Web application)
- [ ] Add redirect URI: `http://localhost:7860/callback`
- [ ] Copy Client ID: `_______________`
- [ ] Copy Client Secret: `_______________`

---

## 🚀 **HUGGING FACE SPACES**

- [ ] Create account at huggingface.co
- [ ] Create new Space: `mindmirror-ai`
- [ ] SDK: Gradio, Hardware: CPU basic (free), Visibility: Private
- [ ] Upload files: `app.py`, `requirements.txt`, `ai/`, `utils/`
- [ ] Add secrets:
  - [ ] `GOOGLE_CLIENT_ID`
  - [ ] `GOOGLE_CLIENT_SECRET`
  - [ ] `REDIRECT_URI` = `https://YOUR_USERNAME-mindmirror-ai.hf.space/callback`
  - [ ] `FRONTEND_URL` = (update after Vercel)
  - [ ] `PORT` = `7860`
- [ ] Wait for build to complete
- [ ] Copy Space URL: `_______________`
- [ ] Update Google OAuth redirect URIs with Space URL

---

## 🌐 **VERCEL DEPLOYMENT**

- [ ] Install Vercel CLI: `npm install -g vercel`
- [ ] Login: `vercel login`
- [ ] Deploy: `vercel` (from frontend folder)
- [ ] Set env vars:
  - [ ] `REACT_APP_API_URL` = HF Space URL
  - [ ] `REACT_APP_GOOGLE_CLIENT_ID` = Google Client ID
- [ ] Deploy to production: `vercel --prod`
- [ ] Copy production URL: `_______________`
- [ ] Update HF Space `FRONTEND_URL` secret with Vercel URL
- [ ] Update Google OAuth:
  - [ ] Add origin: Vercel URL
  - [ ] Add redirect: `Vercel_URL/callback`

---

## ✅ **FINAL TESTING**

- [ ] Open production URL
- [ ] Click "Sign in with Google"
- [ ] Authorize app
- [ ] Create journal entry
- [ ] Verify AI response appears
- [ ] Check Google Drive for files
- [ ] Test on mobile device
- [ ] Verify responsive design

---

## 📊 **CREDENTIALS TRACKER**

**Google Cloud**:
- Client ID: `_______________`
- Client Secret: `_______________`

**Hugging Face**:
- Username: `_______________`
- Space URL: `_______________`

**Vercel**:
- Production URL: `_______________`

---

## ⏱️ **TIME ESTIMATE: 1.5-2 hours**

---

## 🆘 **QUICK TROUBLESHOOTING**

**"Redirect URI mismatch"** → Check Google Console URIs match exactly

**"Failed to fetch"** → HF Space may be cold-starting (wait 30s)

**"Session expired"** → Clear cache, HF Space may have restarted

**Build fails** → Check HF Space logs, verify files uploaded

---

**📖 For detailed instructions, see MANUAL_SETUP_GUIDE.md**
