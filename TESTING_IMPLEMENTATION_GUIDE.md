# Testing Implementation Guide - KarigorAI

## 🚀 **Quick Start (5 Minutes)**

### **Step 1: Run Your First Test**
```bash
# Backend testing
pytest tests/conftest.py -v

# Frontend testing  
cd ui && npm test
```

### **Step 2: Check Test Coverage**
```bash
# Backend coverage
pytest --cov=. --cov-report=html

# Frontend coverage
cd ui && npm test -- --coverage --watchAll=false
```

---

## 📋 **Implementation Checklist**

### ✅ **Phase 1: Foundation (COMPLETED)**
- [x] ✅ Backend test dependencies installed (`pytest`, `httpx`, etc.)
- [x] ✅ Frontend test dependencies installed (`@testing-library/react`, `jest`)
- [x] ✅ Test directory structure created (`tests/`, `ui/__tests__/`)
- [x] ✅ Configuration files created (`conftest.py`, `jest.config.js`)
- [x] ✅ Sample test files created with examples

### 🔧 **Phase 2: Immediate Next Steps (30 minutes)**

#### **Backend Tests to Run Now**
```bash
# Test your API endpoints
pytest tests/unit/test_api_server.py::TestHealthEndpoints::test_health_check -v

# Test with mocked dependencies
pytest tests/unit/test_api_server.py::TestStoryGeneration -v
```

#### **Frontend Tests to Run Now**
```bash
cd ui

# Test component rendering
npm test -- __tests__/pages/GeneratePage.test.tsx

# Run specific test suite
npm test -- --testNamePattern="renders the page"
```

---

## 🛠️ **Development Workflow Integration**

### **Before Committing Code**
```bash
# Run all tests
pytest && cd ui && npm test -- --watchAll=false && cd ..

# Check coverage
pytest --cov=. --cov-fail-under=80
cd ui && npm test -- --coverage --coverageThreshold='{"global":{"branches":70,"functions":70,"lines":70,"statements":70}}'
```

### **During Development**
```bash
# Watch mode for frontend
cd ui && npm test -- --watch

# Specific test file
pytest tests/unit/test_api_server.py -v
```

---

## 🧪 **Test Examples You Can Run Right Now**

### **1. API Health Check Test**
```python
# File: tests/unit/test_api_server.py (line 15)
def test_health_check(self, client):
    response = client.get("/system/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

**Run it:**
```bash
pytest tests/unit/test_api_server.py::TestHealthEndpoints::test_health_check -v
```

### **2. Story Generation Test**
```python
# File: tests/unit/test_api_server.py (line 44)
@patch('api_server.agent')
def test_generate_story_success(self, mock_agent, client):
    mock_agent.generate_story_and_image.return_value = (
        "Generated test story", "Test image prompt", "gemini-test", 100, 200
    )
    # ... test logic
```

**Run it:**
```bash
pytest tests/unit/test_api_server.py::TestStoryGeneration::test_generate_story_success -v
```

### **3. Frontend Component Test**
```typescript
// File: ui/__tests__/pages/GeneratePage.test.tsx (line 55)
it('renders the page with all necessary elements', async () => {
  render(<GeneratePage />)
  expect(screen.getByText('Story Generation')).toBeInTheDocument()
})
```

**Run it:**
```bash
cd ui && npm test -- --testNamePattern="renders the page"
```

---

## 🔍 **Debugging Failed Tests**

### **Common Issues & Solutions**

#### **1. Import Errors**
```
Error: ModuleNotFoundError: No module named 'api_server'
```
**Solution:**
```bash
# Add project root to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest tests/unit/test_api_server.py
```

#### **2. Frontend Module Not Found**
```
Error: Cannot find module '@testing-library/react'
```
**Solution:**
```bash
cd ui && npm install --save-dev @testing-library/react @testing-library/jest-dom
```

#### **3. Database Connection Issues**
```
Error: sqlite3.OperationalError: database is locked
```
**Solution:** Tests use temporary databases (see `temp_db` fixture in `conftest.py`)

---

## 📊 **Test Monitoring Dashboard**

### **Coverage Reports**
```bash
# Generate HTML coverage report
pytest --cov=. --cov-report=html
open htmlcov/index.html

# Frontend coverage
cd ui && npm test -- --coverage
open coverage/lcov-report/index.html
```

### **Test Performance**
```bash
# Time each test
pytest --durations=10

# Slow test analysis
pytest --durations=0 | grep "slowest"
```

---

## 🎯 **Priority Testing Areas**

### **Critical Path Tests (Must Have)**
1. **Story Generation Workflow** ⭐⭐⭐
   ```bash
   pytest tests/unit/test_api_server.py::TestStoryGeneration -v
   ```

2. **Character Management** ⭐⭐⭐
   ```bash
   pytest tests/unit/test_api_server.py::TestCharacterManagement -v
   ```

3. **System Health** ⭐⭐
   ```bash
   pytest tests/unit/test_api_server.py::TestHealthEndpoints -v
   ```

### **Frontend Priority Tests**
1. **Generate Page Functionality** ⭐⭐⭐
   ```bash
   cd ui && npm test -- GeneratePage.test.tsx
   ```

2. **Navigation & Routing** ⭐⭐
   ```bash
   cd ui && npm test -- Navigation.test.tsx
   ```

---

## 🚀 **Advanced Testing Features**

### **Load Testing**
```python
# File: tests/performance/test_load.py
import asyncio
import time
from httpx import AsyncClient

async def test_concurrent_story_generation():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        tasks = []
        for i in range(10):
            task = ac.post("/generate", json={
                "story_prompt": f"Test story {i}",
                "character": "himu"
            })
            tasks.append(task)
        
        start = time.time()
        responses = await asyncio.gather(*tasks)
        end = time.time()
        
        assert all(r.status_code == 200 for r in responses)
        assert end - start < 30  # All should complete within 30 seconds
```

### **End-to-End Testing with Playwright**
```bash
# Install Playwright
cd ui && npx playwright install

# Run E2E tests
npx playwright test
```

---

## 🔄 **Continuous Integration Setup**

### **GitHub Actions Workflow**
```yaml
# File: .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: pip install pytest pytest-cov httpx
      - run: pytest --cov=. --cov-report=xml
      
  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: cd ui && npm ci
      - run: cd ui && npm test -- --coverage --watchAll=false
```

---

## 📝 **Writing New Tests**

### **Backend Test Template**
```python
# tests/unit/test_new_feature.py
import pytest
from unittest.mock import Mock, patch
from conftest import client, mock_config_loader

class TestNewFeature:
    def test_feature_success(self, client):
        # Arrange
        payload = {"key": "value"}
        
        # Act
        response = client.post("/new-endpoint", json=payload)
        
        # Assert
        assert response.status_code == 200
        assert response.json()["success"] is True
```

### **Frontend Test Template**
```typescript
// ui/__tests__/components/NewComponent.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import NewComponent from '../../components/NewComponent'

describe('NewComponent', () => {
  it('renders correctly', () => {
    render(<NewComponent />)
    expect(screen.getByText('Expected Text')).toBeInTheDocument()
  })
  
  it('handles user interaction', async () => {
    render(<NewComponent />)
    fireEvent.click(screen.getByRole('button'))
    expect(screen.getByText('Updated Text')).toBeInTheDocument()
  })
})
```

---

## 🎯 **Success Metrics**

### **Weekly Goals**
- [ ] **Week 1**: 50% backend test coverage
- [ ] **Week 2**: Frontend component tests for all pages
- [ ] **Week 3**: Integration tests for API workflows
- [ ] **Week 4**: E2E tests for user journeys

### **Quality Gates**
- ✅ All new features must have 80%+ test coverage
- ✅ No commits without passing tests
- ✅ Critical bugs must have regression tests
- ✅ Performance tests for high-traffic endpoints

---

## 🆘 **Getting Help**

### **Test Debugging Commands**
```bash
# Verbose test output
pytest -vv -s

# Stop on first failure
pytest -x

# Run only failed tests
pytest --lf

# Test specific pattern
pytest -k "test_generate_story"
```

### **Common Test Patterns**
1. **Arrange-Act-Assert** (AAA pattern)
2. **Mock external dependencies** (API calls, database)
3. **Test edge cases** (empty input, large data, errors)
4. **Verify side effects** (database changes, API calls)

---

**✨ You now have a complete testing foundation! Start with the health check test and build from there. Each test you write makes your app more reliable and easier to maintain.** 