# KarigorAI Testing Documentation

## 📋 Overview

This documentation provides comprehensive guidance for testing the KarigorAI project, a Python FastAPI backend with Next.js frontend, featuring Google Gemini AI integration and SQLite database. Our testing strategy achieves **97.8% test success rate** with robust coverage across all major components.

## 🎯 Current Test Status

- **✅ 91/93 tests PASSING (97.8% success rate)**
- **⏭️ 2 tests SKIPPED** (unimplemented endpoints)
- **❌ 0 tests FAILED**

## 🏗️ Test Architecture

### Directory Structure

```
tests/
├── unit/
│   ├── test_api_server.py     # API endpoint tests
│   ├── test_llm_handler.py    # LLM service tests
│   └── test_main_agent.py     # Main agent logic tests
├── integration/               # Integration tests (future)
├── conftest.py               # Pytest configuration and fixtures
└── requirements-test.txt     # Testing dependencies
```

### Test Categories

#### 1. **API Server Tests** (`test_api_server.py`)
- **Health Endpoints**: System health and status checks
- **Story Generation**: AI story creation workflows
- **Character Management**: Character loading, creation, deletion
- **History Management**: Story history, favorites, sorting
- **Analytics**: Dashboard metrics and export functionality
- **Settings Management**: Configuration updates
- **API Key Management**: Authentication handling
- **Image Generation**: AI image creation services
- **Database Functions**: SQLite operations
- **System Metrics**: Performance monitoring

#### 2. **LLM Handler Tests** (`test_llm_handler.py`)
- **Initialization**: API key handling, model configuration
- **Story Generation**: Google Gemini integration
- **Image Generation**: Multiple image service providers
- **Utility Methods**: Token counting, text processing
- **Error Handling**: Network failures, API limits
- **Configuration Management**: Model settings
- **Integration Workflows**: End-to-end AI workflows

#### 3. **Main Agent Tests** (`test_main_agent.py`)
- **Agent Initialization**: Character-based agent setup
- **Story Generation**: Complete story workflows
- **Character Processing**: Persona management
- **Retrieval Integration**: Context retrieval systems
- **Error Scenarios**: Graceful failure handling

## 🚀 Running Tests

### Prerequisites

```bash
# Ensure you're in the project root directory
cd /path/to/KarigorAI

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install testing dependencies
pip install -r requirements-test.txt
```

### Basic Test Execution

```bash
# Run all tests with verbose output
PYTHONPATH=. pytest tests/ -v

# Run specific test file
PYTHONPATH=. pytest tests/unit/test_api_server.py -v

# Run specific test class
PYTHONPATH=. pytest tests/unit/test_llm_handler.py::TestStoryGeneration -v

# Run specific test method
PYTHONPATH=. pytest tests/unit/test_api_server.py::TestStoryGeneration::test_generate_story_success -v
```

### Advanced Test Options

```bash
# Run with short traceback for cleaner output
PYTHONPATH=. pytest tests/ -v --tb=short

# Run with coverage report
PYTHONPATH=. pytest tests/ -v --cov=. --cov-report=html

# Run tests in parallel (requires pytest-xdist)
PYTHONPATH=. pytest tests/ -v -n auto

# Run only failed tests from last run
PYTHONPATH=. pytest tests/ -v --lf

# Stop on first failure
PYTHONPATH=. pytest tests/ -v -x
```

## 🔧 Test Configuration

### Environment Setup

Tests use isolated environments and mocking to avoid dependencies on external services:

```python
# Example environment isolation
@patch.dict(os.environ, {'GOOGLE_GEMINI_API_KEY': 'test_api_key'})
@patch('google.generativeai.configure')
@patch('google.generativeai.GenerativeModel')
def test_llm_functionality(self, mock_model, mock_configure):
    # Test implementation
```

### Key Testing Patterns

#### 1. **Dependency Injection Mocking**
```python
def setup_method(self):
    self.mock_config_loader = Mock()
    self.mock_config_loader.get_config.side_effect = lambda key, default=None: {
        'model_name': 'gemini-1.5-flash-latest',
        'llm.temperature': 0.7,
        # ... other config values
    }.get(key, default)
```

#### 2. **API Response Mocking**
```python
@patch('api_server.agent')
def test_api_endpoint(self, mock_agent, client):
    mock_agent.generate_story_and_image.return_value = (
        "Generated story content",
        "Generated image prompt"
    )
    response = client.post("/generate", json=request_data)
    assert response.status_code == 200
```

#### 3. **Exception Handling Tests**
```python
def test_error_scenario(self):
    mock_agent.generate_story_and_image.side_effect = Exception("AI service error")
    with pytest.raises(Exception):
        response = client.post("/generate", json=request_data)
```

## 🛠️ Fixtures and Utilities

### Core Fixtures (`conftest.py`)

```python
@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)

@pytest.fixture
def temp_db():
    """Temporary database for testing"""
    # Creates isolated test database

@pytest.fixture
def mock_environment():
    """Mock environment variables"""
    # Sets up test environment
```

## 🐛 Troubleshooting Guide

### Common Issues and Solutions

#### 1. **Import Errors**
```bash
# Problem: ModuleNotFoundError
# Solution: Always use PYTHONPATH=.
PYTHONPATH=. pytest tests/ -v
```

#### 2. **API Key Issues**
```python
# Problem: Real API keys being used in tests
# Solution: Proper environment variable mocking
@patch.dict(os.environ, {}, clear=True)  # Clears all env vars
@patch.dict(os.environ, {'API_KEY': 'test_key'})  # Sets test key
```

#### 3. **Database Conflicts**
```python
# Problem: Tests interfering with each other
# Solution: Use isolated test databases
@pytest.fixture
def temp_db():
    db_path = "test_temp.db"
    # Setup temporary database
    yield db_path
    # Cleanup after test
```

#### 4. **Mock Configuration Issues**
```python
# Problem: Mocks not being applied correctly
# Solution: Proper mock hierarchy and return values
mock_agent.method.return_value = expected_value
mock_agent.method.side_effect = [value1, value2]  # Multiple calls
```

### Debugging Failed Tests

```bash
# Run with detailed output
PYTHONPATH=. pytest tests/unit/test_failing.py -v -s

# Use Python debugger
PYTHONPATH=. pytest tests/unit/test_failing.py -v --pdb

# Print variables during test
PYTHONPATH=. pytest tests/unit/test_failing.py -v --capture=no
```

## 📊 Test Coverage Analysis

### Current Coverage Areas

| Component | Coverage | Notes |
|-----------|----------|-------|
| API Endpoints | 95%+ | All major endpoints covered |
| LLM Integration | 90%+ | Multiple AI providers tested |
| Character System | 85%+ | Core persona functionality |
| Database Operations | 80%+ | CRUD and advanced queries |
| Error Handling | 85%+ | Various failure scenarios |

### Running Coverage Reports

```bash
# Generate HTML coverage report
PYTHONPATH=. pytest tests/ --cov=. --cov-report=html

# View coverage in terminal
PYTHONPATH=. pytest tests/ --cov=. --cov-report=term-missing

# Generate XML for CI/CD
PYTHONPATH=. pytest tests/ --cov=. --cov-report=xml
```

## 🔄 Continuous Integration

### GitHub Actions Integration

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      - name: Run tests
        run: PYTHONPATH=. pytest tests/ -v --cov=.
```

## 📝 Best Practices

### Writing New Tests

1. **Follow AAA Pattern**:
   ```python
   def test_feature(self):
       # Arrange
       setup_data = create_test_data()
       
       # Act
       result = function_under_test(setup_data)
       
       # Assert
       assert result == expected_value
   ```

2. **Use Descriptive Names**:
   ```python
   def test_generate_story_with_valid_character_returns_success(self):
       # Clear test intent from name
   ```

3. **Mock External Dependencies**:
   ```python
   @patch('external_service.api_call')
   def test_feature(self, mock_api):
       mock_api.return_value = test_response
       # Test implementation
   ```

4. **Test Edge Cases**:
   ```python
   def test_empty_input_raises_validation_error(self):
   def test_invalid_api_key_returns_unauthorized(self):
   def test_network_timeout_handles_gracefully(self):
   ```

### Test Maintenance

1. **Regular Test Reviews**: Review tests quarterly for relevance
2. **Update Mocks**: Keep mocked responses aligned with real APIs
3. **Performance Monitoring**: Watch for slow-running tests
4. **Documentation Updates**: Keep this document current with changes

## 🔮 Future Enhancements

### Planned Test Improvements

1. **Integration Tests**: End-to-end workflow testing
2. **Performance Tests**: Load and stress testing
3. **Security Tests**: Authentication and authorization
4. **Contract Tests**: API contract validation
5. **Visual Regression Tests**: Frontend UI testing

### Test Infrastructure

1. **Test Data Management**: Centralized test data factory
2. **Parallel Execution**: Faster test suite execution
3. **Test Reporting**: Enhanced reporting and metrics
4. **Environment Management**: Multiple test environments

## 📞 Support and Resources

### Getting Help

1. **Check this documentation** for common patterns and solutions
2. **Review existing tests** for similar functionality examples
3. **Run tests in isolation** to identify specific issues
4. **Use verbose output** (`-v`) and short tracebacks (`--tb=short`)

### Useful Commands Reference

```bash
# Quick test status check
PYTHONPATH=. pytest tests/ --tb=short | grep -E "(PASSED|FAILED|SKIPPED|failed|passed|skipped|=====)"

# Test specific functionality
PYTHONPATH=. pytest tests/ -k "story_generation" -v

# Debug specific test
PYTHONPATH=. pytest tests/unit/test_api_server.py::TestStoryGeneration::test_generate_story_success -v -s

# Update test snapshots (if using snapshot testing)
PYTHONPATH=. pytest tests/ --snapshot-update
```

---

## 📄 Conclusion

This testing documentation provides a comprehensive foundation for maintaining and extending the KarigorAI test suite. With our current **97.8% test success rate**, we have established a robust testing framework that ensures code quality, prevents regressions, and supports confident development.

Remember to keep tests updated as the codebase evolves, and always write tests for new features before implementation (TDD approach when possible).

**Happy Testing! 🧪✨** 