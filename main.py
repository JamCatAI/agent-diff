#!/usr/bin/env python3
"""agent-diff — run any task on two LLMs and let Claude diff the results."""
import argparse
import os

# auto-load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
import sys
import threading

from runners import RUNNERS, API_KEY_MAP

PROVIDERS = list(RUNNERS.keys())


def check_key(provider: str) -> None:
    key = API_KEY_MAP[provider]
    if not os.environ.get(key):
        print(f"error: {key} not set (required for --{provider})", file=sys.stderr)
        sys.exit(2)


def run_parallel(task: str, system: str, model_a: str, model_b: str) -> tuple[str, str]:
    results = {}
    errors  = {}

    def run(name):
        try:
            results[name] = RUNNERS[name](task, system)
        except Exception as e:
            errors[name] = e

    threads = [
        threading.Thread(target=run, args=(model_a,)),
        threading.Thread(target=run, args=(model_b,)),
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    if errors:
        for name, err in errors.items():
            print(f"error ({name}): {err}", file=sys.stderr)
        sys.exit(1)

    return results[model_a], results[model_b]


def main():
    parser = argparse.ArgumentParser(
        prog="agent-diff",
        description="Run a task on two LLMs and let Claude diff the outputs.",
    )
    parser.add_argument("task", nargs="?", help="Task / prompt to run (or - for stdin)")
    parser.add_argument("--a",  choices=PROVIDERS, default="gemini",
                        help="First model (default: gemini)")
    parser.add_argument("--b",  choices=PROVIDERS, default="groq",
                        help="Second model (default: groq)")
    parser.add_argument("--system", default="",
                        help="Optional system prompt passed to both models")
    parser.add_argument("--format", choices=["console", "md"], default="console", dest="fmt")
    parser.add_argument("--output", "-o", default=None, help="Save report to file")
    parser.add_argument("--no-diff", action="store_true",
                        help="Skip Claude diff analysis — just show both responses")
    args = parser.parse_args()

    # load task
    if args.task is None or args.task == "-":
        task = sys.stdin.read().strip()
    else:
        task = args.task.strip()

    if not task:
        print("error: empty task", file=sys.stderr)
        sys.exit(2)

    if args.a == args.b:
        print("error: --a and --b must be different providers", file=sys.stderr)
        sys.exit(2)

    # check keys
    check_key(args.a)
    check_key(args.b)
    if not args.no_diff:
        check_key("claude")  # diff always uses Claude

    print(f"Running {args.a} and {args.b} in parallel...", file=sys.stderr)
    response_a, response_b = run_parallel(task, args.system, args.a, args.b)
    print("✓ Both responses received", file=sys.stderr)

    diff_text = ""
    if not args.no_diff:
        print("Diffing with Claude...", file=sys.stderr)
        from differ import diff
        diff_text = diff(task, args.a, response_a, args.b, response_b)
        print("✓ Diff complete", file=sys.stderr)

    from formatter import console, markdown
    if args.fmt == "md":
        output = markdown(task, args.a, response_a, args.b, response_b, diff_text)
    else:
        output = console(task, args.a, response_a, args.b, response_b, diff_text)

    if args.output:
        os.makedirs(os.path.dirname(args.output) if os.path.dirname(args.output) else ".", exist_ok=True)
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Saved: {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
