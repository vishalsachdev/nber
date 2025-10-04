#!/usr/bin/env python3
"""
Generate AI summaries for NBER video presentations using OpenAI GPT-4o-mini.
This script reads transcripts and creates concise summaries for each presentation.
"""

import json
import os
from openai import OpenAI
from dotenv import load_dotenv
from collections import OrderedDict

# Load environment variables
load_dotenv()

def get_openai_client():
    """Initialize OpenAI client with API key from environment."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    return OpenAI(api_key=api_key)

def generate_summary(client, video):
    """
    Generate a concise summary of a video presentation using OpenAI.

    Args:
        client: OpenAI client instance
        video: Video dictionary with title, presenters, and transcript

    Returns:
        String summary or None if transcript unavailable
    """
    if not video.get('transcript'):
        return None

    title = video['title']
    presenters = ', '.join([p['name'] for p in video.get('presenters', [])])
    transcript = video['transcript']

    # Limit transcript to ~12k chars to stay well within token limits
    transcript_excerpt = transcript[:12000]

    prompt = f"""You are summarizing an academic presentation from the NBER Economics of Transformative AI Workshop.

Title: {title}
Presenters: {presenters}

Based on the following transcript excerpt, create a concise 2-3 paragraph summary that captures:
1. The main research question or topic
2. Key findings or arguments presented
3. Important implications or conclusions

Keep the summary accessible to economists and policymakers. Be specific about the content.

Transcript:
{transcript_excerpt}

Summary:"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert at summarizing economics research presentations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=500
        )

        summary = response.choices[0].message.content.strip()
        return summary

    except Exception as e:
        print(f"Error generating summary for '{title}': {e}")
        return None

def restructure_with_summary(video, summary):
    """Restructure video dict with summary field in correct position."""
    ordered = OrderedDict()

    # Core identification
    ordered['id'] = video.get('id', '')
    ordered['title'] = video.get('title', '')
    ordered['url'] = video.get('url', '')

    # Authors/Presenters
    ordered['presenters'] = video.get('presenters', [])
    ordered['num_presenters'] = video.get('num_presenters', 0)

    # Metadata - add summary after description
    ordered['description'] = video.get('description', '')
    ordered['ai_summary'] = summary  # New field
    ordered['upload_date'] = video.get('upload_date', 'Unknown')
    ordered['days_ago'] = video.get('days_ago', None)

    # Transcript info
    ordered['has_transcript'] = video.get('has_transcript', False)
    ordered['word_count'] = video.get('word_count', 0)
    ordered['char_count'] = video.get('char_count', 0)

    # Transcript content (last)
    ordered['transcript'] = video.get('transcript', None)

    return ordered

def main():
    """Generate summaries for all videos and update JSON file."""
    # Load video data
    print("Loading video data...")
    with open('nber_videos_transcripts.json', 'r', encoding='utf-8') as f:
        videos = json.load(f)

    # Initialize OpenAI client
    print("Initializing OpenAI client...")
    client = get_openai_client()

    # Generate summaries
    print(f"\nGenerating summaries for {len(videos)} videos...\n")

    updated_videos = []
    summary_count = 0

    for i, video in enumerate(videos, 1):
        title = video['title']
        print(f"{i}/{len(videos)}. {title[:60]}...")

        if not video.get('has_transcript'):
            print("   ⏭️  No transcript available - skipping")
            summary = None
        else:
            print("   🤖 Generating AI summary...")
            summary = generate_summary(client, video)

            if summary:
                word_count = len(summary.split())
                print(f"   ✅ Summary generated ({word_count} words)")
                summary_count += 1
            else:
                print("   ❌ Failed to generate summary")

        # Restructure video with summary
        updated_video = restructure_with_summary(video, summary)
        updated_videos.append(updated_video)
        print()

    # Save updated data
    print(f"Saving updated data to nber_videos_transcripts.json...")
    with open('nber_videos_transcripts.json', 'w', encoding='utf-8') as f:
        json.dump(updated_videos, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Complete!")
    print(f"   Total videos: {len(videos)}")
    print(f"   Summaries generated: {summary_count}")
    print(f"   Videos without transcripts: {len(videos) - summary_count}")

    # Estimate cost
    avg_input_tokens = 4000  # Approximate for transcript + prompt
    avg_output_tokens = 200  # Approximate for summary
    cost_per_video = (avg_input_tokens / 1_000_000 * 0.15) + (avg_output_tokens / 1_000_000 * 0.60)
    total_cost = cost_per_video * summary_count

    print(f"\n💰 Estimated API cost: ${total_cost:.4f}")

if __name__ == '__main__':
    main()