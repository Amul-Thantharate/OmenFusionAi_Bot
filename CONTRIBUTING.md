# Contributing to OmenFusionAi_Bot

## 🌟 Welcome

Thank you for considering contributing to OmenFusionAi_Bot! This document provides guidelines and steps for contributing to make the process smooth and effective.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Process](#development-process)
- [Pull Request Process](#pull-request-process)
- [Style Guidelines](#style-guidelines)
- [Community](#community)

## 📜 Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:

- Be respectful and inclusive
- Exercise empathy and kindness
- Provide constructive feedback
- Focus on what is best for the community
- Show courtesy and respect towards other community members

## 🚀 Getting Started

1. Fork the repository
2. Clone your fork:
```bash
git clone https://github.com/Amul-Thantharate/OmenFusionAi_Bot.git
cd OmenFusionAi_Bot
```
3. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Unix/MacOS
venv\Scripts\activate     # Windows
```
4. Install dependencies:
```bash
pip install -r requirements.txt
```

## 💻 Development Process

### 1. Choose an Issue
- Look for issues labeled `good first issue` or `help wanted`
- Comment on the issue to express your interest
- Wait for assignment or confirmation

### 2. Create a Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-fix-name
```

### 3. Development Guidelines
- Follow PEP 8 style guide
- Add type hints to functions
- Write comprehensive docstrings
- Include unit tests for new features
- Keep commits atomic and well-described

### 4. Testing
- Run existing tests:
```bash
python -m pytest
```
- Add new tests for your features
- Ensure all tests pass before submitting

## 🔄 Pull Request Process

1. Update Documentation
   - Add/update docstrings
   - Update README.md if needed
   - Add to CHANGELOG.md

2. Submit PR
   - Fill out PR template completely
   - Link related issues
   - Provide clear description

3. Code Review
   - Address review comments
   - Make requested changes
   - Maintain clear communication

4. Merge
   - Squash commits if requested
   - Ensure CI passes
   - Wait for maintainer approval

## 📝 Style Guidelines

### Python Code
- Follow PEP 8
- Use type hints
- Maximum line length: 88 characters
- Use descriptive variable names
- Document complex logic

### Commit Messages
```
type(scope): Brief description

Detailed description of changes
```
Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation
- style: Formatting
- refactor: Code restructuring
- test: Adding tests
- chore: Maintenance

### Documentation
- Clear and concise
- Include code examples
- Update relevant sections
- Check for typos

## 🛠️ Development Setup

### Required Tools
- Python 3.8+
- Git
- Your favorite IDE (VSCode recommended)
- pytest for testing

### Environment Setup
1. Copy .env.example:
```bash
cp .env.example .env
```

## 🎯 Future Goals

- Multi-language support
- Voice message processing
- Advanced image generation
- Custom AI models

## ❓ Questions?

- Create an issue
- Join our community
- Contact maintainers

Thank you for contributing to OmenFusionAi_Bot! 🚀
