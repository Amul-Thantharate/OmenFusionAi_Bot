---
layout: default
title: Changelog
nav_order: 4
---

# 📝 Changelog
{: .no_toc }

Track OmenFusionAi_Bot's version history and updates.
{: .fs-6 .fw-300 }

## 📋 Table of Contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## [3.1.0] - 2025-01-06 🚀

### 🗑️ Removed
- 🎥 Removed YouTube video download functionality
- 🔧 Removed `/videos` and `/clear` commands
- 📦 Removed YouTube-related dependencies
- 📄 Cleaned up documentation and help messages

### 🔄 Changed
- 🎵 Simplified audio commands section
- 📦 Updated requirements.txt to remove yt-dlp package

## [3.0.0] - 2025-01-04 🎯

### ✨ Added
- 🤖 Migrated to Groq API with Mixtral-8x7b model
- 🔊 Enhanced text-to-speech functionality
- 🛠️ Improved error handling and user feedback
- 🔑 Better API key management through environment variables

### 🔄 Changed
- 🔄 Switched from OpenAI to Groq for main chat functionality
- 🤖 Updated model selection to use Mixtral-8x7b
- 💬 Improved chat command structure
- 📝 Enhanced error messages and user guidance

### 🗑️ Removed
- 🔌 OpenAI integration and related commands
- 🔑 Legacy API key handling methods

## [2.5.0] - 2025-01-06 🎉

### ✨ Added
- New video analysis features:
  - `/analyze_video` command for AI-powered video insights
  - Support for video file uploads up to 50MB
  - Detailed video content analysis using Gemini Vision

### 🔧 Changed
- Improved error handling and user feedback
- Better handling of YouTube transcripts
- Enhanced help messages with emojis
- Organized constants in a dedicated file

### 🎨 UI/UX
- Added emojis throughout the bot responses
- More detailed command descriptions
- Better error messages with troubleshooting steps
- Clear file size and format requirements

### 🔒 Security
- Improved environment variable handling
- Better API key management
- Secure file handling and cleanup

### 🐛 Fixed
- Fixed circular import issues
- Improved video file size validation
- Better error handling for unavailable YouTube transcripts
- Fixed maintenance mode issues

### 📚 Documentation
- Updated README with new features
- Added detailed setup instructions
- Improved command documentation
- Added usage examples

## [2.4.0] - 2025-01-10 🚀

### ✨ New Features
- Added `/setgroqapi` command for users to set their own Groq API key
- Added `/setreplicateapi` command for users to set their own Replicate API key
- API keys can now be set individually by each user
- API keys are stored securely in memory

### 🔄 Changes
- Removed voice response functionality
- Removed `/togglevoice` command
- Removed setup command functionality
- Simplified maintenance mode toggle
- Moved API keys to per-user session storage

### 🔧 Core Improvements
- Enhanced security for API key handling
- Improved command registration system
- Better error handling and user feedback
- Optimized memory usage for user sessions

### 🔒 Security
- API keys are now stored per user in memory
- Messages containing API keys are automatically deleted
- Added ADMIN_USER_ID to environment variables
- Improved environment variable handling

### 📚 Documentation
- Updated README with new API key commands
- Added API key setup instructions
- Removed voice-related documentation
- Updated environment variable requirements

## [2.3.1] - 2025-01-08 🛠️

### Major Changes
- 🔄 Enhanced Image Analysis UI
  - Added interactive buttons for image analysis options
  - Unified image description using Groq's LLaMA model
  - Improved response formatting and clarity

### Features Added
- 🖼️ New Image Analysis Options:
  - "Describe Image": Detailed analysis using Groq
  - "Generate Caption": Creative captions using Replicate
  - "Analyze Objects": Object detection and scene analysis

### Technical Improvements
- 🛠️ Code Refactoring:
  - Unified image analysis using Groq's LLaMA model
  - Streamlined caption generation with Replicate
  - Enhanced error handling and feedback
  - Better memory management
  - Improved response times

### Documentation
- 📚 Updated image analysis commands
- 🔑 Added new environment variable requirements
- 📝 Enhanced troubleshooting guide

## [2.3.0] - 2025-01-08 🚀

### Major Changes
- 🔄 Replaced Together AI with Replicate for image generation
- 🎨 Integrated Recraft AI v3 model for enhanced image quality
- ⚡ Improved image generation reliability and speed

### Updates
- 📦 Updated dependencies:
  - Removed Together AI dependency
  - Added Replicate SDK >= 0.22.0
  - Updated environment variable configuration

### Technical Improvements
- 🛠️ Refactored image generation module
- 🔧 Enhanced error handling for image generation
- 📝 Updated documentation and help messages

### Documentation
- 📚 Updated setup instructions for Replicate API
- 🔑 Added Replicate API key configuration guide
- 🎨 Updated image generation command descriptions

### Bug Fixes
- 🐛 Fixed image generation timeout issues
- 🔧 Improved error messaging for API failures
- 🔄 Enhanced response format handling

### Security
- 🔒 Improved API key management
- 🛡️ Enhanced error logging for better debugging
- 🔐 Updated secure key storage methods

## [2.2.0] - 2025-01-06 🎨

### New Features
- 🖼️ Added image-to-text functionality using Groq Vision API
- 🔄 Support for direct image uploads and URL analysis
- 📝 Intelligent image description with detailed context
- 🎯 Three ways to analyze images:
  - Direct image uploads
  - Reply to images with `/describe`
  - URL analysis with `/describe [URL]`

### Improvements
- 🔧 Enhanced error handling and user feedback
- 📚 Updated documentation and help messages
- ⚡ Improved response times and reliability

## [1.4.0] - 2025-01-06 📚

### Enhancements
- 📚 Improved `/help` command with better categorization
- 🔄 Updated Together AI package to version 1.3.11
- 🎨 Enhanced message formatting for better readability
- 🛠️ Fixed Markdown formatting issues in help messages

### Bug Fixes
- 🔧 Fixed entity parsing error in help command
- ✨ Improved command descriptions and categorization
- 🎯 Fixed Markdown escaping in bot messages

### Dependencies
- ⬆️ Upgraded `together` package to v1.3.11
- ⬆️ Updated `aiohttp` to v3.11.11
- ⬆️ Updated `pillow` to v10.4.0
- ⬆️ Updated `tqdm` to v4.67.1

## 🔮 Upcoming Features

### [3.2.0] - Planned 🎯
- 🔊 Enhanced audio processing
- 🎨 Better image generation
- 💭 Improved chat context
- 🛠️ More maintenance features

### [3.3.0] - Planned ✨
- 🌎 Multi-language support
- 🎨 Advanced image editing
- 🔊 Enhanced voice features

## 📈 Version History

### 🧪 Beta Releases
- 🚀 Beta 0.9.0 - Initial testing release
- 🐛 Beta 0.9.1 - Bug fixes and stability
- ⚡ Beta 0.9.2 - Performance improvements
- 🔒 Beta 0.9.3 - Security enhancements
- ✨ Beta 0.9.4 - Final beta release

### 🔬 Alpha Releases
- 🎯 Alpha 0.1.0 - Core functionality
- 💬 Alpha 0.2.0 - Basic chat features
- 🎨 Alpha 0.3.0 - Image generation
- 🔌 Alpha 0.4.0 - API integration
- 🖥️ Alpha 0.5.0 - User interface

## ⚠️ Deprecation Notices

### Version 1.0.0
- 🎨 Legacy image generation endpoint
- 💬 Basic text-only responses
- 🔧 Simple command structure

## 🔒 Security Updates

### Version 1.0.0
- 🔑 Secure API key handling
- 🔐 Webhook authentication
- ⚡ Rate limiting implementation
- ✅ Input validation
- 📝 Error logging

## ⚡ Performance Improvements

### Version 1.0.0
- ⚡ Async operations
- 🐳 Docker optimization
- 💾 Response caching
- 🧮 Memory management
- 🔄 Error recovery

## 🐛 Bug Fixes

### Version 1.0.0
- 🧹 Fixed memory leaks
- 🛠️ Improved error handling
- 🔧 Enhanced stability
- 🔧 Better timeout handling
- 📦 Updated dependencies
