from typing import Dict, Any
import requests

class OllamaService:
    def __init__(self, base_url: str = "http://localhost:11434/api/generate"):
        self.base_url = base_url

    async def analyze_medical_text(self, text: str) -> Dict[str, Any]:
        prompt = f"""
        Create an HTML table from this medical test data with 4 columns:
        Параметр | Значение | Единица измерения | Нормальный уровень
        
        Medical text to analyze:
        {text}
        """
        
        response = requests.post(
            self.base_url,
            json={
                "model": "llama2",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 1024
                }
            }
        )
        return response.json()
