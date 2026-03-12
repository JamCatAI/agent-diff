"""AI-powered diff engine — uses Claude to compare two LLM responses."""
import os
import anthropic

DIFF_SYSTEM = """You are an expert AI output analyst. You compare two LLM responses to the same task.
Your job is to surface meaningful differences — not cosmetic ones.

Focus on:
- Factual disagreements or contradictions
- Reasoning quality and depth
- What each model got right or wrong
- Unique insights one has that the other misses
- Tone and confidence calibration

Be direct, specific, and cite exact phrases from the responses."""

DIFF_PROMPT = """Task given to both models:
<task>
{task}
</task>

Model A ({model_a}) response:
<response_a>
{response_a}
</response_a>

Model B ({model_b}) response:
<response_b>
{response_b}
</response_b>

Compare these two responses. Structure your analysis as:

## What they agree on
(shared claims, approaches, conclusions)

## Where they diverge
(specific disagreements, different framings, missing pieces)

## Quality delta
Which response is stronger overall and why? Be honest — call out lazy or wrong answers.

## Verdict
One sentence: which model won this task and why."""


def diff(task: str, model_a: str, response_a: str, model_b: str, response_b: str) -> str:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    prompt = DIFF_PROMPT.format(
        task=task,
        model_a=model_a,
        response_a=response_a,
        model_b=model_b,
        response_b=response_b,
    )
    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=2048,
        thinking={"type": "adaptive"},
        system=DIFF_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        return stream.get_final_message().content[-1].text
