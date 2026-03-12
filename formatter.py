"""Terminal and markdown output for agent-diff."""
import textwrap

BOLD  = "\033[1m"
DIM   = "\033[2m"
CYAN  = "\033[96m"
GREEN = "\033[92m"
YELLOW= "\033[93m"
RESET = "\033[0m"
SEP   = "─" * 72


def _wrap(text: str, width: int = 72, indent: str = "  ") -> str:
    lines = text.strip().splitlines()
    wrapped = []
    for line in lines:
        if line.strip() == "":
            wrapped.append("")
        else:
            wrapped.extend(
                textwrap.wrap(line, width=width - len(indent),
                              initial_indent=indent, subsequent_indent=indent)
            )
    return "\n".join(wrapped)


def console(
    task: str,
    model_a: str, response_a: str,
    model_b: str, response_b: str,
    diff_text: str,
) -> str:
    lines = [
        SEP,
        f"  {BOLD}agent-diff{RESET}  {CYAN}{model_a}{RESET} vs {CYAN}{model_b}{RESET}",
        SEP,
        f"  {BOLD}Task{RESET}",
        _wrap(task),
        "",
        SEP,
        f"  {BOLD}{model_a.upper()} response{RESET}",
        _wrap(response_a),
        "",
        SEP,
        f"  {BOLD}{model_b.upper()} response{RESET}",
        _wrap(response_b),
        "",
        SEP,
        f"  {BOLD}{GREEN}Diff analysis (by Claude){RESET}",
        SEP,
        _wrap(diff_text),
        SEP,
    ]
    return "\n".join(lines)


def markdown(
    task: str,
    model_a: str, response_a: str,
    model_b: str, response_b: str,
    diff_text: str,
) -> str:
    return f"""# agent-diff: {model_a} vs {model_b}

## Task
{task}

---

## {model_a.capitalize()} response
{response_a}

---

## {model_b.capitalize()} response
{response_b}

---

## Diff analysis (by Claude)
{diff_text}
"""
