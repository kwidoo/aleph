import sys
import traceback
import importlib

try:
    Continue = importlib.import_module("continue.api").Continue
except ModuleNotFoundError:
    class Continue:
        async def complete(self, *args, **kwargs):
            raise RuntimeError("Continue package is not installed")
from knowledge_manager import knowledge_hub

class DebugAgent:
    def __init__(self):
        self.c = Continue()
        self.error_patterns = self._load_error_patterns()

    async def diagnose_error(self, error_traceback):
        error_type = self._identify_error_type(error_traceback)
        context = knowledge_hub.query(error_type, n_results=3)

        prompt = f"""
        Debug this error:
        {error_traceback}

        Context from codebase:
        {context['documents']}

        Provide:
        1. Explanation of the error
        2. Step-by-step solution
        3. Fixed code snippet
        """
        return await self.c.complete(prompt)

    def _identify_error_type(self, traceback_str):
        for pattern, error_type in self.error_patterns.items():
            if pattern in traceback_str:
                return error_type
        return "unknown_error"

    def _load_error_patterns(self):
        return {
            "Cannot read properties of undefined": "null_pointer",
            "is not a function": "type_error",
            "Unexpected token": "syntax_error",
            "Failed to resolve component": "vue_component_error",
            "404 (Not Found)": "api_error"
        }

    def watch_console(self):
        original_error = console.error

        def error_wrapper(*args, **kwargs):
            error_traceback = traceback.format_exc()
            self.diagnose_error(error_traceback)
            original_error(*args, **kwargs)

        console.error = error_wrapper

DebugAgent().watch_console()
