# 📈 Advanced Topics & Next Steps for Streamlit Cloud Deployment

After you have a stable deployment, you may want to enhance, scale, and secure your app. Below are recommended next‑step actions.

---

## 1️⃣ Custom Domain (Paid Tier)

If you upgrade to the **Streamlit Cloud paid plan ($20 / month)** you can attach a custom domain.

1. In the Streamlit Cloud dashboard, open **Settings → Domain**.
2. Click **Add custom domain** and enter your domain (e.g., `app.myfitness.ai`).
3. Follow the DNS instructions:
   - Add a **CNAME** record pointing to `cname.share.streamlit.io`.
   - If you use a root domain (`myfitness.ai`), add an **ALIAS/ANAME** record.
4. Verify the domain – Streamlit will automatically provision an SSL certificate via **Let’s Encrypt**.
5. Once verified, your app will be reachable at `https://app.myfitness.ai`.

> **Tip:** Keep the free tier for development and only upgrade when you need a custom domain or more RAM.

---

## 2️⃣ CI/CD with GitHub Actions (Zero‑Touch Deploys)

Even though Streamlit Cloud auto‑deploys on push, you might want a **GitHub Actions** workflow to run tests before deployment.

```yaml
# .github/workflows/ci.yml
name: CI & Deploy

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Run tests
        run: |
          pytest -q

  # No explicit deploy step needed – Streamlit Cloud will pick up the push automatically.
```

**Benefits:**
- Fails fast if tests break.
- Guarantees that only passing code reaches the cloud.

---

## 3️⃣ Handling Large Model Files with Git LFS

Your repository contains a ~26 MB `best_model.h5`. GitHub’s normal limit is 100 MB per file, but you may still want **Git LFS** for future large assets.

```bash
# Install Git LFS (once per machine)
git lfs install
# Track .h5 files
git lfs track "*.h5"
# Add .gitattributes (auto‑created) and commit
git add .gitattributes
git commit -m "Enable Git LFS for model files"
# Push the large file
git add best_model.h5
git commit -m "Add model via LFS"
git push origin main
```

**Note:** Streamlit Cloud automatically pulls LFS files, but the first pull can be a few seconds longer.

---

## 4️⃣ Performance Optimizations for Production

| Area | Recommendation | Code Snippet |
|------|----------------|--------------|
| **Model Loading** | Cache with `@st.cache_resource` and lazy‑load only when needed. | ```python\n@st.cache_resource\ndef load_model():\n    return tf.keras.models.load_model('best_model.h5')\n\nif st.button('Start Trainer'):\n    model = load_model()\n``` |
| **Data Processing** | Cache heavy data transforms with `@st.cache_data`. | ```python\n@st.cache_data\ndef preprocess(df):\n    # expensive ops\n    return processed_df\n``` |
| **Session State** | Store temporary user selections to avoid recomputation. | ```python\nif 'selected_exercises' not in st.session_state:\n    st.session_state.selected_exercises = []\n``` |
| **Static Assets** | Serve images, CSS, and fonts from a CDN (e.g., Cloudflare). | Add `https://cdn.jsdelivr.net/...` URLs in `index.html` or CSS. |
| **Network Calls** | Batch API calls when possible; use async `httpx` if you have many external requests. | ```python\nimport httpx\nasync with httpx.AsyncClient() as client:\n    resp = await client.get(url)\n``` |

---

## 5️⃣ Security Hardening

1. **Never expose secrets** – they are stored in Streamlit Cloud’s encrypted secrets store.
2. **Rate‑limit API endpoints** – if you expose any custom FastAPI routes, use `slowapi` or `starlette` middleware.
3. **CORS** – Streamlit Cloud already sets `Access‑Control‑Allow‑Origin: *`. If you add custom back‑ends, restrict origins.
4. **Content‑Security‑Policy** – add a CSP header via a small `streamlit` plugin if you embed external iframes.
5. **Dependency Auditing** – run `pip-audit` locally before each push:
   ```bash
   pip install pip-audit
   pip-audit -r requirements.txt
   ```

---

## 6️⃣ Monitoring & Alerts

### 6.1 Built‑in Streamlit Metrics
```python
import streamlit as st
import time

# Simple heartbeat metric
st.metric(label="Uptime (seconds)", value=int(time.time() - st.session_state.get('start_time', time.time())))
```

### 6.2 External Monitoring (Free)
- **UptimeRobot** – monitor the public URL every 5 min and receive email/SMS alerts.
- **Google Analytics** – add the GA script in `index.html` (via `st.components.v1.html`).

### 6.3 Logging
- Streamlit Cloud automatically captures `print` statements.
- For structured logs, use `loguru`:
  ```python
  from loguru import logger
  logger.info('User {} started a workout', username)
  ```
  Logs appear in the **Logs** view.

---

## 7️⃣ Scaling Beyond the Free Tier

| Tier | RAM | CPU | Cost | When to Upgrade |
|------|-----|-----|------|-----------------|
| Free | 1 GB | 1 vCPU | $0 | Small demo, < 10 concurrent users |
| Paid (Standard) | 2 GB | 2 vCPU | $20/mo | > 10 concurrent users, heavy model, custom domain |
| Paid (Pro) | 4 GB+ | 4 vCPU+ | $40+/mo | Production SaaS, heavy traffic |

**Upgrade Steps**:
1. In Streamlit Cloud, go to **Settings → Billing**.
2. Choose the plan that fits your RAM/CPU needs.
3. Redeploy – the new resources are applied automatically.

---

## 8️⃣ Future‑Proofing

- **Containerization**: If you ever outgrow Streamlit Cloud, you can export the same `requirements.txt` and `config.toml` into a Dockerfile and run on any cloud provider.
- **Modular Architecture**: Keep heavy ML inference in a separate micro‑service (e.g., FastAPI on Render) and call it from Streamlit via HTTP. This reduces RAM usage on the Streamlit side.
- **Versioned Model Management**: Store models in an S3 bucket or Google Cloud Storage and load the latest version at runtime.

---

## 9️⃣ Quick Recap Checklist (Post‑Deployment)

- [ ] **Custom domain** (if paid tier) – DNS & SSL set up.
- [ ] **GitHub Actions CI** – tests pass on every push.
- [ ] **Git LFS** – large assets tracked.
- [ ] **Caching** – `@st.cache_resource` & `@st.cache_data` used.
- [ ] **Secrets** – all API keys stored in Streamlit secrets.
- [ ] **Monitoring** – uptime robot + basic metrics.
- [ ] **Security** – dependencies audited, rate limiting added.
- [ ] **Scaling** – plan for upgrade if traffic grows.

---

## 🎉 You’re All Set!

Your Fitness AI Trainer is now:
- **Live** on a public URL.
- **Secure** with encrypted secrets.
- **Optimized** for performance and cost.
- **Ready** for future growth.

Enjoy showing off your AI‑powered fitness app to the world! 🚀
