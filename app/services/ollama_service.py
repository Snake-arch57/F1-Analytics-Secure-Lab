import os
import requests
import json

class OllamaService:
    def __init__(self):
        # Mantemos o nome da classe para não quebrar o seu ChatController
        self.api_key = os.getenv('GROQ_API_KEY')
        self.model = os.getenv('GROQ_MODEL', 'llama3-8b-8192')
        self.base_url = 'https://api.groq.com/openai/v1/chat/completions'

    def generate_response_stream(self, user_prompt, context_data=None, system_prompt=None):
        if not self.api_key:
            yield "⚠️ ERRO: A chave GROQ_API_KEY não foi configurada corretamente no arquivo .env!"
            return

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        messages = []
        
        if not system_prompt:
            system_prompt = "Você é um analista especialista em Fórmula 1. Responda com base estritamente nos dados fornecidos."
            
        if context_data:
            system_prompt += f"\n\n[DADOS DE CONTEXTO DO BANCO]:\n{context_data}"

        messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True
        }

        try:
            with requests.post(self.base_url, headers=headers, json=payload, stream=True, timeout=60) as response:
                if response.status_code != 200:
                    yield f"\n🛑 [ERRO GROQ {response.status_code}]: {response.text}"
                    return
                
                for line in response.iter_lines():
                    if line:
                        line_text = line.decode('utf-8')
                        if line_text.startswith('data: '):
                            data_str = line_text[6:]
                            if data_str.strip() == '[DONE]':
                                break
                            try:
                                json_data = json.loads(data_str)
                                delta = json_data['choices'][0]['delta']
                                if 'content' in delta:
                                    yield delta['content']
                            except Exception:
                                pass
        except Exception as e:
            yield f"\n💥 [FALHA DE CONEXÃO COM A GROQ]: {e}"
