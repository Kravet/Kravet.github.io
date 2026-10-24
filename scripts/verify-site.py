#!/usr/bin/env python3
"""Check the static portfolio contract without third-party dependencies."""

from html.parser import HTMLParser
import math
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_SECTIONS = {
    "hero",
    "achievements",
    "battery-alarm",
    "engineering",
    "apps",
    "learning",
    "teaching",
    "experience",
    "about",
    "contact",
}
REQUIRED_APP_LISTINGS = {
    "https://play.google.com/store/apps/details?id=com.seetree.prod",
    "https://play.google.com/store/apps/details?id=ua.tickets.gd",
    "https://play.google.com/store/apps/details?id=pl.tickets.avia",
    "https://play.google.com/store/apps/details?id=com.kissandfly.avia",
    "https://play.google.com/store/apps/details?id=de.zalando.mobile",
    "https://play.google.com/store/apps/details?id=com.mobiledatalabs.mileiq",
    "https://play.google.com/store/apps/details?id=com.onoff24.android",
}


class PortfolioParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.links = []
        self.product_icons = []
        self.product_icon_links = []
        self.local_resources = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        if tag == "a" and "href" in attrs:
            self.links.append(attrs["href"])
            if "product-icon-link" in attrs.get("class", "").split():
                self.product_icon_links.append(attrs["href"])
        if tag == "img" and "product-app-icon" in attrs.get("class", "").split():
            self.product_icons.append(attrs)
        if tag in {"img", "script", "link", "source"}:
            path = attrs.get("src") or attrs.get("href")
            if path:
                self.local_resources.append(path)


def main():
    page = ROOT / "index.html"
    assert page.is_file(), "Portfolio page has not been built yet"
    html = page.read_text(encoding="utf-8")
    parser = PortfolioParser()
    parser.feed(html)

    missing_sections = REQUIRED_SECTIONS - parser.ids
    assert not missing_sections, f"Missing portfolio sections: {sorted(missing_sections)}"
    missing_app_listings = REQUIRED_APP_LISTINGS - set(parser.links)
    assert not missing_app_listings, f"Missing Google Play links: {sorted(missing_app_listings)}"
    assert len(parser.product_icons) == len(REQUIRED_APP_LISTINGS), (
        f"Expected {len(REQUIRED_APP_LISTINGS)} square Play Store app icons, "
        f"found {len(parser.product_icons)}"
    )
    assert set(parser.product_icon_links) == REQUIRED_APP_LISTINGS, (
        "Each app icon must link to its matching Google Play listing"
    )
    assert all(
        icon.get("width") and icon.get("width") == icon.get("height")
        for icon in parser.product_icons
    ), (
        "Play Store app icons must use square dimensions"
    )
    assert not re.search(r'<meta\s+name="robots"\s+content="noindex', html), (
        "Published portfolio must allow search indexing"
    )
    assert 'rel="canonical" href="https://kravet.github.io/"' in html, (
        "Published portfolio needs its canonical URL"
    )
    assert any(link.endswith(".pdf") and "download" in html for link in parser.links), (
        "The page needs a local downloadable CV"
    )

    for resource in parser.local_resources:
        if re.match(r"^(?:[a-z]+:|//|#)", resource, re.I):
            continue
        resource_path = (ROOT / resource.split("?", 1)[0]).resolve()
        assert resource_path.is_relative_to(ROOT), f"Resource escapes the site: {resource}"
        assert resource_path.is_file(), f"Missing local resource: {resource}"

    for link in parser.links:
        if link.startswith("#"):
            assert link[1:] in parser.ids, f"Broken section link: {link}"

    robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
    assert "Allow: /" in robots and "Disallow: /" not in robots, (
        "Published robots.txt must allow crawling"
    )
    assert_battery_alarm_gallery_fits()
    print(
        f"Portfolio contract passed: {len(REQUIRED_SECTIONS)} sections, "
        f"{len(parser.product_icons)} linked square Play icons, local assets resolved."
    )


def assert_battery_alarm_gallery_fits():
    css = (ROOT / "css/styles.css").read_text(encoding="utf-8")

    def declarations(selector):
        match = re.search(rf"(?m)^\s*{re.escape(selector)}\s*\{{([^}}]*)\}}", css)
        assert match, f"Missing CSS rule for {selector}"
        return dict(
            (key.strip(), value.strip())
            for declaration in match.group(1).split(";")
            if ":" in declaration
            for key, value in [declaration.split(":", 1)]
        )

    gallery = declarations(".project-gallery")
    frame = declarations(".device-shot")
    screen = declarations(".device-shot img")
    project_main = declarations(".project-main")
    assert project_main.get("justify-content") == "flex-start", (
        "Battery Alarm content is vertically centered beside the tall phone gallery"
    )
    section = declarations(".section")
    section_padding = float(re.search(r"([\d.]+)px", section["padding-block"]).group(1))
    assert section_padding <= 80, (
        f"Portfolio section padding is {section_padding:g}px per side; "
        "the long page needs tighter section spacing"
    )
    min_height = float(re.search(r"([\d.]+)px", gallery["min-height"]).group(1))
    assert min_height <= 340, (
        f"Battery Alarm gallery minimum height is {min_height:g}px; "
        "the featured card should not be stretched by its screenshots"
    )
    max_frame_width = float(re.findall(r"([\d.]+)px", frame["width"])[-1])
    assert max_frame_width <= 128, (
        f"Battery Alarm phone width reaches {max_frame_width:g}px; "
        "the mockups are larger than needed"
    )
    frame_aspect_ratio = float(frame["aspect-ratio"])
    assert abs(frame_aspect_ratio - 0.48) < 0.001, (
        f"Battery Alarm phone frame ratio is {frame_aspect_ratio:g}; "
        "the mockups should keep a normal handset proportion"
    )
    assert screen.get("position") == "absolute" and screen.get("inset") == "7px", (
        "Battery Alarm screenshots must stay inside the phone frame"
    )
    gallery_padding = [float(value) for value in re.findall(r"([\d.]+)px", gallery["padding"])]
    top_padding, bottom_padding = gallery_padding[0], gallery_padding[2]
    frame_width = max_frame_width
    frame_padding = float(re.search(r"([\d.]+)px", frame["padding"]).group(1))
    frame_border = float(re.search(r"([\d.]+)px", frame["border"])
                         .group(1))
    frame_height = frame_width / frame_aspect_ratio
    screen_height = frame_height - 2 * (frame_padding + frame_border)
    assert screen_height <= 252, (
        f"Battery Alarm screenshot height is {screen_height:g}px; "
        "phone screens should stay at a normal handset height"
    )
    gallery_content_height = min_height - top_padding - bottom_padding

    for selector in (".device-main", ".device-alert"):
        transform = declarations(selector)["transform"]
        translate_y = abs(float(re.search(r"translateY\(([-\d.]+)px\)", transform).group(1)))
        rotation = abs(float(re.search(r"rotate\(([-\d.]+)deg\)", transform).group(1)))
        angle = math.radians(rotation)
        rotated_height = frame_height * math.cos(angle) + frame_width * math.sin(angle)
        required_height = rotated_height + 2 * translate_y
        assert required_height <= gallery_content_height, (
            f"{selector} needs {required_height:.1f}px but the gallery shows only "
            f"{gallery_content_height:.1f}px; the phone mockup is clipped"
        )


if __name__ == "__main__":
    main()
