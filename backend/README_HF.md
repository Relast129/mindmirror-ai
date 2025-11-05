---
title: MindMirror AI
emoji: 🧠
colorFrom: purple
colorTo: blue
sdk: gradio
sdk_version: 4.0.0
app_file: app_hf.py
pinned: false
license: mit
---

# 🧠 MindMirror AI - Backend API

Privacy-first emotional reflection dashboard with multi-modal input.

## Features

- 🔐 Google OAuth authentication
- 💾 Google Drive storage (your data stays in YOUR Drive)
- 🎤 Multi-modal input (text, voice, image, video)
- 🤖 AI-powered emotion detection
- ✨ Personalized reflections and insights
- 📊 Mood tracking and analytics

## API Endpoints

- `POST /api/login` - OAuth login
- `POST /api/submit` - Submit journal entry
- `GET /api/history` - Get entry history
- `GET /api/download` - Download file
- `POST /api/feedback` - Add feedback
- `GET /callback` - OAuth callback handler

## Privacy

All your data is stored only in your Google Drive. We do not retain or access your files.

## Frontend

The React frontend is deployed separately on Vercel.

## License

MIT
