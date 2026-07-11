import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


REPO_ROOT = Path(__file__).resolve().parents[1]
LANDING_ROOT = REPO_ROOT / "web" / "landing"


class _LandingParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.ids = set()
        self.hrefs = []
        self.meta = []
        self.text = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        self.tags.append((tag, attributes))
        if attributes.get("id"):
            self.ids.add(attributes["id"])
        if tag == "meta":
            self.meta.append(attributes)
        if tag in {"a", "link"} and attributes.get("href"):
            self.hrefs.append(attributes["href"])

    def handle_data(self, data):
        self.text.append(data)


class PublicLandingContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = LANDING_ROOT / "index.html"
        cls.source = cls.index.read_text(encoding="utf-8")
        cls.parser = _LandingParser()
        cls.parser.feed(cls.source)

    def test_required_public_files_exist(self):
        for filename in ("index.html", "fnp-qnn-landing.css", "favicon.svg", "robots.txt"):
            with self.subTest(filename=filename):
                self.assertTrue((LANDING_ROOT / filename).is_file())

    def test_document_has_accessible_navigation_contract(self):
        html = next(attributes for tag, attributes in self.parser.tags if tag == "html")
        self.assertEqual(html.get("lang"), "en")
        self.assertIn('href="#main-content"', self.source)
        self.assertIn("main-content", self.parser.ids)
        self.assertIn('href="#education"', self.source)
        self.assertIn("education", self.parser.ids)
        education = next(
            attributes for tag, attributes in self.parser.tags if tag == "section" and attributes.get("id") == "education"
        )
        self.assertEqual(education.get("aria-labelledby"), "education-title")
        self.assertIn("education-title", self.parser.ids)

    def test_metadata_and_local_assets_are_complete(self):
        self.assertIn("<title>FNP-QNN", self.source)
        meta_names = {item.get("name"): item.get("content", "") for item in self.parser.meta}
        self.assertIn("description", meta_names)
        self.assertTrue(meta_names["description"].strip())
        self.assertIn("viewport", meta_names)
        for href in self.parser.hrefs:
            parsed = urlparse(href)
            if parsed.scheme or parsed.netloc or href.startswith("#"):
                continue
            self.assertTrue((LANDING_ROOT / parsed.path).is_file(), href)

    def test_public_boundary_and_secret_hygiene_are_present(self):
        text = " ".join(self.parser.text).lower()
        for phrase in ("alpha-local", "non-clinical", "local simulation evidence only", "human review"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)
        for forbidden in ("c:\\users\\", "begin private key", "api_key=", "secret_key="):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, self.source.lower())


if __name__ == "__main__":
    unittest.main()
