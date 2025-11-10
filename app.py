from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        city_input = request.form['city']
        #capitalizes city input
        city_name = city_input.title()
        city = {
            "name": city_name,
            "weather": "Sunny, 75°F",
            "cost_of_living": "$2000/month avg",
            "crime_rate": "Low",
            "future_score": 85
        }
        return render_template('result.html', city=city)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
