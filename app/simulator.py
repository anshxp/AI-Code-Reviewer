from __future__ import annotations

import contextlib
import io
import sys
from dataclasses import dataclass, field


SAFE_BUILTINS = {
    "abs": abs,
    "bool": bool,
    "enumerate": enumerate,
    "float": float,
    "int": int,
    "len": len,
    "list": list,
    "max": max,
    "min": min,
    "print": print,
    "range": range,
    "str": str,
    "sum": sum,
}


@dataclass
class ExecutionResult:
    output: str = ""
    error: str = ""
    steps: list[str] = field(default_factory=list)
    variables: dict[str, str] = field(default_factory=dict)


class CodeSimulator:
    def run(self, source: str, max_steps: int = 300) -> ExecutionResult:
        result = ExecutionResult()
        buffer = io.StringIO()
        step_count = 0
        filename = "<user_code>"
        globals_dict = {"__builtins__": SAFE_BUILTINS}

        def tracer(frame, event, arg):
            nonlocal step_count
            if frame.f_code.co_filename != filename:
                return tracer
            if event == "line":
                step_count += 1
                snapshot = self._format_locals(frame.f_locals)
                result.steps.append(f"Line {frame.f_lineno}: {snapshot}")
                result.variables = snapshot
                if step_count >= max_steps:
                    raise RuntimeError("Execution stopped after too many steps.")
            return tracer

        try:
            code = compile(source, filename, "exec")
            with contextlib.redirect_stdout(buffer):
                previous_tracer = sys.gettrace()
                sys.settrace(tracer)
                try:
                    exec(code, globals_dict, globals_dict)
                finally:
                    sys.settrace(previous_tracer)
        except Exception as error:
            result.error = f"{type(error).__name__}: {error}"
        finally:
            result.output = buffer.getvalue().strip()

        return result

    def _format_locals(self, values: dict[str, object]) -> dict[str, str]:
        formatted: dict[str, str] = {}
        for key, value in values.items():
            if key == "__builtins__":
                continue
            try:
                formatted[key] = repr(value)
            except Exception:
                formatted[key] = "<unrepresentable>"
        return formatted