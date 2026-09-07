---
description: Deploy Fitness AI Trainer to Streamlit Community Cloud
---

# Deploy to Streamlit Community Cloud

This workflow guides you through deploying your Fitness AI Trainer application to Streamlit Community Cloud.

## Prerequisites

1. GitHub account with your project pushed to a repository
2. Streamlit Community Cloud account (free at share.streamlit.io)
3. MongoDB Atlas account (free tier) for cloud database
4. All API keys ready (Google Fit, DeepSeek, etc.)

## Step 1: Prepare Your Repository

Ensure your GitHub repository has:
- ✅ `main.py` (your Streamlit app entry point)
- ✅ `requirements.txt` (all dependencies)
- ✅ `packages.txt` (system dependencies - already present)
- ✅ `.gitignore` (to exclude `.env`, `venv/`, etc.)

**Important:** Do NOT commit your `.env` file to GitHub!

## Step 2: Clean Up requirements.txt

// turbo
```bash
# Remove duplicate entries and create a clean requirements.txt
```

Your requirements.txt has duplicates. We'll clean this up.

## Step 3: Create packages.txt (System Dependencies)

Your `packages.txt` already exists with necessary system dependencies for OpenCV and MediaPipe.

## Step 4: Set Up MongoDB Atlas (Cloud Database)

1. Go to https://www.mongodb.com/cloud/atlas
2. Create a free cluster (M0 tier)
3. Create a database user with password
4. Whitelist all IPs (0.0.0.0/0) for Streamlit Cloud access
5. Get your connection string (looks like: `mongodb+srv://username:password@cluster.mongodb.net/`)

## Step 5: Push to GitHub

// turbo
```bash
# Ensure all changes are committed and pushed
git add .
git commit -m "Prepare for Streamlit Cloud deployment"
git push origin main
```

## Step 6: Deploy on Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Sign in with GitHub
3. Click "New app"
4. Select your repository
5. Set main file path: `main.py`
6. Click "Advanced settings"
7. Add your secrets (see Step 7)
8. Click "Deploy"

## Step 7: Configure Secrets

In Streamlit Cloud's "Advanced settings" → "Secrets", add your environment variables in TOML format:

```toml
# MongoDB Configuration
MONGODB_CONNECTION_STRING = "mongodb+srv://username:password@cluster.mongodb.net/"
MONGODB_DATABASE = "fitness_ai"

# Email Configuration (for password reset)
EMAIL_ADDRESS = "your-email@gmail.com"
EMAIL_PASSWORD = "your-app-password"

# Google Fit API
GOOGLE_CLIENT_ID = "your-client-id.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "your-client-secret"

# DeepSeek API
DEEPSEEK_API_KEY = "your-deepseek-api-key"

# Google Gemini API
GOOGLE_API_KEY = "your-google-api-key"
```

## Step 8: Monitor Deployment

- Watch the deployment logs in Streamlit Cloud dashboard
- Fix any errors that appear
- Once deployed, you'll get a URL like: `https://your-app-name.streamlit.app`

## Step 9: Test Your Deployed App

1. Visit your app URL
2. Test user registration
3. Test login
4. Test all features (exercise recognition, diet planner, chatbot, etc.)
5. Verify MongoDB data is being saved

## Common Issues & Solutions

### Issue: Large Model Files
**Problem:** `best_model.h5` (26MB) and other model files might be too large for GitHub.

**Solution:**
1. Use Git LFS (Large File Storage)
2. Or upload models to cloud storage (AWS S3, Google Cloud Storage)
3. Download models on app startup

### Issue: Cold Starts
**Problem:** Free tier apps sleep after inactivity.

**Solution:**
- Apps wake up when accessed (takes ~30 seconds)
- Consider paid tier for always-on apps

### Issue: Memory Limits
**Problem:** Free tier has 1GB RAM limit.

**Solution:**
- Optimize model loading (lazy load)
- Use smaller model versions
- Consider Streamlit Cloud paid tier (more resources)

## Alternative: Deploy to Render

If you prefer Render instead:

1. Go to https://render.com
2. Create new "Web Service"
3. Connect your GitHub repository
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `streamlit run main.py --server.port=$PORT --server.address=0.0.0.0`
6. Add environment variables in Render dashboard
7. Deploy

**Note:** Render's free tier has significant cold starts (can take 1-2 minutes to wake up).

## Post-Deployment Optimization

1. **Enable caching** - Use `@st.cache_data` and `@st.cache_resource` for expensive operations
2. **Optimize model loading** - Load models only when needed
3. **Monitor usage** - Check Streamlit Cloud analytics
4. **Set up custom domain** (optional, paid feature)

## Maintenance

- **Updates:** Push to GitHub → Auto-deploys to Streamlit Cloud
- **Logs:** View in Streamlit Cloud dashboard
- **Secrets:** Update in Streamlit Cloud settings
- **Rollback:** Revert git commit and push

---

## Quick Deployment Checklist

- [ ] Clean requirements.txt (no duplicates)
- [ ] Create MongoDB Atlas cluster
- [ ] Push code to GitHub (without .env)
- [ ] Sign up for Streamlit Cloud
- [ ] Deploy app from GitHub
- [ ] Add secrets in Streamlit Cloud
- [ ] Test all features
- [ ] Share your app URL! 🎉
