# 🚀 Kepler Explorer
Machine Learning-Powered Exoplanet Classification & Analysis  
**Team Syntax Error | Round 1**

Kepler Explorer is a web application powered by machine learning that analyzes transit photometry data from NASA's Kepler Space Telescope to detect and characterize exoplanet candidates. It combines classification and regression models to provide detailed exoplanet insights with an intuitive, space-themed interface for researchers, students, and space enthusiasts.

---

## 📋 Table of Contents
- [Overview](#-overview)  
- [Features](#-features)  
- [Tech Stack](#-tech-stack)  
- [Usage](#-usage)  
- [Database](#-database)  
- [Team](#-team-syntax-error)  
  

---

## 🌟 Overview
Kepler Explorer is a machine learning-powered web application that analyzes transit photometry data from NASA's Kepler Space Telescope to identify and characterize exoplanet candidates. The system combines classification and regression models to provide comprehensive exoplanet analysis with an intuitive, space-themed interface.

Built by **Team Syntax Error** for Round 1, this tool makes exoplanet verification accessible to researchers, students, and space enthusiasts alike.

---

## ✨ Features

### 🔬 Core ML Capabilities
- **Exoplanet Classification:** Binary classification to distinguish confirmed exoplanets from false positives using 9 transit parameters  
- **Radius Prediction:** Regression model to estimate planetary radius in Earth radii for confirmed candidates  
- **Confidence Scoring:** Probability scores (0-100%) for all predictions  
- **Planet Type Classification:** Automatic categorization as Earth-sized, Super-Earth, or Gas Giant based on radius  

### 🎨 Interactive User Interface
- **Real-time Predictions:** Instant feedback with visual confidence meters  
- **Interactive Visualizations:** Chart.js graphs including doughnut charts, bar charts, line charts, and radar charts  
- **Responsive Design:** Fully responsive space-themed UI for desktop, tablet, and mobile  
- **Prediction History:** Session-based tracking of all classifications with detailed parameter display  
- **Auto Database Cleanup:** Maintains only the 10 most recent predictions  

### 📊 Parameter Analysis
The system analyzes 13 Kepler transit parameters:  
- **Orbital characteristics:** period, epoch, duration  
- **Transit signal metrics:** depth, SNR, impact parameter  
- **Host star properties:** temperature, gravity, radius  
- **Planetary environment:** equilibrium temperature, insolation flux  

---

## 🛠️ Tech Stack

### Backend
| Technology | Version | Purpose |
|------------|--------|---------|
| Python     | 3.8+   | Core programming language |
| Flask      | 2.0+   | Web framework |
| scikit-learn | 1.0+ | Machine learning models |
| SQLite     | 3      | Database |
| NumPy      | 1.21+  | Numerical computing |
| pandas     | 1.3+   | Data manipulation |
| joblib     | 1.1+   | Model persistence |

### Frontend
| Technology | Purpose |
|------------|--------|
| HTML5      | Structure |
| CSS3       | Styling with CSS Grid/Flexbox |
| JavaScript | Interactivity |
| Chart.js   | Interactive visualizations |

### Machine Learning Models
| Model File | Description |
|------------|------------|
| classifier.pkl | Binary classification model (Confirmed/False Positive) |
| regressor.pkl  | Radius prediction regression model |
| scalar_x.pkl   | Input feature scaler |
| scalar_y.pkl   | Output radius scaler |

---

### Input Parameters
| Parameter     | Description           | Unit |
|---------------|-------------------|------|
| koi_period    | Orbital period      | days |
| koi_time0bk   | Transit epoch       | days |
| koi_impact    | Impact parameter    | -    |
| koi_duration  | Transit duration    | hours|
| koi_depth     | Transit depth       | ppm  |
| koi_model_snr | Signal-to-noise ratio | -  |
| koi_steff     | Star temperature    | K    |
| koi_slogg     | Star gravity        | log(g) |
| koi_srad      | Star radius         | solar radii |
| koi_teq       | Equilibrium temperature | K |
| koi_insol     | Insolation flux     | Earth flux |

## 🎮 Usage

### Home Page
- Introduction to Kepler Explorer  
- Overview of features  
- Navigation to Classification and About pages  

### Classification
- Enter 11 Kepler transit parameters  
- Click **"Analyze Planet"** to run ML inference  
- View results including:  
  - Classification (Confirmed Planet / False Positive)  
  - Confidence score  
  - Planet probability  
  - Estimated radius (if confirmed)  
  - Planet type  

### Regression
- Direct radius prediction for any object  
- Enter 10 parameters  
- Get estimated planetary radius  

### Insights
- View stellar statistics from the Kepler dataset  
- Track session prediction history  
- See all 17 parameters for each prediction  
- Clear history using the **Clear History** button  

### About
- Project information  
- Technology stack details  
- FAQ section

  
🗄️ Database

SQLite (cosmos.db) schema:
| Column        | Type    | Description                                        |
| ------------- | ------- | -------------------------------------------------- |
| id            | INTEGER | Primary key (auto-increment)                       |
| time          | TEXT    | Timestamp of prediction                            |
| label         | TEXT    | 'Confirmed Planet' or 'False Positive'             |
| confidence    | REAL    | Confidence score (0-100)                           |
| probability   | REAL    | Planet probability (0-100)                         |
| radius        | REAL    | Estimated radius in Earth radii                    |
| planet_type   | TEXT    | 'Earth-sized', 'Super-Earth', 'Gas Giant', or NULL |
| koi_period    | REAL    | Orbital period                                     |
| koi_time0bk   | REAL    | Transit epoch                                      |
| koi_impact    | REAL    | Impact parameter                                   |
| koi_duration  | REAL    | Transit duration                                   |
| koi_depth     | REAL    | Transit depth                                      |
| koi_model_snr | REAL    | Signal-to-noise ratio                              |
| koi_steff     | REAL    | Star temperature                                   |
| koi_slogg     | REAL    | Star gravity                                       |
| koi_srad      | REAL    | Star radius                                        |
| koi_teq       | REAL    | Equilibrium temperature                            |
| koi_insol     | REAL    | Insolation flux                                    |

## 👥 Team Syntax Error

| Role                     | Name                           |
|--------------------------|--------------------------------|
| ML Engineer              | Rajat Kantode, Animesh Kewale |
| Frontend & Backend Developer | Abhinandan Pakhare            |
