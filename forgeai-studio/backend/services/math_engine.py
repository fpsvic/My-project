import re
import math


def _thinking_wrap(thinking: str, heading: str, body: str, mode: str) -> str:
    if mode == "forge_thinking":
        return (
            f"### <i class=\"fa-solid fa-infinity text-violet-500 mr-2\"></i> Thinking Process\n"
            f"{thinking}\n\n---\n\n### {heading}\n{body}"
        )
    if mode == "forge_instant":
        first_para = body.split("\n\n")[0]
        return f"### {heading}\n\n{first_para}"
    return f"### {heading}\n{body}"


def _parse_polynomial_terms(expr: str) -> list[tuple[int, int]]:
    """Return list of (coefficient, power) for each term in a polynomial."""
    expr = expr.replace(" ", "").replace("–", "-")
    pattern = re.compile(r"([+-]?\d*)(x)(?:\^(\d+))?|([+-]?\d+)")
    terms: list[tuple[int, int]] = []
    for m in pattern.finditer(expr):
        if m.group(2):  # has x
            raw_coeff = m.group(1)
            if raw_coeff in ("", "+"):
                coeff = 1
            elif raw_coeff == "-":
                coeff = -1
            else:
                coeff = int(raw_coeff)
            power = int(m.group(3)) if m.group(3) else 1
            terms.append((coeff, power))
        elif m.group(4):  # constant
            terms.append((int(m.group(4)), 0))
    return terms


def _derivative_response(expr: str, mode: str) -> str:
    heading = "Symbolic Derivative Calculus Solver"
    thinking = (
        "- **Intent:** Symbolic Differentiation.\n"
        "- **Method:** Polynomial Power Rule mapping."
    )

    terms = _parse_polynomial_terms(expr)
    if not terms:
        body = (
            f"Could not symbolically differentiate the expression **\"{expr}\"** offline. "
            "Please input a valid algebraic polynomial such as `3x^3 + 5x^2 - 4x`."
        )
        return _thinking_wrap(thinking, heading, body, mode)

    d_terms: list[str] = []
    steps: list[str] = []

    for coeff, power in terms:
        if power == 0:
            steps.append(f"$\\frac{{d}}{{dx}}[{coeff}] = 0$ (constant derivative is zero)")
        elif power == 1:
            d_terms.append(f"{'+' if coeff >= 0 else ''}{coeff}")
            steps.append(f"$\\frac{{d}}{{dx}}[{coeff}x] = {coeff}$")
        else:
            new_coeff = coeff * power
            new_power = power - 1
            power_str = "x" if new_power == 1 else f"x^{{{new_power}}}"
            d_terms.append(f"{'+' if new_coeff >= 0 else ''}{new_coeff}{power_str}")
            steps.append(
                f"$\\frac{{d}}{{dx}}[{coeff}x^{{{power}}}] = "
                f"({coeff} \\cdot {power})x^{{{power}-1}} = {new_coeff}{power_str}$"
            )

    result = " ".join(d_terms).lstrip("+").strip() or "0"
    numbered = "\n".join(f"{i+1}. {s}" for i, s in enumerate(steps))

    body = (
        f"To find the derivative of **$f(x) = {expr}$** we apply the Power Rule:\n\n"
        "$$\\frac{d}{dx}[x^n] = n \\cdot x^{n-1}$$\n\n"
        f"**Step-by-step differentiation:**\n{numbered}\n\n"
        f"$$\\frac{{d}}{{dx}}[{expr}] = {result}$$"
        f"\n\n[MATH_CARD: formula: d/dx [ {expr} ] | result: {result} | style: violet]"
    )
    return _thinking_wrap(thinking, heading, body, mode)


def _integral_response(expr: str, mode: str) -> str:
    heading = "Symbolic Integral Calculus Solver"
    thinking = (
        "- **Intent:** Symbolic Integration.\n"
        "- **Method:** Reverse Power Rule."
    )

    terms = _parse_polynomial_terms(expr)
    if not terms:
        body = (
            f"Could not symbolically integrate the expression **\"{expr}\"** offline. "
            "Please input a valid algebraic expression such as `3x^2 + 2x`."
        )
        return _thinking_wrap(thinking, heading, body, mode)

    i_terms: list[str] = []
    steps: list[str] = []

    for coeff, power in terms:
        new_power = power + 1
        raw_val = coeff / new_power
        if raw_val == int(raw_val):
            val_str = str(int(raw_val))
        else:
            val_str = f"\\frac{{{coeff}}}{{{new_power}}}"
        sign = "+" if coeff / new_power >= 0 else ""
        power_str = "x" if new_power == 1 else f"x^{{{new_power}}}"
        i_terms.append(f"{sign}{val_str}{power_str}")
        steps.append(
            f"$\\int [{coeff}x^{{{power}}}]\\,dx = "
            f"\\frac{{{coeff}}}{{{power}+1}}x^{{{power}+1}} = {val_str}{power_str}$"
        )

    result = " ".join(i_terms).lstrip("+").strip() + " + C"
    numbered = "\n".join(f"{i+1}. {s}" for i, s in enumerate(steps))

    body = (
        f"To evaluate $\\int ({expr})\\,dx$ we apply the Reverse Power Rule:\n\n"
        "$$\\int x^n\\,dx = \\frac{x^{n+1}}{n+1} + C$$\n\n"
        f"**Step-by-step integration:**\n{numbered}\n\n"
        f"$$\\int ({expr})\\,dx = {result}$$"
        f"\n\n[MATH_CARD: formula: \\int [ {expr} ] dx | result: {result} | style: violet]"
    )
    return _thinking_wrap(thinking, heading, body, mode)


def _trig_response(query: str, mode: str) -> str:
    heading = "Trigonometric Ratio Evaluator"
    thinking = (
        "- **Intent:** Trigonometry Evaluation.\n"
        "- **Input Metrics:** Parsed angular constraints."
    )

    m = re.search(
        r"(sin|cos|tan|csc|sec|cot)\s*\(?(\d+(?:\.\d+)?)\)?\s*(deg|rad|degree|radian|°)?",
        query,
        re.IGNORECASE,
    )
    if not m:
        body = (
            f"Could not resolve trig arguments from **\"{query}\"**. "
            "Try `sin(45 deg)` or `cos(1.047 rad)`."
        )
        return _thinking_wrap(thinking, heading, body, mode)

    ratio = m.group(1).lower()
    val = float(m.group(2))
    unit_raw = (m.group(3) or "deg").lower()
    unit = "deg" if unit_raw.startswith("deg") or unit_raw == "°" else "rad"

    rad_val = math.radians(val) if unit == "deg" else val

    trig_fns = {
        "sin": math.sin, "cos": math.cos, "tan": math.tan,
        "csc": lambda r: 1 / math.sin(r),
        "sec": lambda r: 1 / math.cos(r),
        "cot": lambda r: 1 / math.tan(r),
    }
    computed = round(trig_fns[ratio](rad_val), 5)

    unit_label = "degrees" if unit == "deg" else "radians"
    deg_sym = "°" if unit == "deg" else "\\text{ rad}"
    body = (
        "Evaluating **$\\" + ratio + "(" + str(val) + "\\text{ " + unit_label + "})$**:\n\n"
        "1. **Input Angle**: $" + str(val) + deg_sym + "$\n"
        f"2. **Radian Conversion**: ${rad_val:.5f}\\text{{ rad}}$\n"
        "3. **Result**: $\\" + ratio + "(" + f"{rad_val:.5f}" + ") \\approx " + str(computed) + "$"
        f"\n\n[MATH_CARD: formula: {ratio}({val} {unit}) | result: {computed} | style: violet]"
    )
    return _thinking_wrap(thinking, heading, body, mode)


def _arithmetic_response(query: str, mode: str) -> str:
    heading = "Arithmetic Evaluator"
    thinking = (
        "- **Intent:** Arithmetic Reduction.\n"
        "- **Method:** Safe expression evaluation."
    )

    clean = (
        query.lower()
        .replace("plus", "+").replace("minus", "-")
        .replace("times", "*").replace("divided by", "/")
        .replace("÷", "/").replace("^", "**")
    )
    safe = re.sub(r"[^0-9+\-*/().\s*]", "", clean)

    try:
        result = eval(safe, {"__builtins__": {}})  # noqa: S307
        if not isinstance(result, (int, float)) or not math.isfinite(result):
            raise ValueError
        body = (
            f"Evaluating **${safe}$**:\n\n"
            f"1. **Expression**: ${safe}$\n"
            f"2. **Result**: ${result}$"
            f"\n\n[MATH_CARD: formula: {safe} | result: {result} | style: violet]"
        )
    except Exception:
        body = f"Could not safely evaluate **\"{query}\"**. Please enter a valid arithmetic expression."

    return _thinking_wrap(thinking, heading, body, mode)


def generate_math_response(query: str, mode: str) -> str:
    q = query.lower().strip()
    q = re.sub(r"^(what is|whats|what's|calculate|solve|evaluate|compute|find|value of)\s+", "", q)
    q = q.rstrip("?")

    if "derivative" in q or "d/dx" in q:
        expr = re.sub(r"derivative of|d/dx", "", q).strip()
        return _derivative_response(expr, mode)

    if any(w in q for w in ("integral", "integrate", "antiderivative")):
        expr = re.sub(r"integral of|integrate|antiderivative of", "", q).strip()
        return _integral_response(expr, mode)

    if re.search(r"(sin|cos|tan|csc|sec|cot)\s*\(?\d", q, re.IGNORECASE):
        return _trig_response(q, mode)

    return _arithmetic_response(q, mode)
