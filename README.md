# AI India House Price Prediction Platform

A production-grade, AI-powered real estate pricing platform built with Python, Streamlit, and Scikit-learn.

## Overview
This platform predicts house prices across India using machine learning and location intelligence. It features a premium PropTech-inspired UI, automated data cleaning pipelines, and interactive market analytics.

## Features
- **Price Prediction**: Predict property prices (in ₹ Lakhs/Crore) using an optimized XGBoost Regressor.
- **Market Insights**: Interactive Plotly dashboards analyzing price trends, location premiums, and size metrics.
- **AI Insights**: Dynamically generated insights on the real estate market derived directly from the trained models.
- **Automated ML Pipeline**: Includes data cleaning, outlier removal, coordinate fixing, feature engineering, and hyperparameter tuning with Cross-Validation.

## Dataset Information
- **Size**: ~38,000 properties (after cleaning outliers and duplicates)
- **Features**: City, Location, Latitude, Longitude, Bedrooms, Area (sq.ft)
- **Engineered Features**: Bedroom Density, Location Clusters (K-Means), Area Categories, Premium Location Scores.
- **Target**: Property Price (Lakhs)

## Model Architecture
The training pipeline evaluates four models using 5-Fold Cross Validation:
1. Linear Regression
2. Random Forest Regressor (with RandomizedSearchCV)
3. Gradient Boosting Regressor
4. XGBoost Regressor (with RandomizedSearchCV)

The platform automatically selects and deploys the best performing model.

## Installation
1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Training
To retrain the models from scratch:
```bash
python train.py
```
This will generate new artifacts in the `models/` directory.

## Deployment
To run the web application locally:
```bash
streamlit run app.py
```
The application is fully compatible with Streamlit Community Cloud and can be deployed instantly without code modifications.

## Roadmap
- Integrate API for live property data ingestion
- Add property image generation and styling using GenAI
- Expand feature set to include property amenities (parking, security, etc.)
