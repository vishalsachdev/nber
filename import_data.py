"""
Import video data from JSON to Supabase database
"""

import json
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# Get Supabase credentials
supabase_url = os.getenv('VITE_SUPABASE_URL')
supabase_key = os.getenv('VITE_SUPABASE_SUPABASE_ANON_KEY')

if not supabase_url or not supabase_key:
    print("Error: Missing Supabase credentials in .env file")
    exit(1)

supabase: Client = create_client(supabase_url, supabase_key)

# Load video data
with open('nber_videos_transcripts.json', 'r', encoding='utf-8') as f:
    videos = json.load(f)

print(f"Loaded {len(videos)} videos from JSON file")

# Import presenters first (to avoid duplicates)
presenter_map = {}
all_presenters = []

for video in videos:
    for presenter in video.get('presenters', []):
        name = presenter['name']
        if name not in presenter_map:
            presenter_map[name] = {
                'name': name,
                'affiliation': presenter['affiliation'],
                'scholar_url': presenter.get('scholar_url')
            }

print(f"Found {len(presenter_map)} unique presenters")

# Insert presenters
for presenter_data in presenter_map.values():
    try:
        result = supabase.table('presenters').upsert(
            presenter_data,
            on_conflict='name'
        ).execute()
        print(f"✓ Inserted presenter: {presenter_data['name']}")
    except Exception as e:
        print(f"✗ Error inserting presenter {presenter_data['name']}: {e}")

# Get all presenters with IDs
presenters_result = supabase.table('presenters').select('*').execute()
presenter_id_map = {p['name']: p['id'] for p in presenters_result.data}

# Import videos
for video in videos:
    video_data = {
        'id': video['id'],
        'title': video['title'],
        'url': video['url'],
        'description': video.get('description', ''),
        'ai_summary': video.get('ai_summary'),
        'upload_date': video.get('upload_date'),
        'has_transcript': video.get('has_transcript', False),
        'word_count': video.get('word_count', 0),
        'char_count': video.get('char_count', 0),
        'transcript': video.get('transcript')
    }

    try:
        result = supabase.table('videos').upsert(video_data).execute()
        print(f"✓ Inserted video: {video['title'][:50]}...")

        # Insert video-presenter relationships
        for presenter in video.get('presenters', []):
            presenter_id = presenter_id_map.get(presenter['name'])
            if presenter_id:
                rel_data = {
                    'video_id': video['id'],
                    'presenter_id': presenter_id
                }
                supabase.table('video_presenters').upsert(rel_data).execute()

    except Exception as e:
        print(f"✗ Error inserting video {video['title']}: {e}")

print("\n✅ Data import complete!")
