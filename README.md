# 🤖 NovaChat AI

## 🌟 Welcome to NovaChat AI - Your Advanced AI-Powered Telegram Assistant!

Transform your Telegram experience with NovaChat AI, an advanced AI assistant that brings the power of intelligent conversations and creative imagery right to your chat! Powered by Groq's cutting-edge language models and state-of-the-art image generation, NovaChat AI is your gateway to the future of digital interaction.

### ✨ Why Choose NovaChat AI?

- 🧠 **Advanced AI Chat**: Engage in natural, context-aware conversations
- 🎨 **Dual Image Generation**: Create stunning visuals with both quick and high-quality options
- 🔐 **Security First**: Your data's privacy is our top priority
- ⚡ **Lightning Fast**: Powered by Groq's high-performance AI models
- 🎯 **User-Focused**: Intuitive commands and customizable settings

## 🔑 Getting Your API Keys

### Groq API Key
1. Visit [Groq Cloud Console](https://console.groq.com)
2. Sign up or log in to your account
3. Go to API Keys section
4. Click "Create New API Key"
5. Copy your API key
6. In NovaChat AI, use `/setgroqkey your_key_here`

### Together AI Key
1. Go to [Together AI Platform](https://together.ai)
2. Create an account or sign in
3. Navigate to API section
4. Generate a new API key
5. Copy the key
6. Use `/settogetherkey your_key_here` in NovaChat AI

### Replicate API Key (Coming in v1.1)
1. Visit [Replicate](https://replicate.com)
2. Sign up for an account
3. Go to Account Settings
4. Find API Tokens section
5. Generate new token
6. Will be used with upcoming video generation feature

## 🚀 Key Features

### 💬 Intelligent Chat
- Advanced language understanding with Groq's Llama3-8b-8192
- Context-aware responses
- Customizable AI parameters
- Chat history management

### 🎨 Image Generation
- `/image` - Quick image generation
- `/imagine` - High-quality artistic creations
- Multiple style options
- Progress tracking

### ⚙️ Powerful Controls
- Customizable settings
- Chat history export (PDF/Markdown)
- API key management
- User session handling

## 📦 Prerequisites

- Python 3.8+
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- Groq API Key (optional)
- Together AI Key (optional)

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/NovaChat-AI.git
cd NovaChat-AI
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your tokens and settings
```

## 🎮 Quick Start

1. Set up your bot with [@BotFather](https://t.me/botfather)
2. Configure your `.env` file
3. Run the bot:
```bash
python app/main.py
```

## 📚 Documentation

Visit our comprehensive documentation:
- [📘 Setup Guide](docs/setup.md)
- [🎮 Command Reference](docs/commands.md)
- [📋 Changelog](docs/changelog.md)

## 🔒 Security

- Secure API key handling
- No persistent storage of sensitive data
- Private conversation handling
- Auto-deletion of sensitive messages

## 🎯 Roadmap

### Version 1.1
- Multi-language support
- Voice message processing
- Custom image styles
- Chat summarization
- Video generation Using (Replicate)

### Version 1.2
- Group chat support
- Image editing capabilities
- Custom AI model selection
- Advanced prompt templates
- Prompt Enhancements for image generation

### Version 1.3
- Custom AI model selection
- Speech-to-Text integration
- Voice message processing
- Image captioning

## 🤝 Contributing

We welcome contributions! Please read our contribution guidelines before submitting pull requests.

## 📄 License

NovaChat AI is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🌟 Show Your Support

If you find NovaChat AI helpful, please give it a star! ⭐

---

Made with ❤️ by the NovaChat AI Team
