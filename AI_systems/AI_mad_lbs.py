# The following program generates an AI-based Mad Libs Story
from openai import OpenAI

OPENAI_API_KEY = "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"

client = OpenAI(api_key=OPENAI_API_KEY)

prompts = [
    "an emotion",
    "a color",
    "a noun",
    "an adjective",
    "a verb (past tense)",
    "a plural noun",
    "a type of food",
    "another adjective",
    "a verb",
    "a noun (plural)",
    "an occupation",
    "an type of animal",
    "an adjective",
    "a verb (past tense)",
    "a noun",
    "a name",
    "another name"
]

list_of_words = []

for item in prompts:
    user_input = input(f"Enter {item}: ").strip()
    list_of_words.append(user_input)

word_list = "\n".join([f"{i+1}.{word}" for i, word in enumerate(list_of_words)])

prompt = {
    "Generate a funny, kid-friendly, two-paragraph Mad Libs story using the 17 words. \n"
    "Use each word at least once. \n"
    "Do not list the words. Write a story."
}

response = client.responses.create(
    model="gpt-4o-mini",
    input=f"{prompt}\n\nHere are the 17 words:\n{word_list}"
)
print("\nYour Story:\n")
print(response.output_text.strip())