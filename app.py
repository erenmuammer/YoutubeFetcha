import streamlit as st
import pandas as pd
import io
import re
from youtube_fetcher import fetch_all_channel_videos # Import the main function

st.set_page_config(
    page_title="YouTube Video Exporter",
    page_icon="📊", # Favicon
    layout="centered", # Center layout for a cleaner look
    initial_sidebar_state="collapsed",
)

# --- Custom CSS for Modern Look ---
st.markdown("""
<style>
    .stButton>button {
        background-color: #FF4B4B;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        border: none;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #E03C3C;
        color: white;
    }
    .stTextInput>div>div>input {
        border-radius: 8px;
    }
    .stDataFrame {
        border: 1px solid #e1e4e8;
        border-radius: 8px;
    }
    h1 {
        color: #FF4B4B;
    }
    .dataframe a {
        color: #FF4B4B;
        text-decoration: none;
    }
    .dataframe a:hover {
        text-decoration: underline;
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 YouTube Channel Video Exporter")
# Removed the static description, will be dynamic based on selection
# st.write("Enter a YouTube channel URL to get the top 200 most popular videos and their stats.")

# --- Helper Function to Convert DataFrame to Excel in Memory ---
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Create a copy of the dataframe for Excel export
        df_excel = df.copy()
        # Convert links to clickable format in Excel
        df_excel['Link'] = df_excel['Link'].apply(lambda x: f'=HYPERLINK("{x}","Watch Video")')
        df_excel.to_excel(writer, index=False, sheet_name='Videos')
    processed_data = output.getvalue()
    return processed_data

# --- Streamlit UI Elements ---
channel_url = st.text_input(
    "YouTube Channel URL",
    placeholder="e.g., https://www.youtube.com/@google or channel ID/username link",
    label_visibility="collapsed"
)

# --- Selection for Sorting --- 
col1, col2 = st.columns(2)
with col1:
    sort_option = st.radio(
        "Select Video Ranking:",
        ('Latest Videos', 'Most Popular Videos'),
        horizontal=True, # Display options side-by-side
        label_visibility="collapsed"
    )
    
with col2:
    video_count = st.selectbox(
        "Number of Videos",
        options=[10, 50, 100, 200],
        index=0, # Default to 10 videos
    )

if st.button("🚀 Fetch Videos"):
    if channel_url:
        # Determine sort_by parameter based on user choice
        if sort_option == 'Latest Videos':
            sort_key = 'latest'
            sort_desc = f"Latest {video_count}"
        else:
            sort_key = 'popular'
            sort_desc = f"Top {video_count} Most Popular"

        st.write(f"Fetching the **{sort_desc}** videos for the channel...")
        with st.spinner("🔍 Fetching video data... This might take a moment..."):
            try:
                # Call the fetcher function with the sort key and video count
                df_videos, message = fetch_all_channel_videos(channel_url, sort_by=sort_key, max_videos=video_count)

                if df_videos is not None and not df_videos.empty:
                    st.success(f"✅ {message}")

                    # Create clickable links in the DataFrame while keeping the separate Link column
                    df_display = df_videos.copy()
                    
                    # Rename Link column to be more descriptive
                    df_display = df_display.rename(columns={'Link': 'Video URL'})

                    st.subheader(f"📈 Data Preview (First 5 of {sort_desc})")
                    st.dataframe(
                        df_display.head(5),
                        use_container_width=True
                    )

                    excel_data = to_excel(df_videos)

                    try:
                        channel_name_match = re.search(r"channel \'(.*?)\'.", message)
                        if channel_name_match:
                            channel_name = channel_name_match.group(1)
                            safe_channel_name = re.sub(r'[^\w\- ]', '', channel_name).strip().replace(' ', '_')
                            # Update filename based on sort key and count
                            file_name_suffix = "latest" if sort_key == 'latest' else "popular"
                            file_name = f"{safe_channel_name}_{file_name_suffix}_{len(df_videos)}_videos.xlsx"
                        else:
                            file_name_suffix = "latest" if sort_key == 'latest' else "popular"
                            file_name=f"youtube_{file_name_suffix}_{len(df_videos)}_videos.xlsx"
                    except Exception:
                        file_name_suffix = "latest" if sort_key == 'latest' else "popular"
                        file_name=f"youtube_{file_name_suffix}_{len(df_videos)}_videos.xlsx"

                    st.download_button(
                        label=f"📥 Download {sort_desc} Excel File", # Dynamic label
                        data=excel_data,
                        file_name=file_name,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key='download_button'
                    )
                elif df_videos is not None and df_videos.empty:
                     st.info(f"ℹ️ {message}")
                else:
                    st.error(f"❌ Error: {message}")

            except ValueError as ve:
                 st.error(f"❌ Configuration Error: {ve}")
            except Exception as e:
                st.error(f"❌ An unexpected error occurred: {e}")
                st.exception(e)

    else:
        st.warning("⚠️ Please enter a YouTube Channel URL.") 