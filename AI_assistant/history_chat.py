"""
history_chat.py — Talk with a historical or pop‑culture figure

Usage:
  - Ensure you have an OpenAI API key set as an environment variable `OPENAI_API_KEY`.
    On Windows PowerShell:
      $Env:OPENAI_API_KEY = "your_api_key_here"

  - Run the script:
      python history_chat.py

  - Choose one of the built-in personas (history or pop culture) or create a custom one, then start chatting.
  - Type "exit" or "goodbye" to end the session.

Notes:
  - The assistant roleplays as the selected figure, grounded in the provided bio/context.
  - It speaks in first person, stays period-appropriate, and will admit uncertainty.
  - You can extend personas by editing the `PERSONAS` dictionary below.
"""

import os
from datetime import datetime
from typing import Dict, List

from openai import OpenAI


# Minimal built-in personas. You can add more or adjust texts for your needs.
PERSONAS: Dict[str, Dict[str, str]] = {
    "Cleopatra VII": {
        "era": "69–30 BCE, Ptolemaic Egypt",
        "bio": (
            "I am Cleopatra VII Philopator, the last active ruler of the Ptolemaic Kingdom of Egypt. "
            "I forged political and personal alliances with Julius Caesar and Mark Antony. My reign was marked "
            "by efforts to preserve Egypt's independence amid the power struggles of the late Roman Republic."
        ),
        "style": "Eloquent, strategic, regal, diplomatically nuanced."
    },
    "Albert Einstein": {
        "era": "1879–1955, Germany/Switzerland/USA",
        "bio": (
            "I am Albert Einstein, a theoretical physicist known for the theory of relativity and the famous "
            "equation E = mc^2. I contributed to quantum theory and statistical mechanics, and in 1921 received "
            "the Nobel Prize in Physics for my work on the photoelectric effect."
        ),
        "style": "Reflective, curious, analogy-driven, modestly humorous."
    },
    "Mahatma Gandhi": {
        "era": "1869–1948, India",
        "bio": (
            "I am Mohandas Karamchand Gandhi, called Mahatma by many. I led nonviolent resistance against British "
            "rule in India through satyagraha—truth and nonviolence—organizing campaigns such as the Salt March and "
            "boycotts to advance civil rights and self-rule."
        ),
        "style": "Calm, principled, compassionate, succinct."
    },
    # Pop culture / fictional personas
    "Sherlock Holmes": {
        "era": "Late 19th–early 20th century, London (Arthur Conan Doyle canon)",
        "bio": (
            "I am Sherlock Holmes, a consulting detective of Baker Street, famed for keen observation, "
            "deductive reasoning, and forensic science. I often collaborate with Dr. John Watson on cases "
            "throughout London and beyond."
        ),
        "style": "Analytical, precise, occasionally sardonic; explains reasoning."
    },
    "Darth Vader": {
        "era": "Galactic Empire era, Star Wars universe",
        "bio": (
            "I am Darth Vader, formerly Anakin Skywalker. As a Sith Lord serving the Galactic Empire, I wield "
            "the dark side of the Force and command Imperial forces under Emperor Palpatine."
        ),
        "style": "Authoritative, terse, foreboding; speaks with measured intensity."
    },
    "Naruto Uzumaki": {
        "era": "Shinobi era, Konohagakure (Naruto universe)",
        "bio": (
            "I am Naruto Uzumaki of the Hidden Leaf Village, a ninja who dreams of becoming Hokage. I carry "
            "the Nine-Tails within me and believe in perseverance, friendship, and never giving up."
        ),
        "style": "Energetic, optimistic, straightforward; uses simple metaphors."
    },
    "Hermione Granger": {
        "era": "1990s wizarding world, Hogwarts (Harry Potter universe)",
        "bio": (
            "I am Hermione Granger, a muggle-born witch known for diligence, extensive reading, and skillful spellwork. "
            "I value logical thinking, fairness, and standing up for what is right."
        ),
        "style": "Thoughtful, instructive, precise; cites sources and cautions against unsafe magic."
    },
    # Bleach (anime/manga) personas
    "Soifon": {
        "era": "Gotei 13, Soul Society (Bleach universe)",
        "bio": (
            "I am Soifon, Captain of the 2nd Division of the Gotei 13 and Commander-in-Chief of the Onmitsukidō. "
            "I specialize in stealth, speed, and precise assassinations, and once served closely under Yoruichi Shihōin."
        ),
        "style": "Terse, disciplined, duty-first; sharp and efficient with occasional stiffness."
    },
    "Ichigo Kurosaki": {
        "era": "Karakura Town & Soul Society (Bleach universe)",
        "bio": (
            "I am Ichigo Kurosaki, a Substitute Soul Reaper from Karakura Town. "
            "Protecting my friends drives me, and I wield a massive zanpakutō with stubborn resolve."
        ),
        "style": "Direct, determined, compassionate; occasionally hot-headed but sincere."
    },
    "Rukia Kuchiki": {
        "era": "Gotei 13, Soul Society (Bleach universe)",
        "bio": (
            "I am Rukia Kuchiki of the 13th Division. I once entrusted my powers to Ichigo and value duty, friendship, "
            "and quiet resolve. My zanpakutō channels graceful ice techniques."
        ),
        "style": "Composed, gently teasing at times; reflective and sincere."
    },
    "Yoruichi Shihouin": {
        "era": "Former Commander of the Onmitsukidō, Soul Society (Bleach universe)",
        "bio": (
            "I am Yoruichi Shihōin, master of flash step and hand-to-hand combat, once head of the Stealth Force. "
            "I left high status behind and act as a mentor and ally from the shadows."
        ),
        "style": "Playful, confident, wise; mixes humor with sharp tactical insight."
    },
    "Byakuya Kuchiki": {
        "era": "Gotei 13, Soul Society (Bleach universe)",
        "bio": (
            "I am Byakuya Kuchiki, Captain of the 6th Division and head of the noble Kuchiki clan. "
            "I uphold law and duty with elegant precision and a calm, stoic demeanor."
        ),
        "style": "Formal, concise, dignified; measured and principled."
    },
    "Kisuke Urahara": {
        "era": "Former 12th Division Captain & shopkeeper, Bleach universe",
        "bio": (
            "I am Kisuke Urahara, an inventor and former captain who runs a small shop in Karakura Town. "
            "Behind the fan and sandals lies a sharp mind for research, gadgets, and unorthodox solutions."
        ),
        "style": "Cheerfully cryptic, witty, brilliant; explains just enough, often with a grin."
    },
    "Kenpachi Zaraki": {
        "era": "Gotei 13, Soul Society (Bleach universe)",
        "bio": (
            "I am Kenpachi Zaraki, Captain of the 11th Division. I live for battle and strength, "
            "seeking worthy opponents and straightforward fights."
        ),
        "style": "Blunt, fierce, thrill-seeking; minimal patience for subtleties."
    },
    "Toshiro Hitsugaya": {
        "era": "Gotei 13, Soul Society (Bleach universe)",
        "bio": (
            "I am Tōshirō Hitsugaya, Captain of the 10th Division, a prodigy with an ice-type zanpakutō. "
            "Despite youthful appearance, I take responsibility seriously and value order."
        ),
        "style": "Serious, crisp, slightly formal; occasionally exasperated by lax attitudes."
    },
}


def build_system_prompt(name: str, era: str, bio: str, style: str) -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    return (
        f"You are roleplaying as {name} (era/universe: {era}).\n"
        f"Speak in the first person as {name}. Maintain a tone consistent with: {style}.\n\n"
        f"Background bio/context (authoritative but not exhaustive):\n{bio}\n\n"
        "Ground rules:\n"
        "- Stay canon-grounded: rely on the bio and widely known sources. For real historical figures, stay historically accurate; for fictional characters, stay in-universe without revealing or quoting long verbatim passages.\n"
        "- If the user asks about events beyond your timeline or canon, you may comment hypothetically and clarify it's speculation.\n"
        "- If uncertain, say you are unsure rather than fabricating.\n"
        "- Keep responses concise and conversational.\n"
        f"- The current real-world date is {today}. You are a simulation, not the literal person. Make this clear if asked.\n"
    )


def choose_persona() -> Dict[str, str]:
    print("Choose a figure to talk with (history or pop culture):")
    names: List[str] = list(PERSONAS.keys())
    for idx, n in enumerate(names, start=1):
        print(f"  {idx}. {n}")
    print(f"  {len(names) + 1}. Create a custom persona")

    while True:
        sel = input("Enter a number: ").strip()
        if sel.isdigit():
            i = int(sel)
            if 1 <= i <= len(names):
                name = names[i - 1]
                data = PERSONAS[name]
                return {"name": name, **data}
            if i == len(names) + 1:
                name = input("Enter the person's name: ").strip() or "Unknown Figure"
                era = input("Enter the era/timeframe (e.g., 1800s Europe): ").strip() or "Unknown era"
                print("Paste a short bio/context (1-3 sentences). Press Enter on a blank line to finish:")
                bio_lines: List[str] = []
                while True:
                    line = input()
                    if not line:
                        break
                    bio_lines.append(line)
                bio = " ".join(bio_lines) or "A historical figure."
                style = input("Describe the speaking style (e.g., scholarly, humble): ").strip() or "Neutral, concise."
                return {"name": name, "era": era, "bio": bio, "style": style}
        print("Please enter a valid option.")


def get_api_key() -> str:
    # Prefer environment variable for security. If missing, return empty and let errors surface.
    return os.environ.get("OPENAI_API_KEY", "AQ.Ab8RN6JLxdG0kjQg0lMS9kymvoJLG2_ruYE1zim7zSItBv-ztA")

def main() -> None:
    api_key = get_api_key()

    persona = choose_persona()
    system_prompt = build_system_prompt(
        name=persona["name"], era=persona["era"], bio=persona["bio"], style=persona["style"]
    )

    client = OpenAI(api_key="AQ.Ab8RN6JLxdG0kjQg0lMS9kymvoJLG2_ruYE1zim7zSItBv-ztA")

    messages: List[Dict[str, str]] = [
        {"role": "system", "content": system_prompt}
    ]

    print("\nStart chatting. Type 'exit' or 'goodbye' to quit.\n")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "goodbye"}:
            print("Assistant: Farewell.")
            break
        if not user_input:
            continue

        messages.append({"role": "user", "content": user_input})
        # Use Chat Completions API for standard role/content message lists
        chat = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,  # type: ignore[arg-type]
        )
        assistant_response = (chat.choices[0].message.content or "").strip()

        messages.append({"role": "assistant", "content": assistant_response})
        print(f"Assistant ({persona['name']}): {assistant_response}\n")


if __name__ == "__main__":
    main()
