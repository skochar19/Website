from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from translations import TRANSLATIONS
import sqlite3
import os
import requests as req

load_dotenv()

app = Flask(__name__)
app.secret_key = "settle-smart-secret-key-change-me"

# ---------------------------------------------------
# Flask-Login setup
# ---------------------------------------------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# ---------------------------------------------------
# Database setup
# ---------------------------------------------------
def get_db():
    conn = sqlite3.connect("settle_smart.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            county_name TEXT NOT NULL,
            searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS compare_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            county1 TEXT NOT NULL,
            county2 TEXT NOT NULL,
            searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            user_message TEXT NOT NULL,
            bot_reply TEXT NOT NULL,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS counties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            summer_temp INTEGER,
            winter_temp INTEGER,
            avg_cost_of_living INTEGER,
            crime_safety TEXT,
            school_quality TEXT,
            diversity_percent REAL,
            crime_explanation TEXT,
            school_explanation TEXT,
            race_white REAL,
            race_black REAL,
            race_hispanic REAL,
            race_asian REAL,
            race_american_indian REAL,
            race_native_hawaiian REAL,
            race_multiracial REAL,
            lat REAL,
            lng REAL
        )
    """)
    conn.commit()
    conn.close()
    seed_counties()

def seed_counties():
    """Insert county data if the table is empty."""
    conn = get_db()
    if conn.execute("SELECT COUNT(*) FROM counties").fetchone()[0] > 0:
        conn.close()
        return

    counties_data = [
        # name, sum_t, win_t, cost, crime, school, div%,
        # crime_expl, school_expl,
        # white, black, hispanic, asian, am_indian, nat_hawaii, multiracial,
        # lat, lng
        ("Allegany County", 83, 28, 1550, "Medium", "Medium", 14,
         "Allegany County has moderate crime rates, largely concentrated in Cumberland city. Rural areas are generally safe, but property crime in the urban core keeps the rating at medium.",
         "Schools here are improving but still face funding challenges tied to the county's economic decline from the coal industry. Test scores and graduation rates are near the state average.",
         87.3, 8.0, 1.7, 1.0, 0.2, 0.0, 1.7, 39.65, -78.76),

        ("Anne Arundel County", 87, 32, 2400, "Medium", "High", 32,
         "Anne Arundel has a mixed profile — suburban areas near Annapolis and Severna Park are quite safe, while parts of Glen Burnie see higher property crime rates, keeping the overall rating at medium.",
         "Home to some of Maryland's top-ranked schools, Anne Arundel benefits from strong county funding and a well-regarded school administration. Many schools score above state averages.",
         69.5, 16.3, 7.3, 3.9, 0.3, 0.1, 2.6, 38.98, -76.49),

        ("Baltimore County", 86, 31, 2100, "High", "Medium", 43,
         "Baltimore County (separate from Baltimore City) has elevated crime in areas like Dundalk and Owings Mills, driven by proximity to urban centers. Suburban pockets are safer but the county average sits high.",
         "Schools vary significantly by area — affluent communities like Towson have excellent schools, while western parts of the county lag. Overall performance is mid-tier for Maryland.",
         58.8, 27.5, 5.2, 6.0, 0.3, 0.0, 2.1, 39.40, -76.60),

        ("Calvert County", 87, 34, 2350, "Low", "High", 22,
         "Calvert is one of Maryland's safest counties. Its rural character, tight-knit communities, and limited urban density contribute to very low crime rates across the board.",
         "Calvert County Public Schools consistently earn top marks, with high graduation rates, strong SAT/ACT scores, and well-funded programs. A great choice for families prioritizing education.",
         78.8, 12.9, 3.7, 1.6, 0.3, 0.1, 2.6, 38.54, -76.59),

        ("Caroline County", 88, 33, 1700, "Medium", "Low", 25,
         "Crime rates are moderate for Caroline County. While overall violent crime is low, property crime in Denton and economic stressors in rural areas keep safety at an average level.",
         "Caroline County schools face challenges from limited funding and rural poverty. Graduation rates and standardized test performance fall below the Maryland state average.",
         76.5, 14.0, 6.6, 0.8, 0.3, 0.0, 1.7, 38.88, -75.83),

        ("Carroll County", 85, 29, 2300, "Low", "High", 11,
         "Carroll County is among Maryland's safest, with very low rates of both violent and property crime. Its largely rural, suburban landscape and stable community fabric drive this strong safety record.",
         "Carroll County schools rank highly across Maryland. Strong community investment, low student-to-teacher ratios, and high parental involvement result in excellent academic outcomes.",
         89.9, 3.5, 3.2, 1.8, 0.2, 0.0, 1.5, 39.58, -76.99),

        ("Cecil County", 86, 30, 1850, "Medium", "Medium", 15,
         "Cecil County sees moderate crime, with higher rates near Elkton along major highway corridors. Suburban and rural areas are comparatively safer, balancing out the county's overall rating.",
         "Cecil County schools offer average quality for Maryland. Resources are sufficient but not exceptional, and performance varies between rural schools and those near the Pennsylvania border.",
         85.5, 6.7, 4.2, 1.2, 0.3, 0.1, 2.0, 39.61, -75.83),

        ("Charles County", 88, 34, 2400, "Low", "Medium", 60,
         "Charles County maintains low crime rates thanks to strong suburban development, active community policing, and a growing middle-class population relocating from the DC metro area.",
         "Schools in Charles County are solid, with improving graduation rates and several highly-rated magnet programs. The district benefits from a growing tax base and community engagement.",
         43.2, 43.9, 5.5, 3.3, 0.6, 0.1, 3.4, 38.53, -77.01),

        ("Dorchester County", 88, 33, 1650, "High", "Low", 37,
         "Dorchester County has above-average crime rates, particularly in Cambridge. Economic challenges, high poverty levels, and limited social services contribute to elevated property and violent crime.",
         "Schools in Dorchester face serious funding and performance challenges. High poverty rates, low graduation rates, and below-average test scores make it one of Maryland's weaker school districts.",
         64.0, 27.7, 4.9, 1.2, 0.3, 0.0, 1.8, 38.57, -76.08),

        ("Frederick County", 85, 30, 2600, "Low", "High", 26,
         "Frederick County is one of Maryland's safest larger counties. Rapid suburban growth has brought investment and strong policing. Both violent and property crime rates remain well below state averages.",
         "Frederick County Public Schools are consistently top-rated in Maryland. Strong funding, excellent teacher retention, and a growing, educated population all contribute to outstanding academic performance.",
         75.0, 9.0, 8.7, 4.5, 0.2, 0.1, 2.5, 39.41, -77.41),

        ("Garrett County", 78, 22, 1500, "Low", "Medium", 4,
         "Garrett County has very low crime rates. Its remote, rural mountain setting means a small, tight-knit population and minimal criminal activity — one of Maryland's safest counties.",
         "Schools in Garrett County are adequate but limited by rural isolation and a small tax base. Performance is middle-of-the-road for Maryland, though the community values education highly.",
         96.4, 1.1, 1.1, 0.5, 0.1, 0.0, 0.8, 39.41, -79.41),

        ("Harford County", 85, 30, 2000, "Low", "Medium", 24,
         "Harford County is a safe suburban county. Low violent crime and moderate property crime, combined with strong community policing near Aberdeen Proving Ground, keep safety ratings favorable.",
         "Harford County schools perform well, supported by military-community investment and stable suburban funding. Several schools rank among the state's best, especially at the high school level.",
         77.0, 13.1, 4.3, 3.1, 0.2, 0.1, 2.3, 39.54, -76.35),

        ("Howard County", 86, 31, 3300, "Low", "High", 48,
         "Howard County is among Maryland's safest counties. Excellent community resources, high median incomes, and proactive law enforcement contribute to consistently low crime across the county.",
         "Howard County Public School System is nationally recognized as one of the best in the country. Exceptional funding, diverse magnet programs, and high academic standards make it Maryland's top school district.",
         54.2, 18.3, 6.5, 17.5, 0.2, 0.1, 3.2, 39.27, -76.80),

        ("Kent County", 87, 32, 1900, "Low", "Medium", 22,
         "Kent County has low crime rates characteristic of its small, rural Eastern Shore community. Chestertown is a peaceful college town environment that keeps overall crime minimal.",
         "Kent County schools are average for Maryland. The rural district has a small student population and limited resources, though teachers are dedicated and graduation rates are acceptable.",
         78.2, 14.8, 4.3, 1.0, 0.1, 0.0, 1.5, 39.21, -76.07),

        ("Montgomery County", 86, 30, 3500, "Low", "High", 60,
         "Montgomery County has low crime relative to its large population and proximity to DC. Robust county resources, diverse community programs, and strong policing keep it among Maryland's safest major counties.",
         "Montgomery County Public Schools is one of the largest and most celebrated school systems in the nation. Top-ranked nationally, it offers exceptional magnet programs, high diversity, and outstanding academic results.",
         45.2, 17.8, 19.0, 15.2, 0.2, 0.0, 2.6, 39.08, -77.15),

        ("Prince George's County", 88, 33, 2400, "Medium", "Medium", 75,
         "Prince George's County has moderate crime rates — higher near urban centers like Hyattsville and Landover, but safer in suburban areas like Bowie and College Park. Crime has improved significantly in recent years.",
         "Schools in Prince George's County are improving under ongoing reform efforts. Performance varies widely across the district, with some schools excelling while others in lower-income areas face persistent challenges.",
         13.9, 62.1, 17.2, 4.5, 0.2, 0.0, 2.0, 38.82, -76.75),

        ("Queen Anne's County", 87, 33, 2500, "Low", "High", 14,
         "Queen Anne's County is very safe, benefiting from a low-density rural and suburban mix. Crime rates are among the lowest on Maryland's Eastern Shore, with minimal violent crime reported.",
         "Queen Anne's County schools perform well above the state average. Small class sizes, engaged parents, and solid county investment make it one of the Eastern Shore's best school systems.",
         86.5, 6.8, 3.6, 1.1, 0.3, 0.0, 1.8, 39.04, -76.07),

        ("Saint Mary's County", 87, 34, 2100, "Low", "Medium", 26,
         "Saint Mary's County has low crime rates, influenced by a stable military and government workforce centered around NAS Patuxent River. Community cohesion keeps both violent and property crime low.",
         "Schools in Saint Mary's County are solid and well-funded relative to their size. Military family presence contributes to school stability, though performance is average-to-good compared to statewide rankings.",
         74.9, 14.1, 4.9, 2.8, 0.3, 0.1, 2.9, 38.29, -76.64),

        ("Somerset County", 88, 33, 1600, "Medium", "Low", 49,
         "Somerset County has moderate crime despite its small size. Economic hardship and high poverty rates in Princess Anne contribute to above-average crime for a rural county.",
         "Somerset County schools are among Maryland's lowest-ranked. Deep rural poverty, low funding, and high student need create persistent educational challenges, with graduation rates and test scores below state averages.",
         51.5, 41.7, 3.5, 0.9, 0.4, 0.0, 2.0, 38.20, -75.69),

        ("Talbot County", 87, 33, 2400, "Low", "Medium", 22,
         "Talbot County has low crime rates overall. Easton is a prosperous small city with active policing, and the rural areas around it are peaceful. Property crime is minimal.",
         "Talbot County schools perform at or slightly above the Maryland average. The district is small but benefits from the county's above-average household incomes and involved community members.",
         78.2, 12.7, 6.3, 1.3, 0.2, 0.0, 1.4, 38.77, -76.08),

        ("Washington County", 85, 29, 1850, "Medium", "Medium", 21,
         "Washington County has moderate crime, concentrated in Hagerstown. Urban economic stress and proximity to I-81 drug corridors contribute to higher property crime, while rural areas remain safe.",
         "Washington County schools are average for Maryland. The district faces challenges from poverty in Hagerstown but has invested in vocational and technical education programs that serve the community well.",
         80.4, 10.7, 4.5, 1.8, 0.2, 0.1, 2.4, 39.64, -77.72),

        ("Wicomico County", 88, 32, 1700, "High", "Low", 37,
         "Wicomico County has above-average crime rates, particularly in Salisbury. Urban density, poverty, and a transient population near Salisbury University contribute to elevated violent and property crime.",
         "Wicomico County schools face significant challenges. Limited funding, high poverty rates among students, and below-average test scores put the district in the lower tier of Maryland school systems.",
         64.1, 25.0, 5.2, 3.2, 0.2, 0.0, 2.3, 38.36, -75.60),

        ("Worcester County", 88, 33, 2500, "High", "Medium", 20,
         "Worcester County sees elevated crime largely due to Ocean City's seasonal tourism economy. High summer foot traffic drives up property crime and DUI incidents, skewing the annual statistics.",
         "Worcester County schools perform at a medium level. The resort economy limits long-term educational investment, though small class sizes and dedicated staff provide reasonable academic outcomes.",
         79.9, 13.4, 3.4, 1.4, 0.2, 0.0, 1.6, 38.18, -75.39),

        ("Baltimore City", 87, 32, 1900, "High", "Low", 73,
         "Baltimore City has some of the highest crime rates in the nation, particularly for violent crime. Concentrated poverty, historical disinvestment, and limited economic opportunity in many neighborhoods drive these rates — though waterfront and inner-harbor areas have improved significantly.",
         "Baltimore City Public Schools face systemic challenges including underfunding, aging infrastructure, and high student poverty rates. While some magnet and charter schools perform excellently, the overall district lags well behind state and national averages.",
         28.3, 62.1, 4.8, 2.7, 0.3, 0.0, 1.8, 39.29, -76.61),
    ]

    conn.executemany("""
        INSERT INTO counties (
            name, summer_temp, winter_temp, avg_cost_of_living,
            crime_safety, school_quality, diversity_percent,
            crime_explanation, school_explanation,
            race_white, race_black, race_hispanic, race_asian,
            race_american_indian, race_native_hawaiian, race_multiracial,
            lat, lng
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, counties_data)
    conn.commit()
    conn.close()

init_db()

# ---------------------------------------------------
# User class for Flask-Login
# ---------------------------------------------------
class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    if row:
        return User(row["id"], row["username"], row["email"])
    return None

# ---------------------------------------------------
# Language support
# ---------------------------------------------------
@app.context_processor
def inject_lang():
    lang = session.get('lang', 'en')
    return {'t': TRANSLATIONS[lang], 'lang': lang}

@app.route("/set-lang/<code>")
def set_lang(code):
    if code in ('en', 'es'):
        session['lang'] = code
    return redirect(request.referrer or url_for('index'))

# ---------------------------------------------------
# Scoring: returns raw 0–100 AND star 1.0–5.0
# ---------------------------------------------------
def compute_raw_score(entry: dict) -> int:
    score = 70
    if entry["schoolQuality"] == "High":   score += 10
    elif entry["schoolQuality"] == "Low":  score -= 10
    if entry["crimeSafety"] == "Low":      score += 10
    elif entry["crimeSafety"] == "High":   score -= 10
    diversity = entry["diversityPercent"]
    score += max(0, 10 - abs(50 - diversity) // 5)
    cost = entry["averageCostOfLiving"]
    if cost <= 1900:   score += 5
    elif cost >= 3000: score -= 5
    return max(0, min(100, score))

def compute_star_score(entry: dict) -> float:
    raw = compute_raw_score(entry)
    star = round(1.0 + (raw / 100.0) * 4.0, 1)
    return star


def get_county_overview(county_name: str) -> dict:
    conn = get_db()
    row = conn.execute("SELECT * FROM counties WHERE name = ?", (county_name,)).fetchone()
    conn.close()

    if row is None:
        return None

    entry = {
        "name": row["name"],
        "summerTemp": row["summer_temp"],
        "winterTemp": row["winter_temp"],
        "averageCostOfLiving": row["avg_cost_of_living"],
        "crimeSafety": row["crime_safety"],
        "schoolQuality": row["school_quality"],
        "diversityPercent": row["diversity_percent"],
        "crime_explanation": row["crime_explanation"],
        "school_explanation": row["school_explanation"],
        "lat": row["lat"],
        "lng": row["lng"],
        "race": {
            "white": row["race_white"],
            "black": row["race_black"],
            "hispanic": row["race_hispanic"],
            "asian": row["race_asian"],
            "american_indian": row["race_american_indian"],
            "native_hawaiian": row["race_native_hawaiian"],
            "multiracial": row["race_multiracial"],
        },
    }
    entry["overall_score"] = compute_star_score(entry)
    return entry


def get_all_county_names() -> list:
    conn = get_db()
    rows = conn.execute("SELECT name FROM counties ORDER BY name").fetchall()
    conn.close()
    return [r["name"] for r in rows]


# ---------------------------------------------------
# Routes
# ---------------------------------------------------
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", counties=get_all_county_names())


@app.route("/explore", methods=["GET"])
def explore():
    return render_template("explore.html", counties=get_all_county_names())


@app.route("/result", methods=["GET", "POST"])
def result():
    if request.method == "POST":
        selected_county = request.form.get("county")
    else:
        selected_county = request.args.get("county")

    if not selected_county:
        return render_template("explore.html", counties=get_all_county_names(), error="Please select a county.")
    overview = get_county_overview(selected_county)

    # Save to search history if logged in (only on POST to avoid double-saving from history clicks)
    if current_user.is_authenticated and request.method == "POST":
        conn = get_db()
        conn.execute(
            "INSERT INTO search_history (user_id, county_name) VALUES (?, ?)",
            (current_user.id, selected_county),
        )
        conn.commit()
        conn.close()

    return render_template("result.html", county=overview)


@app.route("/compare", methods=["GET", "POST"])
def compare():
    county1 = county2 = county1_name = county2_name = None
    if request.method == "POST":
        county1_name = request.form.get("county1")
        county2_name = request.form.get("county2")
    elif request.args.get("county1") and request.args.get("county2"):
        county1_name = request.args.get("county1")
        county2_name = request.args.get("county2")

    if county1_name: county1 = get_county_overview(county1_name)
    if county2_name: county2 = get_county_overview(county2_name)

    if county1 and county2:
        if request.method == "POST" and current_user.is_authenticated:
            conn = get_db()
            conn.execute(
                "INSERT INTO compare_history (user_id, county1, county2) VALUES (?, ?, ?)",
                (current_user.id, county1_name, county2_name),
            )
            conn.commit()
            conn.close()
        return render_template(
            "compare_result.html",
            county1=county1, county2=county2,
        )

    return render_template(
        "compare.html",
        counties=get_all_county_names(),
        county1_name=county1_name, county2_name=county2_name,
    )


@app.route("/assistant", methods=["GET"])
def assistant():
    return render_template("assistant.html")


# ---------------------------------------------------
# Auth routes
# ---------------------------------------------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        confirm = request.form.get("confirm", "").strip()

        if not username or not email or not password:
            flash("All fields are required.", "error")
            return render_template("signup.html")
        if password != confirm:
            flash("Passwords do not match.", "error")
            return render_template("signup.html")
        if len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return render_template("signup.html")

        conn = get_db()
        existing = conn.execute(
            "SELECT id FROM users WHERE username = ? OR email = ?", (username, email)
        ).fetchone()
        if existing:
            conn.close()
            flash("Username or email already taken.", "error")
            return render_template("signup.html")

        password_hash = generate_password_hash(password)
        conn.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, password_hash),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        user = User(row["id"], row["username"], row["email"])
        login_user(user)
        flash("Account created! Welcome, " + username + ".", "success")
        return redirect(url_for("index"))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        remember = request.form.get("remember") == "on"

        conn = get_db()
        row = conn.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, username)).fetchone()
        conn.close()

        if row and check_password_hash(row["password_hash"], password):
            user = User(row["id"], row["username"], row["email"])
            login_user(user, remember=remember)
            flash("Welcome back, " + row["username"] + "!", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid username/email or password.", "error")
            return render_template("login.html")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You've been logged out.", "success")
    return redirect(url_for("index"))


@app.route("/history")
@login_required
def history():
    conn = get_db()
    explore_rows = conn.execute(
        "SELECT county_name, searched_at FROM search_history WHERE user_id = ? ORDER BY searched_at DESC LIMIT 20",
        (current_user.id,),
    ).fetchall()
    compare_rows = conn.execute(
        "SELECT county1, county2, searched_at FROM compare_history WHERE user_id = ? ORDER BY searched_at DESC LIMIT 20",
        (current_user.id,),
    ).fetchall()
    chat_rows = conn.execute(
        "SELECT user_message, bot_reply, sent_at FROM chat_history WHERE user_id = ? ORDER BY sent_at DESC LIMIT 20",
        (current_user.id,),
    ).fetchall()
    conn.close()
    return render_template("history.html", explore_rows=explore_rows, compare_rows=compare_rows, chat_rows=chat_rows)


# ---------------------------------------------------
# AI Chatbot endpoint
# ---------------------------------------------------
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    message = data.get("message", "").strip()
    county_nm = data.get("county", "")
    history = data.get("history", [])

    if not message:
        return jsonify({"reply": "Please type a message."})

    county_data = get_county_overview(county_nm) if county_nm else {}

    system_prompt = f"""You are Settle Smart's friendly AI assistant helping people decide where to live in Maryland.

Currently viewed county: {county_nm}
County data snapshot:
- Summer Temp: {county_data.get('summerTemp')}°F, Winter Temp: {county_data.get('winterTemp')}°F
- Monthly Cost of Living: ${county_data.get('averageCostOfLiving')}
- Crime & Safety Level: {county_data.get('crimeSafety')}
- School Quality: {county_data.get('schoolQuality')}
- Diversity (People of Color): {county_data.get('diversityPercent')}%
- Overall Star Rating: {county_data.get('overall_score')} / 5.0
- Crime Context: {county_data.get('crime_explanation', '')}
- School Context: {county_data.get('school_explanation', '')}

You have knowledge of all 24 Maryland counties.
Be concise (under 100 words), warm, and genuinely helpful.
Based on the token limit, make sure you are fully responding the question, don't truncate any part.
If asked to compare counties, draw on your Maryland knowledge.
Never make up data — use the snapshot above for this county and general knowledge for others.
{"Respond in Spanish." if session.get("lang") == "es" else ""}"""

    # Convert history to Gemini format
    gemini_history = []
    for msg in history[-6:]:
        if not isinstance(msg, dict):
            continue
        content = str(msg.get("content", "")).strip()
        if not content:
            continue

        msg_role = msg.get("role", "user")
        role = "model" if msg_role == "assistant" else "user"

        gemini_history.append({
            "role": role,
            "parts": [{"text": content}]
        })

    gemini_history.append({
        "role": "user",
        "parts": [{"text": message}]
    })

    try:
        api_key = os.environ.get("GEMINI_API_KEY", "")

        response = req.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}",
            headers={"Content-Type": "application/json"},
            json={
                "systemInstruction": {
                    "parts": [{"text": system_prompt}]
                },
                "contents": gemini_history,
                "generationConfig": {
                    "maxOutputTokens": 700,
                    "temperature": 0.7
                }
            },
            timeout=20,
        )

        result_json = response.json()

        if not response.ok:
            error_message = result_json.get("error", {}).get("message", response.text)
            reply = f"API error: {error_message}"
        else:
            candidates = result_json.get("candidates", [])
            if not candidates:
                reply = "Sorry, I couldn't generate a response."
            else:
                parts = candidates[0].get("content", {}).get("parts", [])
                text_parts = [p.get("text", "") for p in parts if "text" in p]
                reply = "".join(text_parts).strip()
                reply = reply.replace("**", "")
                reply = reply or "Sorry, I couldn't generate a response."

    except Exception as e:
        reply = f"Sorry, something went wrong: {str(e)}"

    if current_user.is_authenticated:
        conn = get_db()
        conn.execute(
            "INSERT INTO chat_history (user_id, user_message, bot_reply) VALUES (?, ?, ?)",
            (current_user.id, message, reply),
        )
        conn.commit()
        conn.close()

    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(debug=True)