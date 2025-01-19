import base64
import requests
from groq import Groq
import os
from dotenv import load_dotenv

class ImageCaptioner:
    def __init__(self):
        load_dotenv()
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        self.groq_client = Groq(api_key=self.groq_api_key)
        
    async def generate_caption(self, image_url, prompt=None):
        """
        Generate a caption for an image using Groq
        
        Args:
            image_url (str): URL of the image or base64 encoded image data
            prompt (str, optional): Custom prompt for the caption. Defaults to a general description request.
        
        Returns:
            tuple: (success, caption or error message)
        """
        try:
            if not prompt:
                prompt = "Please give me a caption for this image in not more than 20 words. Focus on the main elements and mood."
            
            # Create messages for the API call
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        }
                    ]
                }
            ]
            
            # Make the API call
            chat_completion = self.groq_client.chat.completions.create(
                messages=messages,
                model="llama-3.2-11b-vision-preview",
                temperature=0.3,
                max_tokens=100
            )
            
            caption = chat_completion.choices[0].message.content.strip()
            return True, caption
            
        except Exception as e:
            return False, f"Error generating caption: {str(e)}"
