from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Explanation:
    title: str
    description: str
    fix: str


EXPLANATIONS = {
    "syntax_error": Explanation(
        title="Syntax problem",
        description="Python could not understand the line. This usually means a colon, bracket, or indentation mark is missing.",
        fix="Check the line before the error and make sure the structure is complete.",
    ),
    "assignment_in_condition": Explanation(
        title="Assignment used in a condition",
        description="A condition should compare values with ==, not assign with =.",
        fix="Replace = with == inside if or while checks.",
    ),
    "undefined_name": Explanation(
        title="Name used before it was created",
        description="Python tried to read a variable that has not been assigned yet.",
        fix="Create the variable first or spell it the same way everywhere.",
    ),
    "possible_infinite_loop": Explanation(
        title="Possible endless loop",
        description="A while loop can repeat forever if its condition never changes.",
        fix="Make sure something inside the loop updates the value that controls the condition.",
    ),
    "no_issues": Explanation(
        title="No issues found",
        description="The code looks structurally sound based on the beginner checks in this app.",
        fix="Try running it to see the output and watch the variables update.",
    ),
}


def get_explanation(code: str) -> Explanation:
    return EXPLANATIONS.get(code, EXPLANATIONS["no_issues"])