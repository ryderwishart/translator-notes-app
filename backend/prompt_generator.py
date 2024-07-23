class PromptGenerator:
    def __init__(self, chroma_manager, bible_manager):
        self.chroma_manager = chroma_manager
        self.bible_manager = bible_manager

    def generate_prompt(self, user_query: str, verse_reference: str) -> str:
        bible_verse = self.bible_manager.get_verse(verse_reference)
        relevant_docs = self.chroma_manager.query(user_query, n_results=10)
        template_docs = relevant_docs.get('template_docs', [])

        relevant_examples = '\n'.join(relevant_docs)
        example_templates = '\n'.join(template_docs)

        prompt = (
            f"User Query: {user_query}\n\n"
            f"Bible Verse:\n{verse_reference}: {bible_verse}\n\n"
            f"Relevant Examples:\n{relevant_examples}\n\n"
            f"Example templates (adapt this style):\n{example_templates}\n\n"
            "Note that some of the templates may be more relevant than others, "
            "and you should address specific nuances of each verse.\n"
            "Based on the user query, the Bible verse, and the relevant examples, "
            "please provide a thoughtful response using the style and register of "
            "the template docs provided. Do not add any additional comments; only return "
            "the new notes.\n\n"
            "NEW TRANSLATOR NOTES:\n"
        )

        return prompt
