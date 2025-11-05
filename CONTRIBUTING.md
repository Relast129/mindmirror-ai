# 🤝 Contributing to MindMirror AI

Thank you for your interest in contributing to MindMirror AI! This document provides guidelines for contributing to the project.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Testing](#testing)
- [Documentation](#documentation)

---

## 📜 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of:
- Age, body size, disability, ethnicity
- Gender identity and expression
- Level of experience
- Nationality, personal appearance, race
- Religion, or sexual identity and orientation

### Our Standards

**Positive behavior includes:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards others

**Unacceptable behavior includes:**
- Harassment, trolling, or derogatory comments
- Publishing others' private information
- Any conduct that could be considered inappropriate

---

## 🚀 Getting Started

### Prerequisites

- Node.js 18+
- Python 3.9+
- Git
- Google Cloud account
- Hugging Face account

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork:
```bash
git clone https://github.com/your-username/mindmirror-ai.git
cd mindmirror-ai
```

3. Add upstream remote:
```bash
git remote add upstream https://github.com/original-owner/mindmirror-ai.git
```

### Set Up Development Environment

Follow the [SETUP_GUIDE.md](SETUP_GUIDE.md) to configure your local environment.

---

## 🔄 Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

**Branch naming conventions:**
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions/modifications

### 2. Make Changes

- Write clean, readable code
- Follow coding standards (see below)
- Add tests for new features
- Update documentation as needed

### 3. Test Your Changes

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# Manual testing
npm start  # Frontend
uvicorn main:app --reload  # Backend
```

### 4. Commit Your Changes

```bash
git add .
git commit -m "feat: add voice emotion analysis"
```

See [Commit Guidelines](#commit-guidelines) below.

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

---

## 💻 Coding Standards

### Python (Backend)

**Style Guide:** PEP 8

```python
# Good
def process_emotion(text: str) -> Dict[str, Any]:
    """
    Process emotion from text input.
    
    Args:
        text: Input text to analyze
        
    Returns:
        Dictionary containing emotion analysis
    """
    result = emotion_detector.detect(text)
    return result

# Bad
def processEmotion(text):
    result=emotion_detector.detect(text)
    return result
```

**Key Points:**
- Use type hints
- Write docstrings for all functions
- Use meaningful variable names
- Keep functions small and focused
- Use async/await for I/O operations

**Linting:**
```bash
# Install tools
pip install black flake8 mypy

# Format code
black .

# Check style
flake8 .

# Type checking
mypy .
```

### JavaScript/React (Frontend)

**Style Guide:** Airbnb JavaScript Style Guide

```javascript
// Good
const EmotionCard = ({ emotion, confidence }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  
  return (
    <div className="emotion-card">
      <h3>{emotion}</h3>
      <p>{Math.round(confidence * 100)}%</p>
    </div>
  );
};

// Bad
function EmotionCard(props) {
  var expanded = false;
  return <div><h3>{props.emotion}</h3></div>
}
```

**Key Points:**
- Use functional components with hooks
- Use const/let, never var
- Use arrow functions
- Destructure props
- Use meaningful component names

**Linting:**
```bash
# Install ESLint
npm install --save-dev eslint

# Run linter
npm run lint

# Fix auto-fixable issues
npm run lint -- --fix
```

---

## 📝 Commit Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/).

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Test additions/modifications
- `chore`: Build process or auxiliary tool changes

### Examples

```bash
# Feature
git commit -m "feat(voice): add real-time transcription"

# Bug fix
git commit -m "fix(auth): resolve Google OAuth redirect issue"

# Documentation
git commit -m "docs(api): update endpoint documentation"

# Breaking change
git commit -m "feat(api): change reflection response format

BREAKING CHANGE: reflection endpoint now returns nested emotion object"
```

---

## 🔀 Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] Documentation is updated
- [ ] Commit messages follow conventions
- [ ] Branch is up to date with main

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How has this been tested?

## Screenshots (if applicable)
Add screenshots for UI changes

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests added/updated
- [ ] All tests passing
```

### Review Process

1. **Automated Checks:** CI/CD runs tests
2. **Code Review:** Maintainer reviews code
3. **Feedback:** Address review comments
4. **Approval:** Maintainer approves PR
5. **Merge:** PR is merged to main

---

## 🧪 Testing

### Backend Testing

```bash
cd backend

# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run tests
pytest

# With coverage
pytest --cov=. --cov-report=html
```

**Test Structure:**
```python
# tests/test_emotion_detector.py
import pytest
from ai.emotion_detector import EmotionDetector

@pytest.mark.asyncio
async def test_detect_joy():
    detector = EmotionDetector()
    result = await detector.detect_emotion("I'm so happy!")
    
    assert result['primary_emotion'] == 'joy'
    assert result['confidence'] > 0.5
```

### Frontend Testing

```bash
cd frontend

# Run tests
npm test

# With coverage
npm test -- --coverage

# Watch mode
npm test -- --watch
```

**Test Structure:**
```javascript
// src/components/__tests__/TextInput.test.js
import { render, screen, fireEvent } from '@testing-library/react';
import TextInput from '../TextInput';

test('submits text input', () => {
  const handleSubmit = jest.fn();
  render(<TextInput onReflectionGenerated={handleSubmit} />);
  
  const textarea = screen.getByPlaceholderText(/express yourself/i);
  fireEvent.change(textarea, { target: { value: 'Test input' } });
  
  const button = screen.getByText(/generate reflection/i);
  fireEvent.click(button);
  
  expect(handleSubmit).toHaveBeenCalled();
});
```

---

## 📚 Documentation

### Code Documentation

**Python:**
```python
def generate_reflection(text: str, emotion: str) -> Dict[str, str]:
    """
    Generate personalized reflection based on emotion.
    
    Args:
        text: User's input text
        emotion: Detected emotion (joy, sadness, etc.)
        
    Returns:
        Dictionary containing reflection, poem, and advice
        
    Raises:
        ValueError: If emotion is not supported
        
    Example:
        >>> reflection = generate_reflection("I'm happy", "joy")
        >>> print(reflection['poem'])
    """
    pass
```

**JavaScript:**
```javascript
/**
 * Generate AI reflection from user input
 * @param {string} content - User's input text
 * @param {string} contentType - Type of content (text, voice, etc.)
 * @param {boolean} generateArt - Whether to generate mood art
 * @returns {Promise<Object>} Reflection object with emotion, poetry, and art
 * @throws {Error} If API request fails
 */
async function generateReflection(content, contentType, generateArt) {
  // Implementation
}
```

### README Updates

When adding features, update:
- Feature list in README.md
- Setup instructions if needed
- API documentation
- Deployment guide if applicable

---

## 🎯 Areas for Contribution

### High Priority

- [ ] Improve emotion detection accuracy
- [ ] Add more language support
- [ ] Optimize AI model performance
- [ ] Enhance mobile responsiveness
- [ ] Add accessibility features (WCAG 2.1)

### Medium Priority

- [ ] Add data export formats (PDF, CSV)
- [ ] Implement email notifications
- [ ] Create mood prediction model
- [ ] Add dark mode
- [ ] Improve error handling

### Low Priority

- [ ] Add social sharing (optional)
- [ ] Create mobile app
- [ ] Add community features
- [ ] Implement gamification
- [ ] Add more visualization options

---

## 🐛 Reporting Bugs

### Before Reporting

1. Check existing issues
2. Verify it's reproducible
3. Test on latest version

### Bug Report Template

```markdown
**Describe the bug**
Clear description of the bug

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What should happen

**Screenshots**
If applicable

**Environment:**
- OS: [e.g., Windows 10]
- Browser: [e.g., Chrome 96]
- Version: [e.g., 1.0.0]

**Additional context**
Any other relevant information
```

---

## 💡 Feature Requests

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
Clear description of the problem

**Describe the solution**
What you want to happen

**Describe alternatives**
Alternative solutions considered

**Additional context**
Mockups, examples, etc.
```

---

## 📞 Getting Help

- **GitHub Issues:** For bugs and features
- **Discussions:** For questions and ideas
- **Discord:** For real-time chat (if available)
- **Email:** support@mindmirror.ai

---

## 🏆 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in the README

---

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to MindMirror AI! Together, we're building a better mental wellness tool for Gen Z. 💙**
