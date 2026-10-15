"""Render a 1920x1080 CATV promo HTML file to PNG.

Usage: python3 render.py poster.html poster.png
"""
import os
import pathlib
import shutil
import subprocess
import sys

W, H = 1920, 1080


def find_chromium():
    for name in ("chromium", "chromium-browser", "google-chrome"):
        path = shutil.which(name)
        if path:
            return path
    root = pathlib.Path(os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers"))
    hits = sorted(root.glob("chromium-*/chrome-linux*/chrome")) if root.exists() else []
    return str(hits[-1]) if hits else None


def render(src, out):
    url = pathlib.Path(src).resolve().as_uri()
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        chrome = find_chromium()
        if not chrome:
            sys.exit("Playwright and Chromium not found")
        subprocess.run([chrome, "--headless", "--no-sandbox", "--hide-scrollbars",
                        f"--window-size={W},{H}", "--virtual-time-budget=5000",
                        f"--screenshot={pathlib.Path(out).resolve()}", url], check=True)
        return
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": W, "height": H})
        page.goto(url, wait_until="networkidle")
        page.evaluate("document.fonts.ready")
        page.screenshot(path=out, clip={"x": 0, "y": 0, "width": W, "height": H})
        browser.close()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    render(sys.argv[1], sys.argv[2])
    print(f"saved {sys.argv[2]}")
