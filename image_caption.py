import replicate
import os
from dotenv import load_dotenv

class ImageCaptioner:
    def __init__(self):
        load_dotenv()
        self.replicate_api_key = os.getenv('REPLICATE_API_KEY')
        if not self.replicate_api_key:
            raise ValueError("REPLICATE_API_KEY not found in environment variables")
        
    async def generate_caption(self, image_url, prompt=None):
        """
        Generate a caption for an image using Replicate's LLaVA model
        
        Args:
            image_url (str): URL of the image to caption
            prompt (str, optional): Custom prompt for the caption. Defaults to a general description request.
        
        Returns:
            tuple: (success, caption or error message)
        """
        try:
            if not prompt:
                prompt = "Please describe this image in detail. What do you see?"
                
            output = replicate.run(
                "yorickvp/llava-13b:80537f9eead1a5bfa72d5ac6ea6414379be41d4d4f6679fd776e9535d1eb58bb",
                input={
                    "image": image_url,
                    "top_p": 1,
                    "prompt": prompt,
                    "max_tokens": 1024,
                    "temperature": 0.2
                }
            )
            
            # Collect the streamed output
            caption = ""
            for item in output:
                caption += str(item)
            
            return True, caption.strip()
            
        except Exception as e:
            return False, f"Error generating caption: {str(e)}"
