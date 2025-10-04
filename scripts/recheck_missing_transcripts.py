#!/usr/bin/env python3
"""
Recheck videos that were missing transcripts and update the status file.
"""

import json
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound


def get_transcript(video_id):
    """Fetch transcript for a video."""
    try:
        api = YouTubeTranscriptApi()
        transcript_data = api.fetch(video_id)

        if hasattr(transcript_data, 'snippets'):
            transcript_text = ' '.join([snippet.text for snippet in transcript_data.snippets])
            return transcript_text
        else:
            return None
    except (TranscriptsDisabled, NoTranscriptFound):
        return None
    except Exception:
        return None


def main():
    # Load status file
    with open('video_status.json', 'r', encoding='utf-8') as f:
        status_data = json.load(f)

    # Load full transcript data
    with open('nber_videos_transcripts.json', 'r', encoding='utf-8') as f:
        transcript_data = json.load(f)

    # Get videos that need rechecking
    videos_to_check = [v for v in status_data['videos'] if v['needs_recheck']]

    if not videos_to_check:
        print("No videos need rechecking.")
        return

    print(f"Rechecking {len(videos_to_check)} videos for transcripts...\n")

    newly_available = []
    still_missing = []

    for i, video in enumerate(videos_to_check, 1):
        print(f"{i}/{len(videos_to_check)}. {video['title']}")
        print(f"   ID: {video['id']}")
        print(f"   Checking...")

        transcript = get_transcript(video['id'])

        if transcript:
            word_count = len(transcript.split())
            char_count = len(transcript)
            print(f"   ✓ NOW AVAILABLE ({char_count:,} chars, ~{word_count:,} words)")

            # Update status
            video['status'] = 'completed'
            video['has_transcript'] = True
            video['word_count'] = word_count
            video['needs_recheck'] = False
            del video['reason']

            # Update transcript data
            for t in transcript_data:
                if t['id'] == video['id']:
                    t['transcript'] = transcript
                    t['has_transcript'] = True
                    t['word_count'] = word_count
                    t['char_count'] = char_count
                    break

            newly_available.append(video['id'])
        else:
            print(f"   ✗ Still not available")
            still_missing.append(video['id'])

        print()

    # Update counts
    status_data['videos_with_transcripts'] = sum(1 for v in status_data['videos'] if v['has_transcript'])
    status_data['videos_needing_check'] = sum(1 for v in status_data['videos'] if v['needs_recheck'])
    status_data['videos_to_recheck'] = still_missing

    # Save updated files
    with open('video_status.json', 'w', encoding='utf-8') as f:
        json.dump(status_data, f, indent=2, ensure_ascii=False)

    with open('nber_videos_transcripts.json', 'w', encoding='utf-8') as f:
        json.dump(transcript_data, f, indent=2, ensure_ascii=False)

    print(f"Updated video_status.json and nber_videos_transcripts.json")
    print(f"\nResults:")
    print(f"  Newly available: {len(newly_available)}")
    print(f"  Still missing: {len(still_missing)}")
    print(f"\nTotal progress:")
    print(f"  With transcripts: {status_data['videos_with_transcripts']}/{status_data['total_videos']}")
    print(f"  Still need checking: {status_data['videos_needing_check']}")


if __name__ == '__main__':
    main()