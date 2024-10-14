import os
import openai

# 从环境变量中获取 API 密钥
api_key = os.getenv('OPENAI_API_KEY').split(';')[1]


class Client:
    def __init__(self, model='gpt-4o'):
        self.client = openai.OpenAI()
        self.client.api_key = api_key
        self.model = model

    def run(self, prompt):

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return completion.choices[0].message.content