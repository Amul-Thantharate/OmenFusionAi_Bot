# OmenFusionAi_Bot AI Release Notes

## Latest Release - v2.4.0 (January 10, 2025)

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

## Required Environment Variables
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
ADMIN_USER_ID=your_admin_telegram_id
ROOT_PASSWORD=your_admin_password
```

## Optional API Keys
Users can set these directly through the bot:
- Groq API Key (`/setgroqapi`)
- Replicate API Key (`/setreplicateapi`)

---

## Previous Releases

### v2.3.1 (January 8, 2025)

#### Major Changes
- 🔄 Enhanced Image Analysis UI
  - Added interactive buttons for image analysis options
  - Unified image description using Groq's LLaMA model
  - Added Replicate-powered creative captions

#### Features Added
- 🖼️ New Image Analysis Options:
  - "Describe Image": Detailed analysis using Groq
  - "Generate Caption": Creative captions using Replicate
- 🎨 Improved User Experience:
  - Inline keyboard for easy selection
  - Real-time processing status updates
  - Better error handling and feedback

#### Technical Improvements
- 🛠️ Code Refactoring:
  - Unified image analysis using Groq's LLaMA model
  - Streamlined caption generation with Replicate
  - Enhanced error handling and logging
- 🔧 Performance:
  - Optimized image processing
  - Better memory management
  - Improved response times

#### Documentation
- 📚 Updated image analysis commands
- 🔑 Added new environment variable requirements
- 📝 Enhanced troubleshooting guide

#### Bug Fixes
- 🐛 Fixed image processing errors
- 🔧 Improved error messages
- 🔄 Enhanced session handling

### v2.3.0 (January 8, 2025)

#### Major Changes
- 🔄 Replaced Together AI with Replicate for image generation
- 🎨 Integrated Recraft AI v3 model for enhanced image quality
- ⚡ Improved image generation reliability and speed

#### Updates
- 📦 Updated dependencies:
  - Removed Together AI dependency
  - Added Replicate SDK >= 0.22.0
- 🔑 API Key Management:
  - Removed Together AI key requirement
  - Added Replicate API key support
  - Updated environment variable configuration

#### Technical Improvements
- 🛠️ Refactored image generation module
- 🔧 Enhanced error handling for image generation
- 📝 Updated documentation and help messages
- 🔄 Streamlined API response handling

#### Documentation
- 📚 Updated setup instructions for Replicate API
- 🔑 Added Replicate API key configuration guide
- 🎨 Updated image generation command descriptions

#### Bug Fixes
- 🐛 Fixed image generation timeout issues
- 🔧 Improved error messaging for API failures
- 🔄 Enhanced response format handling

#### Security
- 🔒 Improved API key management
- 🛡️ Enhanced error logging for better debugging
- 🔐 Updated secure key storage methods


## Upcoming Features
- Enhanced error handling
- More AI model options
- Improved image generation
- Better video analysis
- Group chat enhancements
- Custom model selection

## Acknowledgments
- Thanks to all contributors
