# 🤗 Hugging Face Spaces Deployment Fix

## ❌ **Current Problem**

Your HF Space shows "Not Found" because the files aren't properly configured for Hugging Face Spaces.

---

## ✅ **Solution: Manual File Upload**

Since we're using a local Git repo, we need to manually push the backend files to your HF Space.

### **Option A: Push from Local Backend Folder** (Recommended)

```powershell
# Navigate to backend folder
cd "C:\Users\ramzy\Downloads\MindMirror AI\backend"

# Initialize git if not already done
git init

# Add HF Space as remote (replace with your space URL)
git remote add hf https://huggingface.co/spaces/RelastJJ/mindmirror-ai

# Add all files
git add .

# Commit
git commit -m "Deploy Flask backend to HF Spaces"

# Push to HF Space
git push hf main --force
```

### **Option B: Use HF Web Interface**

1. Go to: https://huggingface.co/spaces/RelastJJ/mindmirror-ai/tree/main
2. Click **"Add file"** → **"Upload files"**
3. Upload these files from `backend` folder:
   - `app_hf.py`
   - `api_server.py`
   - `app.py`
   - `requirements.txt`
   - `Dockerfile`
   - `README_HF.md` (rename to `README.md`)
   - Entire `ai/` folder
   - Entire `utils/` folder
   - `.env.example`

---

## 🔑 **Required Environment Variables**

After uploading files, add these secrets in HF Space settings:

1. Go to: https://huggingface.co/spaces/RelastJJ/mindmirror-ai/settings

2. Add these secrets:

```
GOOGLE_CLIENT_ID=356653662187-dm09nvnch9vsquj8ci37pes3t93tpffc.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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
REDIRECT_URI=https://relastjj-mindmirror-ai.hf.space/callback
FRONTEND_URL=https://creative-praline-fe6c40.netlify.app
OPENROUTER_API_KEY=<your-openrouter-key>
PORT=7860
```

---

## 📋 **File Structure in HF Space**

Your HF Space should have this structure:

```
/
├── README.md (the README_HF.md file)
├── Dockerfile
├── app_hf.py (entry point)
├── api_server.py
├── app.py
├── requirements.txt
├── .env.example
├── ai/
│   ├── __init__.py
│   ├── orchestrator.py
│   ├── reflection.py
│   ├── reflection_generator.py
│   ├── emotion.py
│   ├── art.py
│   └── speech.py
└── utils/
    ├── __init__.py
    ├── google_oauth.py
    ├── drive_manager.py
    ├── session_store.py
    └── file_helpers.py
```

---

## 🧪 **Testing After Deployment**

1. **Check Logs**:
   - Go to your Space
   - Click **"Logs"** tab
   - Look for:
     ```
     ✅ Flask app imported successfully
     🚀 Starting MindMirror AI on Hugging Face Spaces
     📍 Port: 7860
     ```

2. **Test API**:
   ```bash
   curl https://relastjj-mindmirror-ai.hf.space/api/login -X POST -H "Content-Type: application/json" -d '{"code":null}'
   ```

3. **Expected Response**:
   ```json
   {
     "auth_url": "https://accounts.google.com/o/oauth2/v2/auth?...",
     "status": 200
   }
   ```

---

## 🚀 **Quick Deploy Script**

Save this as `deploy_hf.ps1`:

```powershell
# Deploy to Hugging Face Spaces
$backendPath = "C:\Users\ramzy\Downloads\MindMirror AI\backend"
$spaceName = "RelastJJ/mindmirror-ai"

Write-Host "🚀 Deploying to Hugging Face Spaces..." -ForegroundColor Green

# Navigate to backend
cd $backendPath

# Check if git is initialized
if (-not (Test-Path ".git")) {
    Write-Host "📦 Initializing git..." -ForegroundColor Yellow
    git init
}

# Add HF remote
Write-Host "🔗 Adding HF Space remote..." -ForegroundColor Yellow
git remote remove hf 2>$null
git remote add hf "https://huggingface.co/spaces/$spaceName"

# Add files
Write-Host "📁 Adding files..." -ForegroundColor Yellow
git add .

# Commit
Write-Host "💾 Committing..." -ForegroundColor Yellow
git commit -m "Deploy Flask backend to HF Spaces - $(Get-Date -Format 'yyyy-MM-dd HH:mm')"

# Push
Write-Host "🚢 Pushing to HF Spaces..." -ForegroundColor Yellow
git push hf main --force

Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host "🔗 Check your space: https://huggingface.co/spaces/$spaceName" -ForegroundColor Cyan
```

Run it:
```powershell
.\deploy_hf.ps1
```

---

## 🔧 **Troubleshooting**

### **Problem: "Not Found" persists**

**Solution**:
1. Check HF Space logs for errors
2. Verify `README.md` has `sdk: docker`
3. Ensure `Dockerfile` is present
4. Check all files are uploaded

### **Problem: "Import Error"**

**Solution**:
1. Check `requirements.txt` has all dependencies
2. Verify folder structure matches above
3. Check logs for specific missing modules

### **Problem: "Port already in use"**

**Solution**:
1. HF Spaces uses port 7860 by default
2. Ensure `Dockerfile` exposes 7860
3. Ensure `app_hf.py` uses port 7860

---

## 📞 **Need Help?**

1. **Check Logs**: HF Space → Logs tab
2. **Check Files**: HF Space → Files tab
3. **Check Settings**: HF Space → Settings tab

---

## ✅ **Success Checklist**

- [ ] Files uploaded to HF Space
- [ ] `README.md` has `sdk: docker`
- [ ] `Dockerfile` present and correct
- [ ] Environment variables set
- [ ] Space shows "Running" status
- [ ] Logs show "Flask app imported successfully"
- [ ] API endpoint responds

---

**Once deployed, your backend will be at:**
`https://relastjj-mindmirror-ai.hf.space`

**Test it with:**
```bash
curl https://relastjj-mindmirror-ai.hf.space/api/login -X POST -H "Content-Type: application/json" -d '{}'
```
