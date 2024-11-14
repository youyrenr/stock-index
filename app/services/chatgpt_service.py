import httpx
from typing import Dict, Any

class ChatGPTService:
    def __init__(self):
        self.api_key = "sk-xXnHiArpp5sZtPyd1117624046C4464cA60bB2A66eFbB1Bd"
        self.base_url = "https://chatapi.midjourney-vip.cn/v1"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    async def create_completion(self, messages: list,
                              model: str = "gpt-4o-mini",
                              temperature: float = 0.9,
                              max_tokens: int = 1000) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json={
                        "model": model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    },
                    timeout=300.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                raise Exception(f"HTTP error occurred: {str(e)}")
            except Exception as e:
                raise Exception(f"An error occurred: {str(e)}")