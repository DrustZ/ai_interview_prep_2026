"""LeetCode-style solution for prompt-template normalization and counting."""

import re
from typing import Dict, List


class Solution:
    WHITESPACE = re.compile(r"\s+")
    PLACEHOLDER = re.compile(r"\{[A-Za-z0-9_]+\}")

    def countTemplates(self, templates: List[str]) -> Dict[str, int]:
        count_by_key: Dict[str, int] = {}

        for template in templates:
            key = self.normalize(template)
            count_by_key[key] = count_by_key.get(key, 0) + 1

        return count_by_key

    def normalize(self, template: str) -> str:
        # Collapse whitespace first, then normalize valid placeholders.
        template = self.WHITESPACE.sub(" ", template).strip()
        return self.PLACEHOLDER.sub("{}", template)
