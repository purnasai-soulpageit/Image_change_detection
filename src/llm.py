import os
from openai import OpenAI

from dotenv import load_dotenv
from pathlib import Path

print("loaded env file")
print(load_dotenv(Path("src\\.env")))


class LLmDescriptor():
    def __init__(self):
        self.api_key = os.getenv("api_key")
        self.client = OpenAI(api_key=self.api_key)
        self.model_choice=os.getenv("model")
        self.prompt = os.getenv("prompt")

    def prepare_content(self, croped_diff_imgs):
        content =  [{"type": "text", "text": self.prompt}]
        
        for crop_diff_img in croped_diff_imgs:
            input =     {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{crop_diff_img}"}
                        },
            content.extend(input)
        return content


    def get_image_description(self, content):

        response = self.client.chat.completions.create(
            model=self.model_choice,
            messages=[
                {
                    "role": "user",
                    "content": content
                }
            ],
            max_tokens=300,
        )

        # Extract and return the description
        return response.choices[0].message.content