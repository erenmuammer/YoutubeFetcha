# YoutubeFetcha

A Streamlit web application that allows you to export video data as .xlsx file from YouTube channels. You can fetch either the latest 200 videos or the top 200 most popular videos from any YouTube channel.

## Features

- Export video data from any YouTube channel
- Choose between latest 200 videos or top 200 most popular videos
- Export data to Excel format
- Modern and user-friendly interface
- Detailed video statistics including views, likes, comments, and more

## Prerequisites

- Python 3.7 or higher
- YouTube Data API v3 key

## Getting a YouTube API Key

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the YouTube Data API v3 for your project
4. Go to the Credentials page
5. Click "Create Credentials" and select "API Key"
6. Copy your API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/YoutubeFetcha.git
cd YoutubeFetcha
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root and add your YouTube API key:
```
YOUTUBE_API_KEY=your_api_key_here
```

## Usage

1. Run the Streamlit app:
```bash
streamlit run app.py
```

2. Open your web browser and navigate to the URL shown in the terminal (typically http://localhost:8501)

3. Enter a YouTube channel URL (e.g., https://www.youtube.com/@google)

4. Choose whether you want to fetch the latest 200 videos or the top 200 most popular videos

5. Click "Fetch Videos" and wait for the data to be processed

6. Download the Excel file containing the video data

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
