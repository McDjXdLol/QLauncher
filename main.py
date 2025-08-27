from flask import Flask, jsonify, render_template, Response
import json
import configparser
import subprocess
import requests
import os
import datetime

# Create the Flask application instance.
app = Flask(__name__)

# This configuration setting ensures that JSON responses will use Unicode characters,
# which is important for languages with special characters like Polish.
app.config['JSON_AS_ASCII'] = False

# Global variables to store the filenames for YouTube and weather data.
JSON_FILE_YOUTUBE = None
JSON_FILE_WEATHER = None

# A dictionary to hold all the settings loaded from the .ini file.
config = {}

# The name of the configuration file.
INI_FILE = "config.ini"


def load_ini():
    """
    Loads configuration settings from the 'config.ini' file into the global `config` dictionary.

    This function reads sections like 'AppSettings', 'Apps', 'Links', and 'Socials'.
    It also sets the global JSON file paths for YouTube and weather data based on the config.
    """
    global config
    parser = configparser.ConfigParser()

    # This line preserves the case of option names in the .ini file.
    parser.optionxform = str
    parser.read(INI_FILE, encoding="utf-8")

    # Load each section into the main config dictionary, using an empty dict if the section is not found.
    config['Settings'] = dict(
        parser['AppSettings']) if 'AppSettings' in parser else {}
    config['Apps'] = dict(parser['Apps']) if 'Apps' in parser else {}
    config['Links'] = dict(parser['Links']) if 'Links' in parser else {}
    config['Socials'] = dict(parser['Socials']) if 'Socials' in parser else {}

    # Set the global JSON file paths from the 'Settings' section.
    global JSON_FILE_YOUTUBE, JSON_FILE_WEATHER
    JSON_FILE_YOUTUBE = config['Settings'].get(
        'YoutubeJSON', 'youtube_data.json')
    JSON_FILE_WEATHER = config['Settings'].get(
        'WeatherJSON', 'weather_data.json')


@app.route("/")
def home():
    """
    Route for the main home page.

    It retrieves the home page template name from the configuration and renders it.
    """
    template_file = config['Settings'].get('HomePage', 'index.html')
    return render_template(template_file)


# A placeholder list for "anime" data, used when a real API is not available.
anime_placeholder = [
    {
        "img": "https://placehold.co/150x220?text=Anim+Test",
        "status": "Episode 7",
        "title": "Test API",
        "url": "about:blank"
    }
]


def load_youtube_from_file():
    try:
        with open(JSON_FILE_YOUTUBE, 'r', encoding='utf-8') as f:
            youtube_dict = json.load(f)
        return youtube_dict
    except FileNotFoundError:
        return {}


def file_create(filename):
    """
    Checks if a file needs to be updated based on a configurable time interval.

    Args:
        filename (str): The path to the file to check.

    Returns:
        bool: True if the file is older than the renewal interval, False otherwise.
    """
    try:
        # Get the data renewal interval from the config.
        interval = int(config['Settings'].get('DataRenewalInterval', 6))
    except (ValueError, TypeError):
        # Default to 6 minutes if the value is invalid.
        interval = 6

    # Get the file's last modification time.
    create_ts = os.path.getmtime(filename)
    create_date = datetime.datetime.fromtimestamp(create_ts)
    now = datetime.datetime.now()

    # Compare the file age with the interval.
    if now - create_date > datetime.timedelta(minutes=interval):
        return True
    else:
        return False


def save_weather_to_file(data):
    """
    Saves a dictionary of weather data to the JSON file.

    Args:
        data (dict): The weather data to save.
    """
    with open(JSON_FILE_WEATHER, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)


def should_update_weather_file():
    """
    Determines if the weather data file should be updated.

    Returns:
        bool: True if the file doesn't exist or is older than the interval, False otherwise.
    """
    if not os.path.exists(JSON_FILE_WEATHER):
        return True
    return file_create(JSON_FILE_WEATHER)


def fetch_weather_from_api():
    """
    Fetches weather data from the OpenWeatherMap API.

    It uses the API key, latitude, and longitude from the config file.

    Returns:
        dict: The weather data as a dictionary or an error message.
    """
    api_key = config['Settings'].get('WeatherAPIKey', '')
    if not api_key:
        return {"error": "No API key provided"}

    lat = config['Settings'].get('Latitude', '0')
    lon = config['Settings'].get('Longitude', '0')

    # Construct the API URL with the config values.
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"

    try:
        # Make the GET request.
        response = requests.get(url)

        # Check if the request was successful.
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API request failed with status code {response.status_code}"}
    except requests.RequestException as e:
        # Catch any request-related errors.
        return {"error": str(e)}


def update_weather_file(data):
    """
    Deletes the old weather file and saves the new data to it.

    Args:
        data (dict): The new weather data.
    """
    # Remove the existing file to prevent issues.
    if os.path.exists(JSON_FILE_WEATHER):
        os.remove(JSON_FILE_WEATHER)

    # Save the new data.
    save_weather_to_file(data)
    print("Weather data downloaded!")


def get_weather_data_from_api():
    """
    A high-level function that gets weather data, either from the local file or the API.

    It first checks if the local file is fresh. If not, it fetches from the API and updates the file.

    Returns:
        dict: The weather data.
    """
    print("Getting weather data...")
    if should_update_weather_file():
        # If the file needs to be updated, fetch from the API.
        data = fetch_weather_from_api()
        if "error" not in data:
            update_weather_file(data)
        return data
    else:
        # If the file is fresh, load from the file and print how old it is.
        ts = os.path.getmtime(JSON_FILE_WEATHER)
        age_minutes = (datetime.datetime.now() -
                       datetime.datetime.fromtimestamp(ts)).total_seconds() / 60
        print(
            f"Weather file is up-to-date, last update {age_minutes:.1f} min ago")
        with open(JSON_FILE_WEATHER, "r", encoding="utf-8") as f:
            return json.load(f)


@app.route("/api/weather")
def get_weather():
    """
    API endpoint to get weather data.

    Returns:
        Response: A JSON response with weather data.
    """
    data = get_weather_data_from_api()

    # Serialize the data to a JSON string and set the correct mimetype.
    return Response(json.dumps(data, ensure_ascii=False), mimetype='application/json')


@app.route("/api/socials")
def get_socials():
    """
    API endpoint to get social media links from the config.
    """
    return jsonify(config.get('Socials', {})), 200


@app.route("/api/anime")
def get_anime():
    """
    API endpoint to get placeholder anime data.
    """
    # It will be later replaced with actual data loading like YouTube data.
    return jsonify(anime_placeholder), 200


@app.route("/api/youtube")
def get_youtube():
    """
    API endpoint to get YouTube data from the local JSON file.
    """
    youtube_data = load_youtube_from_file()
    # Format the data into a list of dictionaries.
    youtube_list = [dict(url=url, **data)
                    for url, data in youtube_data.items()]
    return jsonify(youtube_list), 200


@app.route("/api/settings")
def api_settings():
    """
    API endpoint to get application settings from the config.
    """
    return jsonify(config.get('Settings', {})), 200


@app.route("/api/apps")
def api_apps():
    """
    API endpoint to get application paths from the config.
    """
    return jsonify(config.get('Apps', {})), 200


@app.route("/api/links")
def api_links():
    """
    API endpoint to get general links from the config.
    """
    return jsonify(config.get('Links', {})), 200


@app.route("/run/<app_name>", methods=["POST"])
def run_app(app_name):
    """
    API endpoint to run a local application.

    This endpoint is designed to be called with a POST request.
    It looks up the app's path in the config and executes it.
    """
    apps = config.get('Apps', {})
    if app_name in apps:
        path = apps[app_name]
        try:
            # Use subprocess to run the app. `shell=True` is a security risk,
            # but is used here for simplicity.
            subprocess.Popen(path, shell=True)
            return jsonify({"status": "ok"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "App not found"}), 404


@app.route("/reload_settings", methods=["POST"])
def reload_settings():
    """
    API endpoint to reload the settings from the .ini file.

    This is useful for applying changes without restarting the server.
    """
    load_ini()
    return jsonify({"status": "reloaded"}), 200


if __name__ == "__main__":
    # This block runs only when the script is executed directly.
    # It's the starting point of the application.

    # Load the configuration at startup.
    load_ini()

    # Get the host IP and port from the config file, with default values.
    work_on_ip = config['Settings'].get("IP", '0.0.0.0')
    work_on_port = config['Settings'].get("Port", 5000)

    try:
        # Try to convert the port to an integer.
        work_on_port = int(work_on_port)
    except (ValueError, TypeError):
        # Fallback to the default port if conversion fails.
        work_on_port = 5000

    # Start the Flask development server.
    # `debug=False` is used for production; it should be `True` for development.
    app.run(debug=False, host=work_on_ip, port=work_on_port)
