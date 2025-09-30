#!/usr/bin/env python3
"""
Check recent videos from NBER YouTube channel to see upload dates.
"""

import yt_dlp
from datetime import datetime


def check_recent_uploads(channel_url):
    """Check the most recent videos and their upload dates."""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'playlistend': 10,  # Check last 10 videos
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        print(f"Checking recent videos from {channel_url}...\n")
        info = ydl.extract_info(channel_url, download=False)

        if 'entries' not in info:
            print("No videos found")
            return

        print("Recent videos:")
        print("-" * 80)

        for i, entry in enumerate(info['entries'][:10], 1):
            if entry is None:
                continue

            upload_date_str = entry.get('upload_date', 'Unknown')
            if upload_date_str != 'Unknown':
                upload_date = datetime.strptime(upload_date_str, '%Y%m%d')
                days_ago = (datetime.now() - upload_date).days
                date_display = f"{upload_date.strftime('%Y-%m-%d')} ({days_ago} days ago)"
            else:
                date_display = 'Unknown'

            print(f"{i}. {entry['title']}")
            print(f"   Uploaded: {date_display}")
            print(f"   ID: {entry['id']}")
            print()


if __name__ == '__main__':
    channel_url = "https://www.youtube.com/@NBERvideos/videos"
    check_recent_uploads(channel_url)