import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class LLMInterface:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def get_completion(self, prompt):
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You draft wise, experienced, linguistically informed translation notes from an evangelical perspective. The purpose of these notes is to assist translators in avoiding cross-cultural and linguistic misunderstanding while translating the Bible into new languages. The template documents are especially important, as they provide a style and register for the notes to follow. These notes will be used by translators to inform their translation work, so they should be helpful and informative for this serious task."},
                {"role": "user", "content": prompt}
            ],
            n=1,
            temperature=0.8,
        )
        return response.choices[0].message.content.strip()
