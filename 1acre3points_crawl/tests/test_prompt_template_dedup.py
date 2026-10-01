import importlib.util
import unittest
from pathlib import Path


PATH = (
    Path(__file__).resolve().parents[1]
    / "practice"
    / "anthropic"
    / "prompt_template_dedup.py"
)
SPEC = importlib.util.spec_from_file_location("prompt_template_dedup", PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)
Solution = MODULE.Solution


class PromptTemplateDedupTests(unittest.TestCase):
    def setUp(self):
        self.solution = Solution()

    def test_example(self):
        templates = [
            "Summarize  {doc_id}  in  {lang}",
            "Summarize {x} in {y}",
            "Summarize\n{doc_id}\tin\t{lang}   ",
            "Translate {text} to {lang}",
        ]
        self.assertEqual(
            self.solution.countTemplates(templates),
            {
                "Summarize {} in {}": 3,
                "Translate {} to {}": 1,
            },
        )

    def test_only_valid_placeholders_are_replaced(self):
        self.assertEqual(
            self.solution.normalize("  {abc_123} {} {a-b} { x }  "),
            "{} {} {a-b} { x }",
        )

    def test_case_sensitive_and_adjacent_placeholders(self):
        self.assertEqual(
            self.solution.countTemplates(["A{x}{y}", "A{one}{two}", "a{x}{y}"]),
            {"A{}{}": 2, "a{}{}": 1},
        )

    def test_all_whitespace_becomes_empty_key(self):
        self.assertEqual(
            self.solution.countTemplates([" \t\n ", ""]),
            {"": 2},
        )


if __name__ == "__main__":
    unittest.main()
