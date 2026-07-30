"""
survival_game.py — AI-driven survival story game (console)

How to run:
  - Ensure you have an OpenAI API key set as an environment variable `OPENAI_API_KEY`.
    On Windows PowerShell:
      $Env:OPENAI_API_KEY = "your_api_key_here"

  - Run the script:
      python survival_game.py

What it does:
  - The AI acts as a Game Master and gives you a brief, high-stakes scenario.
  - You type your gameplan (multi-line allowed). Finish with a blank line.
  - The AI narrates what happens and clearly states whether you survived.

Safety & scope:
  - This is a fictional roleplay. The Game Master must not provide real-world
    dangerous, illegal, or self-harm instructions. All content remains
    non-actionable and for entertainment only.
"""

from __future__ import annotations

import os
from typing import List, Dict

from google import genai
client = genai.Client()

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Write a haiku about coding."
)
print(response.text)




SYSTEM_PROMPT = (
    "You are an AI Game Master for a short, single-round survival scenario. "
    "Your job:\n"
    "1) Present a vivid, brief, life-threatening fictional setup (3–6 sentences).\n"
    "   - Include a clear immediate objective and 2–4 concrete constraints or hazards.\n"
    "   - Avoid gore; keep PG-13.\n"
    "2) After the player submits a gameplan, evaluate it and narrate the outcome (5–10 sentences).\n"
    "   - Be fair but challenging; use the constraints logically.\n"
    "   - Explain why the plan succeeds or fails; reference the plan's details.\n"
    "   - End with a single machine-readable line: RESULT: SURVIVED or RESULT: FAILED.\n"
    "Important rules:\n"
    "- This is fictional roleplay; do not provide real-life survival or harmful instructions.\n"
    "- Do not instruct illegal activities or self-harm.\n"
    "- If the user asks for real-world guidance, refuse and remind them this is only a story simulation.\n"
)


def choose_difficulty() -> str:
    print("Choose difficulty: 1) Easy  2) Normal  3) Hard")
    while True:
        sel = input("Enter 1/2/3 (default 2): ").strip()
        if sel in {"", "2"}:
            return "Normal"
        if sel == "1":
            return "Easy"
        if sel == "3":
            return "Hard"
        print("Please enter 1, 2, or 3.")


def gather_gameplan() -> str:
    print("\nDescribe your gameplan (multi-line). Press Enter on a blank line to finish:")
    lines: List[str] = []
    while True:
        line = input()
        if not line:
            break
        lines.append(line)
    plan = "\n".join(lines).strip()
    if not plan:
        plan = "I keep calm, observe constraints, and attempt a cautious escape using available cover."
    return plan


def start_round(client: OpenAI, difficulty: str) -> Dict[str, str]:
    messages: List[Dict[str, str]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                "Start a new scenario. Difficulty: "
                f"{difficulty}. Provide only the scenario description."
            ),
        },
    ]
    chat = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,  # type: ignore[arg-type]
    )
    scenario = (chat.choices[0].message.content or "").strip()
    return {"scenario": scenario, "difficulty": difficulty}


def evaluate_plan(client: OpenAI, scenario: str, plan: str) -> str:
    messages: List[Dict[str, str]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "assistant", "content": scenario},
        {
            "role": "user",
            "content": (
                "Here is my gameplan for the scenario above. "
                "Evaluate it and narrate the outcome, then end with 'RESULT: SURVIVED' or 'RESULT: FAILED'.\n\n"
                f"Gameplan:\n{plan}"
            ),
        },
    ]
    chat = client.chat.completions.create(
        model="openai/gpt-oss-20b:free",
        messages=messages,  # type: ignore[arg-type]
    )
    return (chat.choices[0].message.content or "").strip()


def extract_result(narrative: str) -> str:
    tail = narrative.rsplit("\n", 3)
    for line in reversed(tail):
        s = line.strip().upper()
        if s.endswith("RESULT: SURVIVED"):
            return "SURVIVED"
        if s.endswith("RESULT: FAILED"):
            return "FAILED"
    # Fallback if the model forgot the marker
    return "UNKNOWN"


def play_once(client: OpenAI) -> None:
    difficulty = choose_difficulty()
    round_data = start_round(client, difficulty)
    print("\nScenario (", difficulty, "):", sep="")
    print(round_data["scenario"])  # scenario text

    plan = gather_gameplan()
    print("\nThinking...\n")
    narrative = evaluate_plan(client, round_data["scenario"], plan)
    print(narrative)

    result = extract_result(narrative)
    if result == "SURVIVED":
        print("\nYou survived! Well played.")
    elif result == "FAILED":
        print("\nYou did not survive this time. Want to try a different approach?")
    else:
        print("\nResult unclear. The Game Master forgot the marker, but the story above stands.")


def main() -> None:
    api_key = os.environ.get("OPENAI_API_KEY", "")
    client = OpenAI(api_key="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")

    print("Welcome to the Survival Story Game!")
    print("This is a fictional roleplay for entertainment only.\n")

    while True:
        play_once(client)
        again = input("\nPlay again? (y/N): ").strip().lower()
        if again not in {"y", "yes"}:
            print("\nThanks for playing! Stay safe out there — in fiction only.")
            break


if __name__ == "__main__":
    main()
