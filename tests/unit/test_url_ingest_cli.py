from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread


def _last_json(stdout: str) -> dict[str, object]:
    lines = [line for line in stdout.splitlines() if line.strip()]
    assert lines
    return json.loads(lines[-1])


def _run_local_http_server() -> tuple[ThreadingHTTPServer, Thread, str]:
    body = b"<html><head><title>CLI URL Test</title></head><body><h1>CLI URL</h1><p>It works.</p></body></html>"

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args: object) -> None:
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    url = f"http://127.0.0.1:{server.server_port}/source"
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread, url


def test_cli_parser_includes_ingest_url_help() -> None:
    from llm_wiki_core.cli import build_parser

    help_text = build_parser().format_help()

    assert "ingest-url" in help_text


def test_cli_ingest_url_prints_summary(tmp_path, capsys) -> None:
    from llm_wiki_core.cli import main
    from llm_wiki_core.operations.init import init_vault

    init_vault(tmp_path, purpose="CLI URL")
    server, thread, url = _run_local_http_server()
    try:
        exit_code = main(["ingest-url", str(tmp_path), url])
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "ingest-url success" in output
    assert f"url: {url}" in output
    assert "snapshot: " in output
    assert "source: " in output
    assert "raw: " in output
    assert "created: " in output
    assert "updated: " in output
    assert "next: Query the wiki, lint the vault, or ingest another URL." in output


def test_cli_ingest_url_json_supports_success_output(tmp_path, capsys) -> None:
    from llm_wiki_core.cli import main
    from llm_wiki_core.operations.init import init_vault

    init_vault(tmp_path, purpose="CLI URL JSON")
    server, thread, url = _run_local_http_server()
    try:
        exit_code = main(["ingest-url", str(tmp_path), url, "--json"])
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    assert exit_code == 0
    payload = _last_json(capsys.readouterr().out)
    assert payload["operation"] == "ingest-url"
    assert payload["status"] == "success"
    assert payload["url"] == url
    assert payload["snapshot_path"]
    assert payload["raw_snapshot_path"]


def test_cli_ingest_url_rejects_invalid_url(tmp_path, capsys) -> None:
    from llm_wiki_core.cli import main
    from llm_wiki_core.operations.init import init_vault

    init_vault(tmp_path, purpose="CLI URL invalid")

    exit_code = main(["ingest-url", str(tmp_path), "file:///tmp/source.md"])

    assert exit_code == 1
    captured = capsys.readouterr()
    assert "ingest-url error" in captured.err
    assert "Only explicit http and https URLs are supported" in captured.err


def test_cli_ingest_url_json_error_is_machine_readable(tmp_path, capsys) -> None:
    from llm_wiki_core.cli import main
    from llm_wiki_core.operations.init import init_vault

    init_vault(tmp_path, purpose="CLI URL JSON invalid")

    exit_code = main(["ingest-url", str(tmp_path), "data:text/plain,hello", "--json"])

    assert exit_code == 1
    payload = _last_json(capsys.readouterr().out)
    assert payload["operation"] == "ingest-url"
    assert payload["status"] == "error"
    assert payload["error"]["type"] == "ValueError"
