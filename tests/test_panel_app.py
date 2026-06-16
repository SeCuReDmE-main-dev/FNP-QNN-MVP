import unittest


class PanelAppTests(unittest.TestCase):
    def test_panel_app_builds_without_serving(self):
        import panel_app

        app = panel_app.create_app()
        self.assertEqual(app.title, "FNP-QNN HoloViz Panel")
        self.assertGreaterEqual(len(app.main), 2)
        self.assertGreaterEqual(len(app.sidebar), 2)


if __name__ == "__main__":
    unittest.main()
