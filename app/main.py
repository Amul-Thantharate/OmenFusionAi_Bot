import requests
from PIL import Image
from io import BytesIO
import time
import os
from dotenv import load_dotenv
import logging
from groq import Groq
from fpdf import FPDF
from typing import Optional
from together import Together  # Import Together library

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()

def generate_image(prompt: str) -> tuple[bool, bytes, str]:
    """
    Generate an image using the configured API.
    
    Args:
        prompt (str): The description of the image to generate
    
    Returns:
        tuple[bool, bytes, str]: (success, image_bytes, message) where success is True if image was generated,
                                image_bytes contains the raw image data, and message contains status info
    """
    try:
        url = "https://api.airforce/v1/imagine2"
        headers = {
            "Content-Type": "application/json"
        }
        
        params = {'prompt': prompt}
        start = time.time()
        
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code != 200:
            return False, None, f"API request failed with status code: {response.status_code}"

        elapsed_time = time.time() - start
        return True, response.content, f"Image generated in {elapsed_time:.2f} seconds"

    except Exception as e:
        logger.error(f"Error generating image: {str(e)}")
        return False, None, f"Error generating image: {str(e)}"

def generate_image_together(prompt: str, api_key: str = None) -> tuple[bool, bytes, str]:
    """
    Generate an image using Together's API.
    
    Args:
        prompt (str): The description of the image to generate
        api_key (str): The Together API key for authentication
    
    Returns:
        tuple[bool, bytes, str]: (success, image_bytes, message)
    """
    try:
        if not api_key:
            return False, None, "Please set your Together API key using /settogetherkey command"

        client = Together(api_key=api_key)
        start = time.time()
        
        response = client.images.generate(
            prompt=prompt,
            model="black-forest-labs/FLUX.1-schnell-Free",
            width=1024,
            height=768,
            steps=1,
            n=1,
            response_format="b64_json"
        )
        
        import base64
        image_bytes = base64.b64decode(response.data[0].b64_json)
        
        elapsed_time = time.time() - start
        return True, image_bytes, f"Image generated in {elapsed_time:.2f} seconds using Together AI"

    except Exception as e:
        logger.error(f"Error generating image with Together: {str(e)}")
        if "Invalid API key" in str(e):
            return False, None, "Invalid Together API key. Please check your key and try again."
        return False, None, f"Error generating image: {str(e)}"

def interactive_chat(text: str, temperature: float = 0.7, max_tokens: int = 1024, 
                    model_type: str = "groq", stream: bool = False, api_key: str = None):
    """
    Chat with the Groq AI model.
    
    Args:
        text (str): The user's message
        temperature (float): Controls randomness in the response
        max_tokens (int): Maximum number of tokens in the response
        model_type (str): The model to use (currently only supports "groq")
        stream (bool): Whether to stream the response
        api_key (str): The Groq API key for authentication
        
    Returns:
        str: The AI's response
    """
    try:
        if not api_key:
            return "Please set your Groq API key using /setgroqkey command"

        client = Groq(api_key=api_key)
        
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            model="llama3-8b-8192",
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=1,
            stream=stream
        )
        
        if stream:
            # For streaming responses, return a generator
            return (chunk.choices[0].delta.content for chunk in response)
        else:
            # For non-streaming responses, return the complete text
            return response.choices[0].message.content
            
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        if "Invalid API key" in str(e):
            return "Invalid Groq API key. Please check your key and try again."
        return f"Sorry, I encountered an error: {str(e)}"

def save_chat_history(history: list, format: str = "markdown") -> tuple[bool, str, Optional[bytes]]:
    """
    Save chat history in the specified format.
    
    Args:
        history (list): List of chat messages
        format (str): Format to save in ("markdown" or "pdf")
    
    Returns:
        tuple[bool, str, Optional[bytes]]: (success, message, file_bytes)
    """
    try:
        if not history:
            return False, "No chat history to export.", None

        # Convert history to markdown format
        markdown_content = "# O-Chat History\n\n"
        for msg in history:
            role = "🤖 Assistant" if msg["role"] == "assistant" else "👤 You"
            markdown_content += f"### {role}:\n{msg['content']}\n\n"

        if format.lower() == "markdown":
            return True, "Chat history exported as Markdown.", markdown_content.encode('utf-8')
        
        elif format.lower() == "pdf":
            # Create PDF using FPDF
            pdf = FPDF()
            pdf.add_page()
            
            # Set font for title
            pdf.set_font("Arial", "B", 24)
            pdf.cell(0, 20, "O-Chat History", ln=True, align="C")
            pdf.ln(10)
            
            # Set font for content
            pdf.set_font("Arial", size=12)
            
            # Add each message
            for msg in history:
                role = "🤖 Assistant:" if msg["role"] == "assistant" else "👤 You:"
                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, role, ln=True)
                
                pdf.set_font("Arial", size=12)
                # Split content into lines to handle long messages
                lines = msg["content"].split('\n')
                for line in lines:
                    # Split long lines
                    while len(line) > 0:
                        chunk = line[:90]  # Max chars per line
                        line = line[90:]
                        pdf.multi_cell(0, 10, chunk)
                pdf.ln(5)
            
            return True, "Chat history exported as PDF.", pdf.output(dest='S').encode('latin1')
        
        else:
            return False, f"Unsupported format: {format}", None

    except Exception as e:
        logger.error(f"Error saving chat history: {str(e)}")
        return False, f"Error saving chat history: {str(e)}", None
