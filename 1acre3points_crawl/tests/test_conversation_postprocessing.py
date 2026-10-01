import unittest

from practice.anthropic.conversation_postprocessing import Solution


class ConversationPostprocessingTests(unittest.TestCase):
    def setUp(self):
        self.solution = Solution()

    def test_example(self):
        text = """System:  You are helpful.  <<internal>>

USER:\tHi   there
assistant:  Hello!<<meta>>  How can I help?"""

        self.assertEqual(
            self.solution.parseConversation(text),
            [
                ("system", "You are helpful."),
                ("user", "Hi there"),
                ("assistant", "Hello! How can I help?"),
            ],
        )

    def test_multiple_markers_and_invalid_roles(self):
        text = """user: A<<one>>   B<<two>>C
developer: ignored
random text
ASSISTANT: ok"""

        self.assertEqual(
            self.solution.parseConversation(text),
            [("user", "A BC"), ("assistant", "ok")],
        )

    def test_empty_lines_and_empty_content(self):
        text = " \t\n<<hidden>>\nSystem:\t\n"
        self.assertEqual(self.solution.parseConversation(text), [("system", "")])


if __name__ == "__main__":
    unittest.main()
