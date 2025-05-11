import unittest
from registry import Registry


class TesRegistry(unittest.TestCase):
    def setUp(self):
        # Reset the registry before each test
        Registry._registry = {}

    def test_register_and_retrieve_lang(self):
        class DummyLang:
            pass

        Registry.register(["foo", "bar"])(DummyLang)

        # Check if the correct class is returned for .foo and .bar
        self.assertEqual(Registry.get_lang_for("file.foo"), DummyLang)
        self.assertEqual(Registry.get_lang_for("file.bar"), DummyLang)

        # Check unregistered extension
        self.assertIsNone(Registry.get_lang_for("file.baz"))

    def test_multiple_langs(self):
        class LangA:
            pass

        class LangB:
            pass

        Registry.register(["a"])(LangA)
        Registry.register(["b"])(LangB)

        self.assertEqual(Registry.get_lang_for("test.a"), LangA)
        self.assertEqual(Registry.get_lang_for("test.b"), LangB)

    def test_extension_priority(self):
        class LangC:
            pass

        Registry.register(["c"])(LangC)
        result = Registry.get_lang_for("something.c")
        self.assertEqual(result, LangC)

    def test_case_sensitivity(self):
        class LangX:
            pass

        Registry.register(["x"])(LangX)
        self.assertEqual(Registry.get_lang_for("file.x"), LangX)
        self.assertIsNone(Registry.get_lang_for("file.X"))  # Case sensitive


if __name__ == "__main__":
    unittest.main()
