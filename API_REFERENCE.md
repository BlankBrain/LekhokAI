# KarigorAI - API Reference

## 🔗 Base Information

**Base URL**: `http://localhost:8000`  
**Content-Type**: `application/json`  
**CORS**: Enabled for `http://localhost:3000`

---

## 🏥 Health & Status Endpoints

### GET `/system/health`
**Description**: Basic health check endpoint  
**Response**: 
```json
{
  "status": "healthy",
  "timestamp": "2025-06-09T04:12:59.266392",
  "version": "1.0.0"
}
```

### GET `/system/status`
**Description**: Detailed system metrics  
**Response**:
```json
{
  "system": {
    "cpu_percent": 25.9,
    "memory_percent": 78.0,
    "memory_available_gb": 2.1,
    "disk_percent": 45.2,
    "uptime_seconds": 3600
  },
  "application": {
    "total_requests": 1250,
    "total_errors": 3,
    "total_generations": 89,
    "error_rate": 0.0024
  }
}
```

---

## ✍️ Story Generation Endpoints

### POST `/generate`
**Description**: Generate story content with character persona  
**Request Body**:
```json
{
  "story_prompt": "A mysterious adventure in an old library",
  "character": "himu"
}
```
**Response**:
```json
{
  "story": "Generated narrative content...",
  "image_prompt": "Visual description for image generation...",
  "model_name": "gemini-1.5-flash",
  "input_tokens": 150,
  "output_tokens": 800
}
```

### POST `/generate-image`
**Description**: Generate image from text prompt  
**Request Body**:
```json
{
  "prompt": "A beautiful sunset over mountains",
  "quality": "high",
  "size": "1024x1024"
}
```
**Response**:
```json
{
  "image_data": "base64_encoded_image_data",
  "model_used": "gemini-imagen-3",
  "prompt_enhanced": "Enhanced prompt with quality descriptors"
}
```

---

## 👥 Character Management Endpoints

### GET `/characters`
**Description**: List all available characters  
**Response**:
```json
{
  "characters": [
    {
      "id": "himu",
      "name": "himu",
      "created_at": "2025-06-03T09:03:37.114506",
      "usage_count": 29,
      "last_used": "2025-06-06T10:12:03.903537"
    }
  ]
}
```

### POST `/characters`
**Description**: Create new character  
**Request**: Form data with file upload
- `character`: Character ID (string)
- `name`: Display name (string)  
- `config`: YAML configuration (string)
- `persona_file`: Persona text file (file upload)

**Response**:
```json
{
  "message": "Character created successfully",
  "character_id": "new_character_id"
}
```

### PUT `/characters/{character_id}`
**Description**: Update existing character  
**Request Body**:
```json
{
  "name": "Updated Name",
  "config": "Updated YAML configuration"
}
```

### DELETE `/characters/{character_id}`
**Description**: Delete character  
**Response**:
```json
{
  "message": "Character deleted successfully"
}
```

### POST `/load_character`
**Description**: Load specific character for generation  
**Request Body**:
```json
{
  "character": "himu"
}
```

---

## 📚 History Management Endpoints

### GET `/history`
**Description**: Fetch story history  
**Query Parameters**:
- `sort`: `desc` (default), `asc`, `character`, `model`

**Response**:
```json
{
  "history": [
    {
      "id": 1,
      "timestamp": "2025-06-09T04:00:00.000000",
      "storyPrompt": "Original user prompt",
      "character": "himu",
      "story": "Generated story content",
      "imagePrompt": "Image generation prompt",
      "favourite": 0,
      "modelName": "gemini-1.5-flash",
      "inputTokens": 150,
      "outputTokens": 800
    }
  ]
}
```

### GET `/favourites`
**Description**: Get only favorite stories  
**Response**: Same format as `/history` but filtered

### POST `/history/{history_id}/favourite`
**Description**: Toggle favorite status of story  
**Response**:
```json
{
  "message": "Favourite status updated",
  "is_favourite": true
}
```

### DELETE `/history/{history_id}`
**Description**: Delete story from history  
**Response**:
```json
{
  "message": "Story deleted successfully"
}
```

---

## 📊 Analytics Endpoints

### GET `/analytics/dashboard`
**Description**: Complete analytics dashboard data  
**Response**:
```json
{
  "system_status": {
    "cpu_percent": 25.9,
    "memory_percent": 78.0,
    "disk_percent": 45.2,
    "uptime_seconds": 3600
  },
  "recent_activity": {
    "last_24h": {
      "generations": 15,
      "requests": 127,
      "errors": 1
    }
  },
  "usage_statistics": {
    "character_usage": {
      "himu": 29,
      "harry potter": 2,
      "test": 5
    },
    "model_usage": {
      "gemini-1.5-flash": {
        "count": 25,
        "avg_input_tokens": 145,
        "avg_output_tokens": 780
      }
    }
  },
  "performance_metrics": {
    "avg_response_time_ms": 850,
    "success_rate": 0.997,
    "endpoint_performance": {
      "/generate": { "avg_time": 1200, "success_rate": 0.995 }
    }
  },
  "system_metrics_history": [
    {
      "timestamp": "2025-06-09T04:00:00.000000",
      "cpu_percent": 24.5,
      "memory_percent": 77.8
    }
  ]
}
```

### GET `/analytics/export`
**Description**: Export analytics data  
**Query Parameters**:
- `format`: `json` (default)

**Response**: Complete analytics dataset as downloadable file

---

## ⚙️ Settings Endpoints

### GET `/settings/{category}`
**Description**: Get configuration for specific category  
**Categories**: `safety`, `performance`, `story-generation`, `image-generation`, `system`, `analytics`, `developer`, `ai`

**Example Response** (`/settings/story-generation`):
```json
{
  "style": {
    "default_length": "medium",
    "genre_preferences": ["fiction", "adventure"],
    "narrative_style": "third_person",
    "dialogue_style": "natural"
  },
  "structure": {
    "include_dialogue": true,
    "include_descriptions": true,
    "chapter_breaks": false
  },
  "creativity": {
    "randomness_level": 0.7,
    "prompt_expansion": true,
    "character_development": "medium"
  }
}
```

### POST `/settings/{category}`
**Description**: Update configuration for specific category  
**Request Body**: JSON object with settings to update

### GET `/settings`
**Description**: Get all settings categories overview  
**Response**:
```json
{
  "categories": [
    "safety",
    "performance", 
    "story-generation",
    "image-generation",
    "system",
    "analytics",
    "developer",
    "ai"
  ]
}
```

---

## 🔑 API Key Management

### GET `/api-key`
**Description**: Get current API key status  
**Response**:
```json
{
  "has_key": true,
  "key_preview": "AIza****VpYY",
  "last_updated": "2025-06-09T04:00:00.000000"
}
```

### POST `/api-key`
**Description**: Set or update API key  
**Request Body**:
```json
{
  "api_key": "your_google_api_key_here"
}
```
**Response**:
```json
{
  "message": "API key updated successfully",
  "key_preview": "your_****_here"
}
```

---

## 🛡️ Error Responses

### Standard Error Format
```json
{
  "error": "Error message description",
  "code": "ERROR_CODE",
  "timestamp": "2025-06-09T04:00:00.000000"
}
```

### Common HTTP Status Codes
- **200**: Success
- **400**: Bad Request (invalid parameters)
- **404**: Not Found (invalid endpoint or resource)
- **422**: Unprocessable Entity (validation error)
- **500**: Internal Server Error

### Example Error Responses

#### 400 Bad Request
```json
{
  "error": "Missing required field: story_prompt",
  "code": "MISSING_FIELD",
  "timestamp": "2025-06-09T04:00:00.000000"
}
```

#### 404 Not Found
```json
{
  "error": "Character not found: invalid_character",
  "code": "CHARACTER_NOT_FOUND", 
  "timestamp": "2025-06-09T04:00:00.000000"
}
```

#### 500 Internal Server Error
```json
{
  "error": "AI service temporarily unavailable",
  "code": "AI_SERVICE_ERROR",
  "timestamp": "2025-06-09T04:00:00.000000"
}
```

---

## 📝 Request Examples

### cURL Examples

#### Generate Story
```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "story_prompt": "A robot discovers emotions",
    "character": "himu"
  }'
```

#### Get Character List
```bash
curl -X GET http://localhost:8000/characters
```

#### Update API Key
```bash
curl -X POST http://localhost:8000/api-key \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "your_api_key_here"
  }'
```

#### Get Analytics Dashboard
```bash
curl -X GET http://localhost:8000/analytics/dashboard
```

### JavaScript Examples

#### Generate Story (Fetch API)
```javascript
const response = await fetch('http://localhost:8000/generate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    story_prompt: 'A detective in a cyberpunk city',
    character: 'himu'
  })
});
const data = await response.json();
console.log(data.story);
```

#### Get System Status
```javascript
const status = await fetch('http://localhost:8000/system/status')
  .then(res => res.json());
console.log(`CPU: ${status.system.cpu_percent}%`);
```

### Python Examples

#### Generate Story (requests)
```python
import requests

response = requests.post('http://localhost:8000/generate', json={
    'story_prompt': 'A magical forest adventure',
    'character': 'himu'
})
data = response.json()
print(data['story'])
```

#### Get Analytics Data
```python
import requests

analytics = requests.get('http://localhost:8000/analytics/dashboard').json()
print(f"Total generations: {analytics['recent_activity']['last_24h']['generations']}")
```

---

## 🔄 WebSocket Endpoints

**Note**: Currently not implemented but planned for future versions:
- Real-time generation progress
- Live system metrics streaming
- Multi-user collaboration

---

## 📊 Rate Limiting

**Current Limits**:
- **Story Generation**: 60 requests/minute per IP
- **Character Management**: 30 requests/minute per IP  
- **Analytics**: 120 requests/minute per IP
- **Settings**: 20 requests/minute per IP

**Headers**:
- `X-RateLimit-Limit`: Maximum requests per window
- `X-RateLimit-Remaining`: Requests remaining in current window
- `X-RateLimit-Reset`: Window reset time (Unix timestamp)

---

## 🔒 Authentication

**Current**: No authentication required (local development)  
**Planned**: JWT-based authentication for production deployment

---

## 📚 SDK & Libraries

### JavaScript SDK (Planned)
```javascript
import KarigorAI from 'karigorai-sdk';

const client = new KarigorAI('http://localhost:8000');
const story = await client.generate({
  prompt: 'A space adventure',
  character: 'himu'
});
```

### Python SDK (Planned)
```python
from karigorai import KarigorAI

client = KarigorAI('http://localhost:8000')
story = client.generate(
    prompt='A mystery novel',
    character='himu'
)
```

---

**API Version**: 1.0.0  
**Last Updated**: June 9, 2025  
**Status**: Production Ready ✅ 