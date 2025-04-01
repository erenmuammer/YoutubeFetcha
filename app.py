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
</style>
""", unsafe_allow_html=True)

st.title("📊 YouTube Channel Video Exporter")
# Removed the static description, will be dynamic based on selection
# st.write("Enter a YouTube channel URL to get the top 200 most popular videos and their stats.")

# --- Helper Function to Convert DataFrame to Excel in Memory ---
def to_excel(df):
    output = io.BytesIO()
    # Use openpyxl engine explicitly if needed, pandas usually detects it
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Videos')
    processed_data = output.getvalue()
    return processed_data

# --- Streamlit UI Elements ---
channel_url = st.text_input(
    "YouTube Channel URL",
    placeholder="e.g., https://www.youtube.com/@google or channel ID/username link",
    label_visibility="collapsed"
)

# --- Selection for Sorting --- 
sort_option = st.radio(
    "Select Video Ranking:",
    ('Latest 200 Videos', 'Top 200 Most Popular Videos'),
    horizontal=True, # Display options side-by-side
    label_visibility="collapsed"
)

if st.button("🚀 Fetch Videos"):
    if channel_url:
        # Determine sort_by parameter based on user choice
        if sort_option == 'Latest 200 Videos':
            sort_key = 'latest'
            sort_desc = "Latest 200"
        else:
            sort_key = 'popular'
            sort_desc = "Top 200 Most Popular"

        st.write(f"Fetching the **{sort_desc}** videos for the channel...")
        with st.spinner("🔍 Fetching video data... This might take a moment..."):
            try:
                # Call the fetcher function with the sort key
                df_videos, message = fetch_all_channel_videos(channel_url, sort_by=sort_key)

                if df_videos is not None and not df_videos.empty:
                    st.success(f"✅ {message}")

                    st.subheader(f"📈 Data Preview (First 5 of {sort_desc})")
                    st.dataframe(df_videos.head(5))

                    excel_data = to_excel(df_videos)

                    try:
                        channel_name_match = re.search(r"channel \'(.*?)\'.", message)
                        if channel_name_match:
                            channel_name = channel_name_match.group(1)
                            safe_channel_name = re.sub(r'[^\w\- ]', '', channel_name).strip().replace(' ', '_')
                            # Update filename based on sort key
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