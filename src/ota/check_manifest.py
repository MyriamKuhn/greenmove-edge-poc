import hashlib
import json
from pathlib import Path


MANIFEST_PATH = Path(
    "src/ota/manifest.json"
)

PACKAGE_PATH = Path(
    "src/ota/packages/"
    "greenmove-2.3.0.pkg"
)

DEMO_PUBLIC_MARKER = (
    "greenmove-demo-public-marker"
)


def sha256_file(
    path: Path,
) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def expected_demo_signature(
    checksum: str,
) -> str:
    value = (
        f"{checksum}:"
        f"{DEMO_PUBLIC_MARKER}"
    )

    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def validate_manifest() -> dict:
    manifest = json.loads(
        MANIFEST_PATH.read_text(
            encoding="utf-8"
        )
    )

    checksum = sha256_file(
        PACKAGE_PATH
    )

    checksum_valid = (
        checksum
        == manifest["checksum"]
    )

    signature_valid = (
        manifest["demo_signature"]
        == expected_demo_signature(
            checksum
        )
    )

    return {
        "version": manifest["version"],
        "checksum_valid": checksum_valid,
        "signature_valid": signature_valid,
    }


def main() -> None:
    result = validate_manifest()

    if not result["checksum_valid"]:
        raise SystemExit(
            "[OTA] checksum invalid"
        )

    if not result["signature_valid"]:
        raise SystemExit(
            "[OTA] signature invalid"
        )

    print(
        "[OTA] manifest "
        f'version={result["version"]} '
        "signature=valid "
        "checksum=valid"
    )


if __name__ == "__main__":
    main()