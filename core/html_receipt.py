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

Receipt size: 72mm wide x 75mm tall (fixed — always the same physical size)
The printer has a 15mm physical header gap, so 75mm is the usable print area.
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
# Target receipt height:  75mm (printer has 15mm physical header gap)
#
# wkhtmltoimage works at 96 DPI by default.
# 1mm = 3.7795px at 96 DPI — rendered at 2x for crispness:
#   72mm × 3.7795 × 2 = 544px wide
#   75mm × 3.7795 × 2 = 567px tall
RECEIPT_WIDTH_PX  = 544
RECEIPT_HEIGHT_PX = 567  # 75mm at 2x

# Hard character limit for the description.
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
      width:    {RECEIPT_WIDTH_PX}px;
      height:   {RECEIPT_HEIGHT_PX}px;
      overflow: hidden;
      padding: 16px 18px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
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
            "width":  str(RECEIPT_WIDTH_PX),
            "height": str(RECEIPT_HEIGHT_PX),
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
        options.add_argument(f"--window-size={RECEIPT_WIDTH_PX},{RECEIPT_HEIGHT_PX + 100}")

        # webdriver-manager auto-downloads the right ChromeDriver version
        service = Service(ChromeDriverManager().install())
        driver  = webdriver.Chrome(service=service, options=options)

        # Write HTML to a temp file and load it
        import tempfile
        tmp_html = os.path.join(tempfile.gettempdir(), "receipt_preview", "_render.html")
        with open(tmp_html, "w", encoding="utf-8") as f:
            f.write(html)

        driver.get(f"file:///{tmp_html.replace(os.sep, '/')}")
        time.sleep(0.5)  # let the page settle

        # Screenshot just the body element
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

    # Try imgkit first (faster, no browser startup)
    result = _render_png_imgkit(html, path)
    if result:
        return result

    # Fall back to Selenium
    print("  imgkit unavailable, trying Selenium...")
    return _render_png_selenium(html, path)