# AdSellix Premium AI Audit Tool

## Deployment Guide

### Option 1: Streamlit Cloud (Free, Recommended for Start)

1. **Create GitHub Repository**
   ```bash
   # Create new repo on GitHub, then:
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/adsellix-audit.git
   git push -u origin main
   ```

2. **Deploy to Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Main file path: `app.py`
   - Click "Deploy"

3. **Add Secrets (for Claude API)**
   - In Streamlit Cloud dashboard, go to your app
   - Click "Settings" → "Secrets"
   - Add:
   ```toml
   ANTHROPIC_API_KEY = "your-api-key-here"
   ```

4. **Your app is live!**
   - URL: `https://yourusername-adsellix-audit.streamlit.app`

---

### Option 2: Railway (Low-cost, More Control)

1. **Sign up at [railway.app](https://railway.app)**

2. **Create new project from GitHub**
   - Connect your GitHub repo
   - Railway auto-detects Streamlit

3. **Add environment variables**
   ```
   ANTHROPIC_API_KEY=your-key
   PORT=8501
   ```

4. **Deploy**
   - Cost: ~$5-10/month based on usage

---

### Option 3: DigitalOcean (Full Control)

1. **Create Droplet ($6/month)**
   - Ubuntu 22.04
   - Basic plan

2. **SSH and install**
   ```bash
   sudo apt update
   sudo apt install python3-pip
   pip3 install -r requirements.txt
   ```

3. **Run with systemd**
   ```bash
   # Create service file
   sudo nano /etc/systemd/system/audit.service
   ```
   
   ```ini
   [Unit]
   Description=AdSellix Audit
   After=network.target

   [Service]
   User=root
   WorkingDirectory=/root/audit
   ExecStart=/usr/bin/streamlit run app.py --server.port 80
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

4. **Start service**
   ```bash
   sudo systemctl start audit
   sudo systemctl enable audit
   ```

---

## File Structure

```
audit_framework/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── AUDIT_SPECIFICATION.md # Detailed framework documentation
├── README.md             # This file
└── .streamlit/
    └── config.toml       # Streamlit configuration
```

---

## Data Requirements

### Required Files

| File | Source | How to Download |
|------|--------|-----------------|
| SQP Brand View | Brand Analytics | Seller Central → Brands → Brand Analytics → Search Query Performance → Download |
| PPC Bulk Sheet | Advertising Console | Ads Console → Bulk Operations → Download |
| Business Report | Seller Central | Reports → Business Reports → Detail Page Sales and Traffic → Download |
| FBA Inventory | Seller Central | Inventory → Manage FBA Inventory → Download |

### File Formats Accepted
- CSV (recommended)
- Excel (.xlsx)

---

## Customization

### Adding Your Branding

Edit the CSS in `app.py`:
```python
st.markdown("""
<style>
    .main-header {
        color: #YOUR_BRAND_COLOR;
    }
    /* Add more custom styles */
</style>
""", unsafe_allow_html=True)
```

### Adding New Analysis Modules

1. Create analysis function:
```python
def analyze_new_module(df):
    # Your analysis logic
    return {'insights': [], 'summary': {}}
```

2. Add to main flow:
```python
if st.session_state.audit_data['new_data'] is not None:
    st.session_state.analysis_results['new_module'] = analyze_new_module(...)
```

3. Create new tab in UI

---

## Cost Breakdown

| Component | Cost | Notes |
|-----------|------|-------|
| Streamlit Cloud | Free | For public apps |
| Claude API | ~$0.50-2/audit | Based on token usage |
| Railway (optional) | $5-10/mo | For private apps |
| **Total per audit** | **~$1-2** | At $997/audit = 99%+ margin |

---

## Support

For questions or customization requests, contact [your-email].

---

## License

Proprietary - AdSellix 2026
