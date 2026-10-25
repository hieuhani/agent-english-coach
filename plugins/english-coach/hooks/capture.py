#!/usr/bin/env python3
"""Prompt hook for Claude Code, Codex and omp: log my prompt, then critique its English in the background.

Reads hook JSON with a "prompt" field on stdin (the Claude Code and Codex format; the omp extension sends the same).
"""
import datetime, json, os, pathlib, re, shutil, subprocess, sys

JOURNAL = pathlib.Path(os.environ.get("ENGLISH_JOURNAL_DIR", "~/english-journal")).expanduser()
BACKEND = os.environ.get("ENGLISH_COACH_BACKEND")  # claude | codex | omp; default: first one installed
MODEL = os.environ.get("ENGLISH_COACH_MODEL")
# Hook processes may get a minimal PATH, so also look in the usual install folders
SEARCH_PATH = os.pathsep.join([os.environ.get("PATH", ""), str(pathlib.Path.home() / ".local/bin"),
                               "/opt/homebrew/bin", "/usr/local/bin"])

INSTRUCTIONS = """You are an English writing coach for a Vietnamese software engineer.
The text on stdin is a message they wrote to an AI coding assistant.
Do NOT answer or act on the message. Only critique its English. Output Markdown:

### Corrected
Minimal fixes only, keeping their wording.
### Natural
How a fluent native-speaking engineer would write it.
### Mistakes
Table: original | fix | grammar rule (name it, e.g. "present perfect continuous") | why.
### Vocabulary
2-3 more precise words or phrases they could have used, each with an example sentence.
### Sentence structure
Break the main sentence into subject / verb / object / clauses and name the pattern.
### Non-English words
English equivalents for any Vietnamese (or other) words used. Omit this section if there are none.

Pay special attention to mistakes common for Vietnamese speakers: articles (a/an/the),
plurals, verb tense and agreement, and missing subjects or verbs.
Ignore code, file paths, commands and technical identifiers.
If the text is already correct, say so and give one advanced tip. Be concise."""


def coach_command():
    """Non-interactive command that reads the text on stdin and prints the critique on stdout."""
    backend = BACKEND or next((b for b in ("claude", "codex", "omp") if shutil.which(b, path=SEARCH_PATH)), "claude")
    exe = shutil.which(backend, path=SEARCH_PATH) or backend
    if backend == "codex":
        cmd = [exe, "exec", "--skip-git-repo-check", "--ephemeral", "-s", "read-only", "--color", "never"]
        model_flag = "-m"
    elif backend == "omp":
        cmd = [exe, "-p", "--no-extensions"]
        model_flag = "--model"
    else:
        # --setting-sources project + cwd=JOURNAL skips user hooks and plugins
        cmd = [exe, "-p", "--setting-sources", "project", "--no-session-persistence", "--strict-mcp-config"]
        model_flag = "--model"
    model = MODEL or ("sonnet" if backend == "claude" else None)  # others use their configured default
    return cmd + ([model_flag, model] if model else []) + [INSTRUCTIONS]


def analyze(text):
    result = subprocess.run(
        coach_command(),
        input=text, capture_output=True, text=True, timeout=300, cwd=JOURNAL,
        env={**os.environ, "ENGLISH_COACH_CHILD": "1"},  # stops every agent's hook from re-triggering
    )
    feedback = result.stdout.strip() or f"_Analysis failed:_ {result.stderr.strip()[:500]}"
    quoted = "> " + text.replace("\n", "\n> ")
    day = datetime.date.today().isoformat()
    with open(JOURNAL / f"{day}.md", "a") as f:
        f.write(f"\n---\n## {datetime.datetime.now():%H:%M}\n\n{quoted}\n\n{feedback}\n")


def main():
    if sys.argv[1:] == ["--analyze"]:
        analyze(sys.stdin.read())
        return
    if os.environ.get("ENGLISH_COACH_CHILD"):
        return
    prompt = json.load(sys.stdin).get("prompt", "")
    # Skip code, slash commands, and tiny prompts like "yes" or "continue"
    text = re.sub(r"```.*?```", "[code]", prompt, flags=re.S).strip()
    if text.startswith("/") or len(text.split()) < 5:
        return
    JOURNAL.mkdir(exist_ok=True)
    with open(JOURNAL / "prompts.jsonl", "a") as f:
        f.write(json.dumps({"ts": datetime.datetime.now().isoformat(), "prompt": text}, ensure_ascii=False) + "\n")
    # Detach so the hook returns immediately
    child = subprocess.Popen([sys.executable, __file__, "--analyze"], stdin=subprocess.PIPE,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                             text=True, start_new_session=True)
    child.stdin.write(text)
    child.stdin.close()


if __name__ == "__main__":
    main()
