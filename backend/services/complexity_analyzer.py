def analyze_code(code: str):
    time_complexity = "O(n)"
    space_complexity = "O(1)"
    pattern = "Unknown"
    suggestions = []

    loop_count = code.count("for") + code.count("while")

    if loop_count >= 2:
        time_complexity = "O(n²)"
        pattern = "Nested Loop"
        suggestions.append("Consider reducing nested iterations.")

    elif "sort(" in code or "sorted(" in code:
        time_complexity = "O(n log n)"
        pattern = "Sorting"
        suggestions.append("Sorting increases complexity to O(n log n).")

    elif "recursion" in code or "def " in code:
        pattern = "Recursion"
        suggestions.append("Consider memoization if overlapping subproblems exist.")

    if "set(" in code or "{}" in code:
        suggestions.append("Efficient hash-based lookup detected.")

    if not suggestions:
        suggestions.append("Code structure looks efficient.")

    return {
        "timeComplexity": time_complexity,
        "spaceComplexity": space_complexity,
        "pattern": pattern,
        "suggestions": suggestions,
    }