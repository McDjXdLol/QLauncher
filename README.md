# QLauncher

QLauncher is a simple, customizable home page for your browser. It provides quick access to your favorite applications, links, and social media, along with real-time weather information and the latest YouTube videos from a configured channel (WIP).

## Screenshots
| Dark Theme | Light Theme|
|------------|------------|
|<img width="1280" height="890" alt="Zrzut ekranu 2025-08-27 141951" src="https://github.com/user-attachments/assets/d32b58ec-2aa2-43b0-8e48-2ca05b8f04e8" />| <img width="1280" height="890" alt="Zrzut ekranu 2025-08-27 142100" src="https://github.com/user-attachments/assets/b449fec7-909c-479f-b0b4-e4defd50e2b9" />|

## Roadmap
- [x] Add **screenshots**.
- [ ] Add a **scraper** to download data from YouTube.
- [ ] Implement a **scraper** for various anime websites.
- [ ] Add support for **easily integrating new anime sites**.
- [ ] Possibly add an option to display the **latest videos** from individual YouTube channels.

## Features

*   **Customizable Links & Apps:** Easily add or remove your favorite applications and websites.
*   **Dynamic Weather Display:** Shows current weather conditions based on your location.
*   **(WIP) YouTube Integration:** Fetches and displays the latest videos from a specified YouTube channel.
*   **(WIP) Anime Website Integration:** Fetches and displays currently airing anime.
*   **Simple Configuration:** All settings are managed via a single config.ini file.    
*   **Dark/Light Theme Toggle:** Switch between themes for a comfortable viewing experience.
    

## Getting Started

### Prerequisites

*   `Python` >= 3.13.2
*   `Flask` >= 3.1.2
*   `Requests` >= 2.32.5
    

You can install all required Python packages using pip:

```bash
pip install -r requirements.txt
```

### Configuration

Before running the application, you **MUST** configure the config.ini file.

1.  **Open config.ini** in a text editor.

2.  In the **`[AppSettings]`** section, locate the following keys:
    * **`WeatherAPIKey`**: You need to get a **free API key from OpenWeatherMap**. You can find it [HERE](https://openweathermap.org/).
    * **`Latitude`**: Your geographical latitude.
    * **`Longitude`**: Your geographical longitude.
    * **Others**: Not required, but you can change them to match your preferences.

3.  **Fill in the values** for these keys. Without them, the weather data will not be fetched correctly.

### Running the Application

1.  Make sure you have configured config.ini as described above.    
2.  Run the main Python script:
```bash
python main.py
```
3.  Open your browser and go to http://localhost:5000 (or the IP address and port you've set in config.ini).
    

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
