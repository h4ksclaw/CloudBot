from types import SimpleNamespace

import pytest

from cloudbot.agent.common import download
from cloudbot.agent.tools import github, web

SPEC = "# Bot Tools\n" + "line of the spec\n" * 3000


class EndlessResponse:
    read = 0

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def raise_for_status(self):
        pass

    def iter_content(self, size):
        while True:
            self.read += size
            yield b"x" * size


def test_a_download_stops_reading_at_its_limit(monkeypatch):
    resp = EndlessResponse()
    monkeypatch.setattr(
        "cloudbot.agent.common.requests.get", lambda *a, **k: resp
    )
    with pytest.raises(ValueError, match="over the 1 MB limit"):
        download("https://example.com/10Gb.dat", 1_000_000)
    assert resp.read < 1_100_000


def test_a_long_page_names_its_size_and_where_to_continue():
    first = web.page_of(SPEC, 0)
    assert first.startswith(f"TRUNCATED chars 0-40000 of {len(SPEC)}")
    assert "offset=40000" in first
    rest = web.page_of(SPEC, 40000)
    assert rest.endswith(SPEC[40000:])
    assert "end of page" in rest


def test_a_short_page_comes_back_whole():
    assert web.page_of("short", 0) == "short"


@pytest.mark.asyncio
async def test_a_source_url_is_committed_byte_for_byte(monkeypatch):
    commits = []

    async def call(ctx, name, args):
        commits.append(args)
        return "committed"

    async def no_file(ctx, name, args):
        return "(error: not found)"

    monkeypatch.setattr(
        "cloudbot.agent.tools.github.bump_budget", lambda ctx, kind: None
    )
    monkeypatch.setattr("cloudbot.agent.tools.github.mcp_call_raw", no_file)
    monkeypatch.setattr("cloudbot.agent.tools.github.mcp_call", call)
    monkeypatch.setattr(
        "cloudbot.agent.tools.github._download_text", lambda url: SPEC
    )
    result = await github.edit_github_file(
        SimpleNamespace(context=None),
        {
            "repo": "h4ksclaw/extensions",
            "path": "bot-tools.md",
            "branch": "add/bot-tools",
            "source_url": "https://gist.example/raw/bot-tools.md",
        },
    )
    assert result == "committed"
    assert commits[0]["content"] == SPEC
