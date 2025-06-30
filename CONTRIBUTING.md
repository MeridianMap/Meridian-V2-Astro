# Contributing to Meridian Astrocartography Platform

Thank you for your interest in contributing to Meridian! This document provides comprehensive guidelines for contributing to our astrocartography and ephemeris calculation platform.

## 🚀 Development Setup

### Prerequisites
- **Python**: 3.9+ (recommended: 3.11)
- **Node.js**: 18+ with npm
- **Git**: Latest version
- **Code Editor**: VS Code recommended with extensions:
  - Python extension pack
  - ES7+ React/Redux/React-Native snippets
  - Prettier - Code formatter

### Local Setup Process

1. **Fork and Clone**
   ```bash
   git fork https://github.com/your-username/meridian-map
   git clone https://github.com/your-username/meridian-map.git
   cd "Meridian Map V2.1"
   ```

2. **Backend Setup**
   ```bash
   # Create virtual environment (recommended)
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r backend/requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

4. **Environment Configuration**
   ```bash
   # Backend .env
   cp backend/.env.example backend/.env
   
   # Frontend .env
   echo "VITE_GEOAPIFY_API_KEY=your_key_here" > frontend/.env
   ```

5. **Verify Installation**
   ```bash
   # Test backend
   python -m backend.api &
   curl http://localhost:5000/api/health
   
   # Test frontend  
   cd frontend && npm run dev
   ```

## 📝 Code Style Guidelines

### Python (Backend)
- **Style**: Follow PEP 8 rigorously
- **Docstrings**: Use Google-style docstrings for all functions and classes
- **Type Hints**: Use type annotations for function parameters and return values
- **Line Length**: Maximum 88 characters (Black formatter standard)
- **Imports**: Group imports (standard library, third-party, local) with blank lines

**Example:**
```python
def calculate_astrocartography_line(
    planet: str, 
    birth_date: datetime, 
    coordinates: tuple[float, float]
) -> dict[str, Any]:
    """Calculate astrocartography line for a specific planet.
    
    Args:
        planet: Planet name (e.g., 'sun', 'moon')
        birth_date: Birth date and time
        coordinates: Latitude and longitude tuple
        
    Returns:
        Dictionary containing line calculation results
        
    Raises:
        ValueError: If planet name is invalid
    """
    # Implementation here
    pass
```

### JavaScript/React (Frontend)
- **Style**: Use ES6+ features and modern React patterns
- **Components**: Functional components with hooks only
- **Naming**: PascalCase for components, camelCase for variables/functions
- **File Structure**: One component per file, matching component name
- **Props**: Use TypeScript-style prop validation or PropTypes

**Example:**
```jsx
import React, { useState, useEffect } from 'react';

const AstrocartographyMap = ({ chartData, onLineSelect }) => {
  const [selectedLines, setSelectedLines] = useState([]);
  
  useEffect(() => {
    // Effect logic here
  }, [chartData]);
  
  return (
    <div className="astrocartography-map">
      {/* Component JSX */}
    </div>
  );
};

export default AstrocartographyMap;
```

## 🧪 Testing Standards

### Backend Testing
```bash
# Run all tests
python -m pytest backend/

# Run with coverage
python -m pytest backend/ --cov=backend --cov-report=html

# Run specific test files
python -m pytest backend/test_api.py -v
```

**Test Categories:**
- **Unit Tests**: Individual function testing (`test_*.py`)
- **Integration Tests**: API endpoint testing (`test_api.py`)
- **Calculation Tests**: Astronomical accuracy (`test_ccg*.py`, `test_hd*.py`)

### Frontend Testing
```bash
cd frontend
npm test                    # Run all tests
npm run test:watch         # Watch mode
npm run test:coverage      # With coverage report
```

### Writing Tests
- **Coverage**: Aim for >90% test coverage
- **Naming**: Descriptive test names explaining the scenario
- **Structure**: Arrange-Act-Assert pattern
- **Isolation**: Each test should be independent

**Python Test Example:**
```python
def test_sun_astrocartography_line_calculation():
    """Test that Sun AC line calculation returns valid coordinates."""
    # Arrange
    birth_data = {
        'date': '1990-01-15',
        'time': '14:30',
        'latitude': 40.7128,
        'longitude': -74.0060
    }
    
    # Act
    result = calculate_astrocartography_lines(birth_data, ['sun'])
    
    # Assert
    assert 'sun_ac' in result
    assert isinstance(result['sun_ac'], list)
    assert len(result['sun_ac']) > 0
```

## 🔄 Git Workflow

### Branch Naming
- `feature/descriptive-feature-name` - New features
- `fix/issue-description` - Bug fixes  
- `docs/documentation-updates` - Documentation changes
- `refactor/component-name` - Code refactoring
- `test/test-description` - Test additions

### Commit Message Format
```
type(scope): concise description

feat(astrocartography): add planetary line filtering by orb
fix(api): resolve timezone detection for southern hemisphere
docs(readme): update installation instructions for Windows
test(calculations): add edge case tests for retrograde planets
refactor(ui): simplify chart component state management
```

### Pull Request Process

1. **Pre-PR Checklist:**
   - [ ] All tests pass
   - [ ] Code follows style guidelines
   - [ ] Documentation updated (if needed)
   - [ ] No merge conflicts with main branch
   - [ ] Changes are atomic and focused

2. **PR Description Template:**
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Documentation update
   - [ ] Refactoring
   
   ## Testing
   - [ ] Unit tests added/updated
   - [ ] Integration tests pass
   - [ ] Manual testing completed
   
   ## Screenshots (if applicable)
   
   ## Checklist
   - [ ] Code follows project style guidelines
   - [ ] Self-review completed
   - [ ] Documentation updated
   ```

3. **Review Process:**
   - At least one code review required
   - All CI checks must pass
   - Documentation review for user-facing changes

## 🐛 Bug Reports

### Before Reporting
1. Search existing issues for duplicates
2. Test with the latest version
3. Reproduce the issue consistently

### Bug Report Template
```markdown
**Bug Description**
Clear description of the bug

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**
What should happen

**Environment**
- OS: [e.g., Windows 11, macOS 13]
- Python version: [e.g., 3.11.2]
- Node.js version: [e.g., 18.16.0]
- Browser: [e.g., Chrome 115]

**Additional Context**
Screenshots, error logs, etc.
```

## 💡 Feature Requests

### Feature Request Process
1. **Discussion**: Open a GitHub Discussion first for large features
2. **Research**: Check if similar functionality exists
3. **Design**: Consider impact on existing features
4. **Implementation**: Create detailed implementation plan

### Feature Request Template
```markdown
**Feature Summary**
Brief description of the feature

**Problem Statement** 
What problem does this solve?

**Proposed Solution**
Detailed description of the solution

**Alternatives Considered**
Other solutions you considered

**Implementation Notes**
Technical considerations, if any
```

## 📋 Code Review Guidelines

### For Authors
- Keep PRs focused and reasonably sized (<500 lines)
- Write clear commit messages and PR descriptions
- Respond to feedback promptly and constructively
- Test thoroughly before requesting review

### For Reviewers
- Focus on logic, maintainability, and performance
- Check for security implications
- Verify test coverage for new features
- Be constructive and specific in feedback
- Approve when confident in the changes

## 🏗️ Architecture Guidelines

### Backend Architecture
- **Separation of Concerns**: Keep calculations, API routes, and utilities separate
- **Error Handling**: Comprehensive error handling with meaningful messages
- **Performance**: Cache expensive calculations when possible
- **Modularity**: Keep functions focused and reusable

### Frontend Architecture  
- **Component Structure**: Small, focused, reusable components
- **State Management**: Use React Context for global state, local state for component-specific data
- **Performance**: Implement proper memoization and lazy loading
- **Accessibility**: Follow WCAG guidelines for accessibility

## 📊 Performance Considerations

### Backend Performance
- Use appropriate data structures for calculations
- Implement caching for repeated astronomical calculations
- Profile code to identify bottlenecks
- Optimize database queries (when applicable)

### Frontend Performance
- Implement proper React optimization (memo, useMemo, useCallback)
- Lazy load components and data
- Optimize bundle size with code splitting
- Use efficient rendering patterns for maps and charts

## 🛡️ Security Guidelines

- Never commit API keys or sensitive data
- Validate all user inputs on both frontend and backend
- Use CORS appropriately for API access
- Follow secure coding practices for authentication (when added)

## 🎯 Release Process

1. **Version Bumping**: Follow semantic versioning (MAJOR.MINOR.PATCH)
2. **Changelog**: Update CHANGELOG.md with all changes
3. **Testing**: Run full test suite including manual testing
4. **Documentation**: Ensure all docs are up to date
5. **Deployment**: Follow deployment checklist in DEPLOY.md

## 💬 Communication & Community

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion  
- **Code Reviews**: For technical discussions
- **Documentation**: For user guides and API reference

## 📋 Code of Conduct

This project follows the [Contributor Covenant](https://www.contributor-covenant.org/) code of conduct. Be respectful, inclusive, and constructive in all interactions.

## 🎉 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes for significant contributions
- Special mentions for outstanding contributions

---

Thank you for contributing to Meridian! Your efforts help make astrocartography more accessible to everyone. 🌟
