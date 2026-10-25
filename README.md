# agent-english-coach

Learn English from the prompts you write to coding agents (Claude Code, Codex, omp). Every prompt gets a grammar critique in a daily journal, plus a weekly review.

One plugin works in **Claude Code**, **Codex** and **omp (oh-my-pi)**, including the Code tab of Claude Desktop. It doesn't work in Claude Desktop chat or claude.ai, because they don't run hooks.

## english-coach

Every prompt you send also becomes a small English lesson, and your work isn't interrupted.

- **Background critique**: each prompt goes to a non-interactive agent call in the background. You get a corrected version, a natural version, a table of mistakes with the grammar rule for each, vocabulary suggestions and a sentence-structure breakdown. The feedback goes into `~/english-journal/YYYY-MM-DD.md`.
- **English-only replies**: the agent always replies in English and translates any non-English words you use.
- **Weekly review**: the `review` skill finds your recurring mistakes, explains the grammar in depth, writes 10 exercises and tracks your progress in `mistakes.md`.

Every agent writes to the same journal, so one review covers your mistakes from all of them.

The hook skips prompts shorter than 5 words, slash commands and fenced code blocks.

### How it plugs into each agent

| | Captures the prompt | English-only rule | Entry point |
|---|---|---|---|
| Claude Code | `UserPromptSubmit` hook | `SessionStart` hook | `.claude-plugin/plugin.json`, `hooks/hooks.json` |
| Codex | `UserPromptSubmit` hook | `SessionStart` hook | `.codex-plugin/plugin.json`, `hooks/codex-hooks.json` |
| omp | `input` event (TUI/RPC), `before_agent_start` (`omp -p`) | appended to `systemPrompt` | `package.json` → `omp/english-coach.ts` |

All three call the same `hooks/capture.py` and share `skills/review/SKILL.md`.

### Install

From GitHub (`hieuhani/agent-english-coach`) or a local path to this repo:

```sh
# Claude Code — then use /english-coach:review
claude plugin marketplace add hieuhani/agent-english-coach
claude plugin install english-coach@agent-english-coach

# Codex — then open codex, run /hooks and trust the two english-coach hooks
codex plugin marketplace add hieuhani/agent-english-coach
codex plugin add english-coach@agent-english-coach

# omp
omp plugin marketplace add hieuhani/agent-english-coach
omp plugin install english-coach@agent-english-coach
```

Requires `python3`, plus at least one of `claude`, `codex` or `omp` to run the analysis.

### Configure

Set these environment variables in your shell profile:

| Variable | Default | Meaning |
|---|---|---|
| `ENGLISH_COACH_BACKEND` | first installed of `claude`, `codex`, `omp` | The agent that writes the critique |
| `ENGLISH_COACH_MODEL` | `sonnet` for Claude; the agent's own default otherwise | The model that writes the critique |
| `ENGLISH_JOURNAL_DIR` | `~/english-journal` | Where the journal is saved |

### Updating after you edit the plugin

Each agent installs a cached copy, so bump `version` in `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json` and `package.json`, then run:

```sh
claude plugin marketplace update agent-english-coach && claude plugin update english-coach@agent-english-coach
codex plugin add english-coach@agent-english-coach
omp plugin marketplace update agent-english-coach && omp plugin upgrade english-coach@agent-english-coach
```

### Cost and privacy

Each prompt you write starts one extra agent call, which counts against that agent's usage. The journal stays on your machine.

## License

MIT. See [LICENSE](LICENSE).
