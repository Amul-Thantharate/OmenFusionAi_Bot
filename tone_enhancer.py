from groq import AsyncGroq
import os
import asyncio
from typing import Optional
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

DEFAULT_PROMPT = "Make this text more attractive and professional in tone while making it more interesting and engaging."

class ToneEnhancer:
    def __init__(self):
        load_dotenv(override=True)  # Force reload environment variables
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        
        if not self.groq_api_key:
            raise ValueError("Groq API key not found. Please set GROQ_API_KEY in your .env file")
        
        self.last_enhanced_text = None

    async def enhance_text(self, text: str, prompt: str = DEFAULT_PROMPT) -> tuple[bool, str, str]:
        """
        Enhance the given text using Groq's LLM.
        
        Args:
            text (str): The text to enhance
            prompt (str, optional): Custom prompt for text enhancement
            
        Returns:
            tuple[bool, str, str]: (success, enhanced_text, error_message)
        """
        try:
            if not text:
                return False, "", "Text is required"

            if not prompt:
                prompt = DEFAULT_PROMPT

            logger.info(f"Enhancing text: {text[:100]}...")
            
            # Create Groq client for this request
            groq_client = AsyncGroq(api_key=self.groq_api_key)
            
            # Create the streaming response
            response = await groq_client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a text editor. You will be given a prompt and a text to edit. Edit the text to match the prompt, and only respond with the full edited version of the text - do not include any other information, context, or explanation. If you add on to the text, respond with the full version, not just the new portion. Do not include the prompt or otherwise preface your response. Do not enclose the response in quotes."
                    },
                    {
                        "role": "user",
                        "content": f"Prompt: {prompt}\nText: {text}"
                    }
                ],
                stream=True,
                max_tokens=1024,
                temperature=0.7
            )

            # Process the streaming response
            result = ""
            async for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    result += chunk.choices[0].delta.content

            self.last_enhanced_text = result
            logger.info(f"Enhanced text: {result[:100]}...")
            return True, result, ""

        except Exception as e:
            error_msg = f"Error enhancing text: {str(e)}"
            logger.error(error_msg)
            return False, "", error_msg

async def main():
    # Example usage
    enhancer = ToneEnhancer()
    success, result, error = await enhancer.enhance_text(
        text="A Boys playing basketball",
        prompt=DEFAULT_PROMPT
    )
    if success:
        print("Enhanced text:", result)
    else:
        print("Error:", error)

if __name__ == "__main__":
    asyncio.run(main())
