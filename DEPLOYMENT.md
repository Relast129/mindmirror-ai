# 🚢 MindMirror AI - Production Deployment Guide

Complete guide for deploying MindMirror AI to production using free hosting services.

---

## 🎯 Deployment Architecture

- **Frontend:** Vercel (Free tier)
- **Backend:** Render (Free tier)
- **Storage:** Google Drive (User's own account)
- **AI Models:** Hugging Face Inference API (Free tier)

---

## 📦 Pre-Deployment Checklist

- [ ] Backend tested locally
- [ ] Frontend tested locally
- [ ] Google OAuth configured
- [ ] Hugging Face API token obtained
- [ ] GitHub repository created
- [ ] Environment variables documented

---

## 🔧 Part 1: Backend Deployment (Render)

### Step 1: Prepare Repository

1. Create a GitHub repository
2. Push your code:
```bash
git init
git add .
git commit -m "Initial commit: MindMirror AI"
git branch -M main
git remote add origin https://github.com/yourusername/mindmirror-ai.git
git push -u origin main
```

### Step 2: Create Render Account

1. Go to [Render.com](https://render.com/)
2. Sign up with GitHub
3. Authorize Render to access your repositories

### Step 3: Create Web Service

1. Click **"New +"** → **"Web Service"**
2. Select your repository
3. Configure service:

**Basic Settings:**
- Name: `mindmirror-ai-backend`
- Region: Choose closest to your users
- Branch: `main`
- Root Directory: `backend`
- Environment: `Python 3`
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

**Instance Type:**
- Select **"Free"**

### Step 4: Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"**

Add each variable:
```
SECRET_KEY=<generate-with-openssl-rand-hex-32>
GOOGLE_CLIENT_ID=<your-google-client-id>
GOOGLE_CLIENT_SECRET=<your-google-client-secret>
GOOGLE_REDIRECT_URI=https://your-service-name.onrender.com/auth/callback
FRONTEND_URL=https://your-frontend-domain.vercel.app
HUGGINGFACE_API_TOKEN=<your-hf-token>
```

### Step 5: Deploy

1. Click **"Create Web Service"**
2. Wait for deployment (5-10 minutes)
3. Copy your service URL: `https://mindmirror-ai-backend.onrender.com`

### Step 6: Verify Backend

Visit: `https://your-service-name.onrender.com/health`

Expected response:
```json
{
  "status": "healthy",
  "service": "MindMirror AI",
  "ai_models": "ready"
}
```

---

## 🎨 Part 2: Frontend Deployment (Vercel)

### Step 1: Install Vercel CLI

```bash
npm install -g vercel
```

### Step 2: Prepare Frontend

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Update `.env` for production:
```env
REACT_APP_API_URL=https://your-backend.onrender.com
REACT_APP_GOOGLE_CLIENT_ID=<your-google-client-id>
```

3. Test build locally:
```bash
npm run build
```

### Step 3: Deploy to Vercel

```bash
vercel
```

Follow the prompts:
- Set up and deploy? **Y**
- Which scope? Select your account
- Link to existing project? **N**
- Project name? `mindmirror-ai`
- Directory? `./`
- Override settings? **N**

### Step 4: Add Environment Variables

```bash
vercel env add REACT_APP_API_URL
# Paste: https://your-backend.onrender.com

vercel env add REACT_APP_GOOGLE_CLIENT_ID
# Paste: your-google-client-id
```

### Step 5: Deploy to Production

```bash
vercel --prod
```

Copy your production URL: `https://mindmirror-ai.vercel.app`

---

## 🔐 Part 3: Update Google OAuth

### Step 1: Add Production URLs

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **"APIs & Services" > "Credentials"**
3. Click your OAuth 2.0 Client ID

### Step 2: Update Authorized Origins

Add:
- `https://your-frontend.vercel.app`
- `https://your-backend.onrender.com`

### Step 3: Update Redirect URIs

Add:
- `https://your-backend.onrender.com/auth/callback`

Click **"Save"**

---

## 🧪 Part 4: Testing Production

### Test Checklist

1. **Homepage Load**
   - [ ] Frontend loads without errors
   - [ ] No console errors
   - [ ] UI renders correctly

2. **Authentication**
   - [ ] Google Sign-In button works
   - [ ] OAuth flow completes successfully
   - [ ] User redirected to dashboard

3. **Multi-Modal Input**
   - [ ] Text input and reflection generation
   - [ ] Voice recording and transcription
   - [ ] Image upload and processing
   - [ ] Video upload and processing

4. **Data Persistence**
   - [ ] Files saved to Google Drive
   - [ ] Reflections stored correctly
   - [ ] History loads properly

5. **Performance**
   - [ ] Page load time < 3 seconds
   - [ ] API responses < 5 seconds
   - [ ] No timeout errors

---

## 📊 Part 5: Monitoring & Maintenance

### Render Monitoring

1. Go to Render Dashboard
2. Click your service
3. Check:
   - **Logs:** View application logs
   - **Metrics:** CPU, Memory usage
   - **Events:** Deployment history

### Vercel Monitoring

1. Go to Vercel Dashboard
2. Click your project
3. Check:
   - **Analytics:** Page views, performance
   - **Deployments:** Build history
   - **Logs:** Runtime logs

### Set Up Alerts

**Render:**
- Enable email notifications for deployment failures
- Set up uptime monitoring (UptimeRobot, Pingdom)

**Vercel:**
- Enable deployment notifications
- Set up error tracking (Sentry)

---

## 🔄 Part 6: Continuous Deployment

### Automatic Deployments

**Backend (Render):**
- Automatically deploys on push to `main` branch
- Manual deploy: Click "Manual Deploy" in dashboard

**Frontend (Vercel):**
- Automatically deploys on push to `main` branch
- Manual deploy: `vercel --prod`

### Deployment Workflow

1. Make changes locally
2. Test thoroughly
3. Commit and push:
```bash
git add .
git commit -m "Description of changes"
git push origin main
```
4. Wait for automatic deployment
5. Test production site

---

## ⚡ Part 7: Performance Optimization

### Backend Optimization

1. **Enable Caching:**
```python
# Add to main.py
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

@app.on_event("startup")
async def startup():
    FastAPICache.init(InMemoryBackend())
```

2. **Optimize AI Requests:**
- Cache emotion detection results
- Batch process multiple requests
- Use smaller models for faster responses

### Frontend Optimization

1. **Code Splitting:**
```javascript
// Use React.lazy for route-based splitting
const Dashboard = React.lazy(() => import('./pages/Dashboard'));
```

2. **Image Optimization:**
- Compress images before upload
- Use WebP format
- Implement lazy loading

3. **Bundle Size:**
```bash
npm run build
# Check build/static/js/*.js sizes
# Keep main bundle < 500KB
```

---

## 🔒 Part 8: Security Best Practices

### Environment Variables

- [ ] Never commit `.env` files
- [ ] Use different keys for dev/prod
- [ ] Rotate secrets regularly

### API Security

- [ ] Rate limiting enabled
- [ ] CORS configured correctly
- [ ] Input validation on all endpoints
- [ ] HTTPS enforced

### Data Privacy

- [ ] All data in user's Google Drive
- [ ] No server-side data storage
- [ ] Secure token handling
- [ ] Regular security audits

---

## 💰 Part 9: Cost Management

### Free Tier Limits

**Render Free Tier:**
- 750 hours/month (enough for 1 service)
- Spins down after 15 min inactivity
- 512 MB RAM
- Shared CPU

**Vercel Free Tier:**
- 100 GB bandwidth/month
- Unlimited deployments
- 100 builds/day

**Hugging Face Free Tier:**
- Rate limited API calls
- Shared GPU inference
- May have queuing

### Scaling Considerations

When to upgrade:
- **Render:** > 100 daily active users
- **Vercel:** > 1000 daily visitors
- **Hugging Face:** Consistent rate limiting

---

## 🐛 Part 10: Troubleshooting Production

### Common Issues

**Backend won't start:**
```bash
# Check Render logs
# Verify all environment variables are set
# Ensure requirements.txt is complete
```

**Frontend build fails:**
```bash
# Check Vercel logs
# Verify environment variables
# Test build locally: npm run build
```

**OAuth errors:**
- Verify redirect URIs match exactly
- Check client ID/secret are correct
- Ensure APIs are enabled

**API timeouts:**
- Hugging Face models may be cold-starting
- Increase timeout settings
- Consider upgrading to paid tier

### Emergency Rollback

**Render:**
1. Go to "Events" tab
2. Click previous successful deployment
3. Click "Redeploy"

**Vercel:**
```bash
vercel rollback
```

---

## 📈 Part 11: Analytics & Insights

### Track Key Metrics

1. **User Engagement:**
   - Daily active users
   - Average session duration
   - Entries per user

2. **Technical Metrics:**
   - API response times
   - Error rates
   - Uptime percentage

3. **Business Metrics:**
   - User retention
   - Feature usage
   - Growth rate

### Tools

- **Google Analytics:** User behavior
- **Sentry:** Error tracking
- **LogRocket:** Session replay
- **Mixpanel:** Product analytics

---

## 🎓 Part 12: Next Steps

### Feature Enhancements

- [ ] Email notifications for streaks
- [ ] Social sharing (optional)
- [ ] Export data as PDF
- [ ] Mobile app (React Native)
- [ ] Mood prediction ML model
- [ ] Community features (opt-in)

### Infrastructure Upgrades

- [ ] CDN for static assets
- [ ] Database for metadata (optional)
- [ ] Redis for caching
- [ ] Load balancing

---

## 📞 Support & Resources

- **Render Docs:** https://render.com/docs
- **Vercel Docs:** https://vercel.com/docs
- **FastAPI Deployment:** https://fastapi.tiangolo.com/deployment/
- **React Production:** https://react.dev/learn/start-a-new-react-project

---

## ✅ Deployment Complete!

Your MindMirror AI application is now live and accessible worldwide! 🎉

**Production URLs:**
- Frontend: `https://your-app.vercel.app`
- Backend: `https://your-api.onrender.com`

**Next:** Share with users and gather feedback!

---

**Built with ❤️ for Gen Z mental wellness**
