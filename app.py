# app.py
from flask import Flask, render_template, request, jsonify
import datetime
import pytz

app = Flask(__name__)

# Function to calculate the rate (minutes per slide)
def calculate_rate(slides, minutes_passed):
    if slides == 0:
        return 0
    return minutes_passed / slides

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    presentation_data = request.json.get('presentation_data', {})
    all_presentations_data = {} # This would ideally persist across requests in a real app

    # For this simple example, we'll just process the data sent in the request
    # In a real application, you'd load existing data here

    total_slides_completed = 0
    total_minutes_passed = 0
    individual_rates = {}

    est_timezone = pytz.timezone('US/Eastern')

    for name, data in presentation_data.items():
        slides = int(data.get('slides', 0))
        start_time_str = data.get('start_time')
        end_time_str = data.get('end_time')

        minutes_passed = 0
        if start_time_str and end_time_str:
            try:
                # Get today's date in EST
                today_est = datetime.datetime.now(est_timezone).date()
                start_datetime_est = est_timezone.localize(datetime.datetime.combine(today_est, datetime.datetime.strptime(start_time_str, "%H:%M").time()))
                end_datetime_est = est_timezone.localize(datetime.datetime.combine(today_est, datetime.datetime.strptime(end_time_str, "%H:%M").time()))
                time_difference = end_datetime_est - start_datetime_est
                minutes_passed = time_difference.total_seconds() / 60
            except ValueError:
                return jsonify({"error": "Invalid time format. Please use HH:MM."}), 400

        if slides > 0 and minutes_passed > 0:
            rate = calculate_rate(slides, minutes_passed)
            individual_rates[name] = f"{rate:.3f} minutes per slide"
            total_slides_completed += slides
            total_minutes_passed += minutes_passed

    average_rate = total_minutes_passed / total_slides_completed if total_slides_completed > 0 else 0

    # Assuming total_slides is 196 as in your notebook example
    total_slides = 196
    remaining_slides = total_slides - total_slides_completed

    predicted_time_minutes = remaining_slides * average_rate if average_rate > 0 else 0
    predicted_time_hours = predicted_time_minutes / 60

    # Get current time and convert to EST
    current_time_utc = datetime.datetime.now(datetime.timezone.utc)
    current_time_est = current_time_utc.astimezone(est_timezone)
    estimated_end_time_est = current_time_est + datetime.timedelta(minutes=predicted_time_minutes)


    results = {
        "individual_rates": individual_rates,
        "average_rate": f"{average_rate:.3f} minutes per slide",
        "remaining_slides": remaining_slides,
        "predicted_time": f"{predicted_time_minutes:.2f} minutes ({predicted_time_hours:.2f} hours)",
        "estimated_end_time": estimated_end_time_est.strftime('%Y-%m-%d %H:%M:%S %Z%z')
    }

    return jsonify(results)

if __name__ == '__main__':
    # In a production environment, you would use a production-ready web server
    # For local development, run with debug=True
    app.run(debug=True)
