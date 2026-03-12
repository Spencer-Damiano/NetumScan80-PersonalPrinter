"""
core/html_receipt.py — HTML-based receipt renderer.

Renders a receipt to an HTML file and/or a PNG image.

Conversion priority:
    1. imgkit  — fast, requires wkhtmltopdf to be installed
    2. Selenium — fallback, auto-manages ChromeDriver via webdriver-manager

Install:
    pip install imgkit selenium webdriver-manager
    wkhtmltopdf (optional): https://wkhtmltopdf.org/downloads.html

Receipt size: 72 mm wide × 75 mm tall (fixed — always the same physical size).
The NS8360 has a ~15 mm physical header gap, so 75 mm is the usable print area.
Rendered at 2× for crispness: 544 × 567 px.
"""

import os
from datetime import datetime

try:
    import imgkit
    _IMGKIT_AVAILABLE = True
except ImportError:
    _IMGKIT_AVAILABLE = False

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from webdriver_manager.chrome import ChromeDriverManager
    import time
    _SELENIUM_AVAILABLE = True
except ImportError:
    _SELENIUM_AVAILABLE = False


# ── Geometry ──────────────────────────────────────────────────────────────────
# 1 mm = 3.7795 px at 96 DPI; rendered at 2× for crispness.

RECEIPT_WIDTH_PX  = 544   # 72 mm × 3.7795 × 2
RECEIPT_HEIGHT_PX = 567   # 75 mm × 3.7795 × 2

DESCRIPTION_CHAR_LIMIT = 550

WKHTMLTOIMAGE_PATH = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltoimage.exe"

PRIORITY_LABELS = {
    0: "NOTE",
    1: "CRAWL",
    2: "WALK",
    3: "RUN",
}


# ── HTML builder ──────────────────────────────────────────────────────────────

def _truncate(text: str, limit: int = DESCRIPTION_CHAR_LIMIT) -> str:
    return text[:limit]


def build_html(title: str, description: str, priority: int) -> str:
    """Return a complete HTML string for one receipt."""
    priority_label = PRIORITY_LABELS.get(priority, "UNSET")
    timestamp      = datetime.now().strftime("%Y-%m-%d  %H:%M")
    description    = _truncate(description)

    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    * {{
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }}

    body {{
      font-family: 'Courier New', Courier, monospace;
      background: white;
      width:    {RECEIPT_WIDTH_PX}px;
      height:   {RECEIPT_HEIGHT_PX}px;
      overflow: hidden;
      padding: 16px 18px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }}

    .border     {{ border-top: 2px solid black; }}

    .title {{
      font-size: 34px;
      font-weight: bold;
      text-align: center;
      text-transform: uppercase;
      letter-spacing: 2px;
      padding: 8px 0;
    }}

    .priority {{
      font-size: 16px;
      text-align: center;
      letter-spacing: 1px;
      padding: 6px 0;
    }}

    .description {{
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 8px 0;
      overflow: hidden;
    }}

    .description p {{
      font-size: 20px;
      line-height: 1.45;
      text-align: center;
      word-wrap: break-word;
      width: 100%;
      margin: 0;
    }}

    .timestamp {{
      font-size: 14px;
      text-align: center;
      color: #555;
      padding: 6px 0;
    }}
  </style>
</head>
<body>
  <div>
    <div class="border"></div>
    <div class="title">{title}</div>
    <div class="border"></div>
    <div class="priority">PRIORITY: {priority_label}</div>
    <div class="border"></div>
  </div>

  <div class="description"><p>{description}</p></div>

  <div>
    <div class="border"></div>
    <div class="timestamp">{timestamp}</div>
    <div class="border"></div>
  </div>
</body>
</html>"""


# ── File I/O ──────────────────────────────────────────────────────────────────

def save_html(title: str, description: str, priority: int, path: str) -> str:
    """Write the receipt HTML to a file and return the path."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(build_html(title, description, priority))
    return path


# ── PNG rendering ─────────────────────────────────────────────────────────────

def _render_via_imgkit(html: str, path: str) -> str | None:
    if not _IMGKIT_AVAILABLE:
        return None
    if not os.path.exists(WKHTMLTOIMAGE_PATH):
        return None

    try:
        config  = imgkit.config(wkhtmltoimage=WKHTMLTOIMAGE_PATH)
        options = {
            "width":               str(RECEIPT_WIDTH_PX),
            "height":              str(RECEIPT_HEIGHT_PX),
            "disable-smart-width": "",
            "encoding":            "UTF-8",
            "format":              "png",
        }
        imgkit.from_string(html, path, options=options, config=config)
        return path
    except Exception as e:
        print(f"  imgkit error: {e}")
        return None


def _render_via_selenium(html: str, path: str) -> str | None:
    if not _SELENIUM_AVAILABLE:
        print("  ERROR: selenium / webdriver-manager not installed.")
        print("  Run: pip install selenium webdriver-manager")
        return None

    try:
        import tempfile

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(
            f"--window-size={RECEIPT_WIDTH_PX},{RECEIPT_HEIGHT_PX + 100}"
        )

        service = Service(ChromeDriverManager().install())
        driver  = webdriver.Chrome(service=service, options=options)

        tmp_dir  = os.path.join(tempfile.gettempdir(), "receipt_preview")
        tmp_html = os.path.join(tmp_dir, "_render.html")
        os.makedirs(tmp_dir, exist_ok=True)

        with open(tmp_html, "w", encoding="utf-8") as f:
            f.write(html)

        driver.get(f"file:///{tmp_html.replace(os.sep, '/')}")
        time.sleep(0.5)

        driver.find_element(By.TAG_NAME, "body").screenshot(path)
        driver.quit()
        return path
    except Exception as e:
        print(f"  Selenium error: {e}")
        return None


def render_png(title: str, description: str, priority: int, path: str) -> str | None:
    """
    Render the receipt to a PNG and return the path.
    Tries imgkit first, falls back to Selenium if unavailable.
    Returns None if both fail.
    """
    html   = build_html(title, description, priority)
    result = _render_via_imgkit(html, path)

    if result is None:
        print("  imgkit unavailable, trying Selenium...")
        result = _render_via_selenium(html, path)

    return result