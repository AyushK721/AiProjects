
"""
history_chat_gui.py — GUI to chat with historical or pop-culture figures

How to run:
  - Optional: set GEMINI_API_KEY in your environment (PowerShell)
      $Env:GEMINI_API_KEY = "your_api_key_here"
  - Then:
      python history_chat_gui.py

Notes:
  - This GUI reuses the personas and prompt style from history_chat.py.
  - You can paste an API key in the field if not set in the environment.
  - For custom personas, fill in name/era/bio/style and click Start Chat.
"""

from __future__ import annotations

import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Optional

import google.generativeai as genai

# Import personas + prompt builder from the console version if available
try:
    from history_chat import PERSONAS, build_system_prompt
except Exception:
    # Fallback minimal definitions if import fails
    PERSONAS: Dict[str, Dict[str, str]] = {}

    def build_system_prompt(
        name: str,
        era: str,
        bio: str,
        style: str
    ) -> str:
        return (
            f"You are roleplaying as {name} (era/universe: {era}).\n"
            f"Speak in the first person as {name}. "
            f"Maintain a tone consistent with: {style}.\n\n"
            f"Background bio/context "
            f"(authoritative but not exhaustive):\n{bio}\n\n"
            "Ground rules:\n"
            "- Stay canon-grounded.\n"
            "- If uncertain, say you are unsure rather than fabricating.\n"
            "- Keep responses concise and conversational.\n"
        )


CUSTOM_SENTINEL = "< Custom persona >"


class HistoryChatGUI(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        self.title("History & Pop Culture Chat")
        self.geometry("840x640")
        self.minsize(720, 520)

        # Gemini state
        self.client = None
        self.api_key_var = tk.StringVar(
            value=os.environ.get("GEMINI_API_KEY", "")
        )

        # Conversation state
        self.messages: List[Dict[str, str]] = []
        self.current_persona: Optional[
            Dict[str, str]
        ] = None

        # Build UI
        self._build_top_bar()
        self._build_persona_frame()
        self._build_chat_frame()

        # Initialize persona dropdown
        self._populate_personas()

    # ---------- UI construction ----------

    def _build_top_bar(self) -> None:
        top = ttk.Frame(self)
        top.pack(
            fill="x",
            padx=10,
            pady=8
        )

        ttk.Label(
            top,
            text="AQ.Ab8RN6JLxdG0kjQg0lMS9kymvoJLG2_ruYE1zim7zSItBv-ztA"
        ).pack(side="left")

        entry = ttk.Entry(
            top,
            textvariable=self.api_key_var,
            show="*"
        )
        entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=6
        )

        self.connect_btn = ttk.Button(
            top,
            text="Connect",
            command=self.on_connect
        )
        self.connect_btn.pack(side="left")

    def _build_persona_frame(self) -> None:
        frame = ttk.LabelFrame(
            self,
            text="Persona"
        )
        frame.pack(
            fill="x",
            padx=10,
            pady=8
        )

        # Row 1: dropdown
        row1 = ttk.Frame(frame)
        row1.pack(
            fill="x",
            padx=6,
            pady=4
        )

        ttk.Label(
            row1,
            text="Choose:"
        ).pack(side="left")

        self.persona_var = tk.StringVar()

        self.persona_combo = ttk.Combobox(
            row1,
            textvariable=self.persona_var,
            state="readonly"
        )

        self.persona_combo.pack(
            side="left",
            padx=6,
            fill="x",
            expand=True
        )

        self.persona_combo.bind(
            "<<ComboboxSelected>>",
            self.on_persona_change
        )

        self.start_btn = ttk.Button(
            row1,
            text="Start Chat",
            command=self.on_start_chat,
            state="disabled"
        )

        self.start_btn.pack(
            side="left",
            padx=4
        )

        # Custom persona frame
        self.custom_frame = ttk.Frame(frame)
        self.custom_frame.pack(
            fill="x",
            padx=6,
            pady=4
        )

        self.custom_name = tk.StringVar()
        self.custom_era = tk.StringVar()
        self.custom_style = tk.StringVar()

        grid = self.custom_frame

        ttk.Label(
            grid,
            text="Name:"
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=2,
            pady=2
        )

        ttk.Entry(
            grid,
            textvariable=self.custom_name
        ).grid(
            row=0,
            column=1,
            sticky="ew",
            padx=4,
            pady=2
        )

        ttk.Label(
            grid,
            text="Era/Universe:"
        ).grid(
            row=0,
            column=2,
            sticky="w",
            padx=2,
            pady=2
        )

        ttk.Entry(
            grid,
            textvariable=self.custom_era
        ).grid(
            row=0,
            column=3,
            sticky="ew",
            padx=4,
            pady=2
        )

        ttk.Label(
            grid,
            text="Style:"
        ).grid(
            row=1,
            column=0,
            sticky="w",
            padx=2,
            pady=2
        )

        ttk.Entry(
            grid,
            textvariable=self.custom_style
        ).grid(
            row=1,
            column=1,
            columnspan=3,
            sticky="ew",
            padx=4,
            pady=2
        )

        ttk.Label(
            grid,
            text="Bio/Context (1–3 sentences):"
        ).grid(
            row=2,
            column=0,
            sticky="nw",
            padx=2,
            pady=2
        )

        self.custom_bio = tk.Text(
            grid,
            height=4,
            wrap="word"
        )

        self.custom_bio.grid(
            row=2,
            column=1,
            columnspan=3,
            sticky="ew",
            padx=4,
            pady=2
        )

        grid.columnconfigure(
            1,
            weight=1
        )

        grid.columnconfigure(
            3,
            weight=1
        )

        self._toggle_custom_fields(False)

    def _build_chat_frame(self) -> None:
        frame = ttk.LabelFrame(
            self,
            text="Chat"
        )

        frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=8
        )

        text_frame = ttk.Frame(frame)

        text_frame.pack(
            fill="both",
            expand=True,
            padx=6,
            pady=6
        )

        self.chat_text = tk.Text(
            text_frame,
            wrap="word",
            state="disabled"
        )

        self.chat_text.pack(
            side="left",
            fill="both",
            expand=True
        )

        scroll = ttk.Scrollbar(
            text_frame,
            command=self.chat_text.yview
        )

        scroll.pack(
            side="right",
            fill="y"
        )

        self.chat_text["yscrollcommand"] = scroll.set


        # Input row (multi-line compose box)
        input_row = ttk.Frame(frame)
        input_row.pack(
            fill="x",
            padx=6,
            pady=4
        )

        self.input_text = tk.Text(
            input_row,
            height=3,
            wrap="word"
        )

        self.input_text.pack(
            side="left",
            fill="x",
            expand=True
        )

        self.send_btn = ttk.Button(
            input_row,
            text="Send",
            command=self.on_send,
            state="disabled"
        )

        self.send_btn.pack(
            side="left",
            padx=4
        )

        self.exit_btn = ttk.Button(
            input_row,
            text="Exit",
            command=self.destroy
        )

        self.exit_btn.pack(side="left")

        # Ctrl+Enter sends
        self.input_text.bind(
            "<Control-Return>",
            self._maybe_send
        )

        # macOS Command+Enter
        self.input_text.bind(
            "<Command-Return>",
            self._maybe_send
        )

    def _populate_personas(self) -> None:
        names = list(PERSONAS.keys())
        names.append(CUSTOM_SENTINEL)

        self.persona_combo["values"] = names

        if names:
            self.persona_combo.current(0)

        self.on_persona_change()

    # ---------- Event handlers ----------

    def on_connect(self) -> None:
        key = self.api_key_var.get().strip()

        if not key:
            messagebox.showwarning(
                "API Key",
                "Please enter a Gemini API key or set GEMINI_API_KEY."
            )
            return

        try:
            genai.configure(api_key=key)

            self.client = genai.GenerativeModel(
                "gemini-2.5-flash"
            )

            self.connect_btn.configure(
                text="Connected",
                state="disabled"
            )

            self.start_btn.configure(
                state="normal"
            )

            self._append_info(
                "Connected to Gemini. "
                "Choose a persona and click Start Chat."
            )

        except Exception as e:
            messagebox.showerror(
                "Connection error",
                str(e)
            )

    def on_persona_change(
        self,
        event: Optional[tk.Event] = None
    ) -> None:
        is_custom = (
            self.persona_var.get()
            == CUSTOM_SENTINEL
        )

        self._toggle_custom_fields(
            is_custom
        )

    def on_start_chat(self) -> None:
        if not self.client:
            messagebox.showwarning(
                "Not connected",
                "Connect with your API key first."
            )
            return

        selected = self.persona_var.get()

        if selected == CUSTOM_SENTINEL:

            name = (
                self.custom_name.get().strip()
                or "Unknown Figure"
            )

            era = (
                self.custom_era.get().strip()
                or "Unknown era"
            )

            bio = (
                self.custom_bio.get(
                    "1.0",
                    tk.END
                ).strip()
                or "A historical or fictional figure."
            )

            style = (
                self.custom_style.get().strip()
                or "Neutral, concise."
            )

            persona = {
                "name": name,
                "era": era,
                "bio": bio,
                "style": style,
            }

        else:

            data = PERSONAS.get(selected)

            if not data:
                messagebox.showerror(
                    "Persona error",
                    "Selected persona not found."
                )
                return

            persona = {
                "name": selected,
                **data,
            }

        self.current_persona = persona

        system_prompt = build_system_prompt(
            name=persona["name"],
            era=persona["era"],
            bio=persona["bio"],
            style=persona["style"],
        )

        self.messages = [
            {
                "role": "system",
                "content": system_prompt,
            }
        ]

        self._clear_chat()

        self._append_info(
            f"Chat started as "
            f"{persona['name']}. "
            f"Type a message below."
        )

        self.send_btn.configure(
            state="normal"
        )

        self.input_text.focus_set()

    def _maybe_send(
        self,
        event: tk.Event
    ) -> None:

        if (
            getattr(
                self,
                "input_text",
                None
            )
            is not None
            and event.widget
            is self.input_text
            and self.send_btn["state"]
            == "normal"
        ):
            self.on_send()

    def on_send(self) -> None:

        text = self.input_text.get(
            "1.0",
            tk.END
        ).strip()

        if (
            not text
            or not self.client
            or not self.current_persona
        ):
            return

        self._append_user(text)

        self.input_text.delete(
            "1.0",
            tk.END
        )

        self.send_btn.configure(
            state="disabled"
        )

        threading.Thread(
            target=self._call_model,
            args=(text,),
            daemon=True
        ).start()

    # ---------- Model interaction ----------

    def _call_model(
        self,
        text: str
    ) -> None:

        try:

            self.messages.append(
                {
                    "role": "user",
                    "content": text,
                }
            )

            prompt_parts = []

            for msg in self.messages:

                role = msg["role"]

                if role == "system":

                    prompt_parts.append(
                        "System Instructions:\n"
                        + msg["content"]
                    )

                elif role == "user":

                    prompt_parts.append(
                        "User: "
                        + msg["content"]
                    )

                elif role == "assistant":

                    prompt_parts.append(
                        "Assistant: "
                        + msg["content"]
                    )

            prompt = "\n\n".join(
                prompt_parts
            )

            response = self.client.generate_content(
                prompt
            )

            assistant_response = ""

            if hasattr(response, "text"):

                assistant_response = (
                    response.text.strip()
                )

            self.messages.append(
                {
                    "role": "assistant",
                    "content": assistant_response,
                }
            )

            self.after(
                0,
                lambda: self._append_assistant(
                    self.current_persona["name"],
                    assistant_response,
                ),
            )

        except Exception as e:

            self.after(
                0,
                lambda: self._append_error(
                    f"Error: {e}"
                ),
            )

        finally:

            self.after(
                0,
                lambda: (
                    self.send_btn.configure(
                        state="normal"
                    ),
                    self.input_text.focus_set(),
                ),
            )

    # ---------- Chat helpers ----------

    def _append(
        self,
        who: str,
        text: str
    ) -> None:

        self.chat_text.configure(
            state="normal"
        )

        self.chat_text.insert(
            tk.END,
            f"{who}: {text}\n\n"
        )

        self.chat_text.configure(
            state="disabled"
        )

        self.chat_text.see(
            tk.END
        )

    def _append_info(
        self,
        text: str
    ) -> None:

        self._append(
            "[Info]",
            text
        )

    def _append_user(
        self,
        text: str
    ) -> None:

        self._append(
            "You",
            text
        )

    def _append_assistant(
        self,
        name: str,
        text: str
    ) -> None:

        self._append(
            f"Assistant ({name})",
            text
        )

    def _append_error(
        self,
        text: str
    ) -> None:

        self._append(
            "[Error]",
            text
        )

    def _clear_chat(
        self
    ) -> None:

        self.chat_text.configure(
            state="normal"
        )

        self.chat_text.delete(
            "1.0",
            tk.END
        )

        self.chat_text.configure(
            state="disabled"
        )


    # ---------- Utils ----------

    def _toggle_custom_fields(
        self,
        visible: bool
    ) -> None:

        state = (
            "normal"
            if visible
            else "disabled"
        )

        for child in self.custom_frame.winfo_children():

            try:
                child.configure(
                    state=state
                )

            except tk.TclError:
                pass

        if isinstance(
            self.custom_bio,
            tk.Text
        ):

            if visible:

                self.custom_bio.configure(
                    state="normal"
                )

            else:

                self.custom_bio.configure(
                    state="disabled"
                )


if __name__ == "__main__":

    app = HistoryChatGUI()

    app.mainloop()

