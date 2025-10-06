# UIUC Chat API Debug Notes (2025-10-06)

Purpose: Track investigation and fixes for API errors seen in chat features (Edge Function proxy to UIUC Chat API).

## Symptoms
- Frontend displayed: `Error: UIUC Chat API error: Method Not Allowed`
- Direct curl to upstream sometimes returned `400 Invalid JSON` (due to line breaks in manual curl) and `405 Method Not Allowed` on clean requests.

## Findings
- 405 indicates an HTTP method/path issue at the upstream, not payload (model name, etc.).
- 400 "Invalid JSON" occurred when a newline split the `course_name` in curl; app code uses `JSON.stringify` and should not hit this.
- Upstream response headers showed `x-matched-path: /api/chat-api/chat` confirming routing to the expected path.

## Changes Implemented
1) Edge Function hardening (`api/chat.ts`)
   - Removed hop-by-hop header: `Connection: keep-alive` (disallowed in Edge runtime).
   - Forward upstream `status` and `content-type` while streaming body.
   - Added `OPTIONS` handler with CORS headers (POST, OPTIONS) to avoid preflight 405s.
   - Sent `Accept: text/event-stream` upstream for SSE negotiation.
   - Included header auth if present in body:
     - `Authorization: Bearer <api_key>` and `x-api-key: <api_key>`
     - `x-course-name: <course_name>`
   - Endpoint variants + trailing slash retry:
     - `https://uiuc.chat/api/chat-api/chat`
     - `https://uiuc.chat/api/chat-api/chat/`
     - `https://uiuc.chat/chat-api/chat`
     - `https://uiuc.chat/chat-api/chat/`
   - GET fallback: if POST returns 405, retry as GET with URL-encoded params (`model`, `messages` JSON, `course_name`, `stream`, `temperature`, `retrieval_only`).

2) Frontend headers
   - Added `Accept: text/event-stream` to requests in `frontend/src/lib/openai.ts` and `frontend/src/lib/api.ts`.

## Repro/Verification
- Dev proxy test (Vite):
  - `curl -i http://localhost:5173/api/chat -H 'Content-Type: application/json' -H 'Accept: text/event-stream' --data-raw '{"model":"Qwen/Qwen2.5-VL-72B-Instruct","messages":[{"role":"user","content":"hello"}],"api_key":"REDACTED","course_name":"experimental-chatbot","stream":false}'`
- Edge Function (prod):
  - `curl -i https://nber2025.vercel.app/api/chat -H 'Content-Type: application/json' -H 'Accept: text/event-stream' --data-raw '{...}'`
- Upstream (direct):
  - Ensure single-line JSON (no unescaped newlines). Line breaks yield `400 Invalid JSON`.

## Current Status
- Edge Function now retries with GET if POST is not allowed by upstream and includes broader endpoint/headers. If failures persist, responses include upstream status/text for quicker diagnosis.

## Next Steps / Questions
- Confirm upstream’s expected method/param schema for SSE (docs or Allow header). If GET-only, we can permanently route via GET.
- Validate whether `Authorization` vs body `api_key` is the required auth; adjust if docs specify one.
- Ensure Vercel envs set for prod: `VITE_UIUC_CHAT_API_KEY`, `VITE_UIUC_CHAT_COURSE_NAME`.
- If stable, consider trimming fallback permutations and extra headers.

## Notes
- Model name (e.g., `Qwen/Qwen2.5-VL-72B-Instruct` vs `Qwen2.5-VL-72B-Instruct`) would not cause 405; that would surface as 4xx with a parsed error body.

