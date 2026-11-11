"""The sessions of Claude Code as a source of the ingest (`python -m breadcrumbs ingest claude-code [PATH]`).

Claude Code keeps one JSON-lines file for each session: ~/.claude/projects/<project folder>/<session id>.jsonl. (The
files of its subagents sit deeper, in <session id>/subagents/, and are not read.) The record types that this reads:

    user       message.content is a text (a user turn), or a list of parts: "text" (a user turn) and "tool_result"
               (a tool row; its content is a text or a list of text parts)
    assistant  message.content is a list of parts: "text" and "tool_use" (id, name, input). One message is written as
               one record for each part; the parts join into one row. The "thinking" parts are skipped.
    ai-title   aiTitle: the title of the session

Every other record type (attachments, api requests, file history, modes, system) is skipped, and so is a record whose
isMeta is true. The session meta keeps cwd and branch (gitBranch) of the first record that has them.
"""
import os

from breadcrumbs.transcript import JsonLines, Rows, epoch, files, meta, text_parts

ROOT = "~/.claude/projects"


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
                rows.result(part.get("tool_use_id"), text_parts(part.get("content")), ts)
    return os.path.basename(path)[:-len(".jsonl")], title, meta(skipped=lines.bad, **where), rows.rows


def sessions(path=None):
    """The source of the harness claude-code: the sessions of a file, of a project folder, or of the folder
    ~/.claude/projects (the default), each (id, title, meta, rows)."""
    for found in files(path, ROOT, "*.jsonl", "*/*.jsonl"):
        yield session(found)
