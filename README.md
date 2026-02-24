# Headcount Change Reasons Dashboard

Interactive dashboard analyzing factors driving headcount changes across 1,030 companies.

## Features

- **Multiple Views**: Overview, Detailed Analysis, Comparative View, and Insights
- **Interactive Filters**: Filter by category (Rev Growth, Company Rev, Employee Size, Industry)
- **Rich Visualizations**: 
  - Bar charts showing top reasons
  - Heatmaps of all reasons across groups
  - Comparative radar charts
  - Correlation analysis
  - Distribution plots
- **Key Insights**: Automatic identification of most/least impactful and divisive factors
- **Data Export**: Download filtered data and summary statistics

## Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Deploy to Streamlit Cloud (FREE)

### Step 1: Push to GitHub

```bash
# Initialize git (if not already done)
git init

# Add files
git add .
git commit -m "Initial commit: Headcount dashboard"

# Create repository on GitHub and push
git remote add origin https://github.com/YOUR-USERNAME/headcount-dashboard.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select:
   - Repository: `YOUR-USERNAME/headcount-dashboard`
   - Branch: `main`
   - Main file path: `app.py`
5. Click "Deploy"

Your app will be live at: `https://YOUR-USERNAME-headcount-dashboard.streamlit.app`

## Project Structure

```
headcount-dashboard/
├── app.py                          # Main Streamlit application
├── companies_data_clean.csv        # Cleaned survey data
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

## Data Format

The data contains survey responses from companies about reasons for headcount changes:

- **Categories**: Rev Growth, Company Rev, Employee Size, Industry
- **Subcategories**: Specific groups within each category (e.g., "Up 10-19.9%", "Tech", "50-99 employees")
- **Reasons**: 17 different factors influencing headcount decisions (as percentage of respondents)

## Customization

To add new visualizations or modify existing ones, edit `app.py`. The app uses:
- **Streamlit** for the web interface
- **Pandas** for data manipulation
- **Plotly** for interactive charts
