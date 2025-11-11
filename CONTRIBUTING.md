# Contributing to VORTEX-AML

First off, thank you for considering contributing to VORTEX-AML! It's people like you that make VORTEX-AML such a great tool for the financial compliance community.

## 🌟 How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples** to demonstrate the steps
- **Describe the behavior you observed** and what you expected
- **Include screenshots** if relevant
- **Include your environment details** (OS, Python version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear and descriptive title**
- **Provide a detailed description** of the suggested enhancement
- **Explain why this enhancement would be useful**
- **List any alternative solutions** you've considered

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following our coding standards
3. **Add tests** if you've added code that should be tested
4. **Ensure the test suite passes** (`pytest tests/`)
5. **Update documentation** as needed
6. **Write a clear commit message** describing your changes

## 💻 Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/VORTEX-AML.git
cd VORTEX-AML

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v

# Run linter
flake8 src/
black src/ --check

# Format code
black src/
```

## 📝 Coding Standards

### Python Style Guide

- Follow **PEP 8** style guide
- Use **type hints** for function parameters and return values
- Write **docstrings** for all public functions and classes
- Keep functions **small and focused** (single responsibility)
- Use **meaningful variable names**

### Example:

```python
def calculate_risk_score(
    sanctions_risk: float,
    pep_risk: float,
    adverse_media_risk: float,
    behavioral_risk: float
) -> float:
    """
    Calculate weighted risk score from component risks.
    
    Args:
        sanctions_risk: Sanctions screening risk (0-100)
        pep_risk: PEP database risk (0-100)
        adverse_media_risk: Adverse media risk (0-100)
        behavioral_risk: Behavioral analysis risk (0-100)
    
    Returns:
        Final weighted risk score (0-100)
    """
    weights = {
        'sanctions': 0.40,
        'pep': 0.25,
        'adverse_media': 0.25,
        'behavioral': 0.10
    }
    
    final_score = (
        sanctions_risk * weights['sanctions'] +
        pep_risk * weights['pep'] +
        adverse_media_risk * weights['adverse_media'] +
        behavioral_risk * weights['behavioral']
    )
    
    return min(final_score, 100.0)
```

### Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters
- Reference issues and pull requests after the first line

Example:
```
Add multi-language support for dashboard

- Implement i18n framework
- Add French and Arabic translations
- Update documentation

Closes #123
```

## 🧪 Testing

- Write **unit tests** for new functionality
- Ensure **test coverage** remains above 80%
- Test **edge cases** and error conditions
- Use **pytest fixtures** for common test setup

```python
# tests/test_screening_engine.py
import pytest
from src.screening_engine import ScreeningEngine

@pytest.fixture
def screening_engine():
    return ScreeningEngine()

def test_low_risk_entity(screening_engine):
    result = screening_engine.screen_entity("John Smith")
    assert result.risk_level == "LOW"
    assert result.risk_score < 20

def test_high_risk_entity(screening_engine):
    result = screening_engine.screen_entity("Vladimir Putin")
    assert result.risk_level in ["MEDIUM", "HIGH", "CRITICAL"]
    assert "SANCTIONS_MATCH" in result.flags
```

## 📚 Documentation

- Update **README.md** if you change functionality
- Add **docstrings** to new functions and classes
- Update **API documentation** if you modify endpoints
- Include **examples** for new features

## 🔍 Code Review Process

1. **Automated checks** must pass (tests, linting, formatting)
2. **At least one maintainer** must approve the PR
3. **All conversations** must be resolved
4. **Documentation** must be updated
5. **No merge conflicts** with main branch

## 🎯 Priority Areas

We're especially interested in contributions in these areas:

- 🧠 **Machine Learning Models** - Improved anomaly detection
- 🌍 **Internationalization** - Multi-language support
- 📱 **Mobile App** - iOS and Android applications
- 🔌 **Integrations** - Third-party API connectors
- 📊 **Analytics** - Advanced reporting features
- 🔒 **Security** - Enhanced security measures

## 💬 Community

- **GitHub Discussions** - For questions and ideas
- **GitHub Issues** - For bugs and feature requests
- **Email** - [belfkihosni@gmail.com](mailto:belfkihosni@gmail.com) for private inquiries

## 📜 Code of Conduct

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

**Positive behavior includes:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable behavior includes:**
- Trolling, insulting/derogatory comments, and personal attacks
- Public or private harassment
- Publishing others' private information without permission
- Other conduct which could reasonably be considered inappropriate

## 🙏 Recognition

Contributors will be recognized in:
- **README.md** - Contributors section
- **Release notes** - For significant contributions
- **GitHub** - Contributor badge on profile

## 📞 Questions?

Don't hesitate to reach out:
- 💬 **GitHub Discussions** - For public questions
- 📧 **Email** - [belfkihosni@gmail.com](mailto:belfkihosni@gmail.com)
- 💼 **LinkedIn** - [linkedin.com/in/hosnibelfeki](https://www.linkedin.com/in/hosnibelfeki/)

---

Thank you for contributing to VORTEX-AML! Together, we're transforming financial compliance through AI. 🛡️

**Hosni Belfeki**  
Project Maintainer
