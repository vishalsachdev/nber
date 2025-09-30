#!/usr/bin/env python3
"""
Fetch titles and transcripts from NBER YouTube videos.
"""

import json
import sys
from datetime import datetime, timedelta
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound


def get_recent_videos(channel_url, count=10):
    """
    Fetch most recent videos from a YouTube channel.

    Args:
        channel_url: URL of the YouTube channel
        count: Number of recent videos to fetch (default: 10)

    Returns:
        List of video dictionaries with id, title, and url
    """
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'playlistend': count,
    }

    videos = []

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        print(f"Fetching {count} most recent videos from {channel_url}...")
        info = ydl.extract_info(channel_url, download=False)

        if 'entries' not in info:
            print("No videos found in channel")
            return videos

        for entry in info['entries']:
            if entry is None:
                continue

            # Get more detailed info for each video
            video_url = f"https://www.youtube.com/watch?v={entry['id']}"
            video_info = ydl.extract_info(video_url, download=False)

            upload_date = video_info.get('upload_date', 'Unknown')
            if upload_date != 'Unknown':
                upload_date_obj = datetime.strptime(upload_date, '%Y%m%d')
                upload_date_formatted = upload_date_obj.strftime('%Y-%m-%d')
                days_ago = (datetime.now() - upload_date_obj).days
            else:
                upload_date_formatted = 'Unknown'
                days_ago = None

            videos.append({
                'id': entry['id'],
                'title': video_info.get('title', entry.get('title', 'Unknown')),
                'upload_date': upload_date_formatted,
                'days_ago': days_ago,
                'url': video_url,
                'description': video_info.get('description', '')
            })

    return videos


def get_transcript(video_id):
    """
    Fetch transcript for a video.

    Args:
        video_id: YouTube video ID

    Returns:
        String containing the full transcript, or None if unavailable
    """
    try:
        api = YouTubeTranscriptApi()
        transcript_data = api.fetch(video_id)
        transcript_text = ' '.join([entry['text'] for entry in transcript_data])
        return transcript_text
    except (TranscriptsDisabled, NoTranscriptFound) as e:
        return None
    except Exception as e:
        print(f"   Error: {e}")
        return None


def main():
    # Get number of videos from command line or default to 10
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 10

    channel_url = "https://www.youtube.com/@NBERvideos/videos"

    # Fetch recent videos
    videos = get_recent_videos(channel_url, count=count)

    if not videos:
        print("\nNo videos found.")
        return

    print(f"\nFound {len(videos)} video(s):\n")

    results = []

    for i, video in enumerate(videos, 1):
        print(f"{i}. {video['title']}")
        if video['days_ago'] is not None:
            print(f"   Uploaded: {video['upload_date']} ({video['days_ago']} days ago)")
        else:
            print(f"   Uploaded: {video['upload_date']}")
        print(f"   URL: {video['url']}")
        print(f"   Fetching transcript...")

        transcript = get_transcript(video['id'])

        if transcript:
            print(f"   ✓ Transcript retrieved ({len(transcript)} characters)")
        else:
            print(f"   ✗ No transcript available")

        results.append({
            'id': video['id'],
            'title': video['title'],
            'upload_date': video['upload_date'],
            'days_ago': video['days_ago'],
            'url': video['url'],
            'description': video['description'],
            'transcript': transcript,
            'has_transcript': transcript is not None
        })

        print()

    # Save results to JSON
    output_file = 'nber_videos.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"Results saved to {output_file}")
    print(f"\nSummary:")
    print(f"  Total videos: {len(results)}")
    print(f"  With transcripts: {sum(1 for r in results if r['has_transcript'])}")
    print(f"  Without transcripts: {sum(1 for r in results if not r['has_transcript'])}")


if __name__ == '__main__':
    main()