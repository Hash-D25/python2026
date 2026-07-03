# Simple Social Media App (FastAPI + Streamlit)

A lightweight full-stack social media project where users can sign up, log in, upload images/videos with captions, browse a shared feed, and delete their own posts.

## Live Frontend

Use the deployed Streamlit app here:

**https://hash-d25-python2026-frontend-tajup8.streamlit.app/**

## What This App Does

- User authentication using FastAPI Users + JWT
- Media uploads (image/video) to ImageKit
- Caption support for every post
- Feed view with newest posts first
- Owner-only post deletion
- SQLite storage for users and post metadata

## Tech Stack

- Backend: FastAPI, Uvicorn
- Auth: fastapi-users (JWT bearer strategy)
- Database: SQLite + SQLAlchemy (async) + aiosqlite
- Media storage: ImageKit
- Frontend: Streamlit
- Dependency/runtime manager: uv

## Project Structure

```text
FastAPI-SocialMediaApp/
├── app/
│   ├── app.py         # FastAPI app, routes, and auth router wiring
│   ├── db.py          # SQLAlchemy models + async session setup
│   ├── images.py      # ImageKit client initialization
│   ├── schemas.py     # Pydantic/FastAPI Users schemas
│   └── users.py       # FastAPI Users manager + JWT auth backend
├── frontend.py        # Streamlit frontend
├── main.py            # Local dev entrypoint for backend (uvicorn)
├── pyproject.toml     # Dependencies and project metadata
└── test.db            # SQLite database file (created/used locally)
```

## How It Works

1. Users register/login via auth endpoints.
2. Frontend stores JWT in Streamlit session state.
3. Authenticated uploads go to ImageKit.
4. Backend saves post metadata (URL, file type, caption, owner) in SQLite.
5. Feed endpoint returns all posts with owner flag and user email.
6. Owners can delete their own posts (ImageKit file + DB record).

## API Endpoints (Core)

### Authentication (via FastAPI Users)

- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login (form data: username, password)
- `POST /auth/forgot-password` - Request password reset token
- `POST /auth/verify` - Verify user workflows
- `GET /users/me` - Current authenticated user profile

### App Endpoints

- `POST /upload`
  - Auth required
  - Multipart form fields:
    - `file` (required)
    - `caption` (optional)
  - Uploads media to ImageKit and stores DB metadata

- `GET /feed`
  - Auth required
  - Returns list of posts with:
    - id, user_id, caption, url, file_type, file_name, created_at, is_owner, email

- `DELETE /delete/{post_id}`
  - Auth required
  - Deletes a post only if requester is the owner

## Local Setup

### 1. Clone and enter project

```bash
git clone <your-repo-url>
cd FastAPI-SocialMediaApp
```

### 2. Configure environment variables

Create a `.env` file in project root:

```env
IMAGEKIT_PRIVATE_KEY=your_imagekit_private_key
```

Note: This project currently initializes ImageKit with the private key from environment variables.

### 3. Install dependencies

```bash
uv sync
```

### 4. Run backend

Option A:

```bash
uv run python main.py
```

Option B:

```bash
uv run uvicorn app.app:app --host 0.0.0.0 --port 8000 --reload
```

Backend will be available at:

- API root/docs: http://localhost:8000/docs

### 5. Run Streamlit frontend

Recommended:

```bash
uv run python -m streamlit run frontend.py
```

If `uv run streamlit run frontend.py` fails on Windows with a trampoline/canonicalize path error, using `python -m streamlit` avoids that issue.

Frontend will be available at:

- http://localhost:8501

## Usage Flow

1. Open frontend.
2. Sign up with email/password.
3. Log in.
4. Upload an image or video and add an optional caption.
5. Check feed for your post.
6. Delete your own post using the trash button.

## Configuration Notes

- Database URL is currently set to local SQLite in app code.
- JWT secret is hardcoded in app code for development.
- Streamlit frontend currently targets `http://localhost:8000` backend URLs.

For production, move secrets and URLs to environment variables.

## Deployment Notes

- Frontend can be hosted on Streamlit Community Cloud.
- Backend can be hosted on Render, Railway, Fly.io, Azure, or similar.
- Ensure CORS and backend base URL configuration are set for cross-origin frontend/backend deployments.
- Use a production database (PostgreSQL recommended) instead of local SQLite for scale/reliability.

## Roadmap Ideas

- Like/comment system
- User profiles and avatars
- Pagination / infinite scroll feed
- Search and hashtag support
- Better media transformations and moderation
- CI pipeline and automated tests

## License

Add your preferred license here (MIT, Apache-2.0, etc.).
