from flask import Flask, render_template, request
from data import get_city_data

app = Flask(__name__)

# ---- simple mock for "neighborhood" lookups ----
# you can later swap this to call real APIs
def get_neighborhood_data(name: str):
    name = name.title().strip()
    # demo placeholder values – change to real data later
    demo = {
        "name": name,
        # SAFETY
        "crime_rate": "Low",            # text for display
        "crime_score": 4.0,             # 0-5 numeric score
        # AFFORDABILITY
        "cost_of_living": "$2000/mo avg",
        "tax_rate": "1.8% est.",
        "affordability_score": 3.2,
        # ENVIRONMENT
        "pollution": "Moderate",
        "weather": "Sunny · 75°F avg",
        "disaster_risk": "Low",
        "environment_score": 3.8,
        # LIFESTYLE
        "noise": "Quiet",
        "walk_bike": "Walk 4.2 / Bike 3.8",
        "lifestyle_score": 4.0,
        # SERVICES
        "medical_access": "Hosp/UC within 10 min",
        "services_score": 4.4,
        # COMMUNITY & DEMOGRAPHICS
        "diversity": "High",
        "age_distribution": "Median: 34",
        "income": "$86,000 median",
        "community_score": 3.9,
        # overall (you can compute weighted, here it’s a simple average)
        "overall_score": round((4.0 + 3.2 + 3.8 + 4.0 + 4.4 + 3.9) / 6, 2)
    }
    return demo

@app.route('/', methods=['GET', 'POST'])
def index():
    # main landing page with hero + search + comparison CTA
    if request.method == 'POST':
        city_input = request.form.get('city', '').strip()
        if not city_input:
            return render_template('index.html', error="Please enter a city.")
        city = get_city_data(city_input.title())
        # ensure all fields exist for the template
        city.setdefault("walkability", "—")   # placeholder if not provided
        city.setdefault("pollution", "—")
        city.setdefault("tax_rate", "—")
        city.setdefault("income", "—")
        city.setdefault("noise", "—")
        city.setdefault("medical_access", "—")
        city.setdefault("diversity", "—")
        city.setdefault("age_distribution", "—")
        city.setdefault("overall_score", 4.0)
        return render_template('result.html', city=city)
    return render_template('index.html')

@app.route('/compare', methods=['GET', 'POST'])
def compare():
    left = None
    right = None
    if request.method == 'POST':
        n1 = request.form.get('n1', '').strip()
        n2 = request.form.get('n2', '').strip()
        if n1:
            left = get_neighborhood_data(n1)
        if n2:
            right = get_neighborhood_data(n2)
    return render_template('compare.html', left=left, right=right)

if __name__ == '__main__':
    app.run(debug=True)
