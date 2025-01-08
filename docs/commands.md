---
layout: default
title: Command Reference
nav_order: 3
---

# 🤖 AIFusionBot Commands

This document provides a comprehensive guide to all available commands in AIFusionBot.

# Bot Commands

Try these commands with our live bot: [@AIFusionCom_Bot](https://t.me/AIFusionCom_Bot)

## Getting Started
- `/start` - Start the bot
- `/help` - Show available commands

## 🎯 General Commands 

### 🚀 /start
Starts the bot and displays welcome message.
- Usage: `/start`
- Response: Welcome message with basic instructions

### ❓ /help
Shows all available commands organized by category.
- Usage: `/help`
- Response: List of commands with descriptions

### 💭 /chat
Start a conversation with the AI.
- Usage: `/chat <your message>`
- Example: `/chat Tell me about quantum computing`
- Response: AI-generated response

## 🎨 Image Commands 

### 🖼️ /imagine
Generate an image from text description.
- Usage: `/imagine <description>`
- Example: `/imagine sunset over mountains with purple sky`
- Response: AI-generated image

### ✨ /enhance
Improve the last image generation prompt.
- Usage: `/enhance`
- Response: Enhanced version of previous image

### 🔍 /describe
Generate caption for an image.
- Usage: Send image followed by `/describe`
- Response: AI-generated image description

## 📸 Image Analysis Commands

### Direct Image Interaction
When you send an image to the bot, you'll get an interactive menu with two options:
- 📝 **Describe Image**: Get a detailed analysis using Groq's LLaMA model
- 🔍 **Generate Caption**: Get a creative caption using Replicate

### Image Analysis Commands
- `/describe` - Analyze an image in detail
  - Reply to any image with this command
  - Uses Groq's LLaMA model for detailed analysis
  - Supports voice output if enabled
  - Example: Reply to an image with `/describe`

- `/caption` - Generate a creative caption
  - Reply to any image with this command
  - Uses Replicate for creative captions
  - Example: Reply to an image with `/caption`

### Image Generation
- `/imagine` - Generate images from text descriptions
  - Uses Replicate's Recraft v3 model
  - Example: `/imagine a beautiful sunset over mountains`

## 🔊 Audio Commands 

### 🎵 /transcribe
Convert speech to text.
- Usage: Send voice message or audio file with `/transcribe`
- Response: Text transcription

### 🗣️ /voice
Convert text to speech.
- Usage: `/voice <text>`
- Example: `/voice Hello, how are you?`
- Response: Voice message

### 📝 /formats
Show available audio formats.
- Usage: `/formats`
- Response: List of supported formats

### 🌎 /lang
Show supported languages.
- Usage: `/lang`
- Response: List of supported languages

## 📊 Status Commands

### 🔔 /subscribe
Subscribe to bot status notifications. You will receive alerts when:
- 🔴 Bot goes offline due to errors
- 🟢 Bot comes back online
- 🛠️ System maintenance starts/ends
- 📢 Critical updates or changes

### 🔕 /unsubscribe
Unsubscribe from bot status notifications.

## ⚙️ Settings Commands 

### 🛠️ /settings
View current bot settings.
- Usage: `/settings`
- Response: Current configuration

### 🗑️ /togglevoice
Toggle voice responses on/off.
- Usage: `/togglevoice`
- Response: Confirmation message

## 📺 Media Management Commands 

### 📹 /videos
List downloaded videos.
- Usage: `/videos`
- Response: List of saved videos

### 🗑️ /clear
Clear all downloaded videos.
- Usage: `/clear`
- Response: Confirmation message

## 🚨 Error Handling

If a command fails:
1. Check command syntax
2. Verify required API keys are set
3. Check bot status 
4. Try again after a few moments

## 💡 Tips for Best Results

1. **Chat Commands**
   - Be clear and specific
   - Use proper punctuation
   - Maintain context within sessions

2. **Image Generation**
   - Use descriptive prompts
   - Try `/enhance` for better results
   - Be specific about style and details

3. **Audio Processing**
   - Use clear audio for transcription
   - Speak clearly for voice messages
   - Check supported formats

## ⚡ Rate Limits

- 🎨 Image generation: 50 requests per hour
- 💭 Chat messages: 100 per hour
- 🔊 Audio processing: 25 per hour

## ❓ Need Help?

If you need assistance:
1. Use `/help` for command list
2. Check documentation
3. Report issues on GitHub
