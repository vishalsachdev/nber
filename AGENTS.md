# Repository Guidelines

## Project Structure & Module Organization
- Root: project config (`vercel.json`), environment samples (`.env.example`), data (`articles/`, `nber_videos_transcripts.json`), utilities (`scripts/`, `src/`), and platform folders (`supabase/`).
- Frontend app (Vite + React + TS): `frontend/`
  - Entry and components: `frontend/src/` (e.g., `main.tsx`, `components/`)
  - Static assets: `frontend/public/`
  - API helpers: `frontend/api/`
  - Build output: `frontend/dist/` (configured via root `vercel.json`).

## Build, Test, and Development Commands
- Dev server: `cd frontend && npm install && npm run dev` — runs Vite locally.
- Build: `cd frontend && npm run build` — type-checks and builds to `frontend/dist/`.
- Preview: `cd frontend && npm run preview` — serves the built app.
- Lint: `cd frontend && npm run lint` — runs ESLint.
- Deployment: Vercel uses root `vercel.json` to build from `frontend/`. Clear cache on config changes.

## Coding Style & Naming Conventions
- Language: TypeScript + React, 2-space indentation.
- Components/files: PascalCase for React components (e.g., `SearchBrowse.tsx`), camelCase for utilities, `.css` co-located (e.g., `App.css`).
- Prefer small, focused components; keep props typed with explicit interfaces.
- Use ESLint defaults in `frontend/eslint.config.js`. Avoid unused exports and implicit `any`.

## Testing Guidelines
- No formal test suite yet. If adding tests, place them under `frontend/src/__tests__/` and prefer Vitest + React Testing Library.
- Name tests `<File>.test.tsx` and keep tests fast and deterministic.

## Commit & Pull Request Guidelines
- Use Conventional Commits (e.g., `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`). Scope is encouraged (e.g., `feat(analytics): ...`).
- PRs should include:
  - Clear description and rationale; link related issues.
  - Screenshots/GIFs for UI changes.
  - Check build passes (`npm run build`) and lint is clean.

## Security & Configuration Tips
- Do not commit secrets. Example envs go in `.env.example`; local-only values in `frontend/.env`.
- Vercel Analytics is enabled via `inject()` in `frontend/src/main.tsx`. Enable “Web Analytics” in Vercel to view data.
- Root `vercel.json` ensures the correct build from `frontend/`; do not duplicate conflicting configs.

