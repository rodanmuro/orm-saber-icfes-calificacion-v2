from __future__ import annotations

import json
import sys

from app.modules.omr_reader.errors import GeminiReadError
from app.modules.omr_reader.gemini_reader import ping_gemini_model


def main() -> int:
    try:
        result = ping_gemini_model()
    except GeminiReadError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 1

    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
