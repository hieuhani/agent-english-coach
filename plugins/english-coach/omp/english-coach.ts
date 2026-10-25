// @ts-nocheck
// omp extension: sends each prompt to the shared hooks/capture.py and adds the English-only rule.
import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";

const CAPTURE = fileURLToPath(new URL("../hooks/capture.py", import.meta.url));
const RULE =
  "The user is learning English. Always respond in English only, even if they mix Vietnamese or other " +
  "language words into their messages. If they use a non-English word because they don't know the " +
  "English equivalent, tell them the English word.";

let sawInput = false; // `input` fires in the TUI and RPC modes, not in `omp -p`
let last = { prompt: "", at: 0 };

function capture(prompt) {
  // before_agent_start can re-run for the same submission on retries
  const now = Date.now();
  if (!prompt || (prompt === last.prompt && now - last.at < 60_000)) return;
  last = { prompt, at: now };
  const child = spawn("python3", [CAPTURE], { detached: true, stdio: ["pipe", "ignore", "ignore"] });
  child.on("error", () => {});
  child.stdin.end(JSON.stringify({ prompt }));
  child.unref();
}

export default function (pi) {
  if (process.env.ENGLISH_COACH_CHILD) return;

  // Raw text as typed, before skill or template expansion
  pi.on("input", event => {
    sawInput = true;
    capture(event.text);
  });

  pi.on("before_agent_start", event => {
    if (!sawInput) capture(event.prompt);
    if (Array.isArray(event.systemPrompt)) return { systemPrompt: [...event.systemPrompt, RULE] };
  });
}
