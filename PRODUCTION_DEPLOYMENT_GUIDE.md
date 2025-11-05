# 🚀 MindMirror AI - Production Deployment Guide

## ✅ **What's Been Implemented**

### **Backend Enhancements**
- ✅ **OpenRouter Integration** - Primary AI reflection service with Claude-3-Haiku
- ✅ **3-Level Fallback System**:
  1. OpenRouter (primary)
  2. Hugging Face Inference (fallback 1)
  3. Template-based generator (fallback 2)
  4. Minimal safe response (fallback 3)
- ✅ **Safety Features** - Crisis keyword detection with emergency resources
- ✅ **Caching** - 6-hour LRU cache to reduce API calls
- ✅ **Rate Limit Handling** - Exponential backoff and automatic fallback switching
- ✅ **Comprehensive Tests** - 15+ unit tests covering all scenarios

### **API Improvements**
- ✅ **Async Support** - Proper async/await handling in Flask
- ✅ **Field Name Fixes** - Matches frontend expectations
- ✅ **Error Handling** - Graceful degradation with user-friendly messages

---

## 📋 **Deployment Steps**

### **Step 1: Set Up OpenRouter API Key**

1. **Get API Key**:
   - Go to: https://openrouter.ai/keys
   - Sign up/login
   - Create a new API key
   - Copy the key (starts with `sk-or-v1-...`)

2. **Add to Hugging Face Spaces**:
   - Go to: https://huggingface.co/spaces/RelastJJ/mindmirror-ai/settings
   - Scroll to **"Repository secrets"**
   - Click **"New secret"**
   - Name: `OPENROUTER_API_KEY`
   - Value: Your API key
   - Click **"Save"**

3. **Add to Local .env** (for testing):
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env and add your key:
   OPENROUTER_API_KEY=sk-or-v1-your-key-here
   ```

---

### **Step 2: Push Code to GitHub**

```powershell
cd "C:\Users\ramzy\Downloads\MindMirror AI"
git add .
git commit -m "Add production-ready OpenRouter reflection pipeline"
git push origin main
```

---

### **Step 3: Verify Deployments**

#### **Hugging Face Spaces**
1. Go to: https://huggingface.co/spaces/RelastJJ/mindmirror-ai
2. Wait 2-3 minutes for rebuild
3. Check logs for: "OpenRouter API key configured"
4. Test endpoint:
   ```bash
   curl -X POST https://relastjj-mindmirror-ai.hf.space/api/submit \
     -H "Content-Type: application/json" \
     -d '{"session_token":"test","input_type":"text","text_content":"I feel anxious"}'
   ```

#### **Netlify**
1. Go to: https://app.netlify.com
2. Check deployment status
3. Should auto-deploy from GitHub push

---

### **Step 4: Test the Complete Flow**

1. **Open App**: https://creative-praline-fe6c40.netlify.app
2. **Login**: Click "Continue with Google"
3. **Submit Entry**: Write "I'm feeling anxious about my exams"
4. **Verify**:
   - ✅ Reflection appears (should be from OpenRouter)
   - ✅ Poem line shows
   - ✅ Micro-actions displayed
   - ✅ Art generated
   - ✅ Entry saved to Google Drive

---

## 🧪 **Testing the Reflection Pipeline**

### **Test Locally**

```powershell
cd backend
python -m pytest tests/test_reflection_generator.py -v
```

Expected output:
```
test_validate_reflection_json_valid PASSED
test_check_urgency_positive PASSED
test_openrouter_success PASSED
test_fallback_chain PASSED
... (15 tests total)
```

### **Test API Endpoint**

```bash
# Test with curl
curl -X POST http://localhost:7860/api/submit \
  -F "session_token=YOUR_SESSION_TOKEN" \
  -F "input_type=text" \
  -F "text_content=I'm feeling really anxious today"
```

---

## 📊 **Monitoring & Observability**

### **Check Logs**

**Hugging Face Spaces**:
1. Go to your Space
2. Click **"Logs"** tab
3. Look for:
   - `OpenRouter reflection generated successfully` ✅
   - `Using fallback AI service` ⚠️
   - `Using template-based reflection` ⚠️

**Netlify**:
1. Go to your site
2. Click **"Functions"** → **"Logs"**
3. Check for API call errors

### **Key Metrics to Watch**

- **OpenRouter Success Rate**: Should be >95%
- **Fallback Usage**: Should be <5%
- **Response Time**: Should be <3 seconds
- **Cache Hit Rate**: Should increase over time

---

## 🔒 **Security Checklist**

- ✅ **API Keys**: Never committed to Git
- ✅ **Environment Variables**: Set in HF Spaces and Netlify
- ✅ **Crisis Detection**: Urgent keywords trigger safe responses
- ✅ **Rate Limiting**: Automatic fallback on 429 errors
- ✅ **Input Validation**: All inputs sanitized
- ✅ **CORS**: Properly configured for frontend domain

---

## 🆘 **Troubleshooting**

### **Problem: "OpenRouter API key not set"**

**Solution**:
1. Check HF Spaces secrets
2. Verify key name is exactly `OPENROUTER_API_KEY`
3. Restart the Space

### **Problem: "All reflection models failed"**

**Solution**:
1. Check OpenRouter account has credits
2. Verify API key is valid
3. Check HF Spaces logs for specific errors
4. Template fallback should still work

### **Problem: "Reflection is generic/template-based"**

**Solution**:
1. This means OpenRouter failed
2. Check API key and credits
3. Verify network connectivity from HF Spaces
4. Check OpenRouter status: https://status.openrouter.ai

### **Problem: "Frontend shows 'Failed to submit'"**

**Solution**:
1. Check browser console for errors
2. Verify backend is running
3. Check CORS configuration
4. Verify session token is valid

---

## 💰 **Cost Estimation**

### **OpenRouter Costs** (Claude-3-Haiku)
- **Input**: $0.25 per million tokens
- **Output**: $1.25 per million tokens
- **Average reflection**: ~500 tokens total
- **Cost per reflection**: ~$0.001 (0.1 cents)
- **1000 users/day**: ~$1/day = $30/month

### **Free Tier Options**
- Hugging Face Inference: Free (rate-limited)
- Template Fallback: Free (always available)
- Total cost can be $0 if using only fallbacks

---

## 📈 **Performance Optimization**

### **Caching Strategy**
- **Cache Duration**: 6 hours
- **Cache Key**: Hash of input + context
- **Cache Size**: Max 100 entries (auto-cleanup)
- **Expected Hit Rate**: 20-30% for repeat users

### **Timeout Configuration**
- **OpenRouter**: 12 seconds
- **Hugging Face**: 12 seconds
- **Total Max**: 25 seconds (with retries)
- **User Experience**: Show progress after 5 seconds

---

## 🎯 **Next Steps**

### **Immediate**
1. ✅ Deploy code to production
2. ✅ Add OpenRouter API key
3. ✅ Test complete flow
4. ✅ Monitor logs for 24 hours

### **Short Term** (Next Week)
- [ ] Add Sentry for error tracking
- [ ] Implement usage analytics
- [ ] Add user feedback collection
- [ ] Create admin dashboard

### **Long Term** (Next Month)
- [ ] A/B test different reflection styles
- [ ] Add multilingual support (Sinhala)
- [ ] Implement reflection history analysis
- [ ] Add personalization based on user patterns

---

## 📞 **Support**

If you encounter issues:

1. **Check Logs**: HF Spaces and Netlify logs
2. **Test Locally**: Run tests and local server
3. **Verify Config**: All environment variables set
4. **Check Status**: OpenRouter and HF status pages

---

## 🎉 **Success Criteria**

Your deployment is successful when:

- ✅ Users can login with Google
- ✅ Text/voice/image inputs work
- ✅ Reflections are empathetic and relevant
- ✅ Micro-actions are actionable
- ✅ Art is generated and displayed
- ✅ Data is saved to Google Drive
- ✅ No errors in logs for 24 hours
- ✅ Response time < 5 seconds
- ✅ Fallbacks work when primary fails

---

## 📚 **Additional Resources**

- **OpenRouter Docs**: https://openrouter.ai/docs
- **Hugging Face Inference**: https://huggingface.co/docs/api-inference
- **Flask Async**: https://flask.palletsprojects.com/en/2.3.x/async-await/
- **React Best Practices**: https://react.dev/learn

---

**You're ready to deploy! 🚀**

Push your code, add the API key, and watch your app come to life with production-quality AI reflections!
