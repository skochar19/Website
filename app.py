from flask import Flask, render_template, request
import json

app = Flask(__name__)

# ---------------------------------------------------
# Load Maryland counties from JSON (list of names)
# ---------------------------------------------------
with open("maryland_counties.json", "r") as f:
    counties_data = json.load(f)
    MARYLAND_COUNTIES = counties_data["counties"]

# ---------------------------------------------------
# Base county database (temps, cost, crime, schools, overall diversity)
# NOTE: Values are reasonable placeholders for a project,
# not official stats. Cost is in USD per month.
# ---------------------------------------------------
COUNTY_DATABASE = {
    "Allegany County": {
        "name": "Allegany County",
        "summerTemp": 83,
        "winterTemp": 28,
        "averageCostOfLiving": 1550,
        "crimeSafety": "Medium",
        "schoolQuality": "Medium",
        "diversityPercent": 14
    },
    "Anne Arundel County": {
        "name": "Anne Arundel County",
        "summerTemp": 87,
        "winterTemp": 32,
        "averageCostOfLiving": 2400,
        "crimeSafety": "Medium",
        "schoolQuality": "High",
        "diversityPercent": 32
    },
    "Baltimore County": {
        "name": "Baltimore County",
        "summerTemp": 86,
        "winterTemp": 31,
        "averageCostOfLiving": 2100,
        "crimeSafety": "High",
        "schoolQuality": "Medium",
        "diversityPercent": 43
    },
    "Calvert County": {
        "name": "Calvert County",
        "summerTemp": 87,
        "winterTemp": 34,
        "averageCostOfLiving": 2350,
        "crimeSafety": "Low",
        "schoolQuality": "High",
        "diversityPercent": 22
    },
    "Caroline County": {
        "name": "Caroline County",
        "summerTemp": 88,
        "winterTemp": 33,
        "averageCostOfLiving": 1700,
        "crimeSafety": "Medium",
        "schoolQuality": "Low",
        "diversityPercent": 25
    },
    "Carroll County": {
        "name": "Carroll County",
        "summerTemp": 85,
        "winterTemp": 29,
        "averageCostOfLiving": 2300,
        "crimeSafety": "Low",
        "schoolQuality": "High",
        "diversityPercent": 11
    },
    "Cecil County": {
        "name": "Cecil County",
        "summerTemp": 86,
        "winterTemp": 30,
        "averageCostOfLiving": 1850,
        "crimeSafety": "Medium",
        "schoolQuality": "Medium",
        "diversityPercent": 15
    },
    "Charles County": {
        "name": "Charles County",
        "summerTemp": 88,
        "winterTemp": 34,
        "averageCostOfLiving": 2400,
        "crimeSafety": "Low",
        "schoolQuality": "Medium",
        "diversityPercent": 60
    },
    "Dorchester County": {
        "name": "Dorchester County",
        "summerTemp": 88,
        "winterTemp": 33,
        "averageCostOfLiving": 1650,
        "crimeSafety": "High",
        "schoolQuality": "Low",
        "diversityPercent": 37
    },
    "Frederick County": {
        "name": "Frederick County",
        "summerTemp": 85,
        "winterTemp": 30,
        "averageCostOfLiving": 2600,
        "crimeSafety": "Low",
        "schoolQuality": "High",
        "diversityPercent": 26
    },
    "Garrett County": {
        "name": "Garrett County",
        "summerTemp": 78,
        "winterTemp": 22,
        "averageCostOfLiving": 1500,
        "crimeSafety": "Low",
        "schoolQuality": "Medium",
        "diversityPercent": 4
    },
    "Harford County": {
        "name": "Harford County",
        "summerTemp": 85,
        "winterTemp": 30,
        "averageCostOfLiving": 2000,
        "crimeSafety": "Low",
        "schoolQuality": "Medium",
        "diversityPercent": 24
    },
    "Howard County": {
        "name": "Howard County",
        "summerTemp": 86,
        "winterTemp": 31,
        "averageCostOfLiving": 3300,
        "crimeSafety": "Low",
        "schoolQuality": "High",
        "diversityPercent": 48
    },
    "Kent County": {
        "name": "Kent County",
        "summerTemp": 87,
        "winterTemp": 32,
        "averageCostOfLiving": 1900,
        "crimeSafety": "Low",
        "schoolQuality": "Medium",
        "diversityPercent": 22
    },
    "Montgomery County": {
        "name": "Montgomery County",
        "summerTemp": 86,
        "winterTemp": 30,
        "averageCostOfLiving": 3500,
        "crimeSafety": "Low",
        "schoolQuality": "High",
        "diversityPercent": 60
    },
    "Prince George's County": {
        "name": "Prince George's County",
        "summerTemp": 88,
        "winterTemp": 33,
        "averageCostOfLiving": 2400,
        "crimeSafety": "Medium",
        "schoolQuality": "Medium",
        "diversityPercent": 75
    },
    "Queen Anne's County": {
        "name": "Queen Anne's County",
        "summerTemp": 87,
        "winterTemp": 33,
        "averageCostOfLiving": 2500,
        "crimeSafety": "Low",
        "schoolQuality": "High",
        "diversityPercent": 14
    },
    "Saint Mary's County": {
        "name": "Saint Mary's County",
        "summerTemp": 87,
        "winterTemp": 34,
        "averageCostOfLiving": 2100,
        "crimeSafety": "Low",
        "schoolQuality": "Medium",
        "diversityPercent": 26
    },
    "Somerset County": {
        "name": "Somerset County",
        "summerTemp": 88,
        "winterTemp": 33,
        "averageCostOfLiving": 1600,
        "crimeSafety": "Medium",
        "schoolQuality": "Low",
        "diversityPercent": 49
    },
    "Talbot County": {
        "name": "Talbot County",
        "summerTemp": 87,
        "winterTemp": 33,
        "averageCostOfLiving": 2400,
        "crimeSafety": "Low",
        "schoolQuality": "Medium",
        "diversityPercent": 22
    },
    "Washington County": {
        "name": "Washington County",
        "summerTemp": 85,
        "winterTemp": 29,
        "averageCostOfLiving": 1850,
        "crimeSafety": "Medium",
        "schoolQuality": "Medium",
        "diversityPercent": 21
    },
    "Wicomico County": {
        "name": "Wicomico County",
        "summerTemp": 88,
        "winterTemp": 32,
        "averageCostOfLiving": 1700,
        "crimeSafety": "High",
        "schoolQuality": "Low",
        "diversityPercent": 37
    },
    "Worcester County": {
        "name": "Worcester County",
        "summerTemp": 88,
        "winterTemp": 33,
        "averageCostOfLiving": 2500,
        "crimeSafety": "High",
        "schoolQuality": "Medium",
        "diversityPercent": 20
    },
    "Baltimore City": {
        "name": "Baltimore City",
        "summerTemp": 87,
        "winterTemp": 32,
        "averageCostOfLiving": 1900,
        "crimeSafety": "High",
        "schoolQuality": "Low",
        "diversityPercent": 73
    }
}

# ---------------------------------------------------
# Race breakdown (from MD racial composition table)
# ---------------------------------------------------
RACE_BREAKDOWN = {
    "Allegany County": {
        "white": 87.3,
        "black": 8.0,
        "hispanic": 1.7,
        "asian": 1.0,
        "american_indian": 0.2,
        "native_hawaiian": 0.0,
        "multiracial": 1.7
    },
    "Anne Arundel County": {
        "white": 69.5,
        "black": 16.3,
        "hispanic": 7.3,
        "asian": 3.9,
        "american_indian": 0.3,
        "native_hawaiian": 0.1,
        "multiracial": 2.6
    },
    "Baltimore City": {
        "white": 28.3,
        "black": 62.1,
        "hispanic": 4.8,
        "asian": 2.7,
        "american_indian": 0.3,
        "native_hawaiian": 0.0,
        "multiracial": 1.8
    },
    "Baltimore County": {
        "white": 58.8,
        "black": 27.5,
        "hispanic": 5.2,
        "asian": 6.0,
        "american_indian": 0.3,
        "native_hawaiian": 0.0,
        "multiracial": 2.1
    },
    "Calvert County": {
        "white": 78.8,
        "black": 12.9,
        "hispanic": 3.7,
        "asian": 1.6,
        "american_indian": 0.3,
        "native_hawaiian": 0.1,
        "multiracial": 2.6
    },
    "Caroline County": {
        "white": 76.5,
        "black": 14.0,
        "hispanic": 6.6,
        "asian": 0.8,
        "american_indian": 0.3,
        "native_hawaiian": 0.0,
        "multiracial": 1.7
    },
    "Carroll County": {
        "white": 89.9,
        "black": 3.5,
        "hispanic": 3.2,
        "asian": 1.8,
        "american_indian": 0.2,
        "native_hawaiian": 0.0,
        "multiracial": 1.5
    },
    "Cecil County": {
        "white": 85.5,
        "black": 6.7,
        "hispanic": 4.2,
        "asian": 1.2,
        "american_indian": 0.3,
        "native_hawaiian": 0.1,
        "multiracial": 2.0
    },
    "Charles County": {
        "white": 43.2,
        "black": 43.9,
        "hispanic": 5.5,
        "asian": 3.3,
        "american_indian": 0.6,
        "native_hawaiian": 0.1,
        "multiracial": 3.4
    },
    "Dorchester County": {
        "white": 64.0,
        "black": 27.7,
        "hispanic": 4.9,
        "asian": 1.2,
        "american_indian": 0.3,
        "native_hawaiian": 0.0,
        "multiracial": 1.8
    },
    "Frederick County": {
        "white": 75.0,
        "black": 9.0,
        "hispanic": 8.7,
        "asian": 4.5,
        "american_indian": 0.2,
        "native_hawaiian": 0.1,
        "multiracial": 2.5
    },
    "Garrett County": {
        "white": 96.4,
        "black": 1.1,
        "hispanic": 1.1,
        "asian": 0.5,
        "american_indian": 0.1,
        "native_hawaiian": 0.0,
        "multiracial": 0.8
    },
    "Harford County": {
        "white": 77.0,
        "black": 13.1,
        "hispanic": 4.3,
        "asian": 3.1,
        "american_indian": 0.2,
        "native_hawaiian": 0.1,
        "multiracial": 2.3
    },
    "Howard County": {
        "white": 54.2,
        "black": 18.3,
        "hispanic": 6.5,
        "asian": 17.5,
        "american_indian": 0.2,
        "native_hawaiian": 0.1,
        "multiracial": 3.2
    },
    "Kent County": {
        "white": 78.2,
        "black": 14.8,
        "hispanic": 4.3,
        "asian": 1.0,
        "american_indian": 0.1,
        "native_hawaiian": 0.0,
        "multiracial": 1.5
    },
    "Montgomery County": {
        "white": 45.2,
        "black": 17.8,
        "hispanic": 19.0,
        "asian": 15.2,
        "american_indian": 0.2,
        "native_hawaiian": 0.0,
        "multiracial": 2.6
    },
    "Prince George's County": {
        "white": 13.9,
        "black": 62.1,
        "hispanic": 17.2,
        "asian": 4.5,
        "american_indian": 0.2,
        "native_hawaiian": 0.0,
        "multiracial": 2.0
    },
    "Queen Anne's County": {
        "white": 86.5,
        "black": 6.8,
        "hispanic": 3.6,
        "asian": 1.1,
        "american_indian": 0.3,
        "native_hawaiian": 0.0,
        "multiracial": 1.8
    },
    "Saint Mary's County": {
        "white": 74.9,
        "black": 14.1,
        "hispanic": 4.9,
        "asian": 2.8,
        "american_indian": 0.3,
        "native_hawaiian": 0.1,
        "multiracial": 2.9
    },
    "Somerset County": {
        "white": 51.5,
        "black": 41.7,
        "hispanic": 3.5,
        "asian": 0.9,
        "american_indian": 0.4,
        "native_hawaiian": 0.0,
        "multiracial": 2.0
    },
    "Talbot County": {
        "white": 78.2,
        "black": 12.7,
        "hispanic": 6.3,
        "asian": 1.3,
        "american_indian": 0.2,
        "native_hawaiian": 0.0,
        "multiracial": 1.4
    },
    "Washington County": {
        "white": 80.4,
        "black": 10.7,
        "hispanic": 4.5,
        "asian": 1.8,
        "american_indian": 0.2,
        "native_hawaiian": 0.1,
        "multiracial": 2.4
    },
    "Wicomico County": {
        "white": 64.1,
        "black": 25.0,
        "hispanic": 5.2,
        "asian": 3.2,
        "american_indian": 0.2,
        "native_hawaiian": 0.0,
        "multiracial": 2.3
    },
    "Worcester County": {
        "white": 79.9,
        "black": 13.4,
        "hispanic": 3.4,
        "asian": 1.4,
        "american_indian": 0.2,
        "native_hawaiian": 0.0,
        "multiracial": 1.6
    }
}

# Attach race breakdown to the main county database
for cname, race_data in RACE_BREAKDOWN.items():
    if cname in COUNTY_DATABASE:
        COUNTY_DATABASE[cname]["race"] = race_data

# ---------------------------------------------------
# Coordinates (approximate) for each county – county seat
# ---------------------------------------------------
COUNTY_COORDS = {
    "Allegany County":        {"lat": 39.65, "lng": -78.76},
    "Anne Arundel County":    {"lat": 38.98, "lng": -76.49},
    "Baltimore County":       {"lat": 39.40, "lng": -76.60},
    "Calvert County":         {"lat": 38.54, "lng": -76.59},
    "Caroline County":        {"lat": 38.88, "lng": -75.83},
    "Carroll County":         {"lat": 39.58, "lng": -76.99},
    "Cecil County":           {"lat": 39.61, "lng": -75.83},
    "Charles County":         {"lat": 38.53, "lng": -77.01},
    "Dorchester County":      {"lat": 38.57, "lng": -76.08},
    "Frederick County":       {"lat": 39.41, "lng": -77.41},
    "Garrett County":         {"lat": 39.41, "lng": -79.41},
    "Harford County":         {"lat": 39.54, "lng": -76.35},
    "Howard County":          {"lat": 39.27, "lng": -76.80},
    "Kent County":            {"lat": 39.21, "lng": -76.07},
    "Montgomery County":      {"lat": 39.08, "lng": -77.15},
    "Prince George's County": {"lat": 38.82, "lng": -76.75},
    "Queen Anne's County":    {"lat": 39.04, "lng": -76.07},
    "Saint Mary's County":    {"lat": 38.29, "lng": -76.64},
    "Somerset County":        {"lat": 38.20, "lng": -75.69},
    "Talbot County":          {"lat": 38.77, "lng": -76.08},
    "Washington County":      {"lat": 39.64, "lng": -77.72},
    "Wicomico County":        {"lat": 38.36, "lng": -75.60},
    "Worcester County":       {"lat": 38.18, "lng": -75.39},
    "Baltimore City":         {"lat": 39.29, "lng": -76.61},
}

# ---------------------------------------------------
# Scoring helper
# ---------------------------------------------------
def compute_overall_score(entry: dict) -> int:
    score = 70  # base

    if entry["schoolQuality"] == "High":
        score += 10
    elif entry["schoolQuality"] == "Low":
        score -= 10

    if entry["crimeSafety"] == "Low":
        score += 10
    elif entry["crimeSafety"] == "High":
        score -= 10

    diversity = entry["diversityPercent"]
    score += max(0, 10 - abs(50 - diversity) // 5)

    cost = entry["averageCostOfLiving"]
    if cost <= 1900:
        score += 5
    elif cost >= 3000:
        score -= 5

    score = max(0, min(100, score))
    return score


def get_county_overview(county_name: str) -> dict:
    base = COUNTY_DATABASE.get(county_name)
    if base is None:
        base = {
            "name": county_name,
            "summerTemp": 85,
            "winterTemp": 30,
            "averageCostOfLiving": 2200,
            "crimeSafety": "Medium",
            "schoolQuality": "Medium",
            "diversityPercent": 50,
        }

    overall_score = compute_overall_score(base)
    result = base.copy()
    result["overall_score"] = overall_score

    coords = COUNTY_COORDS.get(county_name, {"lat": 39.0458, "lng": -76.6413})
    result["lat"] = coords["lat"]
    result["lng"] = coords["lng"]

    return result


# ---------------------------------------------------
# Routes
# ---------------------------------------------------
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", counties=MARYLAND_COUNTIES)


@app.route("/result", methods=["POST"])
def result():
    selected_county = request.form.get("county")

    if not selected_county:
        return render_template(
            "index.html",
            counties=MARYLAND_COUNTIES,
            error="Please select a county."
        )

    overview = get_county_overview(selected_county)
    return render_template("result.html", county=overview)


@app.route("/compare", methods=["GET", "POST"])
@app.route("/compare", methods=["GET", "POST"])
def compare():
    county1 = None
    county2 = None
    county1_name = None
    county2_name = None

    if request.method == "POST":
        county1_name = request.form.get("county1")
        county2_name = request.form.get("county2")

        if county1_name:
            county1 = get_county_overview(county1_name)
        if county2_name:
            county2 = get_county_overview(county2_name)

    return render_template(
        "compare.html",
        counties=MARYLAND_COUNTIES,
        county1=county1,
        county2=county2,
        county1_name=county1_name,
        county2_name=county2_name,
    )



if __name__ == "__main__":
    app.run(debug=True)
