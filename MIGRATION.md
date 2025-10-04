# Migration Guide: Streamlit to Modern Frontend

This guide explains how to transition from the original Streamlit application to the new modern React frontend.

## What's Changed

### Architecture
- **Old**: Python Streamlit app with direct JSON file access
- **New**: React + TypeScript frontend with Supabase database backend

### Data Storage
- **Old**: Local JSON file (`nber_videos_transcripts.json`)
- **New**: PostgreSQL database on Supabase with structured tables

### Key Benefits
1. **Better Performance**: Database queries are faster than JSON file parsing
2. **Scalability**: Can easily add more videos without performance degradation
3. **Modern UI**: Responsive design with smooth animations
4. **Type Safety**: TypeScript ensures data consistency
5. **Cloud-Ready**: Easy deployment to Vercel, Netlify, or any static hosting

## Setup Instructions

### 1. Database Setup

The database schema has been created and data has been imported. You now have:
- ✅ Videos table with all transcripts
- ✅ Presenters table with affiliations and Google Scholar links
- ✅ Video-presenter relationships
- ✅ Full-text search indexes

### 2. Environment Configuration

**Important**: Add your OpenAI API key to the `.env` file in the `frontend` directory:

```env
VITE_OPENAI_API_KEY=sk-your-key-here
```

The Supabase credentials are already configured.

### 3. Running the Application

**Development mode**:
```bash
cd frontend
npm run dev
```

Access at: `http://localhost:5173`

**Production build**:
```bash
cd frontend
npm run build
npm run preview
```

### 4. Features Comparison

| Feature | Streamlit App | React Frontend |
|---------|--------------|----------------|
| Search videos | ✅ | ✅ |
| Browse transcripts | ✅ | ✅ |
| Chat with single video | ✅ | ✅ |
| Chat with all videos | ✅ | ✅ |
| Presenters directory | ✅ | ✅ |
| Responsive design | ⚠️ Limited | ✅ Full |
| Loading states | ⚠️ Basic | ✅ Enhanced |
| Error handling | ⚠️ Basic | ✅ Comprehensive |
| Animations | ❌ | ✅ |
| Streaming responses | ✅ | ✅ |
| Type safety | ❌ | ✅ TypeScript |

## Data Flow Changes

### Old Flow (Streamlit)
```
User → Streamlit → JSON File → OpenAI API
```

### New Flow (React Frontend)
```
User → React App → Supabase → Display
                 → OpenAI API → Stream Response
```

## API Changes

### Fetching Videos
**Old (Streamlit)**:
```python
with open('nber_videos_transcripts.json', 'r') as f:
    videos = json.load(f)
```

**New (React)**:
```typescript
const videos = await fetchVideosWithPresenters();
```

### Chat Functionality
Both implementations use the same OpenAI API with similar prompts, so chat behavior is consistent.

## Deployment Options

The new frontend can be deployed to:

### Vercel (Recommended)
1. Push code to GitHub
2. Import project to Vercel
3. Add environment variables
4. Deploy

### Netlify
1. Connect GitHub repository
2. Build command: `npm run build`
3. Publish directory: `dist`
4. Add environment variables

### Static Hosting
Build the app and upload the `dist` folder to any static host.

## Maintaining Both Versions

If you want to keep the Streamlit app running alongside the new frontend:

1. The Streamlit app will continue to work with the JSON file
2. The React frontend uses the Supabase database
3. To sync data, re-run the import script when JSON is updated:
   ```bash
   cd frontend
   node import-data.mjs
   ```

## Troubleshooting

### OpenAI API Key Not Working
- Ensure the key is set in `frontend/.env`
- Check the key has the correct format: `sk-...`
- Verify the key is not expired

### Videos Not Loading
- Check Supabase connection in browser console
- Verify environment variables are set correctly
- Ensure data was imported successfully

### Build Errors
- Run `npm install` to ensure dependencies are installed
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`

## Next Steps

1. Add your OpenAI API key to `frontend/.env`
2. Test the application: `cd frontend && npm run dev`
3. Deploy to production hosting
4. Share with users!

## Need Help?

Check the `frontend/README.md` for detailed documentation.
