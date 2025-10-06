// API functions for fetching video data
// For local development, using JSON file directly

export interface Presenter {
  id?: string;
  name: string;
  affiliation: string;
  scholar_url?: string;
}

export interface VideoWithPresenters {
  id: string;
  title: string;
  url: string;
  description?: string;
  upload_date?: string;
  has_transcript: boolean;
  transcript?: string;
  word_count?: number;
  ai_summary?: string;
  presenters: Presenter[];
}

// Load videos from JSON file
export async function fetchVideosWithPresenters(): Promise<VideoWithPresenters[]> {
  try {
    // Fetch the JSON file from the parent directory
    const response = await fetch('/nber_videos_transcripts.json');
    if (!response.ok) {
      throw new Error(`Failed to fetch videos: ${response.statusText}`);
    }
    const videos = await response.json();
    return videos;
  } catch (error) {
    console.error('Error fetching videos:', error);
    throw error;
  }
}

// Search videos by query
export async function searchVideos(
  query: string,
  videos: VideoWithPresenters[]
): Promise<VideoWithPresenters[]> {
  const lowerQuery = query.toLowerCase();

  return videos.filter(video => {
    // Search in title
    if (video.title.toLowerCase().includes(lowerQuery)) {
      return true;
    }

    // Search in presenters
    if (video.presenters.some(p => p.name.toLowerCase().includes(lowerQuery))) {
      return true;
    }

    // Search in transcript
    if (video.transcript && video.transcript.toLowerCase().includes(lowerQuery)) {
      return true;
    }

    // Search in summary
    if (video.ai_summary && video.ai_summary.toLowerCase().includes(lowerQuery)) {
      return true;
    }

    return false;
  });
}

// Get all unique presenters with video counts
export async function getAllPresenters(): Promise<(Presenter & { videoCount: number })[]> {
  const videos = await fetchVideosWithPresenters();
  const presenterMap = new Map<string, Presenter & { videoCount: number }>();

  videos.forEach(video => {
    video.presenters.forEach(presenter => {
      if (presenterMap.has(presenter.name)) {
        presenterMap.get(presenter.name)!.videoCount++;
      } else {
        presenterMap.set(presenter.name, {
          ...presenter,
          videoCount: 1
        });
      }
    });
  });

  return Array.from(presenterMap.values()).sort((a, b) =>
    a.name.localeCompare(b.name)
  );
}

// Get all unique presenters (legacy)
export async function fetchPresenters(videos: VideoWithPresenters[]): Promise<Presenter[]> {
  const presenterMap = new Map<string, Presenter>();

  videos.forEach(video => {
    video.presenters.forEach(presenter => {
      if (!presenterMap.has(presenter.name)) {
        presenterMap.set(presenter.name, presenter);
      }
    });
  });

  return Array.from(presenterMap.values()).sort((a, b) =>
    a.name.localeCompare(b.name)
  );
}

// Chat with AI (using UIUC Chat API)
export async function chatWithOpenAI(
  messages: { role: string; content: string }[],
  contextPrompt: string
): Promise<ReadableStream> {
  const apiKey = import.meta.env.VITE_UIUC_CHAT_API_KEY;
  const courseName = import.meta.env.VITE_UIUC_CHAT_COURSE_NAME || 'experimental-chatbot';

  if (!apiKey) {
    throw new Error('UIUC Chat API key not configured');
  }

  // Combine context and user message like in Streamlit app
  const userMessage = messages[messages.length - 1]?.content || '';
  const combinedMessage = `${contextPrompt}\n\n**Question:** ${userMessage}\n\nPlease answer based on the information above. Be concise and cite specific points when relevant.`;

  const response = await fetch('https://chat.illinois.edu/api/chat-api/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      model: 'Qwen/Qwen2.5-VL-72B-Instruct',
      messages: [
        { role: 'system', content: 'You are a helpful AI assistant. Answer questions based ONLY on the information provided. Do not add document citations.' },
        { role: 'user', content: combinedMessage }
      ],
      api_key: apiKey,
      course_name: courseName,
      stream: true,
      temperature: 0.7,
      retrieval_only: false
    })
  });

  if (!response.ok) {
    throw new Error(`UIUC Chat API error: ${response.statusText}`);
  }

  return response.body as ReadableStream;
}
