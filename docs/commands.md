---
layout: default
title: Command Reference
nav_order: 3
---

# 🤖 OmenFusionAi_Bot Commands

This document provides a comprehensive guide to all available commands in OmenFusionAi_Bot.

## 🌟 Available Commands

### 🤖 General Commands
- `/start` - Start the bot and get a welcome message
- `/help` - Show the help menu with all available commands
- `/status` - Check the bot's current status

### 💬 Chat Commands
- `/chat` - Start a chat conversation with the bot
- `/clear_chat` - Clear your chat history
- `/export` - Export your chat history

### 🎨 Image Commands
- `/imagine` - Generate an image from a text description
- `/describe` - Analyze and describe an image
- `/enhance` - Enhance an image generation prompt

### 🔑 API Key Management
- `/setgroqapi` - Set your Groq API key for chat and image analysis
- `/setreplicateapi` - Set your Replicate API key for image generation

### 🛠️ Admin Commands
These commands are only available to administrators:
- `/maintenance` - Toggle maintenance mode
- `/broadcast` - Send a message to all users
- `/stats` - View bot usage statistics

## 📝 Command Details

### General Commands

#### `/start`
- Description: Initializes the bot and displays welcome message
- Usage: `/start`
- Example: `/start`

#### `/help`
- Description: Shows all available commands and their usage
- Usage: `/help`
- Example: `/help`

#### `/status`
- Description: Shows current bot status and settings
- Usage: `/status`
- Example: `/status`

### Chat Commands

#### `/chat`
- Description: Start or continue a chat conversation
- Usage: `/chat [message]`
- Example: `/chat Tell me about AI`

#### `/clear_chat`
- Description: Clear your chat history
- Usage: `/clear_chat`
- Example: `/clear_chat`

#### `/export`
- Description: Export your chat history
- Usage: `/export`
- Example: `/export`

### Image Commands

#### `/imagine`
- Description: Generate an image from text description
- Usage: `/imagine [description]`
- Example: `/imagine a sunset over mountains`

#### `/describe`
- Description: Analyze and describe an image
- Usage: Reply to an image with `/describe`
- Example: `/describe` (as reply to image)

#### `/enhance`
- Description: Enhance an image generation prompt
- Usage: `/enhance [prompt]`
- Example: `/enhance sunset over mountains`

### API Key Management

#### `/setgroqapi`
- Description: Set your personal Groq API key
- Usage: `/setgroqapi [API_KEY]`
- Note: Message will be deleted immediately for security
- Example: `/setgroqapi abc123...`

#### `/setreplicateapi`
- Description: Set your personal Replicate API key
- Usage: `/setreplicateapi [API_KEY]`
- Note: Message will be deleted immediately for security
- Example: `/setreplicateapi xyz789...`

### Admin Commands

#### `/maintenance`
- Description: Toggle maintenance mode
- Usage: `/maintenance [on/off] [message]`
- Example: `/maintenance on Updating systems`

#### `/broadcast`
- Description: Send message to all users
- Usage: `/broadcast [message]`
- Example: `/broadcast Bot will be updated tonight`

#### `/stats`
- Description: View bot usage statistics
- Usage: `/stats`
- Example: `/stats`

## 🔒 Security Notes

- API key commands will automatically delete your message
- Keys are stored securely in memory only
- Keys are not persisted between bot restarts
- Admin commands require proper authentication
