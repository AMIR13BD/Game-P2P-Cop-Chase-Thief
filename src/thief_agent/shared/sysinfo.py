"""Best-effort local machine spec for the Step-0 declaration (stdlib only)."""

import os
import platform


def system_spec() -> dict:
    return {
        "os": platform.platform(),
        "python": platform.python_version(),
        "cpu_type": platform.processor() or platform.machine(),
        "cpu_cores": os.cpu_count() or 0,
    }
