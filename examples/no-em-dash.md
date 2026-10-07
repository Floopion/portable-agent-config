---
name: "no-em-dash"
description: "No em dashes, en dashes or double hyphens in anything you write"
metadata:
  type: feedback
  scope: portable
---

Never use em dashes, en dashes or double hyphens in any output: chat, code comments, commit messages, PR text and generated documents.

**Why:** they read as machine-written, and that matters most in text published under your name.

**How to apply:**
- Use a colon, a comma or two sentences instead; if you reach for a dash, rewrite the sentence.
- In generated HTML or Markdown, check for the HTML dash entities as well as the characters before handing it over.
