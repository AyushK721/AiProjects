
from google import genai

# ==========================================
# CONFIG
# ==========================================

API_KEY = "AQ.Ab8RN6JLxdG0kjQg0lMS9kymvoJLG2_ruYE1zim7zSItBv-ztA"

SYSTEM_PROMPT = """
You are the Architect of Doom.

Rules:
- Start by describing a unique, highly specific funny, but deadly situation.
- The player will tell you what they do.
- Judge whether they LIVE or DIE.
- If they LIVE:
  - Describe how they survive.
  - Immediately present a NEW deadly situation.
- If they DIE:
  - Describe their demise.
  - End your response with exactly:
    GAME OVER
- make sure it isn't super hard to survive
- dont just say that their idea doesnt work, only fail them if they're move isn't good enough, it will always work, but not always save them.
- sometimes, if they're idea is funny but wouldn't actually work, let it work, its supposed to be a funny unserious game, although still makae it possible to fail but make it a bit harder to fail
- keep everything to about 2-3 sentences, make sure you dont have to scroll to much so use line breaks every now and then
- make it so it gets harder to survive each repeat  
"""

# ==========================================
# SETUP
# ==========================================
score = 0

client = genai.Client(api_key=API_KEY)

chat_history = [
    {
        "role": "user",
        "parts": [{"text": SYSTEM_PROMPT}]
    }
]

print("\n--- WELCOME TO THE ARCHITECT OF DOOM ---\n"
      "\n(This game is super easy, chances are you wont lose, have fun and be creative!)")

# Start the game
start_prompt = "Start the game. What is my first deadly situation?"

chat_history.append(
    {
        "role": "user",
        "parts": [{"text": start_prompt}]
    }
)

response = client.models.generate_content(
    model="gemini-3.1-flash-lite",
    contents= chat_history
)

print("THE ARCHITECT:")
print(response.text)
print()

chat_history.append(
    {
        "role": "model",
        "parts": [{"text": response.text}]
    }
)

# ==========================================
# GAME LOOP
# ==========================================

while True:
    move = input("YOUR MOVE: ").strip()

    if move.lower() in ("quit", "exit"):
        print("Thanks for playing.")
        break

    chat_history.append(
        {
            "role": "user",
            "parts": [{"text": move}]
        }
    )

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents = chat_history
    )

    reply = response.text

    print("\nTHE ARCHITECT:")
    print(reply)
    print()

    chat_history.append(
        {
            "role": "model",
            "parts": [{"text": reply}]
        }
    )
    score += 1
    print("Score: " + str(score))
    if "GAME OVER" in reply.upper():
        break
