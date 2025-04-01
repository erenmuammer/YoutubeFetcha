# YouTube Video Data Fetcher

A Python application to fetch and export video data from YouTube channels. This tool uses the YouTube Data API v3 to retrieve video information such as titles, publication dates, and view counts, then presents it in a clean interface with options to download the data as an Excel file.

## Features

- **Easy Channel Selection**: Enter any YouTube channel URL or handle
- **Flexible Video Sorting**: Choose between latest videos or most popular videos
- **Customizable Results**: Select how many videos to retrieve (10, 50, 100, or 200)
- **Clickable Links**: Video links are clickable both in the UI and in the exported Excel file
- **Simple Data Export**: Download the results as a formatted Excel file

## Requirements

- Python 3.6+
- YouTube Data API v3 Key
- Required Python packages (see `requirements.txt`)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/ytdatafetch.git
   cd ytdatafetch
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up your YouTube API key:
   - Create a `.env` file in the root directory
   - Add your YouTube API key: `YOUTUBE_API_KEY=your_api_key_here`

## Usage

1. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

2. Enter a YouTube channel URL (in any of these formats):
   - `https://www.youtube.com/@channelname`
   - `https://www.youtube.com/channel/CHANNEL_ID`
   - `@channelname`

3. Select your preferences:
   - Choose between "Latest Videos" or "Most Popular Videos"
   - Select the number of videos to fetch (10, 50, 100, or 200)

4. Click "Fetch Videos" to retrieve the data

5. Download the results using the "Download Excel File" button

## API Key Information

To use this application, you need a YouTube Data API v3 key:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select an existing one)
3. Navigate to "APIs & Services" > "Library"
4. Search for "YouTube Data API v3" and enable it
5. Go to "APIs & Services" > "Credentials"
6. Create an API key and copy it
7. Paste the key in your `.env` file

## Security Notes

- Never commit your `.env` file to version control
- The `.gitignore` file is configured to exclude the `.env` file
- For production deployment, use environment variables on your hosting platform

## Example Output

The application provides a preview of the data and allows you to download it as an Excel file with the following columns:

- Title
- Published Date
- View Count
- Video URL (clickable)

## Limitations

- The YouTube Data API has quota limits (10,000 units per day)
- Each request for video details consumes quota units
- Be mindful of the number of videos you fetch to avoid exceeding your quota

## License

This project is licensed under the MIT License - see the LICENSE file for details. 