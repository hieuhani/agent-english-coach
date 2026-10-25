#!/usr/bin/env python3
"""SessionStart hook: stdout is added to Claude's context for the session."""
import os

if not os.environ.get("ENGLISH_COACH_CHILD"):
    print("The user is learning English. Always respond in English only, even if they mix "
          "Vietnamese or other language words into their messages. If they use a non-English "
          "word because they don't know the English equivalent, tell them the English word.")
