# YouTube Data Fetcher

A Python application that allows users to fetch video data from a YouTube channel using the YouTube Data API v3. The app provides a user interface to input a YouTube channel link and displays a preview of the fetched data, including video titles, publication dates, view counts, and clickable links. The data can be exported to an Excel file.

## Features

- Fetch videos from any YouTube channel by URL or channel ID
- Choose between latest or most popular videos
- Select number of videos to fetch (10, 50, 100, 200)
- Preview data in the app
- Export to Excel with clickable links
- Easy-to-use interface

## Setup

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. **Important**: Set your YouTube Data API key as an environment variable:
   ```
   export YOUTUBE_API_KEY=your_api_key_here
   ```
   **Never hardcode your API key directly in the source code!**

4. Run the app:
   ```
   streamlit run app.py
   ```

## How to get a YouTube API Key

1. Go to the [Google Developers Console](https://console.developers.google.com/)
2. Create a new project
3. Enable the YouTube Data API v3
4. Create credentials (API Key)
5. Use the API key as an environment variable

## Usage

1. Enter a YouTube channel URL (e.g., https://www.youtube.com/@channelname)
2. Choose sorting option (latest videos or most popular)
3. Select the number of videos to fetch
4. Click "Fetch Videos" and wait for the data to load
5. Preview the data and download the Excel file

## Dependencies

- streamlit
- pandas
- google-api-python-client
- openpyxl

## Features of the Exported Data

- Video Title
- Video URL
- Publication Date
- View Count
- Like Count
- Comment Count
- Duration
- Description
- Thumbnail URL

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is not affiliated with YouTube or Google. It uses the official YouTube Data API to fetch publicly available data. 