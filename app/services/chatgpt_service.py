import httpx
from typing import Dict, Any

class ChatGPTService:
    def __init__(self):
        self.api_key = "sk-xXnHiArpp5sZtPyd1117624046C4464cA60bB2A66eFbB1Bd"
        self.api_key2 = "sk-V5VZhXji4hKeB0zd37IudJ9gy6TAcFWLSolAbQDdDMyroK97"
        self.base_url = "https://chatapi.midjourney-vip.cn/v1"
        self.base_url2 = "https://api.aikeji.vip/v1"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        self.headers2 = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key2}"
        }

    def _get_base_url(self, model: str) -> str:
        return self.base_url2 if "gemini" in model.lower() else self.base_url

    def _get_header(self, model: str) -> dict:
        return self.headers2 if "gemini" in model.lower() else self.headers

    def _get_max_token(self, model: str) -> int:
        return 500000 if "gemini" in model.lower() else 5000

    async def create_completion(self, messages: list,
                              model: str = "gpt-4o-mini",  # 默认模型
                              temperature: float = 0.85) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            try:
                base_url = self._get_base_url(model)
                max_tokens = self._get_max_token(model)

                response = await client.post(
                    f"{base_url}/chat/completions",
                    headers=self._get_header(model),
                    json={
                        "model": model,
                        "messages": messages,
                        "temperature": temperature
                    },
                    timeout=300.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                raise Exception(f"HTTP error occurred: {str(e)}")
            except Exception as e:
                raise Exception(f"An error occurred: {str(e)}")