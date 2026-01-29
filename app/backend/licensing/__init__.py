from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LicenseStatus:
    valid: bool
    message: str


def validate_license(_: str) -> LicenseStatus:
    return LicenseStatus(valid=False, message="Licensing disabled in MVP")
