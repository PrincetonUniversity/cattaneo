#!/usr/bin/env python3
"""Debug script to check header positioning"""

from playwright.sync_api import sync_playwright

TARGET_URL = "file:///Users/bino/Downloads/cattaneo/_site"

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1440, "height": 900})

    page.goto(f"{TARGET_URL}/index.html")
    page.wait_for_load_state("networkidle")

    # Get computed styles
    header_styles = page.evaluate("""
        () => {
            const header = document.querySelector('header');
            const styles = window.getComputedStyle(header);
            return {
                position: styles.position,
                top: styles.top,
                display: styles.display,
                width: styles.width,
                backgroundColor: styles.backgroundColor,
                zIndex: styles.zIndex
            };
        }
    """)

    print("Header computed styles at 1440x900:")
    for key, value in header_styles.items():
        print(f"  {key}: {value}")

    # Check if media query matches
    media_matches = page.evaluate("""
        () => window.matchMedia('(min-width: 992px)').matches
    """)
    print(f"\nMedia query (min-width: 992px) matches: {media_matches}")

    # Get all stylesheets
    stylesheets = page.evaluate("""
        () => {
            return Array.from(document.styleSheets).map(sheet => {
                try {
                    return sheet.href || 'inline';
                } catch (e) {
                    return 'inaccessible';
                }
            });
        }
    """)
    print(f"\nLoaded stylesheets: {stylesheets}")

    browser.close()
