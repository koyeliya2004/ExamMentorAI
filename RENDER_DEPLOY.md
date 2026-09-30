# Deploy ExamMentorAI on Render

This repository is configured to deploy the existing backend as a Render Web Service without changing the application design.

## One-time setup

1. In Render, choose **New +** → **Blueprint**.
2. Connect the `koyeliya2004/ExamMentorAI` repository.
3. Select the `master` branch.
4. Render reads `render.yaml` and creates the `exammentorai-backend` web service using `backend/Dockerfile`.
5. In the service dashboard, open **Environment** and add your real secret values.

## Required secret

Add this in Render only — never commit it to GitHub:

```text
HF_TOKEN=hf_your_real_hugging_face_token
```

The token is intentionally not stored in this repository. `render.yaml` declares the variable with `sync: false`, which makes Render ask for it securely.

## Deploy behavior

- Root directory: `backend`
- Deployment runtime: Docker
- Dockerfile: `backend/Dockerfile`
- Render supplies a `PORT` environment variable automatically. The server must listen on that value and bind to `0.0.0.0`.

## If Render asks for commands

Use the Blueprint/Docker deployment instead of manually setting Build and Start commands. If you deploy manually, use the Dockerfile in `backend/`.

## Security

- Keep `.env` local and excluded from Git.
- Use Render Environment settings for `HF_TOKEN`.
- Rotate the token immediately if it is ever pasted into GitHub, logs, or chat.
