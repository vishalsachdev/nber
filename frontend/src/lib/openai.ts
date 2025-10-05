// UIUC Chat API functions
import type { VideoWithPresenters } from './api';

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

// Chat with a single video
export async function* chatWithVideo(
  title: string,
  presenterNames: string[],
  transcript: string,
  messages: ChatMessage[]
): AsyncGenerator<string> {
  const apiKey = import.meta.env.VITE_UIUC_CHAT_API_KEY;
  const courseName = import.meta.env.VITE_UIUC_CHAT_COURSE_NAME || 'experimental-chatbot';

  if (!apiKey) {
    throw new Error('UIUC Chat API key not configured. Please add VITE_UIUC_CHAT_API_KEY to your .env file.');
  }

  const transcriptExcerpt = transcript.substring(0, 15000) || 'No transcript available';
  const presenters = presenterNames.join(', ');

  // Get the last user message
  const userMessage = messages[messages.length - 1]?.content || '';

  // Combine context and question like in Streamlit app
  const combinedMessage = `Here is a transcript from the NBER Economics of Transformative AI Workshop:

**Video:** ${title}
**Presenters:** ${presenters}

**Transcript:**
${transcriptExcerpt}

**Question:** ${userMessage}

Please answer based on the transcript above. Be concise and cite specific points when relevant.`;

  const response = await fetch('/api/chat', {
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
    const errorText = await response.text();
    throw new Error(`UIUC Chat API error: ${errorText || response.statusText}`);
  }

  // Parse the streaming response (plain text chunks)
  yield* parseStreamingResponse(response.body as ReadableStream);
}

// Chat with all videos using summaries
export async function* chatWithAllVideos(
  videos: VideoWithPresenters[],
  messages: ChatMessage[]
): AsyncGenerator<string> {
  const apiKey = import.meta.env.VITE_UIUC_CHAT_API_KEY;
  const courseName = import.meta.env.VITE_UIUC_CHAT_COURSE_NAME || 'experimental-chatbot';

  if (!apiKey) {
    throw new Error('UIUC Chat API key not configured. Please add VITE_UIUC_CHAT_API_KEY to your .env file.');
  }

  // Create context from summaries
  const summariesContext = videos
    .map((v) => {
      const presenterNames = v.presenters.map(p => p.name).join(', ');
      const summary = v.ai_summary || 'No summary available';
      return `**${v.title}** by ${presenterNames}\n${summary}`;
    })
    .join('\n\n');

  // Get the last user message
  const userMessage = messages[messages.length - 1]?.content || '';

  const combinedMessage = `Here are summaries from ${videos.length} presentations from the NBER Economics of Transformative AI Workshop:

${summariesContext}

**Question:** ${userMessage}

Please answer by synthesizing information across these presentations. When referencing specific presentations, mention the title and presenter.`;

  const response = await fetch('/api/chat', {
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
    const errorText = await response.text();
    throw new Error(`UIUC Chat API error: ${errorText || response.statusText}`);
  }

  // Parse the streaming response (plain text chunks)
  yield* parseStreamingResponse(response.body as ReadableStream);
}

// Parse streaming response from UIUC Chat API (plain text chunks)
export async function* parseStreamingResponse(
  stream: ReadableStream
): AsyncGenerator<string> {
  const reader = stream.getReader();
  const decoder = new TextDecoder();

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      // UIUC API sends plain text chunks - decode and yield as-is
      const chunk = decoder.decode(value, { stream: true });
      if (chunk) {
        yield chunk;
      }
    }
  } finally {
    reader.releaseLock();
  }
}
