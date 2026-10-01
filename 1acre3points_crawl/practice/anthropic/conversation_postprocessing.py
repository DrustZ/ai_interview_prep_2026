"""LeetCode-style conversation post-processing solution."""

import re
from typing import List, Tuple


class Solution:
    MARKER = re.compile(r"<<.*?>>")
    SPACES = re.compile(r"[ \t]+")
    MESSAGE = re.compile(r"^(user|assistant|system):\s*(.*)$", re.IGNORECASE)

    def parseConversation(self, text: str) -> List[Tuple[str, str]]:
        messages = []

        for line in text.splitlines():
            line = self.MARKER.sub("", line)
            line = self.SPACES.sub(" ", line).strip()

            if not line:
                continue

            match = self.MESSAGE.match(line)
            if match:
                role = match.group(1).lower()
                content = match.group(2)
                messages.append((role, content))

        return messages
