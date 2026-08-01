"""Provider-neutral public-endpoint (tunnel) adapter (P23 connectivity).

An interface lets tunnel providers (ngrok, Localtonet, ...) be swapped via config
without code changes. LocalTunnel keeps localhost working; ConfiguredTunnel wraps an
externally-started public HTTPS URL. We never start a paid provider or fabricate a
URL -- obtaining the real public URL is BLOCKED-EXTERNAL. Public counted matches
REQUIRE https://; tokens/URLs come only from ignored env/config and are never logged."""

import os
import re
import socket
from dataclasses import dataclass
from urllib.parse import urlparse

from ..exceptions import ConfigError

LOCAL_HOSTS = frozenset({"127.0.0.1", "localhost", "::1"})
_HEADER_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9-]*$")


def tunnel_headers(env: dict | None = None) -> dict:
    """Optional public-tunnel HTTP headers from PT_TUNNEL_HEADERS, e.g. a provider warning
    bypass like 'localtonet-skip-warning: true'. Format: one or more 'Name: Value' entries
    separated by newlines or ';'. Unset/empty -> {} so default behavior is unchanged. Rejects
    malformed entries and any attempt to set Authorization, so bearer auth is never weakened.
    Values are provider flags (not secrets) and are never logged."""
    raw = (env if env is not None else os.environ).get("PT_TUNNEL_HEADERS", "").strip()
    if not raw:
        return {}
    headers: dict = {}
    for entry in re.split(r"[;\n]", raw):
        entry = entry.strip()
        if not entry:
            continue
        name, sep, value = entry.partition(":")
        name, value = name.strip(), value.strip()
        if not sep or not _HEADER_NAME.match(name) or not value:
            raise ConfigError(f"malformed tunnel header (expected 'Name: Value'): {entry!r}")
        if any(ord(c) < 32 for c in value):
            raise ConfigError("tunnel header value contains control characters")
        if name.lower() == "authorization":
            raise ConfigError("tunnel headers may not override Authorization")
        headers[name] = value
    return headers


def _port_open(host: str, port: int, timeout: float = 0.5) -> bool:
    try:
        with socket.create_connection((host, port), timeout):
            return True
    except OSError:
        return False


def validate_endpoint(url: str) -> bool:
    """True if the URL is a well-formed http(s) MCP endpoint."""
    p = urlparse(url or "")
    return bool(p.scheme in ("http", "https") and p.hostname and p.path)


def validate_public_endpoint(url: str) -> None:
    """Fail closed on a malformed endpoint or a non-local http:// (TLS) endpoint used
    for a public counted match. Localhost may use http for local rehearsal."""
    p = urlparse(url or "")
    if p.scheme not in ("http", "https") or not p.hostname:
        raise ValueError("malformed endpoint URL")
    if p.hostname not in LOCAL_HOSTS and p.scheme != "https":
        raise ValueError("public counted match requires an https:// (TLS) endpoint")


@dataclass
class LocalTunnel:
    """Localhost 'tunnel': no external provider (default; always available)."""

    host: str = "127.0.0.1"
    port: int = 8000

    def public_url(self) -> str:
        return f"http://{self.host}:{self.port}/mcp"

    def healthy(self) -> bool:
        return _port_open(self.host, self.port)


@dataclass
class ConfiguredTunnel:
    """Wrap an externally-provided public HTTPS URL (provider process is external)."""

    url: str

    def public_url(self) -> str:
        return self.url

    def healthy(self) -> bool:
        p = urlparse(self.url)
        return bool(p.hostname) and _port_open(
            p.hostname, p.port or (443 if p.scheme == "https" else 80)
        )


def make_tunnel(cfg: dict):
    """Select a tunnel adapter from config. provider='local' (default) or a configured
    public URL. Missing public URL -> BLOCKED-EXTERNAL (we never fabricate one)."""
    provider = (cfg or {}).get("provider", "local")
    if provider == "local":
        return LocalTunnel(cfg.get("host", "127.0.0.1"), int(cfg.get("port", 8000)))
    url = (cfg or {}).get("url") or os.environ.get("PT_TUNNEL_URL")
    if not url:
        raise RuntimeError("BLOCKED-EXTERNAL: no public tunnel URL configured (PT_TUNNEL_URL)")
    return ConfiguredTunnel(url)
