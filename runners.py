"""LLM runners — each returns a streamed or buffered response string."""
import os


def run_claude(prompt: str, system: str = "") -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    kwargs = dict(
        model="claude-opus-4-6",
        max_tokens=2048,
        thinking={"type": "adaptive"},
        messages=[{"role": "user", "content": prompt}],
    )
    if system:
        kwargs["system"] = system
    with client.messages.stream(**kwargs) as stream:
        return stream.get_final_message().content[-1].text


def run_gemini(prompt: str, system: str = "") -> str:
    import google.generativeai as genai
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel(
        "gemini-2.0-flash",
        system_instruction=system or None,
    )
    return model.generate_content(prompt).text


def run_openai(prompt: str, system: str = "") -> str:
    from openai import OpenAI
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    return client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=2048,
    ).choices[0].message.content


def run_groq(prompt: str, system: str = "") -> str:
    from groq import Groq
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    return client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=2048,
    ).choices[0].message.content


RUNNERS = {
    "claude": run_claude,
    "gemini": run_gemini,
    "openai": run_openai,
    "groq":   run_groq,
}

API_KEY_MAP = {
    "claude": "ANTHROPIC_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "openai": "OPENAI_API_KEY",
    "groq":   "GROQ_API_KEY",
}
