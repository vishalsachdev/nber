# Future Features & Improvements

## Cost Control (CRITICAL for Public Launch)

### 1. Rate Limiting
**Priority:** HIGH
**Effort:** 30 minutes
**Impact:** Prevent cost overruns from abuse

- Per-session message limits (e.g., 10 messages max)
- Global hourly request limits (e.g., 100 requests/hour)
- Session state tracking for rate limit enforcement
- User-facing warnings when approaching limits
- Graceful error messages when limits exceeded

**Implementation Notes:**
- Use `st.session_state` for per-session tracking
- Use file-based counter or Redis for global limits
- Clear session state button to reset counter

### 2. OpenAI Budget Monitoring
**Priority:** HIGH
**Effort:** 15 minutes
**Impact:** Hard cap on monthly spending

- Set budget limit in OpenAI dashboard ($50/month recommended for start)
- Implement graceful degradation when budget exceeded
- Show "Service temporarily unavailable - budget limit reached" message
- Optional: Add admin dashboard showing current usage

**Implementation Notes:**
- OpenAI dashboard: Settings > Limits > Set monthly budget cap
- Add try/catch for quota exceeded errors
- Consider adding usage tracking endpoint

### 3. Context Window Optimization
**Priority:** MEDIUM
**Effort:** 20 minutes
**Impact:** 30-40% cost reduction per request

**Current:**
- Single video: 15K chars transcript + 1K token response
- Multi-video: 10 summaries + 1.2K token response

**Optimized:**
- Single video: 10K chars transcript + 500 token response
- Multi-video: 7 summaries + 600 token response
- Implement message history pruning (keep last 5 exchanges)
- Smart chunking: Only send relevant transcript segments

**Implementation Notes:**
- Update `chat_with_transcript()`: transcript[:15000] → transcript[:10000]
- Update max_tokens: 1000 → 500, 1200 → 600
- Add conversation history pruning after 5 exchanges

### 4. Authentication & Access Control
**Priority:** MEDIUM (if expecting viral traffic)
**Effort:** 30 minutes
**Impact:** Prevent bot abuse, control access

**Options:**
- Simple password protection (easiest)
- Email-based access control
- IP-based rate limiting
- Google OAuth integration

**Implementation Notes:**
- Streamlit supports simple password auth via secrets.toml
- For production, consider streamlit-authenticator package

### 5. Response Caching
**Priority:** LOW (optimization for later)
**Effort:** 2+ hours
**Impact:** Significant cost savings for repeated questions

- Cache common question/answer pairs
- Implement semantic search for similar questions
- Show "Related questions others asked" section
- Use embeddings to find cached similar queries

**Implementation Notes:**
- Use local JSON cache or Redis for storage
- Implement simple string matching first, embeddings later
- Consider using Streamlit's `@st.cache_data` for caching

## Feature Enhancements

### 6. Usage Analytics Dashboard
**Priority:** MEDIUM
**Effort:** 1 hour
**Impact:** Understand user behavior, optimize expensive patterns

- Track which videos get most chats
- Average messages per session
- Most common questions asked
- Token usage per endpoint
- Identify cost-heavy usage patterns

**Implementation Notes:**
- Log interactions to JSON file or lightweight DB
- Create admin page (password protected)
- Consider disabling expensive features if overused

### 7. Semantic Search (Better than Keyword Search)
**Priority:** LOW
**Effort:** 3+ hours
**Impact:** Better search experience, no API cost

- Implement vector embeddings for transcripts
- Use ChromaDB or FAISS for similarity search
- Replace current keyword search with semantic search
- No OpenAI calls needed for search

**Implementation Notes:**
- Generate embeddings once (offline process)
- Store in vector database
- Query at search time without API calls

### 8. Downloadable Chat History
**Priority:** LOW
**Effort:** 30 minutes
**Impact:** Better UX for researchers

- Export chat conversations as PDF/Markdown
- Include video metadata and timestamps
- Allow sharing conversation links

### 9. Video Timestamp Integration
**Priority:** LOW
**Effort:** 2+ hours
**Impact:** Direct linking to relevant video sections

- Link AI responses to specific transcript timestamps
- Generate YouTube URLs with timestamp (?t=123s)
- Show "Jump to this moment in video" links

### 10. Multi-Language Support
**Priority:** LOW
**Effort:** Variable
**Impact:** Broader accessibility

- Translate interface to Spanish, Chinese, etc.
- Use GPT-4o-mini for query translation
- Keep transcripts in English to avoid re-transcription costs

## Technical Debt & Maintenance

### 11. Error Handling Improvements
- Better error messages for API failures
- Retry logic for transient errors
- Graceful degradation when OpenAI unavailable

### 12. Testing Infrastructure
- Unit tests for search functionality
- Integration tests for OpenAI chat functions
- Mock API responses for testing

### 13. Documentation
- User guide for researchers
- API documentation for chat functions
- Deployment guide for self-hosting

## Cost Estimates After Optimization

**Current (no controls):**
- 1K users, 5 chats each: $10-30/month
- 10K users, 10 chats each: $200-600/month ⚠️

**After implementing rate limiting + optimization:**
- 1K users, 5 chats each: $5-15/month ✅
- 10K users, 10 chats each: $50-150/month ✅

**With caching (50% hit rate):**
- 10K users, 10 chats each: $25-75/month ✅✅

## Recommended Implementation Order for Launch

1. **Before Public Launch (CRITICAL):**
   - [ ] Rate limiting (per-session + global)
   - [ ] OpenAI budget cap in dashboard
   - [ ] Context optimization (reduce token usage)

2. **Week 1 After Launch:**
   - [ ] Usage analytics to understand patterns
   - [ ] Monitor actual costs vs. estimates

3. **If costs are high:**
   - [ ] Add authentication
   - [ ] Implement response caching
   - [ ] Further optimize context windows

4. **Future Enhancements:**
   - [ ] Semantic search
   - [ ] Chat export features
   - [ ] Video timestamp integration
