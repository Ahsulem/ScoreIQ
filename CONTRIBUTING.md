# Contributing to ScoreIQ

Thank you for considering contributing to **ScoreIQ**! Every contribution — whether it's a bug fix, new feature, documentation improvement, or test — is appreciated.

---

## 📋 Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [How to Contribute](#how-to-contribute)
3. [Development Setup](#development-setup)
4. [Project Structure](#project-structure)
5. [Commit Message Convention](#commit-message-convention)
6. [Pull Request Guidelines](#pull-request-guidelines)
7. [Reporting Bugs](#reporting-bugs)
8. [Suggesting Features](#suggesting-features)

---

## Code of Conduct

By participating in this project you agree to be respectful and constructive. Harassment, discrimination, or any form of disrespectful behavior will not be tolerated.

---

## How to Contribute

1. **Fork** the repository on GitHub.
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/<your-username>/ScoreIQ.git
   cd ScoreIQ
   ```
3. **Create a branch** for your change:
   ```bash
   git checkout -b feature/my-new-feature
   # or for bug fixes:
   git checkout -b fix/issue-description
   ```
4. **Make your changes** (see Development Setup below).
5. **Commit** following the [convention](#commit-message-convention).
6. **Push** and open a **Pull Request** against the `main` branch.

---

## Development Setup

### 1. Install dependencies

```bash
# Using uv (recommended)
uv sync

# Or using pip
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

### 2. Train the model (required before running the app)

```bash
python src/components/data_ingestion.py
```

### 3. Run the app

```bash
python application.py
```

Open **http://127.0.0.1:5000** to verify everything works.

---

## Project Structure

| Path | Responsibility |
|------|---------------|
| `src/components/` | ML pipeline — data ingestion, transformation, model training |
| `src/pipeline/` | Training & prediction orchestration |
| `application.py` | Flask routes, auth, DB models |
| `templates/` | Jinja2 HTML templates |
| `static/` | CSS and static assets |
| `notebooks/` | EDA and model experimentation notebooks |

---

## Commit Message Convention

Use [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>: <short description>
```

| Type | When to use |
|------|------------|
| `feat` | A new feature |
| `fix` | A bug fix |
| `docs` | Documentation changes only |
| `style` | Formatting, missing semicolons, etc. — no logic change |
| `refactor` | Code refactoring without feature/fix |
| `test` | Adding or updating tests |
| `chore` | Build process, dependency updates |

**Examples:**
```
feat: add CSV export for prediction history
fix: resolve session migration bug on signup
docs: update API endpoints table in README
```

---

## Pull Request Guidelines

- Keep PRs **focused** — one feature or fix per PR.
- Provide a **clear description** of what your PR does and why.
- Reference any related issues: `Closes #12`.
- Ensure the app runs without errors before submitting.
- Update `README.md` or docstrings if your change affects documented behaviour.

---

## Reporting Bugs

Open a [GitHub Issue](https://github.com/Ahsulem/ScoreIQ/issues) and include:

- A clear, descriptive title
- Steps to reproduce the issue
- Expected behaviour vs. actual behaviour
- Relevant logs from the `logs/` directory
- Your Python version (`python --version`) and OS

---

## Suggesting Features

Open a [GitHub Issue](https://github.com/Ahsulem/ScoreIQ/issues) with the label **enhancement** and describe:

- The problem your feature would solve
- Your proposed solution
- Any alternatives you considered
