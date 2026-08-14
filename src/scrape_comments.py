import os
import time
import pandas as pd
from dotenv import load_dotenv
from googleapiclient.discovery import build

# Load the API key from .env into this script's environment
load_dotenv()
api_key = os.getenv("YOUTUBE_API_KEY")

if not api_key:
    raise ValueError("YOUTUBE_API_KEY not found — check your .env file")

youtube = build('youtube', 'v3', developerKey=api_key)


def search_videos(query, max_results=25):
    """Search YouTube for videos matching a query, return list of video IDs + titles."""
    request = youtube.search().list(
        q=query,
        part="snippet",
        type="video",
        maxResults=max_results,
        relevanceLanguage="gu",
        regionCode="IN"
    )
    response = request.execute()

    videos = []
    for item in response.get("items", []):
        videos.append({
            "video_id": item["id"]["videoId"],
            "title": item["snippet"]["title"],
            "channel": item["snippet"]["channelTitle"],
            "query_used": query
        })
    return videos


def get_comments(video_id, max_comments=150):
    """Pull top-level comments from a single video, up to max_comments."""
    comments = []
    next_page_token = None

    while len(comments) < max_comments:
        try:
            request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=100,
                pageToken=next_page_token,
                textFormat="plainText"
            )
            response = request.execute()
        except Exception as e:
            print(f"Skipping {video_id}: {e}")
            break

        for item in response.get("items", []):
            snippet = item["snippet"]["topLevelComment"]["snippet"]
            comments.append({
                "comment_id": item["snippet"]["topLevelComment"]["id"],
                "video_id": video_id,
                "text": snippet["textDisplay"],
                "like_count": snippet["likeCount"],
                "published_at": snippet["publishedAt"]
            })

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return comments


if __name__ == "__main__":
    search_queries = [
        "gujarati movie review", "gujarati web series review", "gujarati film review",
        "gujarati comedy", "gujarati vlog", "gujarati comedy sketch",
        "gujarat cricket reaction", "gujarati sports news", "gujarat local news"
    ]

    # Stage 1: search for videos
    all_videos = []
    for query in search_queries:
        print(f"Searching: {query}")
        videos = search_videos(query)
        all_videos.extend(videos)
        time.sleep(1)

    df_videos = pd.DataFrame(all_videos).drop_duplicates(subset="video_id")
    os.makedirs("data/raw", exist_ok=True)
    df_videos.to_csv("data/raw/video_list.csv", index=False)
    print(f"\nSaved {len(df_videos)} unique videos to data/raw/video_list.csv")

    # Stage 2: pull comments from each video
    all_comments = []
    for idx, row in df_videos.iterrows():
        print(f"[{idx+1}/{len(df_videos)}] Pulling comments from: {row['title'][:50]}...")
        comments = get_comments(row["video_id"], max_comments=150)
        all_comments.extend(comments)
        time.sleep(0.5)

    df_comments = pd.DataFrame(all_comments)
    df_comments.to_csv("data/raw/comments_raw.csv", index=False)
    print(f"\nTotal comments collected: {len(df_comments)}")
    print("Saved to data/raw/comments_raw.csv")