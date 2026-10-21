# Deployment Configuration

## Frontend

Build and serve the `frontend` directory with the hosting provider's static-site service. Set `VITE_API_URL` to the backend origin plus `/api` when the frontend and backend use separate domains, for example `https://api.example.com/api`. For a same-origin deployment, leave it unset so requests use `/api`.

## Backend

Run the Django application from `backend` with `gunicorn config.wsgi:application`. Configure these environment variables in the backend hosting provider:

- `DJANGO_SECRET_KEY`: a unique, randomly generated secret.
- `DEBUG`: `False`.
- `MONGO_URI`: the production MongoDB connection string.
- `GEMINI_API_KEY`: a valid Google AI Studio API key; AI diagnosis and chat return an unavailable response if it is missing.
- `GEMINI_MODEL`: optional; defaults to `gemini-3.6-flash`.
- `GEMINI_FALLBACK_MODEL`: optional; defaults to `gemini-3.5-flash-lite` and is tried if the primary model is unavailable.
- `CORS_ALLOWED_ORIGINS`: comma-separated frontend origins, including the scheme and no trailing slash, when frontend and backend use separate domains.

Keep API keys and secrets in the hosting provider's environment settings. Never commit `.env` files or expose the Gemini key through a `VITE_` variable.

## Verify

After deployment, open `/api/health/` on the backend URL. The response should report `"status": "ok"` and `"mongodb": "connected"`. AI diagnosis and chat also require a valid `GEMINI_API_KEY` in the backend environment.