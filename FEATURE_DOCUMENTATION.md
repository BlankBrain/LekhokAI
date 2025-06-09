# KarigorAI - Complete Feature Documentation

## 🎯 Application Overview

**KarigorAI** is an advanced AI-powered storytelling platform that combines character-driven narrative generation with intelligent image prompt creation. The application features a modern Next.js frontend and a robust Python FastAPI backend, providing users with an intuitive interface for creative storytelling.

**Current Status**: ✅ **FULLY OPERATIONAL**
- Frontend: http://localhost:3000 (Next.js 15.3.3)
- Backend: http://localhost:8000 (Python FastAPI)
- Database: SQLite (history.db)

---

## 🏠 **1. HOME PAGE - Dashboard Overview**

### **Description**
The homepage serves as the central hub, providing quick access to all features and displaying recent creative work.

### **Features**
- **Hero Section**: AI-powered storytelling introduction
- **Quick Action Cards**: Direct access to main features
- **Recent Creations**: Display of 2 most recent stories
- **Beautiful UI**: Glass morphism design with smooth animations

### **How to Use**
1. **Navigate**: Visit http://localhost:3000
2. **Quick Start**: Click "Start Creating" to go directly to story generation
3. **Explore**: Use action cards to access:
   - Generate Stories (PenTool icon)
   - Characters (Users icon) 
   - History (BookOpen icon)
   - Settings (Settings icon)
4. **Review Recent Work**: Scroll down to see recent creations with copy functionality

### **Key Actions**
- **Start Creating** → Direct to `/generate`
- **Explore Characters** → Direct to `/characters`
- **Browse Stories** → Direct to `/history` 
- **Configure Settings** → Direct to `/settings`

---

## ✍️ **2. STORY GENERATION - Creative Writing Engine**

### **Description**
The core feature for generating AI-powered stories with character personas, supporting both text and image prompt creation.

### **Features**
- **Character-Based Generation**: Select from available characters
- **Custom Prompts**: Write your own story ideas
- **Real-time Generation**: Instant story creation
- **Image Prompts**: Automatic visual prompt generation
- **Model Selection**: Choose between different AI models
- **Copy Functionality**: Easy copying of generated content

### **How to Use**
1. **Access**: Navigate to `/generate` or click "Start Creating"
2. **Select Character**: Choose from dropdown (himu, harry potter, test, etc.)
3. **Enter Prompt**: Write your story idea in the text area
4. **Generate**: Click "Generate Story" button
5. **Review**: Read generated story and image prompt
6. **Copy**: Use copy buttons to save content
7. **Regenerate**: Click again for variations

### **Available Characters**
- **himu** (29 usages) - Most popular character
- **harry potter** (2 usages) - Fantasy character
- **test** - Testing character

### **API Endpoints**
- `POST /generate` - Generate story content
- `GET /characters` - Fetch available characters
- `POST /load_character` - Load specific character

### **Response Format**
```json
{
  "story": "Generated narrative content",
  "image_prompt": "Visual description for image generation",
  "model_name": "gemini-1.5-flash",
  "input_tokens": 150,
  "output_tokens": 800
}
```

---

## 👥 **3. CHARACTER MANAGEMENT - Persona System**

### **Description**
Comprehensive character management system for creating, editing, and managing AI storytelling personas.

### **Features**
- **Character Gallery**: Visual grid of all characters
- **Usage Statistics**: Track character popularity and usage
- **Character Creation**: Add new characters with custom personas
- **Character Editing**: Modify existing character configurations
- **Character Deletion**: Remove unwanted characters
- **Metadata Tracking**: Creation date, usage count, last used

### **How to Use**

#### **Viewing Characters**
1. **Access**: Navigate to `/characters`
2. **Browse**: View character cards with usage statistics
3. **Sort**: Characters display usage count and last used date

#### **Adding New Characters**
1. **Click**: "Add New Character" button
2. **Fill Form**:
   - **Character Name**: Unique identifier
   - **Display Name**: Human-readable name
   - **Configuration**: YAML character settings
   - **Persona File**: Upload text file with character background
3. **Submit**: Save new character

#### **Managing Existing Characters**
1. **Edit**: Click edit button on character card
2. **Delete**: Click delete button (with confirmation)
3. **View Details**: Click character name for usage analytics

### **Character Structure**
Each character requires:
- **Name**: Unique identifier
- **Configuration**: YAML file with settings
- **Persona File**: Text document with character background
- **Metadata**: Automatic tracking of usage statistics

### **API Endpoints**
- `GET /characters` - List all characters
- `POST /characters` - Create new character
- `PUT /characters/{id}` - Update character
- `DELETE /characters/{id}` - Delete character

---

## 📚 **4. HISTORY MANAGEMENT - Story Archive**

### **Description**
Complete story history management with search, filtering, favorites, and organizational tools.

### **Features**
- **Story Archive**: Complete history of generated stories
- **Search Functionality**: Find stories by content or prompt
- **Sorting Options**: Sort by date, character, or favorites
- **Favorites System**: Mark and filter favorite stories
- **Copy Functions**: Easy content copying
- **Bulk Operations**: Multiple story management
- **Detailed Views**: Full story content with metadata

### **How to Use**

#### **Browsing History**
1. **Access**: Navigate to `/history`
2. **View**: Browse stories in chronological order
3. **Search**: Use search bar to find specific content
4. **Filter**: Use dropdown to filter by favorites

#### **Sorting Options**
- **Recent First** (default): Newest stories first
- **Oldest First**: Historical progression
- **By Character**: Group by character used
- **Favorites**: Show only starred stories

#### **Managing Stories**
1. **Favorite**: Click heart icon to mark favorites
2. **Copy**: Use copy buttons for story content
3. **Delete**: Remove unwanted stories (with confirmation)
4. **View Details**: See full metadata including:
   - Generation timestamp
   - Character used
   - Token usage statistics
   - Model information

### **Story Metadata**
Each story record includes:
- **ID**: Unique identifier
- **Timestamp**: Creation date/time
- **Story Prompt**: Original user input
- **Character**: Character persona used
- **Story**: Generated narrative
- **Image Prompt**: Visual description
- **Favorite Status**: User marking
- **Model Info**: AI model and token usage

### **API Endpoints**
- `GET /history` - Fetch story history
- `GET /history?sort=desc` - Sorted history
- `GET /favourites` - Favorite stories only
- `POST /history/{id}/favourite` - Toggle favorite
- `DELETE /history/{id}` - Delete story

---

## 📊 **5. ANALYTICS DASHBOARD - System Monitoring**

### **Description**
Comprehensive analytics and monitoring dashboard providing real-time system metrics, usage statistics, and performance tracking.

### **Features**
- **Real-time System Monitoring**: CPU, memory, disk usage
- **Application Metrics**: Request counts, error rates, generation statistics  
- **Usage Analytics**: Character popularity, model usage patterns
- **Performance Tracking**: Response times, success rates
- **Historical Data**: Time-series metrics and trends
- **Data Export**: JSON export functionality

### **How to Use**

#### **System Status Monitoring**
1. **Access**: Navigate to `/analytics`
2. **View Real-time Metrics**:
   - **CPU Usage**: Current processor utilization
   - **Memory Usage**: RAM consumption
   - **Disk Usage**: Storage utilization
   - **System Uptime**: Server running time

#### **Application Analytics**
- **Total Requests**: All API calls served
- **Stories Generated**: Total narrative creations
- **Error Rate**: System reliability metrics
- **Success Rate**: Generation success percentage

#### **Usage Statistics**
- **Character Rankings**: Most popular personas
- **Model Usage**: AI model preferences and performance
- **Daily Activity**: 7-day usage trends
- **Token Analytics**: Input/output token consumption

#### **Performance Metrics**
- **Response Times**: Average API response latency
- **Endpoint Performance**: Individual API endpoint metrics
- **System Health**: Overall application status

### **Dashboard Sections**
1. **System Status Cards**: Real-time vital signs
2. **Usage Charts**: Visual representation of activity
3. **Performance Metrics**: Response time and reliability data
4. **Export Functions**: Data download capabilities

### **API Endpoints**
- `GET /analytics/dashboard` - Complete dashboard data
- `GET /analytics/export?format=json` - Export analytics
- `GET /system/status` - Real-time system metrics
- `GET /system/health` - Health check

### **Data Export**
- **Format**: JSON
- **Content**: Complete analytics dataset
- **Usage**: Backup, external analysis, reporting

---

## ⚙️ **6. SETTINGS & CONFIGURATION - System Control**

### **Description**
Comprehensive configuration system with 8 major categories for fine-tuning AI behavior, system performance, and user preferences.

### **Configuration Categories**

#### **🛡️ 6.1 Safety & Content Controls**
**Purpose**: Content filtering and moderation settings

**Features**:
- **Content Filtering**: Enable/disable with strict mode
- **Category Controls**: Allow/block content types (fiction, adventure, romance, etc.)
- **Moderation Settings**: Auto-review, flagging thresholds, toxicity detection
- **Compliance**: GDPR mode, data retention, user consent

**How to Configure**:
1. Navigate to `/settings`
2. Expand "Safety & Content Controls"
3. Toggle content filtering options
4. Set allowed/blocked categories
5. Configure moderation thresholds
6. Enable compliance features
7. Save changes

#### **⚡ 6.2 Performance & Reliability**
**Purpose**: System performance optimization

**Features**:
- **Caching**: Enable/disable with TTL and size limits
- **Rate Limiting**: Requests per minute, burst limits
- **Reliability**: Retry attempts, timeouts, fallback models
- **Health Checks**: System monitoring intervals

**Configuration Options**:
- Cache settings (TTL, max size, embedding cache)
- Rate limiting (requests/minute, burst limits)
- Retry logic (max attempts, timeout values)
- Health monitoring (check intervals)

#### **📚 6.3 Story Generation Preferences**
**Purpose**: Creative output customization

**Features**:
- **Style Settings**: Length, genre, narrative style, dialogue
- **Structure**: Dialogue inclusion, descriptions, chapter breaks
- **Creativity**: Randomness levels, prompt expansion, complexity

**Customization Options**:
- Story length (short/medium/long/custom)
- Narrative perspective (first/third person)
- Dialogue style (formal/natural/casual)
- Creativity parameters (randomness 0-1)

#### **🖼️ 6.4 Image Generation Controls**
**Purpose**: Visual content generation settings

**Features**:
- **Quality Settings**: Resolution, style, enhancement
- **Content Filters**: NSFW, violence, copyright filtering
- **Generation Options**: Prompt enhancement, negative prompts

**Configuration**:
- Resolution options (512x512, 1024x1024, 1024x1792)
- Style selection (photorealistic, artistic, cartoon, anime)
- Content filtering (NSFW, violence, brand safety)

#### **🔧 6.5 System & Monitoring**
**Purpose**: Logging and monitoring configuration

**Features**:
- **Logging**: Level selection, file output, rotation
- **Monitoring**: Performance tracking, error tracking
- **Notifications**: Email, Slack, Discord webhook integration

**Setup**:
- Log level (DEBUG/INFO/WARNING/ERROR)
- Monitoring toggles (performance, errors, usage)
- Notification configuration (webhooks, thresholds)

#### **📊 6.6 Analytics Configuration**
**Purpose**: Data collection and reporting settings

**Features**:
- **Data Collection**: Usage analytics, performance metrics
- **Retention**: Data storage periods
- **Privacy**: Anonymization options

#### **⚙️ 6.7 Developer Options**
**Purpose**: Development and debugging tools

**Features**:
- **Debug Settings**: Debug mode, verbose logging, tracing
- **API Settings**: Rate limit bypass, extended timeouts
- **Experimental**: Beta features, advanced options

#### **🤖 6.8 AI Model Configuration**
**Purpose**: AI model and API settings

**Features**:
- **API Key Management**: Set and update API keys
- **Model Selection**: Choose default AI models
- **Generation Parameters**: Temperature, token limits

### **How to Use Settings**
1. **Access**: Navigate to `/settings`
2. **Navigate**: Click on any configuration section
3. **Configure**: Adjust settings using toggles, sliders, dropdowns
4. **Save**: Changes auto-save or use save buttons
5. **Test**: Use test features where available

### **API Endpoints**
- `GET /settings/{category}` - Get category settings
- `POST /settings/{category}` - Update category settings
- `GET /api-key` - Get current API key status
- `POST /api-key` - Update API key

---

## 🖼️ **7. IMAGE GENERATION - Visual Content Creation**

### **Description**
Advanced image generation system that creates visual content based on story prompts and custom descriptions.

### **Features**
- **Multiple AI Models**: Gemini Imagen 3, Pollinations.ai Flux.1-dev
- **Quality Control**: High resolution (1024x1024) output
- **Style Options**: Photorealistic, artistic, cartoon styles
- **Prompt Enhancement**: Automatic prompt optimization
- **Real-time Generation**: Fast image creation

### **How to Use**
1. **Story Integration**: Images automatically generated with stories
2. **Custom Generation**: Use image prompt from story generation
3. **Manual Creation**: Direct API access for custom images
4. **Download**: Save generated images locally

### **Supported Models**
- **Gemini Imagen 3**: High-quality photorealistic images
- **Pollinations.ai Flux.1-dev**: Artistic and creative styles

### **API Endpoints**
- `POST /generate-image` - Generate image from prompt

### **Generation Process**
1. Receive text prompt
2. Enhance prompt with quality descriptors
3. Send to selected AI model
4. Return base64 encoded image
5. Display in frontend

---

## 🔧 **8. SYSTEM HEALTH & MONITORING**

### **Description**
Comprehensive system health monitoring with real-time metrics and performance tracking.

### **Features**
- **Health Checks**: Endpoint availability monitoring
- **System Metrics**: CPU, memory, disk usage tracking
- **Performance Monitoring**: Response time analysis
- **Error Tracking**: Application error logging
- **Background Metrics**: Continuous data collection

### **Monitoring Components**
- **Health Endpoint**: `/system/health` - Basic system status
- **Status Endpoint**: `/system/status` - Detailed metrics
- **Metrics Collection**: Background thread collecting data every 30 seconds
- **Historical Data**: 5-minute rolling window of metrics

### **Key Metrics Tracked**
- **System**: CPU usage, memory utilization, disk space
- **Application**: Request counts, error rates, generation statistics
- **Performance**: Response times, success rates, uptime

---

## 🚀 **Getting Started Guide**

### **Quick Start**
1. **Visit Homepage**: http://localhost:3000
2. **Generate First Story**: Click "Start Creating"
3. **Select Character**: Choose from dropdown (e.g., "himu")
4. **Enter Prompt**: Write a story idea
5. **Generate**: Click "Generate Story"
6. **Explore**: View generated story and image prompt

### **Complete Workflow**
1. **Setup Characters**: Add/configure characters in `/characters`
2. **Configure Settings**: Adjust preferences in `/settings`
3. **Generate Stories**: Create content in `/generate`
4. **Manage History**: Organize stories in `/history`
5. **Monitor System**: Check analytics in `/analytics`

### **Best Practices**
- **Character Development**: Create detailed persona files for better stories
- **Prompt Writing**: Be specific and descriptive for better results
- **Settings Tuning**: Adjust creativity and style settings to match preferences
- **Regular Monitoring**: Check analytics for system health and usage patterns

---

## 🔗 **API Reference Summary**

### **Core Endpoints**
- `GET /` - Health check
- `GET /characters` - List characters
- `POST /generate` - Generate stories
- `GET /history` - Fetch story history
- `GET /analytics/dashboard` - Analytics data
- `GET /settings/{category}` - Configuration

### **System Endpoints**
- `GET /system/health` - System health
- `GET /system/status` - System metrics
- `POST /generate-image` - Image generation

### **Management Endpoints**
- `POST /characters` - Add character
- `POST /history/{id}/favourite` - Toggle favorite
- `DELETE /history/{id}` - Delete story
- `POST /api-key` - Update API key

---

## 📈 **Current Application Status**

### **✅ Fully Operational Features**
- Story Generation with Character Personas
- Character Management System
- Complete History Archive
- Real-time Analytics Dashboard
- Comprehensive Settings System
- Image Generation Capabilities
- System Health Monitoring
- Modern Responsive UI

### **📊 Usage Statistics** (Current Session)
- **Characters Available**: 3 (himu, harry potter, test)
- **Most Popular Character**: himu (29 usages)
- **System Uptime**: Active and responsive
- **Health Status**: All endpoints operational

### **🎯 Key Strengths**
- **Character-Driven Storytelling**: Unique persona-based approach
- **Comprehensive Configuration**: Extensive customization options
- **Real-time Monitoring**: Live system analytics
- **Modern UI/UX**: Beautiful glass morphism design
- **API-First Architecture**: Full REST API access
- **Performance Optimized**: Background metrics collection and caching

---

## 🆘 **Support & Troubleshooting**

### **Common Issues**
1. **Server Not Responding**: Check if both servers are running on ports 3000 and 8000
2. **Generation Fails**: Verify API key configuration in settings
3. **Characters Not Loading**: Check character configuration files
4. **Settings Not Saving**: Ensure proper API connectivity

### **Health Check Commands**
```bash
# Backend health
curl http://localhost:8000/system/health

# Frontend accessibility  
curl http://localhost:3000

# System status
curl http://localhost:8000/system/status
```

### **Restart Commands**
```bash
# Backend restart
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload

# Frontend restart
cd ui && npm run dev
```

---

**KarigorAI** - *Unleashing Creativity Through AI-Powered Storytelling* 🎨✨ 