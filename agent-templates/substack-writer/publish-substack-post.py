#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = ["requests", "browser-cookie3"]
# ///
"""
Post Notes to Substack.

Usage:
    ./substack_post.py "Your note content here"
    echo "My note" | ./substack_post.py
    ./substack_post.py < note.txt

Requires: Be logged into substack.com in Firefox.

TODO:
- Image upload support
- Allow posting to drafts
"""

import sys

import browser_cookie3
import requests


def load_firefox_cookies() -> requests.cookies.RequestsCookieJar:
    try:
        return browser_cookie3.firefox(domain_name="substack.com")
    except Exception as e:
        print(f"Error: Failed to load Firefox cookies: {e}", file=sys.stderr)
        sys.exit(1)


def build_doc_content(content: str) -> list:
    paragraphs = content.split("\n\n")
    doc_content = []
    
    for para in paragraphs:
        if para.strip():
            lines = para.split("\n")
            para_content = []
            for i, line in enumerate(lines):
                if line.strip():
                    para_content.append({"type": "text", "text": line})
                    if i < len(lines) - 1:
                        para_content.append({"type": "hardBreak"})
            if para_content:
                doc_content.append({"type": "paragraph", "content": para_content})
        else:
            doc_content.append({"type": "paragraph"})
    
    return doc_content


def post_note(session: requests.Session, content: str) -> str:
    response = session.post(
        "https://substack.com/api/v1/comment/feed",
        json={
            "bodyJson": {
                "type": "doc",
                "attrs": {"schemaVersion": "v1"},
                "content": build_doc_content(content),
            },
            "tabId": "for-you",
            "replyMinimumRole": "everyone",
        },
    )
    
    if response.status_code != 200:
        print(f"Error: Failed to post note (HTTP {response.status_code}): {response.text[:500]}", file=sys.stderr)
        sys.exit(1)
    
    data = response.json()
    note_id = data.get("id")
    if note_id:
        return f"https://substack.com/notes/post/p-{note_id}"
    return str(data)


def main():
    if len(sys.argv) > 1:
        content = sys.argv[1]
    elif not sys.stdin.isatty():
        content = sys.stdin.read()
    else:
        print("Error: No content provided. Pass as argument or pipe to stdin.", file=sys.stderr)
        sys.exit(1)
    
    content = content.strip()
    if not content:
        print("Error: Content is empty", file=sys.stderr)
        sys.exit(1)
    
    session = requests.Session()
    session.cookies = load_firefox_cookies()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:128.0) Gecko/20100101 Firefox/128.0",
        "Accept": "application/json",
        "Origin": "https://substack.com",
        "Referer": "https://substack.com/notes",
    })
    
    url = post_note(session, content)
    print(url)


if __name__ == "__main__":
    main()

