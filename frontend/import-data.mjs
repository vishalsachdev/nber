import { createClient } from '@supabase/supabase-js';
import { readFileSync } from 'fs';
import { config } from 'dotenv';

config({ path: '../.env' });

const supabaseUrl = process.env.VITE_SUPABASE_URL;
const supabaseKey = process.env.VITE_SUPABASE_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseKey) {
  console.error('Error: Missing Supabase credentials in .env file');
  process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseKey);

const videos = JSON.parse(readFileSync('../nber_videos_transcripts.json', 'utf-8'));

console.log(`Loaded ${videos.length} videos from JSON file`);

const presenterMap = new Map();

for (const video of videos) {
  for (const presenter of video.presenters || []) {
    if (!presenterMap.has(presenter.name)) {
      presenterMap.set(presenter.name, {
        name: presenter.name,
        affiliation: presenter.affiliation,
        scholar_url: presenter.scholar_url || null
      });
    }
  }
}

console.log(`Found ${presenterMap.size} unique presenters`);

for (const presenterData of presenterMap.values()) {
  try {
    await supabase.from('presenters').upsert(presenterData, { onConflict: 'name' });
    console.log(`✓ Inserted presenter: ${presenterData.name}`);
  } catch (error) {
    console.log(`✗ Error inserting presenter ${presenterData.name}:`, error);
  }
}

const { data: presenters } = await supabase.from('presenters').select('*');
const presenterIdMap = new Map(presenters.map(p => [p.name, p.id]));

for (const video of videos) {
  const videoData = {
    id: video.id,
    title: video.title,
    url: video.url,
    description: video.description || '',
    ai_summary: video.ai_summary || null,
    upload_date: video.upload_date || null,
    has_transcript: video.has_transcript || false,
    word_count: video.word_count || 0,
    char_count: video.char_count || 0,
    transcript: video.transcript || null
  };

  try {
    await supabase.from('videos').upsert(videoData);
    console.log(`✓ Inserted video: ${video.title.substring(0, 50)}...`);

    for (const presenter of video.presenters || []) {
      const presenterId = presenterIdMap.get(presenter.name);
      if (presenterId) {
        await supabase.from('video_presenters').upsert({
          video_id: video.id,
          presenter_id: presenterId
        });
      }
    }
  } catch (error) {
    console.log(`✗ Error inserting video ${video.title}:`, error);
  }
}

console.log('\n✅ Data import complete!');
