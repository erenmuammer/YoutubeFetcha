import os
import re
import requests
from datetime import datetime
import pandas as pd
from urllib.parse import urlparse, parse_qs
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
API_KEY = os.environ.get("YOUTUBE_API_KEY")
if not API_KEY:
    print("UYARI: YOUTUBE_API_KEY çevre değişkeni bulunamadı. API çağrıları çalışmayacak.")
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"

def get_youtube_service():
    """Builds and returns the YouTube API service object."""
    try:
        service = build(API_SERVICE_NAME, API_VERSION, developerKey=API_KEY)
        return service
    except Exception as e:
        print(f"Error building YouTube service: {e}")
        return None

def extract_channel_identifier(url):
    """Extracts channel ID, username, handle or custom URL from various YouTube channel URL formats."""
    # Standard channel ID pattern: /channel/UC...
    match = re.search(r'/channel/([A-Za-z0-9_-]+)', url)
    if match:
        return {'channelId': match.group(1)}

    # Username pattern: /user/username
    match = re.search(r'/user/([A-Za-z0-9_-]+)', url)
    if match:
        return {'forUsername': match.group(1)}

    # Custom URL pattern: /c/customURL
    match = re.search(r'/c/([A-Za-z0-9_-]+)', url)
    if match:
        # Custom URLs often map to handles now, but API might still work with them.
        # It's often better to search by this name to find the channel ID.
        # For simplicity here, we might need a search step later if this fails.
        # Let's treat it like a handle for now.
        return {'handle': '@' + match.group(1)} # Handles start with @

    # Handle pattern: /@handle
    match = re.search(r'/@([A-Za-z0-9_.-]+)', url)
    if match:
         # Ensure the handle includes the "@" symbol for the API call
        return {'forHandle': '@' + match.group(1)}

    # Last resort: Check if the entire path segment looks like a channel ID
    # (e.g., youtube.com/UC...)
    match = re.search(r'youtube\\.com/([A-Za-z0-9_-]+)', url)
    if match and match.group(1).startswith('UC') and len(match.group(1)) == 24:
         return {'channelId': match.group(1)}
    elif match:
         # Assume it might be a handle or legacy custom URL without /c/ or /@
         # Let's try searching by this identifier as a handle
         return {'forHandle': '@' + match.group(1)}


    return None # Identifier not found


def get_channel_details(youtube, identifier_dict):
    """Gets channel details, including the uploads playlist ID, using the identifier."""
    try:
        request = youtube.channels().list(
            part="contentDetails,snippet", # Added snippet to get title
            **identifier_dict # Pass {'channelId': id} or {'forUsername': name} or {'forHandle': handle}
        )
        response = request.execute()

        if response.get("items"):
            channel_info = response["items"][0]
            uploads_playlist_id = channel_info["contentDetails"]["relatedPlaylists"]["uploads"]
            channel_title = channel_info["snippet"]["title"]
            return uploads_playlist_id, channel_title
        else:
            # If direct lookup fails, try searching for the handle/name
            if 'forHandle' in identifier_dict:
                query = identifier_dict['forHandle']
            elif 'forUsername' in identifier_dict:
                query = identifier_dict['forUsername']
            else: # Should not happen if extraction worked, but as fallback
                print(f"Could not find channel directly with {identifier_dict}. Trying search.")
                # Attempt search if possible based on original failed identifier keys.
                # This part might need refinement based on which identifiers failed.
                return None, None # Fallback if search isn't implemented here

            print(f"Direct lookup failed for {identifier_dict}, trying search with query: '{query}'")
            search_request = youtube.search().list(
                part="snippet",
                q=query,
                type="channel",
                maxResults=1
            )
            search_response = search_request.execute()
            if search_response.get("items"):
                channel_id = search_response["items"][0]["snippet"]["channelId"]
                print(f"Found channel ID via search: {channel_id}")
                # Now get details using the found channel ID
                # Use 'id' key for channel ID lookups
                return get_channel_details(youtube, {'id': channel_id})
            else:
                print(f"Could not find channel via search for query: {query}")
                return None, None

    except HttpError as e:
        print(f"An HTTP error {e.resp.status} occurred: {e.content}")
        return None, None
    except Exception as e:
        print(f"An error occurred getting channel details: {e}")
        return None, None


def get_playlist_video_ids(youtube, playlist_id):
    """Fetches all video IDs from a given playlist ID, handling pagination."""
    video_ids = []
    next_page_token = None

    while True:
        try:
            request = youtube.playlistItems().list(
                part="contentDetails",
                playlistId=playlist_id,
                maxResults=50, # Max allowed by API
                pageToken=next_page_token
            )
            response = request.execute()

            for item in response.get("items", []):
                video_ids.append(item["contentDetails"]["videoId"])

            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break # Exit loop if no more pages
        except HttpError as e:
            print(f"An HTTP error {e.resp.status} occurred fetching playlist items: {e.content}")
            break
        except Exception as e:
            print(f"An error occurred fetching playlist items: {e}")
            break


    return video_ids


def get_video_details(youtube, video_ids):
    """Fetches details (title, publishedAt, viewCount, commentCount) for a list of video IDs."""
    video_details = []
    # Process video IDs in batches of 50 (API limit)
    for i in range(0, len(video_ids), 50):
        batch_ids = video_ids[i:i+50]
        try:
            request = youtube.videos().list(
                part="snippet,statistics", # statistics includes viewCount and commentCount
                id=",".join(batch_ids)
            )
            response = request.execute()

            for item in response.get("items", []):
                video_id = item["id"]
                title = item["snippet"]["title"]
                published_at = item["snippet"]["publishedAt"]
                # Format date/time nicely
                published_date = pd.to_datetime(published_at).strftime('%Y-%m-%d %H:%M:%S')
                stats = item.get("statistics", {})
                view_count = stats.get("viewCount", 0)
                comment_count = stats.get("commentCount", 0) # Get comment count, default to 0 if unavailable/disabled

                video_details.append({
                    "Title": title,
                    "Published At": published_date,
                    "View Count": int(view_count),
                    "Comment Count": int(comment_count), # Add comment count
                    "Link": f"https://www.youtube.com/watch?v={video_id}" # Add video link
                })
        except HttpError as e:
            print(f"An HTTP error {e.resp.status} occurred fetching video details: {e.content}")
            continue # Try next batch
        except Exception as e:
            print(f"An error occurred fetching video details: {e}")
            continue # Try next batch

    return video_details

def fetch_all_channel_videos(channel_url, sort_by='latest', max_videos=200):
    """Main function to fetch video details for a given channel URL, sorted either by latest or popularity.

    Args:
        channel_url (str): The URL of the YouTube channel.
        sort_by (str): Sorting criteria - 'latest' or 'popular'. Defaults to 'latest'.
        max_videos (int): Maximum number of videos to fetch

    Returns:
        tuple: A pandas DataFrame with video details and a status message, or (None, error_message).
    """
    if not API_KEY:
        print("API Key not found. Please set YOUTUBE_API_KEY in your .env file.")
        return None, "API Key not configured. Please contact the administrator."

    youtube = get_youtube_service()
    if not youtube:
        return None, "Failed to initialize YouTube service."

    identifier = extract_channel_identifier(channel_url)
    if not identifier:
        return None, f"Could not extract a valid channel identifier from URL: {channel_url}"

    if 'channelId' in identifier:
        details_param = {'id': identifier['channelId']}
    elif 'forUsername' in identifier:
         details_param = {'forUsername': identifier['forUsername']}
    elif 'forHandle' in identifier:
         handle = identifier['forHandle']
         if not handle.startswith('@'):
             handle = '@' + handle
         details_param = {'forHandle': handle}
    else:
        return None, "Invalid identifier type extracted."

    print(f"Attempting to fetch details using: {details_param}")
    uploads_playlist_id, channel_title = get_channel_details(youtube, details_param)

    if not uploads_playlist_id and ('forHandle' in details_param or 'forUsername' in details_param):
        print(f"Direct lookup failed for {details_param}. Retrying with potentially modified identifier via get_channel_details internal search.")
        uploads_playlist_id, channel_title = get_channel_details(youtube, details_param)

    if not uploads_playlist_id:
         return None, f"Could not find channel or uploads playlist for identifier: {details_param}. Please check the URL or channel identifier."


    print(f"Found Channel: {channel_title}")
    print(f"Fetching all video IDs from uploads playlist: {uploads_playlist_id}...")
    video_ids = get_playlist_video_ids(youtube, uploads_playlist_id)

    empty_df_columns = ['Title', 'Published At', 'View Count', 'Comment Count']
    if not video_ids:
        return pd.DataFrame(columns=empty_df_columns), f"No videos found in the uploads playlist for '{channel_title}'."

    print(f"Found {len(video_ids)} video IDs. Fetching details for all videos...")
    video_details = get_video_details(youtube, video_ids)
    print("Finished fetching details.")

    if video_details:
        df = pd.DataFrame(video_details)
        df['View Count'] = pd.to_numeric(df['View Count'])
        df['Comment Count'] = pd.to_numeric(df['Comment Count'])
        df['Published At'] = pd.to_datetime(df['Published At'])

        # --- Sort based on the sort_by parameter --- 
        if sort_by == 'popular':
            df = df.sort_values(by='View Count', ascending=False)
            sort_description = "most popular"
        else: # Default to 'latest'
            df = df.sort_values(by='Published At', ascending=False)
            sort_description = "latest"
        # -------------------------------------------

        # --- Limit to top 200 --- 
        original_count = len(df)
        if original_count > max_videos:
            df = df.head(max_videos)
            # Adjust message for clarity based on sort type
            if sort_by == 'popular':
                 limit_message = f"top {len(df)} {sort_description}"
            else:
                 limit_message = f"{sort_description} {len(df)}"
        else:
            if sort_by == 'popular':
                 limit_message = f"top {len(df)} {sort_description} (all)"
            else:
                 limit_message = f"{sort_description} {len(df)} (all)"
        # --------------------------

        df.reset_index(drop=True, inplace=True)
        # Optional: Convert date back to string
        # df['Published At'] = df['Published At'].dt.strftime('%Y-%m-%d %H:%M:%S')

        return df, f"Successfully fetched the {limit_message} videos for channel '{channel_title}'."
    elif not video_ids:
         return pd.DataFrame(columns=empty_df_columns), f"No videos found in the uploads playlist for '{channel_title}'."
    else:
        return None, f"Found videos for '{channel_title}', but failed to fetch their details." 