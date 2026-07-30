

from openai import OpenAI

OPENAI_API_KEY = "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"

client = OpenAI(api_key=OPENAI_API_KEY)

end_program = False

while not end_program:
    user_input = input("Enter a prompt: ").strip()

    if user_input.lower() in ["goodbye", "exit"]:
        end_program = True
        print("Have a great day!")
    else:
        prompt = (
            "You are a strict math assistant.\n"
            "Only answer math questions.\n"
            "If the user's message is not a math question, reply exactly:\n"
            "I only answer math questions.\n\n"
            f"User: {user_input}"
        )
        response = client.responses.create(
                    model = "gpt-4o-mini",
                    input = prompt
                )
        assistant_response = response.output_text.strip()
        print("Assistant: " + assistant_response)