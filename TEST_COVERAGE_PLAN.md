# Test Coverage Improvement Plan

## Current Status

- **Current Coverage**: ~60-65% (estimated)
- **Target Coverage**: 70%+
- **Coverage Tools**: pytest-cov with HTML reports

## Coverage Goals by Module

### Core Simulation (Target: 80%+)
- [x] `simulation/engine.py` - Basic tests exist
- [ ] `simulation/engine.py` - Add tests for environmental stimuli integration
- [ ] `simulation/agents.py` - Improve agent behavior tests
- [ ] `simulation/culture.py` - Add more culture evolution tests
- [ ] `simulation/economy.py` - Add more economic system tests
- [ ] `simulation/world.py` - Add world state tests

### Memory Systems (Target: 70%+)
- [ ] `simulation/memory/graph.py` - Add graph memory tests
- [ ] `simulation/memory/vector.py` - Add vector memory tests
- [ ] `simulation/memory/manager.py` - Add memory manager tests

### API Layer (Target: 75%+)
- [x] `auth.py` - Authentication tests added
- [ ] `app.py` - Add API endpoint tests
- [ ] `app.py` - Add error handling tests
- [ ] `app.py` - Add input validation tests

### Adapters (Target: 70%+)
- [ ] `adapters/llm.py` - Add LLM adapter tests
- [ ] `adapters/neo4j.py` - Add Neo4j adapter tests
- [ ] `adapters/storage.py` - Add storage adapter tests

## Test Categories

### Unit Tests
- Test individual functions and methods
- Mock external dependencies
- Fast execution
- High coverage

### Integration Tests
- Test component interactions
- Use real dependencies where possible
- Test data flow
- Moderate execution time

### End-to-End Tests
- Test complete workflows
- Use real services
- Test user scenarios
- Slower execution

## Running Tests

### Basic Test Run
```bash
cd backend
pytest tests/ -v
```

### With Coverage
```bash
cd backend
pytest --cov=simulation --cov=adapters --cov=auth --cov-report=term-missing --cov-report=html tests/
```

### View Coverage Report
```bash
open htmlcov/index.html
```

### Specific Test Categories
```bash
# Unit tests only
pytest -m unit tests/

# Integration tests only
pytest -m integration tests/

# Security tests
pytest -m security tests/
```

## Test Structure

```
backend/tests/
├── __init__.py
├── test_agents.py          # Agent behavior tests
├── test_auth.py            # Authentication tests
├── test_culture.py         # Culture evolution tests
├── test_economy.py        # Economic system tests
├── test_engine.py         # Simulation engine tests
├── test_memory.py         # Memory system tests (to be created)
├── test_api.py            # API endpoint tests (to be created)
└── conftest.py            # Shared fixtures (to be created)
```

## Priority Areas

### High Priority
1. **API Endpoints** - Critical for production
2. **Input Validation** - Security critical
3. **Authentication** - Security critical
4. **Simulation Engine** - Core functionality

### Medium Priority
1. **Memory Systems** - Important for functionality
2. **Cultural Evolution** - Core feature
3. **Economic System** - Core feature

### Low Priority
1. **Adapters** - Can be tested with integration tests
2. **Utilities** - Less critical paths

## Test Data

### Fixtures
Create shared fixtures in `conftest.py`:
- Mock agents
- Mock world state
- Mock simulation engine
- Test configuration

### Test Data Files
- Sample stimuli data
- Sample agent configurations
- Sample world states

## Continuous Improvement

### Regular Tasks
- Run coverage reports weekly
- Identify low-coverage areas
- Add tests for new features
- Update tests for changed code

### Coverage Monitoring
- Set up CI/CD coverage reporting
- Track coverage trends
- Set coverage thresholds
- Block merges below threshold

## Tools and Resources

### Testing Tools
- **pytest**: Test framework
- **pytest-cov**: Coverage plugin
- **pytest-asyncio**: Async test support
- **pytest-mock**: Mocking support

### Coverage Tools
- **coverage.py**: Coverage measurement
- **pytest-cov**: Coverage integration
- **HTML reports**: Visual coverage reports

### Best Practices
- Write tests before fixing bugs
- Test edge cases
- Test error conditions
- Keep tests fast
- Use descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)

## Next Steps

1. ✅ Add authentication tests
2. ⏳ Add API endpoint tests
3. ⏳ Add memory system tests
4. ⏳ Improve simulation engine tests
5. ⏳ Add integration tests
6. ⏳ Set up coverage CI/CD reporting

