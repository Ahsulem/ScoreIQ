from datetime import datetime

from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_dance.contrib.github import github, make_github_blueprint
from flask_dance.consumer import oauth_authorized
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from sqlalchemy import text
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

from src.pipeline.prediction_pipeline import CustomData, PredictPipeline

application = Flask(__name__)

app = application

# ── Config ────────────────────────────────────────────────────────────────────
app.config["SECRET_KEY"] = "medicalchatbot"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///predictions.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# ── GitHub OAuth credentials ──────────────────────────────────────────────
app.config["GITHUB_OAUTH_CLIENT_ID"]     = "Ov23lipsQVDpTLA9mEMP"
app.config["GITHUB_OAUTH_CLIENT_SECRET"] = "aa915dfe6b0bdef3ef1b66ee3a451de19cf76308"

db = SQLAlchemy(app)

# ── GitHub OAuth blueprint ───────────────────────────────────────────────────────────
github_bp = make_github_blueprint(
    client_id     = app.config["GITHUB_OAUTH_CLIENT_ID"],
    client_secret = app.config["GITHUB_OAUTH_CLIENT_SECRET"],
    scope         = "user:email",
)
app.register_blueprint(github_bp, url_prefix="/login")

# ── Flask-Login ───────────────────────────────────────────────────────────────
login_manager = LoginManager(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id: str):
    return db.session.get(User, int(user_id))


# ── Models ───────────────────────────────────────────────────────────────────
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id         = db.Column(db.Integer,  primary_key=True, autoincrement=True)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    password   = db.Column(db.String(256), nullable=False)
    name       = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    github_id  = db.Column(db.String(50), nullable=True)

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"


class Prediction(db.Model):
    __tablename__ = "predictions"

    id                  = db.Column(db.Integer,  primary_key=True, autoincrement=True)
    user_id             = db.Column(db.Integer,  db.ForeignKey("users.id"), nullable=True)
    gender              = db.Column(db.String(20),  nullable=False)
    race_ethnicity      = db.Column(db.String(50),  nullable=False)
    parental_education  = db.Column(db.String(60),  nullable=False)
    lunch               = db.Column(db.String(30),  nullable=False)
    test_prep_course    = db.Column(db.String(30),  nullable=False)
    reading_score       = db.Column(db.Integer,     nullable=False)
    writing_score       = db.Column(db.Integer,     nullable=False)
    predicted_score     = db.Column(db.Float,       nullable=False)
    timestamp           = db.Column(db.DateTime,    default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<Prediction id={self.id} predicted={self.predicted_score:.2f}>"


# ── Create tables on first run ────────────────────────────────────────────────
with app.app_context():
    db.create_all()


# ── Helpers ───────────────────────────────────────────────────────────────────
def _migrate_session_to_db(user) -> int:
    """Write every session prediction to the DB for *user*, then clear the list.
    Returns the number of records migrated."""
    entries = session.get("predictions", [])
    if not entries:
        return 0
    for e in entries:
        try:
            ts = datetime.strptime(e["timestamp"], "%Y-%m-%dT%H:%M:%S")
        except Exception:
            ts = datetime.utcnow()
        record = Prediction(
            user_id            = user.id,
            gender             = e["gender"],
            race_ethnicity     = e["race_ethnicity"],
            parental_education = e["parental_education"],
            lunch              = e["lunch"],
            test_prep_course   = e["test_prep_course"],
            reading_score      = e["reading_score"],
            writing_score      = e["writing_score"],
            predicted_score    = e["predicted_score"],
            timestamp          = ts,
        )
        db.session.add(record)
    db.session.commit()
    count = len(entries)
    session.pop("predictions", None)
    session.modified = True
    return count


# ── Auth routes ──────────────────────────────────────────────────────────────
@app.route("/login-github")
def login_github():
    """Entry point: store the post-auth destination then hand off to flask-dance."""
    # flask-dance pops `github_oauth_next` after the callback and redirects there
    session["github_oauth_next"] = url_for("history")
    return redirect(url_for("github.login"))


# ── GitHub OAuth callback (fires before flask-dance's redirect) ──────────────
@oauth_authorized.connect_via(github_bp)
def github_logged_in(blueprint, token):
    if not token:
        flash("GitHub login failed — no token received.", "danger")
        return False

    # ── Fetch profile ──────────────────────────────────────────────────────────────
    resp = blueprint.session.get("/user")
    if not resp.ok:
        flash("Could not fetch your GitHub profile.", "danger")
        return False

    github_info = resp.json()
    github_id   = str(github_info["id"])
    name        = github_info.get("name") or github_info.get("login", "")

    # ── Resolve email (may be private on profile, so also try /user/emails) ──
    email = github_info.get("email")
    if not email:
        emails_resp = blueprint.session.get("/user/emails")
        if emails_resp.ok:
            for entry in emails_resp.json():
                if entry.get("primary") and entry.get("email"):
                    email = entry["email"]
                    break
    if not email:
        email = f"{github_info.get('login', github_id)}@github.noemail"

    # ── Find or create User ──────────────────────────────────────────────────────
    user = User.query.filter_by(github_id=github_id).first()
    if not user:
        user = User.query.filter_by(email=email).first()
    if user:
        # Link github_id to an existing email-based account if not already set
        if not user.github_id:
            user.github_id = github_id
            db.session.commit()
    else:
        # Brand new user via GitHub
        user = User(
            email     = email,
            name      = name or None,
            password  = generate_password_hash("__github_oauth__"),
            github_id = github_id,
        )
        db.session.add(user)
        db.session.commit()

    login_user(user)
    migrated = _migrate_session_to_db(user)
    if migrated:
        flash(
            f"Signed in via GitHub{', ' + name if name else ''}! "
            f"Your {migrated} prediction{'s' if migrated != 1 else ''} "
            "have been saved to your account.",
            "success",
        )
    else:
        flash(f"Signed in via GitHub{', ' + name if name else ''}!", "success")

    # Return False — we don’t have a token-storage model, so tell
    # flask-dance not to attempt SavedToken persistence.
    return False


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email    = request.form.get("email", "").strip().lower()
        name     = request.form.get("name", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Email and password are required.", "danger")
            return redirect(url_for("signup"))

        if User.query.filter_by(email=email).first():
            flash("That email is already registered. Please log in.", "danger")
            return redirect(url_for("signup"))

        user = User(
            email    = email,
            name     = name or None,
            password = generate_password_hash(password),
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        migrated = _migrate_session_to_db(user)
        if migrated:
            flash(
                f"Welcome to ScoreIQ{', ' + name if name else ''}! "
                f"Your {migrated} prediction{'s' if migrated != 1 else ''} "
                "have been saved to your account.",
                "success",
            )
            return redirect(url_for("history"))
        flash(f"Welcome to ScoreIQ{', ' + name if name else ''}! Your account has been created.", "success")
        return redirect(url_for("index"))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            flash("Invalid email or password. Please try again.", "danger")
            return redirect(url_for("login"))

        login_user(user)
        migrated = _migrate_session_to_db(user)
        if migrated:
            flash(
                f"Welcome back{', ' + user.name if user.name else ''}! "
                f"Your {migrated} prediction{'s' if migrated != 1 else ''} "
                "have been saved to your account.",
                "success",
            )
            return redirect(url_for("history"))
        flash(f"Welcome back{', ' + user.name if user.name else ''}!", "success")
        return redirect(url_for("index"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


# ── App routes ────────────────────────────────────────────────────────────────
@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.route("/predictdata", methods=["GET", "POST"])
def predict_datapoint() -> str:
    if request.method == "GET":
        return render_template("home.html")
    else:
        data = CustomData(
            gender=request.form.get("gender"),
            race_ethnicity=request.form.get("ethnicity"),
            parental_level_of_education=request.form.get("parental_level_of_education"),
            lunch=request.form.get("lunch"),
            test_preparation_course=request.form.get("test_preparation_course"),
            reading_score=float(request.form.get("reading_score")),
            writing_score=float(request.form.get("writing_score")),
        )
        pred_df = data.get_data_as_data_frame()
        print(pred_df)
        print("Before Prediction")
        predict_pipeline = PredictPipeline()

        print("Mid Prediction")
        results = predict_pipeline.predict(pred_df)

        print("After Prediction")

        # ── Persist prediction ──────────────────────────────────────────────────
        if current_user.is_authenticated:
            # Logged-in: save immediately and silently to the database
            record = Prediction(
                user_id            = current_user.id,
                gender             = request.form.get("gender"),
                race_ethnicity     = request.form.get("ethnicity"),
                parental_education = request.form.get("parental_level_of_education"),
                lunch              = request.form.get("lunch"),
                test_prep_course   = request.form.get("test_preparation_course"),
                reading_score      = int(float(request.form.get("reading_score"))),
                writing_score      = int(float(request.form.get("writing_score"))),
                predicted_score    = round(float(results[0]), 2),
            )
            db.session.add(record)
            db.session.commit()
            print(f"Auto-saved to DB for user {current_user.id}: {record}")
        else:
            # Logged-out: store in Flask session only (lost on tab close)
            entry = {
                "gender":             request.form.get("gender"),
                "race_ethnicity":     request.form.get("ethnicity"),
                "parental_education": request.form.get("parental_level_of_education"),
                "lunch":              request.form.get("lunch"),
                "test_prep_course":   request.form.get("test_preparation_course"),
                "reading_score":      int(float(request.form.get("reading_score"))),
                "writing_score":      int(float(request.form.get("writing_score"))),
                "predicted_score":    round(float(results[0]), 2),
                "timestamp":          datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),
            }
            history_list = session.get("predictions", [])
            history_list.append(entry)
            session["predictions"] = history_list
            session.modified = True
            print(f"Saved to session: {entry}")
        # ─────────────────────────────────────────────────────────────────────

        return render_template("home.html", results=f"{results[0]:.2f}")


@app.route("/history")
def history() -> str:
    if current_user.is_authenticated:
        rows = (
            Prediction.query
            .filter_by(user_id=current_user.id)
            .order_by(Prediction.timestamp.desc())
            .all()
        )
        predictions = [
            {
                "index":              i + 1,
                "gender":             r.gender,
                "race_ethnicity":     r.race_ethnicity,
                "parental_education": r.parental_education,
                "lunch":              r.lunch,
                "test_prep_course":   r.test_prep_course,
                "reading_score":      r.reading_score,
                "writing_score":      r.writing_score,
                "predicted_score":    r.predicted_score,
                "timestamp_display":  r.timestamp.strftime("%b %d, %Y  %H:%M"),
                "saved":              True,
            }
            for i, r in enumerate(rows)
        ]
    else:
        raw = session.get("predictions", [])
        predictions = []
        for i, p in enumerate(reversed(raw)):
            entry = dict(p)
            try:
                dt = datetime.strptime(p["timestamp"], "%Y-%m-%dT%H:%M:%S")
                entry["timestamp_display"] = dt.strftime("%b %d, %Y  %H:%M")
            except Exception:
                entry["timestamp_display"] = p.get("timestamp", "")
            entry["index"] = len(raw) - i
            entry["saved"] = False
            predictions.append(entry)
    return render_template("history.html", predictions=predictions)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
