# the following program creates an AI assistant that suggests restaurants.
import os
import json
from openai import OpenAI

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

client = OpenAI(api_key=OPENAI_API_KEY)
with open("dataset.json", "r", encoding="utf-8") as f:
    dataset = json.load(f)

database = dataset["database"]

dataset_text = json.dumps(database, indent = 2)

end_program = False

messages = [
    {
        "role": "system",
        "content": (
            "You are a restaurant recommendation assistant. "
            "Use the provided dataset as background context. \n\n"
            "Find the correct user using either name or user_numbers.\n"
            "Recommend one restaurant chain in their city that fits one of their listed cuisine and budget.\n"
            "Suggest 2-3 typical main dishes and 1 dessert. \n\n"
            "IMPORTANT:\n"
            "- The dataset does not contain ratings, neighborhood, or real menus.\n"
            "- Do NOT invent ratings or neighborhood information. \n"
            "- If asked for ratings or neighborhoods, say the dataset does not include that informatioon."
        )
    },
    {
            "role": "user",
            "content": ("Dataset context:\n" + dataset_text)
    }
]
while not end_program:
    user_input = input("Enter a prompt: ").strip()
    if user_input.lower() in ["goodbye", "exit"]:
        end_program = True
        print("Have a great day!")
    else:
        messages.append({"role": "user", "content": user_input})
        chat = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,  # type: ignore[arg-type]
        )
        assistant_response = (chat.choices[0].message.content or "").strip()
        messages.append({"role": "assistant", "content": assistant_response})
        print("Assistant: " + assistant_response)