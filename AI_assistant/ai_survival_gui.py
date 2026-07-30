
import tkinter as tk
from tkinter import scrolledtext
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

MODEL_NAME = "gemini-3.1-flash-lite"

# ==========================================
# GEMINI SETUP
# ==========================================

client = genai.Client(api_key=API_KEY)

chat_history = [
    {
        "role": "user",
        "parts": [{"text": SYSTEM_PROMPT}]
    }
]

score = 0
game_over = False

# ==========================================
# GUI
# ==========================================

root = tk.Tk()
root.title("Architect of Doom")
root.geometry("850x650")

title_label = tk.Label(
    root,
    text="ARCHITECT OF DOOM",
    font=("Arial", 18, "bold")
)
title_label.pack(pady=10)

score_var = tk.StringVar(value="Score: 0")

score_label = tk.Label(
    root,
    textvariable=score_var,
    font=("Arial", 12)
)
score_label.pack()

chat_box = scrolledtext.ScrolledText(
    root,
    wrap=tk.WORD,
    font=("Consolas", 11)
)
chat_box.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

chat_box.insert(
    tk.END,
    "Welcome to the Architect of Doom!\n"
    "(This game is super easy, chances are you won't lose. "
    "Have fun and be creative!)\n\n"
)
chat_box.config(state="disabled")

bottom_frame = tk.Frame(root)
bottom_frame.pack(fill=tk.X, padx=10, pady=10)

input_box = tk.Entry(
    bottom_frame,
    font=("Arial", 12)
)
input_box.pack(side=tk.LEFT, fill=tk.X, expand=True)

send_button = tk.Button(
    bottom_frame,
    text="Send",
    width=12
)
send_button.pack(side=tk.LEFT, padx=5)

# ==========================================
# HELPERS
# ==========================================

def add_message(sender, text):
    chat_box.config(state="normal")
    chat_box.insert(tk.END, f"{sender}:\n{text}\n\n")
    chat_box.see(tk.END)
    chat_box.config(state="disabled")

def get_ai_response(user_text):
    global chat_history

    chat_history.append(
        {
            "role": "user",
            "parts": [{"text": user_text}]
        }
    )

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=chat_history
    )

    reply = response.text

    chat_history.append(
        {
            "role": "model",
            "parts": [{"text": reply}]
        }
    )

    return reply

def send_message(event=None):
    global score
    global game_over

    if game_over:
        return

    user_text = input_box.get().strip()

    if not user_text:
        return

    input_box.delete(0, tk.END)

    add_message("YOU", user_text)

    try:
        reply = get_ai_response(user_text)

        add_message("THE ARCHITECT", reply)

        score += 1
        score_var.set(f"Score: {score}")

        if "GAME OVER" in reply.upper():
            game_over = True

            input_box.config(state="disabled")
            send_button.config(state="disabled")

            add_message(
                "SYSTEM",
                f"Final Score: {score}"
            )

    except Exception as e:
        add_message("ERROR", str(e))

# ==========================================
# START GAME
# ==========================================

try:
    start_prompt = "Start the game. What is my first deadly situation?"

    first_reply = get_ai_response(start_prompt)

    add_message("THE ARCHITECT", first_reply)

except Exception as e:
    add_message("ERROR", str(e))

# ==========================================
# EVENTS
# ==========================================

send_button.config(command=send_message)
input_box.bind("<Return>", send_message)

input_box.focus()

root.mainloop()
