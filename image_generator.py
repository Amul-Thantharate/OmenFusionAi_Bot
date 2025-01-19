import base64
from groq import Groq
from together import Together
from PIL import Image
import io
import os
import logging
import requests
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class AIImageGenerator:
    def __init__(self):
        load_dotenv(override=True)  # Force reload environment variables
        together_api_key = os.getenv('TOGETHER_API_KEY')
        groq_api_key = os.getenv('GROQ_API_KEY')

        if not together_api_key:
            raise ValueError("Together API key not found. Please set TOGETHER_API_KEY in your .env file")
        if not groq_api_key:
            raise ValueError("Groq API key not found. Please set GROQ_API_KEY in your .env file")

        # Set the API key for Together
        Together().api_key = together_api_key
        self.together_client = Together()
        self.groq_client = Groq(api_key=groq_api_key)
        self.last_enhanced_prompt = None

    def enhance_prompt(self, user_prompt):
        """Enhance the user's prompt using Groq LLM."""
        try:
            chat_completion = self.groq_client.chat.completions.create(
                messages=[{
                    "role": "system",
                    "content": "You are an advanced AI creative assistant (v2.0) specialized in enhancing image generation prompts. Transform user prompts into highly detailed, visually rich descriptions that leverage cutting-edge AI image generation capabilities. Focus on artistic elements including lighting, composition, style, mood, and technical aspects. Maintain conciseness while maximizing visual impact. IMPORTANT: Return only the enhanced prompt without any prefixes or explanatory text."
                },
                {
                    "role": "user",
                    "content": f"Enhance this image prompt: {user_prompt}"
                }],
                model="mixtral-8x7b-32768",  
                temperature=0.7,
                max_tokens=256
            )

            enhanced_prompt = chat_completion.choices[0].message.content.strip()
            prefixes_to_remove = [
                "Here's an enhanced version of the prompt:",
                "Enhanced prompt:",
                "Here's a more detailed version:",
                "Here's the enhanced prompt:"
            ]
            for prefix in prefixes_to_remove:
                if enhanced_prompt.startswith(prefix):
                    enhanced_prompt = enhanced_prompt[len(prefix):].strip()

            logger.info(f"Enhanced prompt: {enhanced_prompt}")
            self.last_enhanced_prompt = enhanced_prompt
            return enhanced_prompt
        except Exception as e:
            logger.error(f"Error enhancing prompt: {str(e)}")
            return None

    def generate_image(self, prompt):
        """Generate images using the Together AI API."""
        try:
            logger.info("Attempting to generate image with Together AI...")
            logger.info(f"Using prompt: {prompt}")

            response = self.together_client.images.generate(
                prompt=prompt,
                model="black-forest-labs/FLUX.1-schnell-Free",
                width=1024,
                height=768,
                steps=1,
                n=1,
                response_format="b64_json"
            )

            if response and hasattr(response, 'data') and len(response.data) > 0:
                image_data = response.data[0].b64_json
                logger.info("Successfully generated image")
                return True, image_data, ""
            else:
                error_msg = "No image data received from API"
                logger.error(error_msg)
                return False, None, error_msg

        except Exception as e:
            error_msg = f"Error generating image: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, None, error_msg

    def save_image(self, b64_json, filename):
        """Save the base64 encoded image to a file."""
        try:
            if not b64_json:
                logger.error("No image data to save")
                return False, "No image data to save"

            img_data = base64.b64decode(b64_json)
            img = Image.open(io.BytesIO(img_data))

            # Ensure the filename has a proper extension
            if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                filename += '.png'  # default to .png if no extension provided

            img.save(filename)
            logger.info(f"Successfully saved image to: {filename}")
            return True, "Image saved successfully"
        except Exception as e:
            error_msg = f"Error saving image: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
