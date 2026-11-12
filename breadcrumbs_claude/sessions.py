"""The sessions of Claude Code as a source of the ingest (`python -m breadcrumbs ingest claude-code [PATH]`).

Claude Code keeps one JSON-lines file for each session: ~/.claude/projects/<project folder>/<session id>.jsonl. (The
files of its subagents sit deeper, in <session id>/subagents/, and are not read.) The record types that this reads:

    user       message.content is a text (a user turn), or a list of parts: "text" (a user turn) and "tool_result"
               (a tool row; its content is a text or a list of parts: a "text" part is its text, a "tool_reference"
               part is its tool_name, an "image" part is its media type in brackets, as [image/jpeg])
    assistant  message.content is a list of parts: "text" and "tool_use" (id, name, input). One message is written as
               one record for each part; the parts join into one row. The "thinking" parts are skipped.
    ai-title   aiTitle: the title of the session

Every other record type (attachments, api requests, file history, modes, system) is skipped, and so is a record whose
isMeta is true. The session meta keeps cwd and branch (gitBranch) of the first record that has them.

The usage of a model request (usage()): an assistant record has message.usage, with the counts of the Anthropic API:
input_tokens (the input that no cache held: it does NOT count the cached tokens), cache_read_input_tokens,
cache_creation_input_tokens (the cache write), output_tokens. One response is written as several records (one for each
part), each with the same message id, requestId and usage: it is counted once, by its requestId (else its message id).
A record of the model "<synthetic>" (a message that Claude Code made itself, with no request) is skipped.
"""
import os

from breadcrumbs import usage as usage_record
from breadcrumbs.transcript import JsonLines, Rows, epoch, files, meta, text_parts

ROOT = "~/.claude/projects"


def result_text(content):
    """The text of a tool result. A part without text is named, so that its call keeps a result row: a tool_reference
    by its tool_name, an image by its media type (the bytes are not kept)."""
    if not isinstance(content, list):
        return text_parts(content)

    def name(part):
        if isinstance(part.get("text"), str):
            return part["text"]
        if part.get("type") == "tool_reference":
            return part.get("tool_name")
        if part.get("type") == "image":
            source = part.get("source")
            return "[%s]" % (source.get("media_type") if isinstance(source, dict) and source.get("media_type") else "image")

    return "\n".join(t for t in map(name, (p for p in content if isinstance(p, dict))) if isinstance(t, str) and t)


def session(path):
    """(id, title, meta, rows) of one session file. The id is the name of the file."""
    lines, rows, title, where = JsonLines(path), Rows(), "", {}
    for record in lines:
        kind, message = record.get("type"), record.get("message")
        if kind == "ai-title":
            title = record.get("aiTitle") or title
        if kind not in ("user", "assistant") or record.get("isMeta") or not isinstance(message, dict):
            continue
        where["cwd"] = where.get("cwd") or record.get("cwd")
        where["branch"] = where.get("branch") or record.get("gitBranch")
        ts, content = epoch(record.get("timestamp")), message.get("content")
        for part in [{"type": "text", "text": content}] if isinstance(content, str) else content or ():
            if not isinstance(part, dict):
                continue
            if part.get("type") == "text":
                rows.say(kind, part.get("text"), ts)
            elif part.get("type") == "tool_use":
                rows.call(part.get("id"), part.get("name"), part.get("input"), ts)
            elif part.get("type") == "tool_result":
                rows.result(part.get("tool_use_id"), result_text(part.get("content")), ts)
    return os.path.basename(path)[:-len(".jsonl")], title, meta(skipped=lines.bad, **where), rows.rows


def sessions(path=None):
    """The source of the harness claude-code: the sessions of a file, of a project folder, or of the folder
    ~/.claude/projects (the default), each (id, title, meta, rows)."""
    for found in files(path, ROOT, "*.jsonl", "*/*.jsonl"):
        yield session(found)


def requests(path):
    """The usage records of one session file, one for each request (breadcrumbs/usage.py record())."""
    sid, seen = os.path.basename(path)[:-len(".jsonl")], set()
    for record in JsonLines(path):
        message = record.get("message")
        use = message.get("usage") if record.get("type") == "assistant" and isinstance(message, dict) else None
        req = record.get("requestId") or message.get("id") if isinstance(use, dict) else None
        if not req or req in seen or message.get("model") == "<synthetic>":
            continue
        seen.add(req)
        yield usage_record.record("claude-code", sid, req, epoch(record.get("timestamp")), message.get("model"), "anthropic",
                                  use.get("input_tokens"), use.get("cache_read_input_tokens"),
                                  use.get("cache_creation_input_tokens"), use.get("output_tokens"), 0)


def usage(path=None):
    """The usage of the harness claude-code: the usage records of the files that sessions(path) reads."""
    for found in files(path, ROOT, "*.jsonl", "*/*.jsonl"):
        yield from requests(found)
