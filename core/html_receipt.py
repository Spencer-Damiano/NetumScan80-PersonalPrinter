"""
core/html_receipt.py — HTML-based receipt renderer.

Renders a receipt to:
  - An HTML file (open in browser)
  - A PNG image (open in image viewer / send to printer)

Conversion priority:
  1. imgkit (needs wkhtmltopdf) — faster
  2. Selenium + Chrome (auto-managed via webdriver-manager) — fallback

Install:
    pip install imgkit selenium webdriver-manager
    wkhtmltopdf (optional): https://wkhtmltopdf.org/downloads.html

Receipt width is fixed at 72mm. Height flows naturally with content —
character limit is the primary control over receipt length.
"""

import os
from datetime import datetime

try:
    import imgkit
    IMGKIT_AVAILABLE = True
except ImportError:
    IMGKIT_AVAILABLE = False

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from webdriver_manager.chrome import ChromeDriverManager
    import time
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# ── Printer geometry ──────────────────────────────────────────────────────────
# NS8360 printable width: 72mm
# 1mm = 3.7795px at 96 DPI — rendered at 2x for crispness:
#   72mm × 3.7795 × 2 = 544px wide
# Height is no longer fixed — it flows with content.
RECEIPT_WIDTH_PX = 544

# Hard character limit — this is now your primary control over receipt length.
# Tune this number to get the physical receipt size you want.
# 550 is the test ceiling; real tasks should be well under that.
DESCRIPTION_CHAR_LIMIT = 550

# wkhtmltopdf binary (only needed if imgkit is being used)
WKHTMLTOIMAGE_PATH = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltoimage.exe"

PRIORITY_LABELS = {
    0: "FUTURE / BREAKDOWN",
    1: "LOW",
    2: "MEDIUM",
    3: "HIGH",
}


def truncate(text: str, limit: int = DESCRIPTION_CHAR_LIMIT) -> str:
    """Hard-truncate text to the character limit."""
    return text[:limit]


def build_html(title: str, description: str, priority: int) -> str:
    """
    Return a complete HTML string for the receipt.
    Description is truncated to DESCRIPTION_CHAR_LIMIT before rendering.
    Height is determined by content — no fixed canvas.
    """
    priority_label = PRIORITY_LABELS.get(priority, "UNKNOWN")
    timestamp      = datetime.now().strftime("%Y-%m-%d  %H:%M")
    description    = truncate(description)

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
      width: {RECEIPT_WIDTH_PX}px;
      padding: 14px 18px 10px 18px;
      /* No fixed height — content defines the receipt length */
    }}

    .border {{
      border-top: 2px solid black;
    }}

    .title {{
      font-size: 34px;
      font-weight: bold;
      text-align: center;
      text-transform: uppercase;
      letter-spacing: 2px;
      padding: 8px 0;
    }}

    .priority {{
      font-size: 22px;
      font-weight: bold;
      text-align: center;
      letter-spacing: 1px;
      padding: 6px 0;
      color: black;
    }}

    .description {{
      padding: 10px 0;
    }}

    .description p {{
      font-size: 24px;
      font-weight: 600;
      line-height: 1.4;
      text-align: center;
      word-wrap: break-word;
      width: 100%;
      margin: 0;
      color: black;
    }}

    .timestamp {{
      font-size: 13px;
      font-weight: bold;
      text-align: center;
      color: black;
      padding: 5px 0 0 0;
    }}
  </style>
</head>
<body>
  <div class="border"></div>
  <div class="title">{title}</div>
  <div class="border"></div>
  <div class="priority">PRIORITY: {priority_label}</div>
  <div class="border"></div>

  <div class="description"><p>{description}</p></div>

  <div class="border"></div>
  <div class="timestamp">{timestamp}</div>
</body>
</html>"""


def save_html(title: str, description: str, priority: int, path: str) -> str:
    """Write the receipt HTML to a file and return the path."""
    html = build_html(title, description, priority)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return path


def _render_png_imgkit(html: str, path: str) -> str | None:
    """Render HTML to PNG using imgkit. Returns path or None on failure."""
    if not IMGKIT_AVAILABLE:
        return None

    if not os.path.exists(WKHTMLTOIMAGE_PATH):
        return None

    try:
        config  = imgkit.config(wkhtmltoimage=WKHTMLTOIMAGE_PATH)
        options = {
            "width": str(RECEIPT_WIDTH_PX),
            # No height option — let imgkit size to content
            "disable-smart-width": "",
            "encoding": "UTF-8",
            "format": "png",
        }
        imgkit.from_string(html, path, options=options, config=config)
        return path
    except Exception as e:
        print(f"  imgkit failed: {e}")
        return None


def _render_png_selenium(html: str, path: str) -> str | None:
    """Render HTML to PNG using headless Chrome via Selenium. Returns path or None on failure."""
    if not SELENIUM_AVAILABLE:
        print("  ERROR: selenium or webdriver-manager not installed.")
        print("  Run: pip install selenium webdriver-manager")
        return None

    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        # Width fixed, height large enough that content is never clipped
        options.add_argument(f"--window-size={RECEIPT_WIDTH_PX},2000")

        service = Service(ChromeDriverManager().install())
        driver  = webdriver.Chrome(service=service, options=options)

        import tempfile
        tmp_html = os.path.join(tempfile.gettempdir(), "receipt_preview", "_render.html")
        with open(tmp_html, "w", encoding="utf-8") as f:
            f.write(html)

        driver.get(f"file:///{tmp_html.replace(os.sep, '/')}")
        time.sleep(0.5)

        # Screenshot the body element — now that height is natural,
        # the body's rendered height == the actual content height, no clipping.
        body = driver.find_element(By.TAG_NAME, "body")
        body.screenshot(path)
        driver.quit()

        return path
    except Exception as e:
        print(f"  Selenium failed: {e}")
        return None


def render_png(title: str, description: str, priority: int, path: str) -> str | None:
    """
    Render the receipt HTML to a PNG image and return the path.
    Tries imgkit first, falls back to Selenium if imgkit/wkhtmltopdf is unavailable.
    Returns None if both methods fail.
    """
    html = build_html(title, description, priority)

    result = _render_png_imgkit(html, path)
    if result:
        return result

    print("  imgkit unavailable, trying Selenium...")
    return _render_png_selenium(html, path)