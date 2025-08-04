import asyncio
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

async def test_grok():
    api_key = os.getenv('GROK_API_KEY')
    print(f"API Key: {api_key[:10] if api_key else 'None'}...")
    
    if not api_key:
        print("No API key found!")
        return
    
    async with aiohttp.ClientSession() as session:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': 'grok-3-fast',
            'messages': [{'role': 'user', 'content': 'Hello'}],
            'max_tokens': 50
        }
        
        try:
            async with session.post('https://api.x.ai/v1/chat/completions', 
                                  headers=headers, json=payload) as response:
                print(f"Status: {response.status}")
                text = await response.text()
                print(f"Response: {text}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_grok())