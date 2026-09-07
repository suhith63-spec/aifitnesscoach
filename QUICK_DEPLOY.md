# 🚀 Quick Deployment Guide

Deploy your Fitness AI Trainer to the cloud in under 10 minutes!

## TL;DR - Fastest Path to Deployment

1. **Set up MongoDB Atlas** (5 min)
   - Go to https://www.mongodb.com/cloud/atlas
   - Create free M0 cluster
   - Get connection string

2. **Deploy to Streamlit Cloud** (3 min)
   - Go to https://share.streamlit.io
   - Connect your GitHub repo
   - Add secrets (MongoDB, API keys)
   - Click Deploy!

3. **Done!** Your app is live at `https://your-app.streamlit.app` 🎉

---

## Detailed Instructions

### Prerequisites
- ✅ GitHub account
- ✅ Code pushed to GitHub repository
- ✅ MongoDB Atlas account (free)
- ✅ API keys ready (Google Fit, DeepSeek, etc.)

### Option 1: Streamlit Community Cloud (Recommended) ⭐

**Why?** Free, easy, built for Streamlit apps.

**Steps:**
1. Visit https://share.streamlit.io
2. Sign in with GitHub
3. Click "New app"
4. Select repository: `[your-username]/Fitness-AI-Trainer`
5. Main file: `main.py`
6. Click "Advanced settings" → Add secrets (see below)
7. Click "Deploy"

**Secrets Format (TOML):**
```toml
MONGODB_CONNECTION_STRING = "mongodb+srv://user:pass@cluster.mongodb.net/"
MONGODB_DATABASE = "fitness_ai"
EMAIL_ADDRESS = "your-email@gmail.com"
EMAIL_PASSWORD = "your-app-password"
GOOGLE_CLIENT_ID = "your-client-id.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "your-client-secret"
DEEPSEEK_API_KEY = "your-deepseek-key"
GOOGLE_API_KEY = "your-google-key"
```

**Deployment Time:** 2-5 minutes  
**Cost:** FREE (for public repos)  
**URL:** `https://[your-app-name].streamlit.app`

---

### Option 2: Render (Alternative)

**Why?** More control, good for complex deployments.

**Steps:**
1. Visit https://render.com
2. Create new "Web Service"
3. Connect GitHub repository
4. Build command: `pip install -r requirements.txt`
5. Start command: `streamlit run main.py --server.port=$PORT --server.address=0.0.0.0`
6. Add environment variables (same as above, but KEY=VALUE format)
7. Deploy

**Deployment Time:** 5-10 minutes  
**Cost:** FREE (with cold starts) or $7/month (always-on)  
**URL:** `https://[your-app-name].onrender.com`

---

## MongoDB Atlas Setup (Required)

Your app needs a cloud database. MongoDB Atlas offers a free tier:

1. **Create Account**
   - Go to https://www.mongodb.com/cloud/atlas
   - Sign up (free)

2. **Create Cluster**
   - Choose "M0 Free" tier
   - Select region (closest to you)
   - Click "Create Cluster"

3. **Create Database User**
   - Go to "Database Access"
   - Click "Add New Database User"
   - Choose password authentication
   - Save username and password

4. **Whitelist IPs**
   - Go to "Network Access"
   - Click "Add IP Address"
   - Choose "Allow Access from Anywhere" (0.0.0.0/0)
   - Confirm

5. **Get Connection String**
   - Go to "Database" → "Connect"
   - Choose "Connect your application"
   - Copy connection string
   - Replace `<password>` with your database password

**Example Connection String:**
```
mongodb+srv://myuser:mypassword@cluster0.abc123.mongodb.net/
```

---

## API Keys Setup

### Google Fit API (Optional)
1. Go to https://console.cloud.google.com
2. Create new project
3. Enable "Fitness API"
4. Create OAuth 2.0 credentials
5. Get Client ID and Client Secret

### DeepSeek API (Optional)
1. Sign up at https://platform.deepseek.com
2. Get API key from dashboard

### Google Gemini API (Optional)
1. Go to https://makersuite.google.com/app/apikey
2. Create API key

---

## Troubleshooting

### "ModuleNotFoundError"
- ✅ Check `requirements.txt` has all dependencies
- ✅ Rebuild app in cloud platform

### "MongoDB Connection Failed"
- ✅ Verify connection string is correct
- ✅ Check IP whitelist (should be 0.0.0.0/0)
- ✅ Verify database user credentials

### "Memory Error"
- ✅ Add caching: `@st.cache_resource` for models
- ✅ Implement lazy loading
- ✅ Consider upgrading to paid tier

### "App is Slow"
- ✅ Use `@st.cache_data` and `@st.cache_resource`
- ✅ Optimize database queries
- ✅ Reduce model size

---

## After Deployment

### Test Your App
- [ ] User registration works
- [ ] Login works
- [ ] Exercise recognition works
- [ ] All features functional
- [ ] Data saves to MongoDB

### Share Your App
- Add URL to your portfolio
- Share on social media
- Add to README.md
- Collect user feedback

### Monitor & Maintain
- Check logs regularly
- Update dependencies monthly
- Backup database data
- Optimize performance

---

## Cost Breakdown

### Free Tier (Recommended for Starting)
- **Streamlit Cloud**: FREE (unlimited public apps)
- **MongoDB Atlas**: FREE (512MB storage)
- **Total**: $0/month ✨

### Paid Tier (For Production)
- **Streamlit Cloud**: $20/month (more resources, custom domain)
- **MongoDB Atlas**: FREE or $9/month (more storage)
- **Total**: $20-29/month

---

## Need More Help?

📚 **Documentation:**
- `DEPLOYMENT_OPTIONS.md` - Detailed comparison of all platforms
- `DEPLOYMENT_CHECKLIST.md` - Step-by-step checklist
- `.agent/workflows/deploy-streamlit-cloud.md` - Complete workflow

🤖 **Run Workflow:**
```
/deploy-streamlit-cloud
```

🌐 **Resources:**
- Streamlit Docs: https://docs.streamlit.io
- Streamlit Forum: https://discuss.streamlit.io
- MongoDB Docs: https://docs.atlas.mongodb.com

---

## Updates After Deployment

To update your deployed app:

1. Make changes locally
2. Test: `streamlit run main.py`
3. Commit: `git commit -am "Your update message"`
4. Push: `git push`
5. Auto-deploys! ✨ (Streamlit Cloud)

---

**Ready to deploy?** Follow the steps above and your app will be live in minutes! 🚀
