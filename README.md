# ScoreIQ — Student Performance Predictor

[![Python Version](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Framework](https://img.shields.io/badge/Framework-Flask-green.svg)](https://flask.palletsprojects.com/)
[![GitHub](https://img.shields.io/badge/GitHub-Ahsulem%2FScoreIQ-181717?logo=github)](https://github.com/Ahsulem/ScoreIQ)

**ScoreIQ** is an end-to-end machine learning web application that predicts a student's math exam score based on demographic and academic inputs. Built with Flask, scikit-learn, CatBoost, and GitHub OAuth, it demonstrates a complete ML workflow — from exploratory data analysis to a production-ready web app with user authentication and persistent prediction history.

---

## 📋 Table of Contents

1. [Project Overview](#-project-overview)
2. [Live Demo](#-live-demo)
3. [Features](#-features)
4. [Technology Stack](#️-technology-stack)
5. [Project Architecture](#️-project-architecture)
6. [Getting Started](#-getting-started)
7. [Running the Application](#-running-the-application)
8. [API Endpoints](#-api-endpoints)
9. [Jupyter Notebooks](#-jupyter-notebooks)
10. [Model Performance](#-model-performance)
11. [Configuration](#️-configuration)
12. [Troubleshooting](#-troubleshooting)
13. [Contributing](#-contributing)
14. [License](#-license)
15. [Future Enhancements](#-future-enhancements)

---

## 📖 Project Overview

**ScoreIQ** aims to understand and predict student performance in mathematics. By analyzing features such as gender, race/ethnicity, parental education level, lunch type, and test preparation course, it builds a regression model that estimates a student's math score with high accuracy.

The application is a production-ready system featuring:
- A clean, Neo-Minimalist web interface
- Email/password authentication and **GitHub OAuth** (one-click sign-in)
- Session-based prediction history for anonymous users, seamlessly migrated to a database-backed account upon sign-up or login
- AWS Elastic Beanstalk deployment support out of the box

---

## 🌐 Live Demo

> Clone the repo and run locally — see [Getting Started](#-getting-started).

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔮 **Math Score Prediction** | Instantly predict a student's math exam score from 7 input features |
| 📊 **Comprehensive EDA** | Detailed exploratory data analysis with visualizations in Jupyter |
| 🤖 **Multi-Model Training** | Trains 7 regression algorithms and selects the best via GridSearchCV |
| 🔐 **User Authentication** | Email/password sign-up & login powered by Flask-Login |
| 🐙 **GitHub OAuth** | One-click sign-in via GitHub using Flask-Dance |
| 📜 **Prediction History** | Full history persisted per user in SQLite (anonymous users use Flask session) |
| 🔄 **Session Migration** | Predictions made before login are automatically migrated to the user's account |
| 🏗️ **Modular ML Pipeline** | Clean separation of data ingestion, transformation, and model training |
| 📝 **Custom Logging & Exceptions** | Structured logging and rich exception traces for easy debugging |
| ☁️ **AWS-Ready** | `.ebextensions` config for one-command Elastic Beanstalk deployment |

---

## 🛠️ Technology Stack

**Backend & Web**
- [Flask](https://flask.palletsprojects.com/) — web framework
- [Flask-Login](https://flask-login.readthedocs.io/) — session management & user authentication
- [Flask-Dance](https://flask-dance.readthedocs.io/) — GitHub OAuth 2.0
- [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/) + SQLite — user & prediction storage
- [Werkzeug](https://werkzeug.palletsprojects.com/) — password hashing

**Machine Learning & Data Science**
- [scikit-learn](https://scikit-learn.org/) — preprocessing pipelines, models, GridSearchCV
- [CatBoost](https://catboost.ai/) — gradient boosting regressor
- [Pandas](https://pandas.pydata.org/) & [NumPy](https://numpy.org/) — data manipulation
- [Matplotlib](https://matplotlib.org/) & [Seaborn](https://seaborn.pydata.org/) — visualization

**Tooling & Deployment**
- [uv](https://github.com/astral-sh/uv) — fast Python package manager (recommended)
- Jupyter Notebook — EDA & experimentation
- AWS Elastic Beanstalk — cloud deployment

---

## 🏗️ Project Architecture

```
ScoreIQ/
├── application.py                   # Flask app — routes, auth, DB models
├── main.py                          # Entry point alias
├── requirements.txt                 # Project dependencies
├── setup.py / pyproject.toml        # Package config
│
├── src/                             # Core source code
│   ├── components/
│   │   ├── data_ingestion.py        # Load CSV → split → save train/test artifacts
│   │   ├── data_transformation.py   # ColumnTransformer pipeline → preprocessor.pkl
│   │   └── model_trainer.py         # GridSearchCV over 7 models → model.pkl
│   ├── pipeline/
│   │   ├── training_pipeline.py     # Orchestrates ingestion → transform → train
│   │   └── prediction_pipeline.py   # Loads artifacts → transforms input → predicts
│   ├── exception.py                 # CustomError with full traceback context
│   ├── logger.py                    # Timestamped rotating file logger
│   └── utils.py                     # save_object / load_object / evaluate_models
│
├── artifacts/                       # Auto-generated ML outputs (gitignored)
│   ├── model.pkl
│   ├── preprocessor.pkl
│   ├── train.csv / test.csv / data.csv
│
├── notebooks/
│   ├── 1 . EDA STUDENT PERFORMANCE .ipynb
│   ├── 2. MODEL TRAINING.ipynb
│   └── data/stud.csv                # Raw dataset
│
├── templates/                       # Jinja2 HTML templates
│   ├── index.html                   # Landing page
│   ├── home.html                    # Prediction form & result
│   ├── history.html                 # Prediction history
│   ├── login.html
│   └── signup.html
│
├── static/css/styles.css            # Application stylesheet
├── instance/predictions.db          # SQLite database (auto-created)
├── logs/                            # Runtime log files (gitignored)
└── .ebextensions/python.config      # AWS Elastic Beanstalk config
```

### ML Pipeline Flow

```
notebooks/data/stud.csv
        │
        ▼
data_ingestion.py  ──→  artifacts/train.csv + test.csv
        │
        ▼
data_transformation.py  ──→  artifacts/preprocessor.pkl
  • Numerical: SimpleImputer(median) + StandardScaler
  • Categorical: SimpleImputer(most_frequent) + OneHotEncoder + StandardScaler
        │
        ▼
model_trainer.py  ──→  artifacts/model.pkl
  • Models: LinearRegression, DecisionTree, RandomForest,
            GradientBoosting, CatBoost, AdaBoost, KNeighbors
  • Selection: GridSearchCV → highest R² (min threshold: 0.6)
        │
        ▼
prediction_pipeline.py
  • Loads preprocessor.pkl + model.pkl
  • Transforms user input → predicts math score
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/Ahsulem/ScoreIQ.git
cd ScoreIQ
```

### 2. Set Up the Environment

#### Recommended — using `uv`

```bash
# Install uv (if not already installed)
# Windows:
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS / Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install all dependencies
uv sync
```

#### Alternative — using `venv` + `pip`

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

---

## 👟 Running the Application

### Step 1 — Train the Model

The `artifacts/` directory is gitignored. Run the training pipeline once to generate `model.pkl` and `preprocessor.pkl`:

```bash
python src/components/data_ingestion.py
# or with uv:
uv run src/components/data_ingestion.py
```

This executes the full pipeline: data ingestion → transformation → model training.

### Step 2 — Start the Flask Server

```bash
python application.py
# or with uv:
uv run application.py
```

### Step 3 — Open the App

Navigate to **http://127.0.0.1:5000** in your browser.

---

## 📝 API Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/` | Landing page | No |
| `GET` | `/predictdata` | Prediction form | No |
| `POST` | `/predictdata` | Submit prediction | No |
| `GET` | `/history` | User prediction history | No (session) / Yes (DB) |
| `GET` | `/signup` | Sign-up form | No |
| `POST` | `/signup` | Create account | No |
| `GET` | `/login` | Login form | No |
| `POST` | `/login` | Authenticate user | No |
| `GET` | `/login-github` | Initiate GitHub OAuth | No |
| `GET` | `/logout` | Log out current user | Yes |

---

## 🧪 Jupyter Notebooks

Located in `notebooks/`:

| Notebook | Description |
|----------|-------------|
| `1 . EDA STUDENT PERFORMANCE .ipynb` | Exploratory data analysis — distributions, correlations, and visualizations that informed feature selection and preprocessing decisions |
| `2. MODEL TRAINING.ipynb` | Initial model experiments — benchmarking all 7 algorithms before refactoring into the `src/` pipeline |

---

## 📈 Model Performance

Seven regression models are evaluated during training:

| Model | Notes |
|-------|-------|
| Linear Regression | Strong baseline for tabular data |
| Decision Tree | Prone to overfit; tuned with criterion |
| Random Forest | Ensemble; tuned n_estimators |
| Gradient Boosting | Learning rate + n_estimators tuned |
| CatBoost Regressor | Handles categoricals natively; depth + learning_rate tuned |
| AdaBoost Regressor | Learning rate + n_estimators tuned |
| K-Neighbors Regressor | n_neighbors + weights tuned |

- **Selection criterion**: Highest R² score on the test set
- **Minimum threshold**: R² ≥ 0.6 (raises error otherwise)
- **Optimization**: `GridSearchCV` with cross-validation

---

## ⚙️ Configuration

### GitHub OAuth

Update the credentials in `application.py` if you want to use your own GitHub OAuth App:

```python
app.config["GITHUB_OAUTH_CLIENT_ID"]     = "<your-client-id>"
app.config["GITHUB_OAUTH_CLIENT_SECRET"] = "<your-client-secret>"
```

> Create an OAuth App at **GitHub → Settings → Developer settings → OAuth Apps**.  
> Set the callback URL to `http://127.0.0.1:5000/login/github/authorized`.

### AWS Elastic Beanstalk

The `.ebextensions/python.config` file is pre-configured. To deploy:

```bash
eb init -p python-3.11 ScoreIQ
eb create scoreiq-env
eb deploy
```

Ensure `artifacts/model.pkl` and `artifacts/preprocessor.pkl` are included before deploying (they are gitignored by default).

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| `FileNotFoundError: artifacts/model.pkl` | Run `python src/components/data_ingestion.py` first |
| `ModuleNotFoundError` | Activate your virtual environment and run `pip install -r requirements.txt` |
| GitHub OAuth redirect error | Verify callback URL in your GitHub OAuth App settings |
| Port already in use | Change port: `app.run(port=5001)` in `application.py` |
| Blank prediction history | For anonymous users, history is stored in the Flask session (cleared on browser close) — sign up to save permanently |

Check the `logs/` directory for detailed runtime error traces.

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for full guidelines.

**Quick steps:**

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m "feat: add your feature"`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🎯 Future Enhancements

- [ ] REST API with JWT authentication for programmatic access
- [ ] Model retraining pipeline triggered from the UI
- [ ] Performance monitoring dashboard (accuracy drift, input distributions)
- [ ] Docker container & docker-compose setup
- [ ] Support for predicting reading and writing scores too
- [ ] Export prediction history as CSV
- [ ] A/B testing framework for model comparison in production
