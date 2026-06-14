"""Generate visual prompts for NanoBanana image generation."""
from __future__ import annotations


def generate_prompt_for_issue(title: str, kind: str, message: str) -> str:
    """Generate a NanoBanana-compatible prompt for an error visualization."""
    
    prompts = {
        "syntax_error": (
            "A cartoon programmer looking confused at a Python code editor. "
            "The code has red squiggly lines under it. "
            "A thought bubble shows a question mark. "
            "Bright, educational, beginner-friendly style. "
            "Light background, clear typography."
        ),
        "assignment_in_condition": (
            "A visual diagram showing the difference between = (assignment) and == (comparison). "
            "Left side: = with an arrow pointing to a box (storing value). "
            "Right side: == with two boxes being compared. "
            "Bright colors, educational, clear labels. "
            "Simple, beginner-friendly illustration."
        ),
        "undefined_name": (
            "A Python variable name appearing with a ghostly 'does not exist' indicator. "
            "Show the name in red text with a 'not defined' label. "
            "Then show the correct definition happening first. "
            "Step-by-step visual flow. "
            "Bright, clear, educational style."
        ),
        "possible_infinite_loop": (
            "A circular arrow loop labeled 'while True' that never ends. "
            "Show the loop condition and variables that never change. "
            "Then show the corrected version with a break or changing condition. "
            "Before and after comparison. "
            "Bright, educational diagram style."
        ),
        "no_issues": (
            "A happy cartoon programmer with a checkmark. "
            "Python code running smoothly with green highlights. "
            "Variables displaying their values correctly. "
            "Celebratory, positive, encouraging style. "
            "Light background, clean design."
        ),
    }
    
    return prompts.get(kind, prompts["no_issues"])


def generate_comparison_prompt(broken_title: str, fixed_title: str) -> str:
    """Generate a prompt for comparing broken vs. fixed code."""
    return (
        f"A side-by-side comparison diagram. "
        f"Left side labeled 'WRONG: {broken_title}' with red X marks. "
        f"Right side labeled 'CORRECT: {fixed_title}' with green checkmarks. "
        f"Show both code snippets with annotations. "
        f"Clear visual difference, educational style, bright colors."
    )
