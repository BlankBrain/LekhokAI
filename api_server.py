from fastapi import FastAPI, Request, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from main_agent import CharacterBasedAgent
import os
import json
import datetime
import logging
import yaml
import sqlite3
from starlette.responses import JSONResponse
from dotenv import load_dotenv, set_key, dotenv_values
from typing import Dict, Any, List
import psutil
import time
from collections import defaultdict
import threading
import signal
import atexit
import multiprocessing
from fastapi import Depends

# Import authentication components
from auth_models import init_auth_db
from auth_middleware import AuthMiddleware, get_current_user, require_auth, require_permission
from auth_routes import auth_router

# Configure multiprocessing to avoid memory leaks
multiprocessing.set_start_method('spawn', force=True)

# Initialize authentication database
init_auth_db()

app = FastAPI(
    title="KarigorAI API",
    description="Enhanced KarigorAI with role-based authentication system",
    version="2.0.0"
)

# Add authentication middleware
app.add_middleware(AuthMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include authentication routes
app.include_router(auth_router)

agent = CharacterBasedAgent()

# Global cleanup registry
cleanup_registry = []

def register_cleanup(cleanup_func):
    """Register cleanup function to be called on shutdown"""
    cleanup_registry.append(cleanup_func)

def cleanup_resources():
    """Clean up all registered resources"""
    for cleanup_func in cleanup_registry:
        try:
            cleanup_func()
        except Exception as e:
            logging.error(f"Error during cleanup: {e}")

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logging.info(f"Received signal {signum}, cleaning up...")
    cleanup_resources()
    os._exit(0)

# Register signal handlers
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

# Register cleanup on normal exit
atexit.register(cleanup_resources)

# Register metrics thread cleanup
def cleanup_metrics_thread():
    """Cleanup metrics collection thread"""
    try:
        # Note: daemon threads will automatically terminate
        pass
    except Exception as e:
        logging.error(f"Error cleaning up metrics thread: {e}")

def cleanup_agent():
    """Cleanup the main agent and its resources"""
    try:
        if hasattr(agent, 'cleanup'):
            agent.cleanup()
    except Exception as e:
        logging.error(f"Error cleaning up agent: {e}")

register_cleanup(cleanup_metrics_thread)
register_cleanup(cleanup_agent)

# --- SQLite History Setup ---
HISTORY_DB = 'history.db'

# --- Analytics & Monitoring Setup ---
analytics_data = {
    "sessions": [],
    "generations": [],
    "errors": [],
    "performance": []
}

# Historical system metrics for graphs (last 5 minutes)
system_metrics_history = []

# CPU tracking variables
# Removed unused _cpu_percent_cache since we now use direct measurement from metrics history

system_metrics = {
    "start_time": time.time(),
    "total_requests": 0,
    "total_errors": 0,
    "total_generations": 0
}

def collect_system_metrics():
    """Collect and store system metrics for historical tracking"""
    # Use interval-based measurement for background collection - this is accurate
    cpu_percent = psutil.cpu_percent(interval=1.0)  # 1 second measurement for accuracy
    memory = psutil.virtual_memory()
    
    timestamp = datetime.datetime.utcnow()
    
    metric = {
        "timestamp": timestamp.isoformat(),
        "cpu_percent": cpu_percent,
        "memory_percent": memory.percent
    }
    
    system_metrics_history.append(metric)
    
    # Keep only last 5 minutes of data (assuming collection every 30 seconds = 10 data points)
    cutoff_time = timestamp - datetime.timedelta(minutes=5)
    system_metrics_history[:] = [
        m for m in system_metrics_history 
        if datetime.datetime.fromisoformat(m["timestamp"]) > cutoff_time
    ]

def get_system_status():
    """Get current system status and metrics"""
    # Get CPU from latest metrics history if available, otherwise use direct measurement
    cpu_percent = 0.0
    
    if system_metrics_history and len(system_metrics_history) > 0:
        latest_metric = system_metrics_history[-1]
        
        metric_time = datetime.datetime.fromisoformat(latest_metric["timestamp"])
        metric_age = (datetime.datetime.utcnow() - metric_time).total_seconds()
        
        # Use historical data if it's less than 90 seconds old
        if metric_age < 90:
            cpu_percent = latest_metric["cpu_percent"]
        else:
            # Fall back to direct measurement if data is stale
            try:
                cpu_percent = psutil.cpu_percent(interval=0.5)
            except Exception as e:
                cpu_percent = 0.0
    else:
        # No history available, use direct measurement
        try:
            cpu_percent = psutil.cpu_percent(interval=0.5)
        except Exception as e:
            cpu_percent = 0.0
    
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    uptime = time.time() - system_metrics["start_time"]
    
    return {
        "system": {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available_gb": memory.available / (1024**3),
            "disk_percent": disk.percent,
            "uptime_seconds": uptime
        },
        "application": {
            "total_requests": system_metrics["total_requests"],
            "total_errors": system_metrics["total_errors"],
            "total_generations": system_metrics["total_generations"],
            "error_rate": system_metrics["total_errors"] / max(system_metrics["total_requests"], 1)
        }
    }

def init_history_db():
    conn = sqlite3.connect(HISTORY_DB)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            story_prompt TEXT NOT NULL,
            character TEXT,
            story TEXT NOT NULL,
            image_prompt TEXT NOT NULL,
            favourite INTEGER DEFAULT 0,
            model_name TEXT,
            input_tokens INTEGER,
            output_tokens INTEGER
        )
    ''')
    
    # Migration: add columns if they don't exist
    c.execute("PRAGMA table_info(history)")
    columns = [row[1] for row in c.fetchall()]
    
    if 'favourite' not in columns:
        c.execute("ALTER TABLE history ADD COLUMN favourite INTEGER DEFAULT 0")
    if 'model_name' not in columns:
        c.execute("ALTER TABLE history ADD COLUMN model_name TEXT")
    if 'input_tokens' not in columns:
        c.execute("ALTER TABLE history ADD COLUMN input_tokens INTEGER")
    if 'output_tokens' not in columns:
        c.execute("ALTER TABLE history ADD COLUMN output_tokens INTEGER")
        
    conn.commit()
    conn.close()

init_history_db()

def get_character_metadata(character_name):
    meta_path = f"character_configs/{character_name}.meta.json"
    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "created_at": None,
        "usage_count": 0,
        "last_used": None
    }

def save_character_metadata(character_name, meta):
    meta_path = f"character_configs/{character_name}.meta.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f)

def ensure_character_metadata():
    config_dir = "character_configs"
    if not os.path.exists(config_dir):
        print(f"[Migration] Directory '{config_dir}' does not exist. Skipping metadata migration.")
        return
    for file in os.listdir(config_dir):
        if file.endswith('.yaml'):
            character_name = file.replace('_config.yaml', '').replace('__config.yaml', '').replace('.yaml', '')
            meta_path = os.path.join(config_dir, f"{character_name}.meta.json")
            if not os.path.exists(meta_path):
                meta = {
                    "created_at": datetime.datetime.utcnow().isoformat(),
                    "usage_count": 0,
                    "last_used": None
                }
                with open(meta_path, "w", encoding="utf-8") as f:
                    json.dump(meta, f)
                print(f"[Migration] Created metadata for character: {character_name}")

# Ensure all characters have metadata on startup
ensure_character_metadata()

# Manual migration script (run this if needed)
if __name__ == "__main__":
    print("Running manual character metadata migration...")
    ensure_character_metadata()
    print("Migration complete.")

@app.get("/characters")
@require_permission("character_view")
def get_characters(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get list of available characters (requires character view permission)"""
    char_names = agent.list_available_characters()
    characters = []
    for name in char_names:
        meta = get_character_metadata(name)
        characters.append({
            "id": name,
            "name": name,
            **meta
        })
    return {"characters": characters}

@app.post("/load_character")
@require_permission("character_view")
async def load_character(request: Request, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Load a character (requires character view permission)"""
    data = await request.json()
    character = data.get("character")
    success = agent.load_character(character)
    return {"success": success}

@app.post("/generate")
@require_permission("story_generate")
async def generate(request: Request, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Generate a story (requires story generation permission)"""
    start_time = time.time()
    try:
        data = await request.json()
        story_prompt = data.get("storyIdea")
        character = data.get("character")
        if character:
            agent.load_character(character)
        story, image_prompt, model_name, input_tokens, output_tokens = agent.generate_story_and_image(story_prompt)
        
        # Update usage metadata
        if character:
            meta = get_character_metadata(character)
            meta["usage_count"] = meta.get("usage_count", 0) + 1
            meta["last_used"] = datetime.datetime.utcnow().isoformat()
            save_character_metadata(character, meta)
            
        # --- Log to history with enhanced tracking including user ---
        conn = sqlite3.connect(HISTORY_DB)
        c = conn.cursor()
        
        # Add user_id column if it doesn't exist
        c.execute("PRAGMA table_info(history)")
        columns = [row[1] for row in c.fetchall()]
        if 'user_id' not in columns:
            c.execute("ALTER TABLE history ADD COLUMN user_id INTEGER")
            conn.commit()
        
        c.execute(
            "INSERT INTO history (timestamp, story_prompt, character, story, image_prompt, model_name, input_tokens, output_tokens, user_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (datetime.datetime.utcnow().isoformat(), story_prompt, character, story, image_prompt, model_name, input_tokens, output_tokens, current_user['id'] if current_user else None)
        )
        conn.commit()
        conn.close()
        
        # Track metrics
        system_metrics["total_generations"] += 1
        response_time = (time.time() - start_time) * 1000
        log_request_metric("/generate", True, response_time)
        
        return {"story": story, "imagePrompt": image_prompt, "modelName": model_name, "inputTokens": input_tokens, "outputTokens": output_tokens}
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        log_request_metric("/generate", False, response_time)
        raise e

@app.get("/history")
@require_permission("story_view_own")
def get_history(sort: str = 'desc', current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get user's story history (requires view own stories permission)"""
    conn = sqlite3.connect(HISTORY_DB)
    c = conn.cursor()
    
    # Add user_id column if it doesn't exist
    c.execute("PRAGMA table_info(history)")
    columns = [row[1] for row in c.fetchall()]
    if 'user_id' not in columns:
        c.execute("ALTER TABLE history ADD COLUMN user_id INTEGER")
        conn.commit()
    
    order_by = "timestamp DESC"
    if sort == 'asc':
        order_by = "timestamp ASC"
    elif sort == 'model':
        order_by = "character ASC, timestamp DESC"
    
    # Filter by user if not super admin
    if current_user and current_user['role'] != 'super_admin':
        c.execute(f"SELECT id, timestamp, story_prompt, character, story, image_prompt, favourite, model_name, input_tokens, output_tokens FROM history WHERE user_id = ? OR user_id IS NULL ORDER BY {order_by}", (current_user['id'],))
    else:
        c.execute(f"SELECT id, timestamp, story_prompt, character, story, image_prompt, favourite, model_name, input_tokens, output_tokens FROM history ORDER BY {order_by}")
    
    rows = c.fetchall()
    conn.close()
    history = [
        {
            "id": row[0],
            "timestamp": row[1],
            "storyPrompt": row[2],
            "character": row[3],
            "story": row[4],
            "imagePrompt": row[5],
            "favourite": bool(row[6]),
            "modelName": row[7],
            "inputTokens": row[8],
            "outputTokens": row[9],
        }
        for row in rows
    ]
    return {"history": history}

@app.post("/history/{history_id}/favourite")
@require_permission("story_edit_own")
def toggle_favourite(history_id: int, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Toggle favourite status of a story (requires edit own stories permission)"""
    conn = sqlite3.connect(HISTORY_DB)
    c = conn.cursor()
    
    # Check ownership or admin privileges
    if current_user['role'] != 'super_admin':
        c.execute("SELECT favourite, user_id FROM history WHERE id = ?", (history_id,))
        row = c.fetchone()
        if not row:
            conn.close()
            raise HTTPException(status_code=404, detail="History record not found")
        if row[1] != current_user['id'] and row[1] is not None:
            conn.close()
            raise HTTPException(status_code=403, detail="Access denied")
    else:
        c.execute("SELECT favourite FROM history WHERE id = ?", (history_id,))
        row = c.fetchone()
        if not row:
            conn.close()
            raise HTTPException(status_code=404, detail="History record not found")
    
    new_fav = 0 if row[0] else 1
    c.execute("UPDATE history SET favourite = ? WHERE id = ?", (new_fav, history_id))
    conn.commit()
    conn.close()
    return {"success": True, "favourite": bool(new_fav)}

@app.get("/favourites")
@require_permission("story_view_own")
def get_favourites(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get user's favourite stories (requires view own stories permission)"""
    conn = sqlite3.connect(HISTORY_DB)
    c = conn.cursor()
    
    # Filter by user if not super admin
    if current_user['role'] != 'super_admin':
        c.execute("SELECT id, timestamp, story_prompt, character, story, image_prompt, favourite, model_name, input_tokens, output_tokens FROM history WHERE favourite = 1 AND (user_id = ? OR user_id IS NULL) ORDER BY timestamp DESC", (current_user['id'],))
    else:
        c.execute("SELECT id, timestamp, story_prompt, character, story, image_prompt, favourite, model_name, input_tokens, output_tokens FROM history WHERE favourite = 1 ORDER BY timestamp DESC")
    
    rows = c.fetchall()
    conn.close()
    favourites = [
        {
            "id": row[0],
            "timestamp": row[1],
            "storyPrompt": row[2],
            "character": row[3],
            "story": row[4],
            "imagePrompt": row[5],
            "favourite": bool(row[6]),
            "modelName": row[7],
            "inputTokens": row[8],
            "outputTokens": row[9],
        }
        for row in rows
    ]
    return {"favourites": favourites}

@app.delete("/history/{history_id}")
@require_permission("story_delete_own")
def delete_history_record(history_id: int, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Delete a story from history (requires delete own stories permission)"""
    conn = sqlite3.connect(HISTORY_DB)
    c = conn.cursor()
    
    # Check ownership or admin privileges
    if current_user['role'] != 'super_admin':
        c.execute("SELECT user_id FROM history WHERE id = ?", (history_id,))
        row = c.fetchone()
        if not row:
            conn.close()
            raise HTTPException(status_code=404, detail="History record not found")
        if row[0] != current_user['id'] and row[0] is not None:
            conn.close()
            raise HTTPException(status_code=403, detail="Access denied")
    else:
        # Check if record exists for admin
        c.execute("SELECT id FROM history WHERE id = ?", (history_id,))
        row = c.fetchone()
        if not row:
            conn.close()
            raise HTTPException(status_code=404, detail="History record not found")
    
    # Delete the record
    c.execute("DELETE FROM history WHERE id = ?", (history_id,))
    conn.commit()
    conn.close()
    return {"success": True, "message": "History record deleted successfully"}

# --- Character Management Endpoints ---
@app.post("/characters")
@require_permission("character_create")
async def add_character(
    character: str = Form(...),
    name: str = Form(...),
    config: str = Form(...),
    persona_file: UploadFile = File(...),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Add a new character (requires character creation permission)"""
    if not character or not name or not config or not persona_file:
        raise HTTPException(status_code=400, detail="Character ID, name, config, and persona file are required")

    # Create character_configs directory if it doesn't exist
    os.makedirs("character_configs", exist_ok=True)
    os.makedirs("personas", exist_ok=True)

    # Always save persona file as personas/{character}.txt
    persona_path = f"personas/{character}.txt"
    try:
        contents = await persona_file.read()
        with open(persona_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save persona file: {str(e)}")

    # Parse and validate YAML, always inject correct persona_file
    try:
        yaml_config = yaml.safe_load(config)
        if not isinstance(yaml_config, dict):
            raise ValueError("Config must be a YAML object")
        yaml_config["persona_file"] = f"{character}.txt"
        config = yaml.dump(yaml_config)
    except Exception as e:
        # Clean up persona file if YAML is invalid
        if os.path.exists(persona_path):
            os.remove(persona_path)
        raise HTTPException(status_code=400, detail=f"Invalid YAML config: {str(e)}")

    # Save character config
    config_path = f"character_configs/{character}.yaml"
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(config)
    except Exception as e:
        # Clean up persona file if config save fails
        if os.path.exists(persona_path):
            os.remove(persona_path)
        raise HTTPException(status_code=500, detail=f"Failed to save character config: {str(e)}")

    # Create metadata with creator info
    meta = {
        "created_at": datetime.datetime.utcnow().isoformat(),
        "created_by": current_user['id'],
        "usage_count": 0,
        "last_used": None
    }
    save_character_metadata(character, meta)
    return {"success": True}

@app.put("/characters/{character_id}")
async def edit_character(character_id: str, request: Request):
    data = await request.json()
    config = data.get("config")
    if not config:
        raise HTTPException(status_code=400, detail="Config required")
    config_path = f"character_configs/{character_id}.yaml"
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(config)
    return {"success": True}

@app.delete("/characters/{character_id}")
async def delete_character(character_id: str):
    config_path = f"character_configs/{character_id}.yaml"
    persona_path = f"personas/{character_id}.txt"
    meta_path = f"character_configs/{character_id}.meta.json"
    
    # Delete all associated files
    for path in [config_path, persona_path, meta_path]:
        if os.path.exists(path):
            os.remove(path)
    
    return {"success": True}

# --- AI Settings Endpoints ---
@app.get("/settings")
def get_settings():
    with open("agent_config.yaml", "r", encoding="utf-8") as f:
        return {"settings": f.read()}

@app.post("/settings")
async def update_settings(request: Request):
    start_time = time.time()
    try:
        data = await request.json()
        settings = data.get("settings")
        if not settings:
            raise HTTPException(status_code=400, detail="Settings required")
        
        # Validate YAML
        try:
            yaml.safe_load(settings)
        except yaml.YAMLError as e:
            raise HTTPException(status_code=400, detail=f"Invalid YAML: {str(e)}")
        
        with open("agent_config.yaml", "w", encoding="utf-8") as f:
            f.write(settings)
        
        response_time = (time.time() - start_time) * 1000
        log_request_metric("/settings", True, response_time)
        return {"success": True}
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        log_request_metric("/settings", False, response_time)
        raise e

@app.get("/settings/safety")
def get_safety_settings():
    """Get safety and content control settings"""
    with open("agent_config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return {"safety": config.get("safety", {})}

@app.post("/settings/safety")
async def update_safety_settings(request: Request):
    """Update safety and content control settings"""
    data = await request.json()
    safety_settings = data.get("safety")
    
    with open("agent_config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    config["safety"] = safety_settings
    
    with open("agent_config.yaml", "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    
    return {"success": True}

@app.get("/settings/performance")
def get_performance_settings():
    """Get performance and reliability settings"""
    with open("agent_config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return {"performance": config.get("performance", {})}

@app.post("/settings/performance")
async def update_performance_settings(request: Request):
    """Update performance and reliability settings"""
    data = await request.json()
    performance_settings = data.get("performance")
    
    with open("agent_config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    config["performance"] = performance_settings
    
    with open("agent_config.yaml", "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    
    return {"success": True}

@app.get("/settings/story-generation")
def get_story_generation_settings():
    """Get story generation preferences"""
    with open("agent_config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return {"story_generation": config.get("story_generation", {})}

@app.post("/settings/story-generation")
async def update_story_generation_settings(request: Request):
    """Update story generation preferences"""
    data = await request.json()
    story_settings = data.get("story_generation")
    
    with open("agent_config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    config["story_generation"] = story_settings
    
    with open("agent_config.yaml", "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    
    return {"success": True}

@app.get("/settings/image-generation")
def get_image_generation_settings():
    """Get image generation controls"""
    with open("agent_config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return {"image_generation": config.get("image_generation", {})}

@app.post("/settings/image-generation")
async def update_image_generation_settings(request: Request):
    """Update image generation controls"""
    data = await request.json()
    image_settings = data.get("image_generation")
    
    with open("agent_config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    config["image_generation"] = image_settings
    
    with open("agent_config.yaml", "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    
    return {"success": True}

@app.get("/settings/system")
def get_system_settings():
    """Get system and monitoring settings"""
    with open("agent_config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return {"system": config.get("system", {})}

@app.post("/settings/system")
async def update_system_settings(request: Request):
    """Update system and monitoring settings"""
    data = await request.json()
    system_settings = data.get("system")
    
    with open("agent_config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    config["system"] = system_settings
    
    with open("agent_config.yaml", "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    
    return {"success": True}

@app.get("/settings/analytics")
def get_analytics_settings():
    """Get analytics dashboard settings"""
    with open("agent_config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return {"analytics": config.get("analytics", {})}

@app.post("/settings/analytics")
async def update_analytics_settings(request: Request):
    """Update analytics dashboard settings"""
    data = await request.json()
    analytics_settings = data.get("analytics")
    
    with open("agent_config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    config["analytics"] = analytics_settings
    
    with open("agent_config.yaml", "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    
    return {"success": True}

@app.get("/settings/developer")
def get_developer_settings():
    """Get developer options"""
    with open("agent_config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return {"developer": config.get("developer", {})}

@app.post("/settings/developer")
async def update_developer_settings(request: Request):
    """Update developer options"""
    data = await request.json()
    developer_settings = data.get("developer")
    
    with open("agent_config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    config["developer"] = developer_settings
    
    with open("agent_config.yaml", "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    
    return {"success": True}

@app.get("/settings/ai")
def get_ai_settings():
    """Get AI settings including image and text generation configuration"""
    try:
        with open('agent_config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        ai_settings = config.get('ai_settings', {})
        return {"ai_settings": ai_settings}
    except Exception as e:
        logging.error(f"Error loading AI settings: {str(e)}")
        return {"ai_settings": {}}

@app.post("/settings/ai")
async def update_ai_settings(request: Request):
    """Update AI settings configuration"""
    try:
        data = await request.json()
        ai_settings = data.get('ai_settings', {})
        
        # Load current config
        with open('agent_config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        # Update AI settings
        config['ai_settings'] = ai_settings
        
        # Save updated config
        with open('agent_config.yaml', 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        logging.info("AI settings updated successfully")
        return {"success": True, "message": "AI settings updated successfully"}
        
    except Exception as e:
        logging.error(f"Error updating AI settings: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update AI settings")

# --- Analytics & Monitoring Endpoints ---
@app.get("/analytics/dashboard")
def get_analytics_dashboard():
    """Get comprehensive analytics dashboard data"""
    
    # Get system status
    status = get_system_status()
    
    # Get recent activity from history
    conn = sqlite3.connect(HISTORY_DB)
    c = conn.cursor()
    
    # Last 24 hours activity
    yesterday = (datetime.datetime.utcnow() - datetime.timedelta(days=1)).isoformat()
    c.execute("SELECT COUNT(*) FROM history WHERE timestamp > ?", (yesterday,))
    recent_generations = c.fetchone()[0]
    
    # Character usage stats
    c.execute("""
        SELECT character, 
               COUNT(*) as usage_count,
               SUM(COALESCE(input_tokens, 0)) as total_input_tokens,
               SUM(COALESCE(output_tokens, 0)) as total_output_tokens
        FROM history 
        WHERE character IS NOT NULL 
        GROUP BY character 
        ORDER BY usage_count DESC 
        LIMIT 10
    """)
    character_usage = [
        {
            "character": row[0], 
            "count": row[1],
            "total_input_tokens": row[2],
            "total_output_tokens": row[3]
        } 
        for row in c.fetchall()
    ]
    
    # Model usage stats
    c.execute("""
        SELECT model_name, COUNT(*) as usage_count, 
               AVG(input_tokens) as avg_input_tokens,
               AVG(output_tokens) as avg_output_tokens
        FROM history 
        WHERE model_name IS NOT NULL 
        GROUP BY model_name 
        ORDER BY usage_count DESC
    """)
    model_usage = [
        {
            "model": row[0], 
            "count": row[1],
            "avg_input_tokens": round(row[2] or 0, 2),
            "avg_output_tokens": round(row[3] or 0, 2)
        } 
        for row in c.fetchall()
    ]
    
    # Daily generation counts for the last week
    c.execute("""
        SELECT DATE(timestamp) as date, COUNT(*) as count
        FROM history 
        WHERE timestamp > datetime('now', '-7 days')
        GROUP BY DATE(timestamp)
        ORDER BY date DESC
    """)
    daily_counts = [{"date": row[0], "count": row[1]} for row in c.fetchall()]
    
    conn.close()
    
    return {
        "system_status": status,
        "recent_activity": {
            "generations_24h": recent_generations,
            "daily_counts": daily_counts
        },
        "usage_statistics": {
            "character_usage": character_usage,
            "model_usage": model_usage
        },
        "performance_metrics": analytics_data["performance"][-50:],  # Last 50 metrics
        "system_metrics_history": system_metrics_history  # Add historical metrics for graphs
    }

@app.get("/analytics/export")
def export_analytics_data(format: str = "json"):
    """Export analytics data in various formats"""
    
    # Get all history data
    conn = sqlite3.connect(HISTORY_DB)
    c = conn.cursor()
    c.execute("SELECT * FROM history ORDER BY timestamp DESC")
    rows = c.fetchall()
    columns = [description[0] for description in c.description]
    conn.close()
    
    data = [dict(zip(columns, row)) for row in rows]
    
    if format == "json":
        return {"data": data, "export_time": datetime.datetime.utcnow().isoformat()}
    else:
        raise HTTPException(status_code=400, detail="Only JSON format is currently supported")

@app.get("/system/status")
def get_system_status_endpoint():
    """Get real-time system status"""
    return get_system_status()

@app.get("/system/health")
def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

# --- Gemini API Key Endpoints ---
@app.get("/api-key")
def get_api_key():
    load_dotenv()
    api_key = os.getenv("GOOGLE_GEMINI_API_KEY", "")
    masked = (api_key[:2] + "****" + api_key[-2:]) if api_key else None
    return {"set": bool(api_key), "masked": masked}

@app.post("/api-key")
async def set_api_key(request: Request):
    data = await request.json()
    api_key = data.get("api_key")
    if not api_key or not isinstance(api_key, str):
        raise HTTPException(status_code=400, detail="API key required")
    
    # Update .env file
    set_key(".env", "GOOGLE_GEMINI_API_KEY", api_key)
    
    # Reinitialize the LLM handler with the new API key
    try:
        success = agent.reinitialize_llm_handler()
        if success:
            return {"success": True, "message": "API key updated and LLM handler reinitialized successfully"}
        else:
            return {"success": False, "error": "Failed to reinitialize LLM handler with new API key"}
    except Exception as e:
        return {"success": False, "error": f"Error updating LLM handler: {str(e)}"}

@app.post("/generate-image")
async def generate_image(request: Request):
    """Generate image from image prompt using configured AI model"""
    start_time = time.time()
    try:
        data = await request.json()
        image_prompt = data.get("imagePrompt", "")
        
        if not image_prompt:
            raise HTTPException(status_code=400, detail="Image prompt is required")
        
        # Load AI settings from config
        with open('agent_config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        ai_settings = config.get('ai_settings', {}).get('image_generation', {})
        quality = ai_settings.get('quality', 'high')
        style = ai_settings.get('style', 'realistic')
        size = ai_settings.get('size', '1024x1024')
        enhance_prompt = ai_settings.get('enhance_prompt', True)
        
        # Enhance prompt if enabled
        if enhance_prompt:
            enhanced_prompt = f"Create a {quality} quality, {style} style image: {image_prompt}. Make it visually appealing and detailed."
        else:
            enhanced_prompt = image_prompt
        
        # Call the image generation function from LLM handler directly
        try:
            # Use the LLM handler's generate_image method which returns ImageGenerationResult
            result = agent.llm_handler.generate_image(enhanced_prompt, quality=quality, size=size)
            
            # Log successful generation
            response_time = (time.time() - start_time) * 1000
            log_request_metric("/generate-image", True, response_time)
            
            return {
                "success": True,
                "image_data": result.image_data,
                "model_used": result.model_name,  # Use actual model name from result
                "prompt_used": result.prompt_used,
                "settings": {
                    "quality": quality,
                    "style": style,
                    "size": size
                },
                "generation_time_ms": result.generation_time_ms
            }
            
        except Exception as e:
            logging.error(f"Image generation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")
            
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        log_request_metric("/generate-image", False, response_time)
        logging.error(f"Error in generate_image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def periodic_metrics_collection():
    """Background thread function to collect metrics every 30 seconds"""
    while True:
        try:
            collect_system_metrics()
            time.sleep(30)  # Collect every 30 seconds
        except Exception as e:
            logging.error(f"Error in periodic metrics collection: {e}")
            time.sleep(30)

def log_request_metric(endpoint: str, success: bool = True, response_time_ms: float = 0):
    """Log request metrics for analytics"""
    system_metrics["total_requests"] += 1
    if not success:
        system_metrics["total_errors"] += 1
    
    metric = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "endpoint": endpoint,
        "success": success,
        "response_time_ms": response_time_ms
    }
    analytics_data["performance"].append(metric)
    
    # Keep only last 1000 metrics
    if len(analytics_data["performance"]) > 1000:
        analytics_data["performance"] = analytics_data["performance"][-1000:]

# Start background metrics collection
metrics_thread = threading.Thread(target=periodic_metrics_collection, daemon=True)
metrics_thread.start() 