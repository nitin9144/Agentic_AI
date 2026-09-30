import importlib.util
import sys
import unittest
from pathlib import Path

import streamlit as st

module_dir = Path(__file__).resolve().parent / 'chatbot'
sys.path.insert(0, str(module_dir))

module_path = module_dir / 'chatbot_frontend.py'
spec = importlib.util.spec_from_file_location('chatbot_frontend_under_test', module_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ChatbotFrontendTests(unittest.TestCase):
    def test_add_thread_is_unique(self):
        st.session_state.clear()
        st.session_state['chat_threads'] = []
        thread_id = 'thread-123'

        module.add_thread(thread_id)
        module.add_thread(thread_id)

        self.assertEqual(st.session_state['chat_threads'], [thread_id])


if __name__ == '__main__':
    unittest.main()
