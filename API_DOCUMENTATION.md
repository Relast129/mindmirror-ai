# 📡 MindMirror AI - API Documentation

Complete API reference for MindMirror AI backend services.

**Base URL:** `http://localhost:8000` (development) or `https://your-api.onrender.com` (production)

---

## 🔐 Authentication

All protected endpoints require a Bearer token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

---

## 📚 API Endpoints

### Health & Status

#### `GET /`
Root endpoint - API information

**Response:**
```json
{
  "message": "🧠 Welcome to MindMirror AI",
  "status": "healthy",
  "version": "1.0.0",
  "description": "Privacy-first emotional reflection dashboard"
}
```

#### `GET /health`
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "service": "MindMirror AI",
  "ai_models": "ready"
}
```

---

## 🔑 Authentication Endpoints

### `POST /auth/google`
Authenticate user with Google OAuth token

**Request Body:**
```json
{
  "token": "google-oauth-access-token"
}
```

**Response:**
```json
{
  "user_id": "123456789",
  "email": "user@example.com",
  "name": "John Doe",
  "picture": "https://...",
  "access_token": "jwt-token-here"
}
```

**Status Codes:**
- `200` - Success
- `401` - Invalid token
- `500` - Server error

---

### `GET /auth/me`
Get current authenticated user information

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Response:**
```json
{
  "user_id": "123456789",
  "email": "user@example.com",
  "name": "John Doe",
  "picture": "https://..."
}
```

**Status Codes:**
- `200` - Success
- `401` - Unauthorized

---

### `POST /auth/logout`
Logout current user

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Response:**
```json
{
  "message": "Successfully logged out"
}
```

---

## 📤 Upload Endpoints

### `POST /upload/text`
Upload text journal entry

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Query Parameters:**
- `google_token` (required): Google OAuth access token

**Request Body:**
```json
{
  "content": "I'm feeling happy today...",
  "title": "Great Day",
  "tags": ["happy", "productive"]
}
```

**Response:**
```json
{
  "success": true,
  "file_id": "google-drive-file-id",
  "file_name": "journal_20231104_120000.json",
  "message": "Text journal saved successfully"
}
```

**Status Codes:**
- `200` - Success
- `401` - Unauthorized
- `500` - Server error

---

### `POST /upload/voice`
Upload voice recording

**Headers:**
```
Authorization: Bearer <jwt-token>
Content-Type: multipart/form-data
```

**Form Data:**
- `file` (required): Audio file (mp3, wav, m4a, ogg, webm)
- `google_token` (required): Google OAuth access token

**Response:**
```json
{
  "success": true,
  "file_id": "google-drive-file-id",
  "file_name": "voice_20231104_120000.webm",
  "message": "Voice note saved and transcribed successfully",
  "transcription": "I'm feeling anxious about tomorrow..."
}
```

**Status Codes:**
- `200` - Success
- `413` - File too large (max 10MB)
- `415` - Unsupported file type
- `500` - Server error

---

### `POST /upload/image`
Upload image or drawing

**Headers:**
```
Authorization: Bearer <jwt-token>
Content-Type: multipart/form-data
```

**Form Data:**
- `file` (required): Image file (jpg, png, gif, webp, bmp)
- `google_token` (required): Google OAuth access token
- `caption` (optional): Image caption

**Response:**
```json
{
  "success": true,
  "file_id": "google-drive-file-id",
  "file_name": "image_20231104_120000.jpg",
  "message": "Image saved successfully"
}
```

**Status Codes:**
- `200` - Success
- `413` - File too large (max 10MB)
- `415` - Unsupported file type
- `500` - Server error

---

### `POST /upload/video`
Upload video clip

**Headers:**
```
Authorization: Bearer <jwt-token>
Content-Type: multipart/form-data
```

**Form Data:**
- `file` (required): Video file (mp4, mov, avi, webm)
- `google_token` (required): Google OAuth access token
- `caption` (optional): Video caption

**Response:**
```json
{
  "success": true,
  "file_id": "google-drive-file-id",
  "file_name": "video_20231104_120000.mp4",
  "message": "Video saved successfully",
  "transcription": "Audio transcription if available"
}
```

**Status Codes:**
- `200` - Success
- `413` - File too large (max 50MB)
- `415` - Unsupported file type
- `500` - Server error

---

## 🧠 Reflection Endpoints

### `POST /reflect/`
Generate AI-powered emotional reflection

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Query Parameters:**
- `google_token` (required): Google OAuth access token

**Request Body:**
```json
{
  "content": "I'm feeling overwhelmed with work...",
  "content_type": "text",
  "generate_art": true,
  "generate_voice": false
}
```

**Response:**
```json
{
  "reflection_id": "reflection_20231104_120000",
  "emotion": "sadness",
  "emotion_confidence": 0.87,
  "emotion_summary": "You're experiencing sadness...",
  "reflection_text": "I hear the weight in your words...",
  "poem": "Tears fall like gentle rain...",
  "advice": "Be gentle with yourself...",
  "art_base64": "base64-encoded-image-data",
  "voice_base64": null,
  "color": "#4169E1",
  "emoji": "😢",
  "timestamp": "2023-11-04T12:00:00"
}
```

**Status Codes:**
- `200` - Success
- `401` - Unauthorized
- `500` - Server error

---

### `GET /reflect/{reflection_id}`
Retrieve specific reflection by ID

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Query Parameters:**
- `google_token` (required): Google OAuth access token

**Response:**
```json
{
  "reflection_id": "reflection_20231104_120000",
  "user_id": "123456789",
  "timestamp": "2023-11-04T12:00:00",
  "original_content": "I'm feeling overwhelmed...",
  "emotion": { ... },
  "reflection": { ... }
}
```

**Status Codes:**
- `200` - Success
- `404` - Reflection not found
- `500` - Server error

---

### `POST /reflect/quick`
Quick emotion detection without full reflection

**Headers:**
```
Authorization: Bearer <jwt-token>
Content-Type: multipart/form-data
```

**Form Data:**
- `content` (required): Text to analyze

**Response:**
```json
{
  "emotion": "joy",
  "confidence": 0.92,
  "summary": "You're feeling joyful and positive! 😊",
  "color": "#FFD700",
  "emoji": "😊",
  "all_emotions": [
    {"label": "joy", "score": 0.92},
    {"label": "love", "score": 0.05}
  ]
}
```

**Status Codes:**
- `200` - Success
- `401` - Unauthorized
- `500` - Server error

---

## 📊 History Endpoints

### `GET /history/moods`
Get mood timeline

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Query Parameters:**
- `google_token` (required): Google OAuth access token
- `days` (optional): Number of days to retrieve (default: 30, max: 365)

**Response:**
```json
[
  {
    "timestamp": "2023-11-04T12:00:00",
    "emotion": "joy",
    "confidence": 0.92,
    "reflection_id": "reflection_20231104_120000",
    "content_preview": "I'm feeling happy today..."
  }
]
```

**Status Codes:**
- `200` - Success
- `401` - Unauthorized
- `500` - Server error

---

### `GET /history/gallery`
Get emotional gallery items

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Query Parameters:**
- `google_token` (required): Google OAuth access token
- `limit` (optional): Maximum items to return (default: 50, max: 200)

**Response:**
```json
[
  {
    "id": "file-id",
    "type": "art",
    "timestamp": "2023-11-04T12:00:00",
    "emotion": "joy",
    "preview_url": "https://drive.google.com/...",
    "thumbnail": "https://..."
  }
]
```

**Status Codes:**
- `200` - Success
- `401` - Unauthorized
- `500` - Server error

---

### `GET /history/stats`
Get user statistics

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Query Parameters:**
- `google_token` (required): Google OAuth access token

**Response:**
```json
{
  "total_entries": 45,
  "total_reflections": 42,
  "current_streak": 7,
  "longest_streak": 14,
  "most_common_emotion": "joy",
  "emotion_distribution": {
    "joy": 20,
    "sadness": 10,
    "neutral": 15
  },
  "entries_by_type": {
    "text": 30,
    "voice": 8,
    "image": 5,
    "video": 2
  },
  "last_entry_date": "2023-11-04"
}
```

**Status Codes:**
- `200` - Success
- `401` - Unauthorized
- `500` - Server error

---

### `GET /history/export`
Export all user data

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Query Parameters:**
- `google_token` (required): Google OAuth access token

**Response:**
```json
{
  "user_id": "123456789",
  "email": "user@example.com",
  "export_date": "2023-11-04T12:00:00",
  "statistics": { ... },
  "mood_timeline": [ ... ],
  "gallery": [ ... ]
}
```

**Status Codes:**
- `200` - Success
- `401` - Unauthorized
- `500` - Server error

---

## 🎨 Emotion Types

Supported emotions:
- `joy` - Happy, excited, positive
- `sadness` - Sad, down, melancholic
- `anger` - Angry, frustrated, annoyed
- `fear` - Anxious, worried, scared
- `love` - Loving, affectionate, caring
- `surprise` - Surprised, amazed, shocked
- `neutral` - Calm, balanced, centered

---

## 🎨 Emotion Colors

Each emotion has an associated color:
- `joy`: `#FFD700` (Gold)
- `sadness`: `#4169E1` (Royal Blue)
- `anger`: `#DC143C` (Crimson)
- `fear`: `#9370DB` (Medium Purple)
- `love`: `#FF69B4` (Hot Pink)
- `surprise`: `#FF8C00` (Dark Orange)
- `neutral`: `#808080` (Gray)

---

## ⚠️ Error Responses

All errors follow this format:

```json
{
  "error": "Error message",
  "status_code": 400
}
```

**Common Status Codes:**
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `413` - Payload Too Large
- `415` - Unsupported Media Type
- `429` - Too Many Requests
- `500` - Internal Server Error

---

## 🔄 Rate Limiting

**Free Tier Limits:**
- 100 requests per minute per user
- 1000 requests per hour per user

**Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1699104000
```

---

## 📝 Example Usage

### Python Example

```python
import requests

# Authenticate
response = requests.post(
    "http://localhost:8000/auth/google",
    json={"token": "google-oauth-token"}
)
data = response.json()
jwt_token = data["access_token"]
google_token = "google-oauth-token"

# Generate reflection
response = requests.post(
    "http://localhost:8000/reflect/",
    headers={"Authorization": f"Bearer {jwt_token}"},
    params={"google_token": google_token},
    json={
        "content": "I'm feeling great today!",
        "content_type": "text",
        "generate_art": True,
        "generate_voice": False
    }
)
reflection = response.json()
print(f"Emotion: {reflection['emotion']}")
```

### JavaScript Example

```javascript
// Authenticate
const authResponse = await fetch('http://localhost:8000/auth/google', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ token: googleOAuthToken })
});
const { access_token, ...user } = await authResponse.json();

// Generate reflection
const reflectionResponse = await fetch(
  `http://localhost:8000/reflect/?google_token=${googleToken}`,
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${access_token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      content: "I'm feeling great today!",
      content_type: "text",
      generate_art: true,
      generate_voice: false
    })
  }
);
const reflection = await reflectionResponse.json();
console.log(`Emotion: ${reflection.emotion}`);
```

---

## 🔒 Security Notes

1. **Never expose JWT tokens** in client-side code
2. **Always use HTTPS** in production
3. **Validate all inputs** before sending to API
4. **Store tokens securely** (httpOnly cookies recommended)
5. **Implement CSRF protection** for state-changing operations

---

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Google Drive API](https://developers.google.com/drive/api)
- [Hugging Face Inference API](https://huggingface.co/docs/api-inference)

---

**API Version:** 1.0.0  
**Last Updated:** November 2023
