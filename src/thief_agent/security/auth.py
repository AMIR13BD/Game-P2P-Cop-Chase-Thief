"""Application-level bearer-token authorization over the real FastMCP transport.

Tokens are validated against an allow-list with a separate revocation set; a revoked
token is rejected even if present in the allow-list."""


class AuthRegistry:
    def __init__(self, valid: set[str], revoked: set[str] | None = None) -> None:
        self.valid = set(valid)
        self.revoked = set(revoked or ())

    def check(self, token: str | None) -> bool:
        return bool(token) and token in self.valid and token not in self.revoked

    def revoke(self, token: str) -> None:
        self.revoked.add(token)


def bearer_from_header(headers: dict) -> str | None:
    """Extract the token from an 'Authorization: Bearer <token>' header."""
    value = (headers or {}).get("authorization", "")
    if value.lower().startswith("bearer "):
        return value[7:].strip()
    return None
