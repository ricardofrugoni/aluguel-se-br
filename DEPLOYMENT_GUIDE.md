# 🚀 Deploy Guide - GitHub + Streamlit Cloud

## Overview

This guide will help you deploy your rental price prediction project to GitHub and make it publicly accessible via Streamlit Cloud.

## Step 1: Prepare GitHub Repository

### 1.1 Initialize Git (if not already done)
```bash
# Initialize git repository
git init

# Add all files
git add .

# First commit
git commit -m "Initial commit: Rental price prediction system"
```

### 1.2 Create GitHub Repository
1. Go to [GitHub.com](https://github.com)
2. Click "New repository"
3. Name: `aluguel-se-br` (or your preferred name)
4. Description: "Machine Learning system for predicting short-term rental prices in São Paulo and Rio de Janeiro"
5. Make it **Public** (for free Streamlit Cloud)
6. **Don't** initialize with README (we already have one)

### 1.3 Connect Local to GitHub
```bash
# Add remote origin
git remote add origin https://github.com/ricardofrugoni/aluguel-se-br.git

# Push to GitHub
git push -u origin main
```

## Step 2: Prepare for Streamlit Cloud

### 2.1 Create Streamlit Configuration
Create `.streamlit/config.toml`:

```toml
[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false
```

### 2.2 Update Requirements
Ensure `requirements.txt` includes all dependencies:

```txt
streamlit>=1.28.0
plotly>=5.17.0
pandas>=1.5.0
numpy>=1.24.0
folium>=0.14.0
scikit-learn>=1.3.0
xgboost>=1.7.0
lightgbm>=4.0.0
catboost>=1.2.0
requests>=2.31.0
```

### 2.3 Create Sample Data
```bash
# Download real data
python scripts/download_data.py

# Create samples for demo
python scripts/prepare_sample.py
```

## Step 3: Deploy to Streamlit Cloud

### 3.1 Access Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub account
3. Click "New app"

### 3.2 Configure App
- **Repository**: `ricardofrugoni/aluguel-se-br`
- **Branch**: `main`
- **Main file path**: `dashboard/globe_app.py`
- **App URL**: Choose custom name (e.g., `airbnb-price-prediction`)

### 3.3 Advanced Settings
```toml
# In Streamlit Cloud settings
Python version: 3.9
Dependencies: requirements.txt
```

## Step 4: Verify Deployment

### 4.1 Check App Status
- App should be available at: `https://airbnb-price-prediction.streamlit.app`
- Check logs for any errors
- Test all dashboard features

### 4.2 Common Issues & Solutions

**Issue: App won't start**
```bash
# Check requirements.txt is complete
# Ensure all imports are available
# Check file paths are correct
```

**Issue: No data showing**
```bash
# Ensure sample_data.csv is in repository
# Check data loading logic in globe_app.py
```

**Issue: Performance problems**
```bash
# Reduce sample size in dashboard
# Optimize data loading with @st.cache_data
```

## Step 5: Update README for Public Access

### 5.1 Add Live Demo Link
Update `README.md`:

```markdown
## 🌐 Live Demo

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://airbnb-price-prediction.streamlit.app)

**Interactive Dashboard**: Explore rental prices with 3D globe visualization
```

### 5.2 Add Badges
```markdown
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
```

## Step 6: Continuous Updates

### 6.1 Update Workflow
```bash
# Make changes locally
git add .
git commit -m "Update dashboard features"
git push origin main

# Streamlit Cloud auto-deploys from main branch
```

### 6.2 Monitor Deployment
- Check Streamlit Cloud dashboard for status
- Monitor app logs for errors
- Test new features after deployment

## Step 7: Share and Promote

### 7.1 Social Media
- LinkedIn: Share project with ML community
- Twitter: Tag relevant hashtags (#MachineLearning #DataScience)
- GitHub: Star your own repository

### 7.2 Portfolio Integration
- Add to your portfolio website
- Include in resume/CV
- Mention in job applications

## Troubleshooting

### Common Deployment Issues

**1. Import Errors**
```python
# Check all imports in globe_app.py
# Ensure requirements.txt has all packages
# Test locally before deploying
```

**2. Data Loading Issues**
```python
# Use relative paths
# Check file exists in repository
# Add error handling for missing files
```

**3. Performance Issues**
```python
# Use @st.cache_data for expensive operations
# Limit data size for demo
# Optimize visualizations
```

### Debug Commands
```bash
# Test locally
streamlit run dashboard/globe_app.py

# Check requirements
pip list

# Verify data files
ls -la data/processed/
```

## Success Checklist

- [ ] ✅ Repository is public on GitHub
- [ ] ✅ All files committed and pushed
- [ ] ✅ Streamlit app deployed successfully
- [ ] ✅ Dashboard loads without errors
- [ ] ✅ Data displays correctly
- [ ] ✅ All features working
- [ ] ✅ README updated with live demo
- [ ] ✅ Documentation complete

## Next Steps

1. **Monitor Usage**: Check Streamlit Cloud analytics
2. **Gather Feedback**: Ask for user feedback
3. **Iterate**: Improve based on feedback
4. **Scale**: Consider paid hosting for production use
5. **Extend**: Add more cities or features

## Support

- 📧 **Email**: ricardo@example.com
- 🐛 **Issues**: GitHub Issues
- 📖 **Docs**: [Documentation](docs/)
- 💬 **Discussions**: GitHub Discussions

---

**🎉 Congratulations!** Your rental price prediction system is now live and accessible to the world!
