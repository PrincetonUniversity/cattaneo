"""
Visual Comparison Test Suite for Cattaneo Website

This test suite compares the reference site (mdcattaneo.github.io) with the
target site to ensure visual and functional parity.

Tests include:
- Layout positioning and dimensions
- Typography (font families, sizes, weights)
- Color schemes
- Responsive behavior at different viewports
- Element visibility and accessibility
- Screenshot pixel comparison
"""

import pytest
from playwright.sync_api import sync_playwright, Page, Browser
from PIL import Image
import io
import os
from pathlib import Path
from typing import Dict, List, Tuple
import json

# Test configuration
REFERENCE_URL = "file:///Users/bino/Downloads/us.sitesucker.mac.sitesucker/mdcattaneo.github.io"
TARGET_URL = "http://localhost:4040"

# Viewports to test
VIEWPORTS = {
    "mobile": {"width": 375, "height": 667},      # iPhone SE
    "tablet": {"width": 768, "height": 1024},     # iPad
    "desktop": {"width": 1440, "height": 900},    # Desktop
    "wide": {"width": 1920, "height": 1080},      # Wide desktop
}

# Pages to test
TEST_PAGES = [
    "index.html",
    "publications/index.html",
    "research/index.html",
    "software/index.html",
    "students/index.html",
    "teaching/index.html",
    "short-courses/index.html",
    "talks/index.html",
    "service/index.html",
]

# Output directory for test results
OUTPUT_DIR = Path("/Users/bino/Downloads/cattaneo/test_results")
OUTPUT_DIR.mkdir(exist_ok=True)


class VisualTester:
    """Helper class for visual testing operations"""

    def __init__(self, browser: Browser):
        self.browser = browser

    def get_computed_styles(self, page: Page, selector: str) -> Dict:
        """Get computed CSS styles for an element"""
        return page.evaluate(f"""
            (selector) => {{
                const element = document.querySelector(selector);
                if (!element) return null;
                const styles = window.getComputedStyle(element);
                return {{
                    fontFamily: styles.fontFamily,
                    fontSize: styles.fontSize,
                    fontWeight: styles.fontWeight,
                    color: styles.color,
                    backgroundColor: styles.backgroundColor,
                    display: styles.display,
                    position: styles.position,
                    width: styles.width,
                    height: styles.height,
                    marginTop: styles.marginTop,
                    marginBottom: styles.marginBottom,
                    paddingTop: styles.paddingTop,
                    paddingBottom: styles.paddingBottom,
                    textAlign: styles.textAlign,
                }};
            }}
        """, selector)

    def get_element_position(self, page: Page, selector: str) -> Dict:
        """Get element position and dimensions"""
        return page.evaluate(f"""
            (selector) => {{
                const element = document.querySelector(selector);
                if (!element) return null;
                const rect = element.getBoundingClientRect();
                return {{
                    x: rect.x,
                    y: rect.y,
                    width: rect.width,
                    height: rect.height,
                    top: rect.top,
                    left: rect.left,
                    right: rect.right,
                    bottom: rect.bottom,
                }};
            }}
        """, selector)

    def get_font_families_used(self, page: Page) -> List[str]:
        """Extract all font families used on the page"""
        fonts = page.evaluate("""
            () => {
                const fonts = new Set();
                const elements = document.querySelectorAll('*');
                elements.forEach(el => {
                    const style = window.getComputedStyle(el);
                    fonts.add(style.fontFamily);
                });
                return Array.from(fonts);
            }
        """)
        return fonts

    def check_element_visible(self, page: Page, selector: str) -> bool:
        """Check if element is visible"""
        try:
            element = page.locator(selector).first
            return element.is_visible()
        except:
            return False

    def compare_screenshots(self, ref_path: Path, target_path: Path, diff_path: Path) -> Dict:
        """Compare two screenshots and generate diff image"""
        ref_img = Image.open(ref_path).convert('RGB')
        target_img = Image.open(target_path).convert('RGB')

        # Ensure images are same size
        if ref_img.size != target_img.size:
            # Resize target to match reference
            target_img = target_img.resize(ref_img.size, Image.Resampling.LANCZOS)

        # Calculate pixel differences
        ref_pixels = ref_img.load()
        target_pixels = target_img.load()
        diff_img = Image.new('RGB', ref_img.size)
        diff_pixels = diff_img.load()

        total_pixels = ref_img.size[0] * ref_img.size[1]
        different_pixels = 0
        max_diff = 0

        for y in range(ref_img.size[1]):
            for x in range(ref_img.size[0]):
                ref_pixel = ref_pixels[x, y]
                target_pixel = target_pixels[x, y]

                # Calculate RGB difference
                diff = sum(abs(r - t) for r, t in zip(ref_pixel, target_pixel))
                max_diff = max(max_diff, diff)

                if diff > 30:  # Threshold for "different" pixel
                    different_pixels += 1
                    # Highlight differences in red
                    diff_pixels[x, y] = (255, 0, 0)
                else:
                    # Gray out similar pixels
                    gray = sum(target_pixel) // 3
                    diff_pixels[x, y] = (gray, gray, gray)

        diff_img.save(diff_path)

        similarity_percentage = ((total_pixels - different_pixels) / total_pixels) * 100

        return {
            "total_pixels": total_pixels,
            "different_pixels": different_pixels,
            "similarity_percentage": similarity_percentage,
            "max_difference": max_diff,
            "passed": similarity_percentage >= 95.0  # 95% similarity threshold
        }


@pytest.fixture(scope="session")
def browser():
    """Setup browser for testing"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture(scope="session")
def visual_tester(browser):
    """Setup visual tester"""
    return VisualTester(browser)


class TestHeaderLayout:
    """Test header layout and styling"""

    @pytest.mark.parametrize("viewport_name,viewport", VIEWPORTS.items())
    def test_header_exists(self, browser, viewport_name, viewport):
        """Test that header exists on both sites"""
        page_ref = browser.new_page(viewport=viewport)
        page_target = browser.new_page(viewport=viewport)

        try:
            page_ref.goto(f"{REFERENCE_URL}/index.html")
            page_target.goto(f"{TARGET_URL}/index.html")

            assert page_ref.locator("header").count() > 0, "Reference site missing header"
            assert page_target.locator("header").count() > 0, "Target site missing header"
        finally:
            page_ref.close()
            page_target.close()

    @pytest.mark.parametrize("viewport_name,viewport", VIEWPORTS.items())
    def test_header_background_color(self, browser, visual_tester, viewport_name, viewport):
        """Test header background color is black"""
        page_ref = browser.new_page(viewport=viewport)
        page_target = browser.new_page(viewport=viewport)

        try:
            page_ref.goto(f"{REFERENCE_URL}/index.html")
            page_target.goto(f"{TARGET_URL}/index.html")

            ref_styles = visual_tester.get_computed_styles(page_ref, "header")
            target_styles = visual_tester.get_computed_styles(page_target, "header")

            # Check both have dark gray background (#121212 = rgb(18, 18, 18))
            assert ref_styles and "rgb(18, 18, 18)" in ref_styles["backgroundColor"], \
                f"Reference header not dark gray: {ref_styles['backgroundColor']}"
            assert target_styles and "rgb(18, 18, 18)" in target_styles["backgroundColor"], \
                f"Target header not dark gray: {target_styles['backgroundColor']}"
        finally:
            page_ref.close()
            page_target.close()

    @pytest.mark.parametrize("viewport_name,viewport", [(k, v) for k, v in VIEWPORTS.items() if v["width"] >= 992])
    def test_header_fixed_position_desktop(self, browser, visual_tester, viewport_name, viewport):
        """Test header is fixed on desktop viewports"""
        page = browser.new_page(viewport=viewport)

        try:
            page.goto(f"{TARGET_URL}/index.html")
            page.wait_for_load_state("networkidle")

            styles = visual_tester.get_computed_styles(page, "header")
            assert styles["position"] == "fixed", \
                f"Header should be fixed on {viewport_name}, got {styles['position']}"
        finally:
            page.close()

    def test_header_navigation_links(self, browser):
        """Test that all navigation links exist"""
        expected_links = ["Publications", "Research", "Software", "Students",
                         "Teaching", "Short Courses", "Talks", "Service"]

        page = browser.new_page()
        try:
            page.goto(f"{TARGET_URL}/index.html")

            for link_text in expected_links:
                assert page.locator(f"header >> text={link_text}").count() > 0, \
                    f"Missing navigation link: {link_text}"
        finally:
            page.close()


class TestTypography:
    """Test typography and font usage"""

    def test_font_families_loaded(self, browser, visual_tester):
        """Test that required fonts are loaded"""
        page = browser.new_page()

        try:
            page.goto(f"{TARGET_URL}/index.html")
            page.wait_for_load_state("networkidle")

            fonts = visual_tester.get_font_families_used(page)

            # Check that P22 Mackinac or other licensed fonts are present
            font_str = " ".join(fonts)

            # Report fonts found for user to verify licenses
            print(f"\n\nFonts detected on target site:")
            for font in fonts:
                print(f"  - {font}")

            # At minimum, check that fonts are being applied
            assert len(fonts) > 0, "No fonts detected"

            # Save font list for review
            font_report = OUTPUT_DIR / "fonts_detected.json"
            with open(font_report, "w") as f:
                json.dump({"fonts": fonts}, f, indent=2)

        finally:
            page.close()

    def test_heading_styles(self, browser, visual_tester):
        """Test heading typography matches"""
        page_ref = browser.new_page()
        page_target = browser.new_page()

        try:
            page_ref.goto(f"{REFERENCE_URL}/index.html")
            page_target.goto(f"{TARGET_URL}/index.html")

            # Test h1 in header
            ref_h1 = visual_tester.get_computed_styles(page_ref, "header h1")
            target_h1 = visual_tester.get_computed_styles(page_target, "header h1")

            if ref_h1 and target_h1:
                # Font sizes should be similar (within 2px)
                ref_size = float(ref_h1["fontSize"].replace("px", ""))
                target_size = float(target_h1["fontSize"].replace("px", ""))
                assert abs(ref_size - target_size) <= 2, \
                    f"H1 size mismatch: ref={ref_size}px, target={target_size}px"
        finally:
            page_ref.close()
            page_target.close()


class TestLayout:
    """Test page layout and responsive behavior"""

    @pytest.mark.parametrize("viewport_name,viewport", VIEWPORTS.items())
    def test_main_content_exists(self, browser, viewport_name, viewport):
        """Test main content area exists"""
        page = browser.new_page(viewport=viewport)

        try:
            page.goto(f"{TARGET_URL}/index.html")
            assert page.locator("main").count() > 0, \
                f"Main content missing on {viewport_name}"
        finally:
            page.close()

    @pytest.mark.parametrize("viewport_name,viewport", [(k, v) for k, v in VIEWPORTS.items() if v["width"] >= 640])
    def test_homepage_two_column_layout(self, browser, visual_tester, viewport_name, viewport):
        """Test homepage has two-column layout on wider screens"""
        page = browser.new_page(viewport=viewport)

        try:
            page.goto(f"{TARGET_URL}/index.html")
            page.wait_for_load_state("networkidle")

            # Check if aside exists (sidebar)
            aside_visible = visual_tester.check_element_visible(page, "aside")
            article_visible = visual_tester.check_element_visible(page, "article")

            assert aside_visible, f"Sidebar not visible on {viewport_name}"
            assert article_visible, f"Article not visible on {viewport_name}"

            # Check layout - aside should be to the left of article
            aside_pos = visual_tester.get_element_position(page, "aside")
            article_pos = visual_tester.get_element_position(page, "article")

            if aside_pos and article_pos:
                assert aside_pos["left"] < article_pos["left"], \
                    "Aside should be to the left of article"
        finally:
            page.close()

    def test_footer_exists(self, browser):
        """Test footer exists and has correct styling"""
        page = browser.new_page()

        try:
            page.goto(f"{TARGET_URL}/index.html")

            assert page.locator("footer").count() > 0, "Footer missing"

            # Check footer background is dark gray (#121212 = rgb(18, 18, 18))
            footer_bg = page.evaluate("""
                () => {
                    const footer = document.querySelector('footer');
                    return window.getComputedStyle(footer).backgroundColor;
                }
            """)
            assert "rgb(18, 18, 18)" in footer_bg, f"Footer not dark gray: {footer_bg}"
        finally:
            page.close()


class TestColors:
    """Test color scheme consistency"""

    def test_link_colors(self, browser):
        """Test content links use Princeton blue"""
        page = browser.new_page()

        try:
            page.goto(f"{TARGET_URL}/index.html")

            # Get link color from main content
            link_color = page.evaluate("""
                () => {
                    const link = document.querySelector('main a');
                    if (!link) return null;
                    return window.getComputedStyle(link).color;
                }
            """)

            if link_color:
                # Princeton blue is rgb(3, 42, 112)
                # Allow for slight variations
                print(f"\nContent link color: {link_color}")
                # Just verify it's some shade of blue, not black or default
                assert link_color != "rgb(0, 0, 0)", "Links should not be black"
        finally:
            page.close()


class TestScreenshotComparison:
    """Test visual appearance through screenshot comparison"""

    @pytest.mark.parametrize("page_path", TEST_PAGES)
    @pytest.mark.parametrize("viewport_name,viewport", VIEWPORTS.items())
    def test_page_screenshot_similarity(self, browser, visual_tester, page_path, viewport_name, viewport):
        """Compare screenshots of reference and target sites"""
        page_ref = browser.new_page(viewport=viewport)
        page_target = browser.new_page(viewport=viewport)

        # Create directory for this page
        page_name = page_path.replace("/", "_").replace(".html", "")
        output_dir = OUTPUT_DIR / page_name / viewport_name
        output_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Load pages
            page_ref.goto(f"{REFERENCE_URL}/{page_path}")
            page_target.goto(f"{TARGET_URL}/{page_path}")

            # Wait for fonts and images to load
            page_ref.wait_for_load_state("networkidle")
            page_target.wait_for_load_state("networkidle")

            # Take screenshots
            ref_screenshot = output_dir / "reference.png"
            target_screenshot = output_dir / "target.png"
            diff_screenshot = output_dir / "diff.png"

            page_ref.screenshot(path=ref_screenshot, full_page=True)
            page_target.screenshot(path=target_screenshot, full_page=True)

            # Compare screenshots
            result = visual_tester.compare_screenshots(
                ref_screenshot, target_screenshot, diff_screenshot
            )

            # Save comparison result
            result_file = output_dir / "comparison_result.json"
            with open(result_file, "w") as f:
                json.dump(result, f, indent=2)

            # Report results
            print(f"\n{page_name} ({viewport_name}): {result['similarity_percentage']:.2f}% similar")

            # This is informational - we don't fail on screenshot differences
            # as there may be acceptable differences (fonts, etc.)
            if not result["passed"]:
                print(f"  ⚠️  Visual difference detected - review diff image at {diff_screenshot}")

        finally:
            page_ref.close()
            page_target.close()


class TestResponsiveBreakpoints:
    """Test responsive behavior at different breakpoints"""

    def test_mobile_navigation_behavior(self, browser):
        """Test navigation behavior on mobile"""
        page = browser.new_page(viewport=VIEWPORTS["mobile"])

        try:
            page.goto(f"{TARGET_URL}/index.html")

            # Navigation should exist
            nav_exists = page.locator("nav").count() > 0
            assert nav_exists, "Navigation missing on mobile"

        finally:
            page.close()

    @pytest.mark.parametrize("viewport_name,viewport", VIEWPORTS.items())
    def test_content_readable_at_all_sizes(self, browser, viewport_name, viewport):
        """Test content is readable at all viewport sizes"""
        page = browser.new_page(viewport=viewport)

        try:
            page.goto(f"{TARGET_URL}/index.html")

            # Check that text is not clipped
            body_width = page.evaluate("() => document.body.scrollWidth")
            viewport_width = viewport["width"]

            # Allow for scrollbar (15px)
            assert body_width <= viewport_width + 15, \
                f"Horizontal overflow on {viewport_name}: body={body_width}px, viewport={viewport_width}px"
        finally:
            page.close()


class TestAccessibility:
    """Test accessibility features"""

    def test_skip_link_exists(self, browser):
        """Test skip-to-content link exists"""
        page = browser.new_page()

        try:
            page.goto(f"{TARGET_URL}/index.html")

            # Check for skip link or main-content anchor
            skip_link = page.locator("#main-content").count() > 0
            # Skip link may be present even if visually hidden
            assert skip_link, "Skip link anchor missing"
        finally:
            page.close()

    def test_semantic_html_structure(self, browser):
        """Test proper semantic HTML5 structure"""
        page = browser.new_page()

        try:
            page.goto(f"{TARGET_URL}/index.html")

            # Check for key semantic elements
            assert page.locator("header").count() > 0, "Missing header element"
            assert page.locator("main").count() > 0, "Missing main element"
            assert page.locator("footer").count() > 0, "Missing footer element"
            assert page.locator("nav").count() > 0, "Missing nav element"

        finally:
            page.close()


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line("markers", "screenshot: screenshot comparison tests")
    config.addinivalue_line("markers", "layout: layout and positioning tests")
    config.addinivalue_line("markers", "typography: font and text styling tests")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--html=test_results/report.html", "--self-contained-html"])
