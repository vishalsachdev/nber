#!/usr/bin/env python3
"""
Extract transcripts for specific NBER YouTube videos.
"""

import json
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound


# Video IDs from the last 24 hours
VIDEOS = [
    {"title": "Algorithms as A Vehicle to Reflective Equilibrium", "id": "-K2Aek8qxh8"},
    {"title": "AI Exposure and the Adaptive Capacity of American…", "id": "64F1sfm5kGI"},
    {"title": "Public Finance in the Age of AI: A Primer", "id": "i2qpFggisxI"},
    {"title": "Transformative AI and Firms", "id": "06kDdPboRMg"},
    {"title": "An Economy of AI Agents", "id": "kE4JQN-vwjM"},
    {"title": "What Is There to Fear in a Post AGI World", "id": "ttSnUiZILoA"},
    {"title": "We Won't Be Missed: Work and Growth in the Era of…", "id": "eP3ic8EOv6w"},
    {"title": "The Impact of AI and Digital Platforms…", "id": "_xTeQgbAPZs"},
    {"title": "The Coasean Singularity? Demand, Supply, and…", "id": "9VJ4oFWk1SE"},
    {"title": "How Much Should We Spend to Reduce A.I.'s…", "id": "PB7zI4Xh_So"},
    {"title": "Artificial Intelligence in Research and Development", "id": "5q31h9uxaUA"},
    {"title": "Genius on Demand: The Value of Transformative…", "id": "Lq2kIqBqTmY"},
    {"title": "Economics of Transformative AI Workshop, Fall 2025 - Welcome", "id": "rYwpBKqCq_A"},
    {"title": "Making AI Count: The Next Measurement Frontier?", "id": "CiDfmCcWDBo"},
    {"title": "Artificial Intelligence, Competition, and Welfare", "id": "TjV-b8s-Svc"},
    {"title": "AI's Use of Knowledge in Society", "id": "GVbipjVhh4w"},
    {"title": "Science in the Age of Algorithms", "id": "lQjlHM9R5Us"},
]


def get_transcript(video_id):
    """
    Fetch transcript for a video using youtube-transcript-api.

    Args:
        video_id: YouTube video ID

    Returns:
        String containing the full transcript, or None if unavailable
    """
    try:
        api = YouTubeTranscriptApi()
        transcript_data = api.fetch(video_id)

        # The fetch returns a FetchedTranscript object with snippets
        if hasattr(transcript_data, 'snippets'):
            transcript_text = ' '.join([snippet.text for snippet in transcript_data.snippets])
            return transcript_text
        else:
            return None
    except (TranscriptsDisabled, NoTranscriptFound):
        return None
    except Exception as e:
        print(f"   Error: {e}")
        return None


def main():
    print(f"Extracting transcripts for {len(VIDEOS)} NBER videos from the last 24 hours...\n")

    results = []
    success_count = 0
    fail_count = 0

    for i, video in enumerate(VIDEOS, 1):
        print(f"{i}/{len(VIDEOS)}. {video['title']}")
        print(f"   ID: {video['id']}")
        print(f"   Fetching transcript...")

        transcript = get_transcript(video['id'])

        if transcript:
            char_count = len(transcript)
            word_count = len(transcript.split())
            print(f"   ✓ Success ({char_count:,} chars, ~{word_count:,} words)")
            success_count += 1
        else:
            print(f"   ✗ No transcript available")
            fail_count += 1

        results.append({
            'id': video['id'],
            'title': video['title'],
            'url': f"https://www.youtube.com/watch?v={video['id']}",
            'transcript': transcript,
            'has_transcript': transcript is not None,
            'char_count': len(transcript) if transcript else 0,
            'word_count': len(transcript.split()) if transcript else 0
        })

        print()

    # Save results to JSON
    output_file = 'nber_videos_transcripts.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"Results saved to {output_file}")
    print(f"\nSummary:")
    print(f"  Total videos: {len(results)}")
    print(f"  With transcripts: {success_count}")
    print(f"  Without transcripts: {fail_count}")

    total_chars = sum(r['char_count'] for r in results if r['has_transcript'])
    total_words = sum(r['word_count'] for r in results if r['has_transcript'])
    print(f"\nTotal content:")
    print(f"  Characters: {total_chars:,}")
    print(f"  Words: ~{total_words:,}")


if __name__ == '__main__':
    main()