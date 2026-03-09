#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib import request


def http_json(url: str, *, method: str = "GET", payload: dict | None = None) -> dict:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    req = request.Request(url, method=method, data=body, headers={"Content-Type": "application/json"})
    with request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Simple PlaybookOS operator helper")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("manifest")
    sub.add_parser("context")

    intake = sub.add_parser("intake")
    intake.add_argument("--message", default="")
    intake.add_argument("--markdown-file")
    intake.add_argument("--resource-name")
    intake.add_argument("--goal-id")
    intake.add_argument("--allow-side-effects", action="store_true")

    args = parser.parse_args()
    base = args.base_url.rstrip("/")

    if args.command == "manifest":
        result = http_json(f"{base}/api/agent/manifest")
    elif args.command == "context":
        result = http_json(f"{base}/api/agent/context")
    else:
        markdown_sop = None
        if args.markdown_file:
            markdown_sop = Path(args.markdown_file).read_text()
        result = http_json(
            f"{base}/api/agent/intake",
            method="POST",
            payload={
                "message": args.message,
                "markdown_sop": markdown_sop,
                "resource_name": args.resource_name,
                "goal_id": args.goal_id,
                "allow_side_effects": args.allow_side_effects,
            },
        )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
