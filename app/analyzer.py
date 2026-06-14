from __future__ import annotations

import ast
import builtins
import re
from dataclasses import dataclass
from typing import Iterable


BUILTIN_NAMES = set(dir(builtins))
CONDITION_PATTERN = re.compile(r"^\s*(if|elif|while)\b.*[^=!<>]=[^=].*$")


@dataclass(frozen=True)
class Issue:
    line: int
    severity: str
    title: str
    message: str
    fix: str
    kind: str


class CodeAnalyzer:
    def analyze(self, source: str) -> list[Issue]:
        issues: list[Issue] = []
        lines = source.splitlines()

        issues.extend(self._detect_syntax(source))
        issues.extend(self._detect_assignment_in_condition(lines))

        try:
            tree = ast.parse(source)
        except SyntaxError:
            return sorted(issues, key=lambda issue: issue.line)

        assigned = self._collect_assigned_names(tree)
        issues.extend(self._detect_undefined_names(tree, assigned))
        issues.extend(self._detect_while_loops(tree))

        return sorted(issues, key=lambda issue: (issue.line, issue.title))

    def _detect_syntax(self, source: str) -> list[Issue]:
        try:
            ast.parse(source)
            return []
        except SyntaxError as error:
            line = error.lineno or 1
            text = (error.text or "").strip()
            message = error.msg
            if text.startswith(("if ", "elif ", "while ")) and ":" not in text:
                message = "This line needs a colon at the end."
            elif "invalid syntax" in error.msg.lower() and "=" in text:
                message = "This line may be using = where a comparison was intended."

            return [
                Issue(
                    line=line,
                    severity="high",
                    title="Syntax error",
                    message=message,
                    fix="Check the line and the one right before it for missing punctuation or indentation.",
                    kind="syntax_error",
                )
            ]

    def _detect_assignment_in_condition(self, lines: Iterable[str]) -> list[Issue]:
        issues: list[Issue] = []
        for index, line in enumerate(lines, start=1):
            if CONDITION_PATTERN.match(line):
                issues.append(
                    Issue(
                        line=index,
                        severity="high",
                        title="Assignment in condition",
                        message="Conditions should compare values, not assign them.",
                        fix="Use == for comparison inside if and while statements.",
                        kind="assignment_in_condition",
                    )
                )
        return issues

    def _collect_assigned_names(self, tree: ast.AST) -> set[str]:
        names: set[str] = set()

        class Collector(ast.NodeVisitor):
            def visit_Name(self, node: ast.Name) -> None:  # type: ignore[override]
                if isinstance(node.ctx, ast.Store):
                    names.add(node.id)

            def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # type: ignore[override]
                names.add(node.name)
                for arg in node.args.args + node.args.kwonlyargs:
                    names.add(arg.arg)
                if node.args.vararg:
                    names.add(node.args.vararg.arg)
                if node.args.kwarg:
                    names.add(node.args.kwarg.arg)
                self.generic_visit(node)

            def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:  # type: ignore[override]
                self.visit_FunctionDef(node)  # type: ignore[arg-type]

            def visit_ClassDef(self, node: ast.ClassDef) -> None:  # type: ignore[override]
                names.add(node.name)
                self.generic_visit(node)

            def visit_Import(self, node: ast.Import) -> None:  # type: ignore[override]
                for alias in node.names:
                    names.add(alias.asname or alias.name.split(".")[0])

            def visit_ImportFrom(self, node: ast.ImportFrom) -> None:  # type: ignore[override]
                for alias in node.names:
                    names.add(alias.asname or alias.name)

        Collector().visit(tree)
        return names

    def _detect_undefined_names(self, tree: ast.AST, assigned: set[str]) -> list[Issue]:
        issues: list[Issue] = []
        seen: set[tuple[int, str]] = set()

        class Checker(ast.NodeVisitor):
            def visit_Name(self, node: ast.Name) -> None:  # type: ignore[override]
                if isinstance(node.ctx, ast.Load):
                    name = node.id
                    if name not in assigned and name not in BUILTIN_NAMES:
                        key = (node.lineno, name)
                        if key not in seen:
                            seen.add(key)
                            issues.append(
                                Issue(
                                    line=node.lineno,
                                    severity="medium",
                                    title=f"'{name}' may be undefined",
                                    message=f"The name '{name}' is read before it is created.",
                                    fix=f"Create '{name}' before this line or check the spelling.",
                                    kind="undefined_name",
                                )
                            )

        Checker().visit(tree)
        return issues

    def _detect_while_loops(self, tree: ast.AST) -> list[Issue]:
        issues: list[Issue] = []

        for node in ast.walk(tree):
            if not isinstance(node, ast.While):
                continue

            if isinstance(node.test, ast.Constant) and node.test.value is True:
                issues.append(
                    Issue(
                        line=node.lineno,
                        severity="high",
                        title="Possible endless loop",
                        message="while True will repeat forever unless a break happens.",
                        fix="Add a break condition or change the loop so the condition can become False.",
                        kind="possible_infinite_loop",
                    )
                )
                continue

            if isinstance(node.test, ast.Compare) and isinstance(node.test.left, ast.Name):
                tracked = node.test.left.id
                if not self._body_updates_name(node.body, tracked):
                    issues.append(
                        Issue(
                            line=node.lineno,
                            severity="medium",
                            title=f"'{tracked}' may never change",
                            message=f"The loop depends on '{tracked}', but the body does not update it.",
                            fix=f"Update '{tracked}' inside the loop or stop the loop another way.",
                            kind="possible_infinite_loop",
                        )
                    )

        return issues

    def _body_updates_name(self, body: list[ast.stmt], name: str) -> bool:
        module = ast.Module(body=body, type_ignores=[])
        for statement in ast.walk(module):
            if isinstance(statement, ast.Name) and isinstance(statement.ctx, ast.Store) and statement.id == name:
                return True
            if isinstance(statement, ast.AugAssign) and isinstance(statement.target, ast.Name) and statement.target.id == name:
                return True
        return False