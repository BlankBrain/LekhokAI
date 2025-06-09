"""
Pytest configuration and shared fixtures for KarigorAI testing.
"""
import pytest
import tempfile
import os
import sqlite3
from fastapi.testclient import TestClient
from unittest.mock import Mock, MagicMock, patch
import yaml

# Import the application modules
from api_server import app
from main_agent import CharacterBasedAgent
from config_loader import ConfigLoader


@pytest.fixture(scope="function")
def temp_db():
    """Create a temporary database for each test function."""
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    
    try:
        # Initialize the test database schema
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Create history table with correct schema
        c.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                story_prompt TEXT,
                character TEXT,
                story TEXT,
                image_prompt TEXT,
                model_name TEXT,
                input_tokens INTEGER DEFAULT 0,
                output_tokens INTEGER DEFAULT 0,
                favourite BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert some test data
        test_data = [
            ('2025-01-01T00:00:00.000Z', 'Test prompt 1', 'himu', 'Test story 1', 'Test image prompt 1', 'gemini-test', 100, 200, False),
            ('2025-01-02T00:00:00.000Z', 'Test prompt 2', 'harry_potter', 'Test story 2', 'Test image prompt 2', 'gemini-test', 150, 250, True),
        ]
        
        c.executemany(
            "INSERT INTO history (timestamp, story_prompt, character, story, image_prompt, model_name, input_tokens, output_tokens, favourite) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            test_data
        )
        
        conn.commit()
        conn.close()
        
        yield db_path
    finally:
        os.close(db_fd)
        os.unlink(db_path)


@pytest.fixture
def client(temp_db):
    """Create a test client with mocked database."""
    with patch('api_server.HISTORY_DB', temp_db):
        with TestClient(app) as test_client:
            yield test_client


@pytest.fixture
def test_config():
    """Create test configuration."""
    return {
        'model_name': 'gemini-test',
        'llm': {
            'temperature': 0.7,
            'top_p': 0.95,
            'top_k': 40
        },
        'max_output_tokens': 1000,
        'safety': {
            'harassment_threshold': 'BLOCK_MEDIUM_AND_ABOVE',
            'hate_speech_threshold': 'BLOCK_MEDIUM_AND_ABOVE',
            'sexually_explicit_threshold': 'BLOCK_MEDIUM_AND_ABOVE',
            'dangerous_content_threshold': 'BLOCK_MEDIUM_AND_ABOVE'
        }
    }


@pytest.fixture
def mock_config_loader(test_config, tmp_path):
    """Mock ConfigLoader with test configuration."""
    mock_loader = Mock(spec=ConfigLoader)
    mock_loader.get_config.side_effect = lambda key, default=None: test_config.get(key, default)
    mock_loader.load_main_config.return_value = True
    mock_loader.load_character_config.return_value = True
    mock_loader.get_available_characters.return_value = ['test_character', 'himu']
    return mock_loader


@pytest.fixture
def sample_character_config():
    """Sample character configuration for testing."""
    return {
        'name': 'test_character',
        'persona_file': 'test.txt',
        'model_settings': {
            'temperature': 0.7
        }
    }


@pytest.fixture
def sample_persona_content():
    """Sample persona content for testing."""
    return """
    This is a test character persona.
    The character is friendly and helpful.
    They enjoy storytelling and creativity.
    
    Writing style:
    - Uses simple, clear language
    - Includes descriptive details
    - Maintains positive tone
    """


@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing."""
    class MockResponse:
        def __init__(self):
            self.text = "This is a test story.\n\nগল্পের জন্য ইমেজ জেনারেশন প্রম্পট (অতি বিস্তারিত): A beautiful landscape with mountains and trees."
            self.parts = ["test"]
            self.usage_metadata = Mock()
            self.usage_metadata.prompt_token_count = 100
            self.usage_metadata.candidates_token_count = 200
    
    return MockResponse()


@pytest.fixture
def mock_gemini_api(monkeypatch, mock_llm_response):
    """Mock Google Gemini API calls."""
    mock_model = Mock()
    mock_model.generate_content.return_value = mock_llm_response
    
    mock_generative_model = Mock(return_value=mock_model)
    monkeypatch.setattr("google.generativeai.GenerativeModel", mock_generative_model)
    monkeypatch.setattr("google.generativeai.configure", Mock())
    
    return mock_model


@pytest.fixture
def mock_character_agent(mock_config_loader):
    """Mock CharacterBasedAgent for testing."""
    agent = Mock(spec=CharacterBasedAgent)
    agent.config_loader = mock_config_loader
    agent.current_character = 'test_character'
    agent.current_persona_chunks = ['test chunk 1', 'test chunk 2']
    agent.current_persona_embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
    
    # Mock methods
    agent.list_available_characters.return_value = ['test_character', 'himu']
    agent.load_character.return_value = True
    agent.generate_story_and_image.return_value = (
        "Test generated story",
        "Test image prompt", 
        "gemini-test",
        100,
        200
    )
    
    return agent


@pytest.fixture
def test_story_data():
    """Sample story data for testing."""
    return {
        'story_prompt': 'A mysterious adventure in an old library',
        'character': 'test_character',
        'generated_story': 'This is a test story about a library adventure.',
        'image_prompt': 'An old library with mysterious books and dim lighting.',
        'model_name': 'gemini-test',
        'input_tokens': 150,
        'output_tokens': 300
    }


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch, tmp_path):
    """Set up test environment variables and paths."""
    # Set test environment variables
    monkeypatch.setenv("GOOGLE_GEMINI_API_KEY", "test_api_key")
    
    # Create test directories
    test_characters_dir = tmp_path / "character_configs"
    test_personas_dir = tmp_path / "personas"
    test_characters_dir.mkdir()
    test_personas_dir.mkdir()
    
    # Mock file paths
    monkeypatch.setattr("api_server.HISTORY_DB", str(tmp_path / "test_history.db"))
    
    return {
        'characters_dir': test_characters_dir,
        'personas_dir': test_personas_dir,
        'tmp_path': tmp_path
    }


@pytest.fixture
def mock_image_generation():
    """Mock image generation response."""
    return {
        'image_data': 'base64_encoded_test_image_data',
        'model_used': 'gemini-imagen-test',
        'prompt_used': 'Enhanced test prompt',
        'generation_time_ms': 2500.0
    }


# Test data constants
TEST_CHARACTERS = {
    'test_character': {
        'name': 'Test Character',
        'persona_file': 'test.txt',
        'created_at': '2025-01-01T00:00:00.000Z',
        'usage_count': 5,
        'last_used': '2025-01-02T00:00:00.000Z'
    },
    'himu': {
        'name': 'Himu',
        'persona_file': 'himu.txt',
        'created_at': '2024-12-01T00:00:00.000Z',
        'usage_count': 29,
        'last_used': '2025-01-01T00:00:00.000Z'
    }
}

TEST_STORY_HISTORY = [
    {
        'id': 1,
        'timestamp': '2025-01-01T00:00:00.000Z',
        'story_prompt': 'A story about adventure',
        'character': 'test_character',
        'story': 'Once upon a time...',
        'image_prompt': 'A beautiful adventure scene',
        'favourite': 0,
        'model_name': 'gemini-test',
        'input_tokens': 100,
        'output_tokens': 200
    },
    {
        'id': 2,
        'timestamp': '2025-01-02T00:00:00.000Z',
        'story_prompt': 'A mystery story',
        'character': 'himu',
        'story': 'The mystery began...',
        'image_prompt': 'A mysterious dark scene',
        'favourite': 1,
        'model_name': 'gemini-test',
        'input_tokens': 150,
        'output_tokens': 250
    }
]

@pytest.fixture
def mock_config_loader():
    """Mock the config loader."""
    mock_loader = Mock()
    mock_loader.load_config.return_value = {
        "story_generation": {
            "temperature": 0.7,
            "max_tokens": 1000
        }
    }
    return mock_loader

@pytest.fixture
def mock_llm_handler():
    """Mock the LLM handler."""
    mock_handler = Mock()
    mock_handler.generate_story_and_image.return_value = (
        "Generated test story",
        "Test image prompt", 
        "gemini-test",
        100,
        200
    )
    mock_handler.generate_image.return_value = "data:image/jpeg;base64,/9j/test"
    return mock_handler

@pytest.fixture
def mock_character_agent():
    """Mock the character agent."""
    mock_agent = Mock()
    mock_agent.generate_story_and_image.return_value = (
        "Generated test story",
        "Test image prompt",
        "gemini-test", 
        100,
        200
    )
    mock_agent.load_character.return_value = True
    mock_agent.list_available_characters.return_value = [
        {"id": "himu", "name": "Himu"},
        {"id": "harry_potter", "name": "Harry Potter"},
        {"id": "test", "name": "Test Character"}
    ]
    return mock_agent

@pytest.fixture
def sample_characters():
    """Sample character data for testing."""
    return {
        "characters": [
            {"id": "himu", "name": "Himu", "usage_count": 29, "created_at": "2025-01-01T00:00:00.000Z"},
            {"id": "harry_potter", "name": "Harry Potter", "usage_count": 2, "created_at": "2025-01-01T00:00:00.000Z"},
            {"id": "test", "name": "Test Character", "usage_count": 5, "created_at": "2025-01-01T00:00:00.000Z"}
        ]
    }

@pytest.fixture
def sample_story_response():
    """Sample story generation response."""
    return {
        "story": "Once upon a time, there was a magical adventure...",
        "image_prompt": "A magical landscape with mountains",
        "model_name": "gemini-test",
        "input_tokens": 150,
        "output_tokens": 300
    }

@pytest.fixture
def sample_history():
    """Sample history data for testing."""
    return [
        {
            "id": 1,
            "timestamp": "2025-01-01T00:00:00.000Z",
            "story_prompt": "Test prompt 1",
            "character": "himu",
            "story": "Test story 1",
            "image_prompt": "Test image prompt 1",
            "model_name": "gemini-test",
            "input_tokens": 100,
            "output_tokens": 200,
            "favourite": False
        },
        {
            "id": 2, 
            "timestamp": "2025-01-02T00:00:00.000Z",
            "story_prompt": "Test prompt 2", 
            "character": "harry_potter",
            "story": "Test story 2",
            "image_prompt": "Test image prompt 2",
            "model_name": "gemini-test",
            "input_tokens": 150,
            "output_tokens": 250,
            "favourite": True
        }
    ]

@pytest.fixture
def mock_environment():
    """Mock environment variables for testing."""
    env_vars = {
        'GOOGLE_API_KEY': 'test_api_key_12345',
        'MODEL_NAME': 'gemini-test'
    }
    with patch.dict(os.environ, env_vars):
        yield env_vars

@pytest.fixture  
def mock_no_api_key():
    """Mock environment with no API key set."""
    with patch.dict(os.environ, {}, clear=True):
        yield

@pytest.fixture
def mock_characters_directory(tmp_path):
    """Create a temporary characters directory with test files."""
    characters_dir = tmp_path / "characters"
    characters_dir.mkdir()
    
    # Create test character files
    himu_file = characters_dir / "himu.txt"
    himu_file.write_text("Himu is a fictional character...")
    
    harry_file = characters_dir / "harry_potter.txt"  
    harry_file.write_text("Harry Potter is a wizard...")
    
    test_file = characters_dir / "test.txt"
    test_file.write_text("Test character description...")
    
    with patch('api_server.CHARACTERS_DIR', str(characters_dir)):
        yield str(characters_dir)

@pytest.fixture
def mock_system_status():
    """Mock system status for analytics tests."""
    return {
        "system": {
            "cpu_percent": 25.0,
            "memory_percent": 75.0,
            "disk_usage": 50.0
        },
        "application": {
            "total_requests": 100,
            "total_errors": 1,
            "uptime": 3600
        }
    }

def insert_test_history(db_path, records):
    """Helper function to insert test history records."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    for record in records:
        c.execute(
            "INSERT INTO history (timestamp, story_prompt, character, story, image_prompt, model_name, input_tokens, output_tokens, favourite) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            record
        )
    
    conn.commit()
    conn.close()

def get_test_history_count(db_path):
    """Helper function to get history record count."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM history")
    count = c.fetchone()[0]
    conn.close()
    return count 