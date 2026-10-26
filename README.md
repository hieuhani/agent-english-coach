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

## Install

From GitHub (`hieuhani/agent-english-coach`) or a local path to this repo:

```sh
# Claude Code
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

## Commands

### Inside your agent

| Action | Claude Code | Codex | omp |
|---|---|---|---|
| Review the last 7 days | `/english-coach:review` | `$english-coach:review` | `/skill:review` |
| Review the last N days | `/english-coach:review 30` | `$english-coach:review 30` | `/skill:review 30` |
| Trust the hooks (once, after install) | — | `/hooks` | — |
| Browse installed plugins | `/plugin` | `/plugins` | `/marketplace` |

You can also ask in plain English, for example *"Review my English journal"*, and the agent loads the skill itself.

Prompts are captured automatically, so there's no command for that. After installing or updating, start a new session so the agent loads the hooks.

### Managing the plugin (in a terminal)

| Action | Claude Code | Codex | omp |
|---|---|---|---|
| List plugins | `claude plugin list` | `codex plugin list` | `omp plugin list` |
| Update | `claude plugin update english-coach@agent-english-coach` | `codex plugin add english-coach@agent-english-coach` | `omp plugin upgrade english-coach@agent-english-coach` |
| Disable | `claude plugin disable english-coach@agent-english-coach` | set `enabled = false` under `[plugins."english-coach@agent-english-coach"]` in `~/.codex/config.toml` | `omp plugin disable english-coach@agent-english-coach` |
| Enable | `claude plugin enable english-coach@agent-english-coach` | set `enabled = true` in the same place | `omp plugin enable english-coach@agent-english-coach` |
| Uninstall | `claude plugin uninstall english-coach@agent-english-coach` | `codex plugin remove english-coach@agent-english-coach` | `omp plugin uninstall english-coach@agent-english-coach` |

Before updating, refresh the marketplace so the agent sees the new version: `claude plugin marketplace update agent-english-coach` or `omp plugin marketplace update agent-english-coach`. Codex reads the marketplace again on `codex plugin add`.

### Reading your journal

| File | What's in it |
|---|---|
| `~/english-journal/YYYY-MM-DD.md` | Feedback on every prompt from that day |
| `~/english-journal/prompts.jsonl` | Your raw prompts, one JSON object per line |
| `~/english-journal/mistakes.md` | Summaries from each review, used to track progress |

```sh
open ~/english-journal/$(date +%F).md    # today's feedback (macOS)
ls ~/english-journal                       # all days
```

Prompts are skipped when they're shorter than 5 words or start with `/`. Fenced code blocks are removed before the analysis.

### Development

```sh
# Run the hook by hand, writing to a test journal
echo '{"prompt": "I has two cat and I want know more about them."}' \
  | ENGLISH_JOURNAL_DIR=/tmp/english-test python3 plugins/english-coach/hooks/capture.py

# Validate the marketplace and the plugin
claude plugin validate .
claude plugin validate plugins/english-coach

# Re-render the icon after editing the script (macOS, needs Pillow)
python3 scripts/make_icon.py plugins/english-coach/assets/icon.png
```

After you edit the plugin, bump `version` in `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json` and `package.json`, because each agent caches installed plugins by version. Then run the update commands above.

## Configure

Set these environment variables in your shell profile:

| Variable | Default | Meaning |
|---|---|---|
| `ENGLISH_COACH_BACKEND` | first installed of `claude`, `codex`, `omp` | The agent that writes the critique |
| `ENGLISH_COACH_MODEL` | `sonnet` for Claude; the agent's own default otherwise | The model that writes the critique |
| `ENGLISH_JOURNAL_DIR` | `~/english-journal` | Where the journal is saved |

## Cost and privacy

Each prompt you write starts one extra agent call, which counts against that agent's usage. The journal stays on your machine.

## License

MIT. See [LICENSE](LICENSE).
