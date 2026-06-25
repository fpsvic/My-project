import re
import math
from fractions import Fraction


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


def _parse_polynomial_terms(expr: str) -> list:
    """Return list of (coefficient, power) for each term in a polynomial."""
    expr = expr.replace(" ", "").replace("–", "-")
    pattern = re.compile(r"([+-]?\d*)(x)(?:\^(\d+))?|([+-]?\d+)")
    terms = []
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

    d_terms = []
    steps = []

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

    i_terms = []
    steps = []

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


# ---------------------------------------------------------------------------
# Algebra
# ---------------------------------------------------------------------------

def _quadratic_response(query: str, mode: str) -> str:
    heading = "Quadratic Equation Solver"
    thinking = (
        "- **Intent:** Solve quadratic ax² + bx + c = 0.\n"
        "- **Method:** Quadratic Formula."
    )

    # Try to extract coefficients from "ax^2 + bx + c" or "a=..., b=..., c=..."
    abc_m = re.search(
        r"a\s*=\s*(-?\d+(?:\.\d+)?)[,\s]+b\s*=\s*(-?\d+(?:\.\d+)?)[,\s]+c\s*=\s*(-?\d+(?:\.\d+)?)",
        query, re.IGNORECASE,
    )
    poly_m = re.search(
        r"(-?\d*(?:\.\d+)?)\s*x\^?2\s*([+-]\s*\d*(?:\.\d+)?)\s*x\s*([+-]\s*\d+(?:\.\d+)?)",
        query, re.IGNORECASE,
    )

    if abc_m:
        a, b, c = float(abc_m.group(1)), float(abc_m.group(2)), float(abc_m.group(3))
    elif poly_m:
        a_s = poly_m.group(1).replace(" ", "") or "1"
        b_s = poly_m.group(2).replace(" ", "") or "0"
        c_s = poly_m.group(3).replace(" ", "") or "0"
        a, b, c = float(a_s if a_s not in ("", "+", "-") else (a_s + "1")), float(b_s), float(c_s)
    else:
        body = (
            "Could not extract coefficients. "
            "Please use the form `2x^2 + 3x - 5 = 0` or `a=2, b=3, c=-5`."
        )
        return _thinking_wrap(thinking, heading, body, mode)

    discriminant = b ** 2 - 4 * a * c
    disc_str = f"{discriminant:.4g}"

    if discriminant > 0:
        x1 = (-b + math.sqrt(discriminant)) / (2 * a)
        x2 = (-b - math.sqrt(discriminant)) / (2 * a)
        roots_str = f"$x_1 = {x1:.4g}$, $x_2 = {x2:.4g}$"
        nature = "two distinct real roots"
        result_label = f"x₁={x1:.4g}, x₂={x2:.4g}"
    elif discriminant == 0:
        x1 = -b / (2 * a)
        roots_str = f"$x = {x1:.4g}$ (repeated root)"
        nature = "one repeated real root"
        result_label = f"x={x1:.4g}"
    else:
        real_part = -b / (2 * a)
        imag_part = math.sqrt(-discriminant) / (2 * a)
        roots_str = (
            f"$x_1 = {real_part:.4g} + {imag_part:.4g}i$, "
            f"$x_2 = {real_part:.4g} - {imag_part:.4g}i$"
        )
        nature = "two complex conjugate roots"
        result_label = f"x={real_part:.4g}±{imag_part:.4g}i"

    body = (
        f"Solving **${a}x^2 + {b}x + {c} = 0$** using the Quadratic Formula:\n\n"
        "$$x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$$\n\n"
        f"**Steps:**\n"
        f"1. **Identify coefficients**: $a = {a}$, $b = {b}$, $c = {c}$\n"
        f"2. **Discriminant**: $\\Delta = b^2 - 4ac = ({b})^2 - 4({a})({c}) = {disc_str}$\n"
        f"3. **Nature of roots**: {nature}\n"
        f"4. **Roots**: {roots_str}\n\n"
        f"$$\\boxed{{{result_label}}}$$"
        f"\n\n[MATH_CARD: formula: {a}x²+{b}x+{c}=0 | result: {result_label} | style: violet]"
    )
    return _thinking_wrap(thinking, heading, body, mode)


def _linear_equation_response(query: str, mode: str) -> str:
    heading = "Linear Equation Solver"
    thinking = (
        "- **Intent:** Solve linear equation ax + b = c.\n"
        "- **Method:** Algebraic isolation."
    )

    # Match patterns like "2x + 3 = 7" or "x - 5 = 10"
    m = re.search(
        r"(-?\d*(?:\.\d+)?)\s*x\s*([+-]\s*\d+(?:\.\d+)?)?\s*=\s*(-?\d+(?:\.\d+)?)",
        query, re.IGNORECASE,
    )
    if not m:
        body = "Could not parse the linear equation. Try `2x + 3 = 7` or `5x - 10 = 0`."
        return _thinking_wrap(thinking, heading, body, mode)

    a_s = m.group(1).replace(" ", "") or "1"
    if a_s in ("", "+"):
        a = 1.0
    elif a_s == "-":
        a = -1.0
    else:
        a = float(a_s)

    b_s = (m.group(2) or "0").replace(" ", "")
    b = float(b_s) if b_s else 0.0
    rhs = float(m.group(3))

    if a == 0:
        body = "Coefficient of x is 0 — this is not a linear equation in x."
        return _thinking_wrap(thinking, heading, body, mode)

    x = (rhs - b) / a
    body = (
        f"Solving **${a}x {'+' if b >= 0 else ''}{b} = {rhs}$**:\n\n"
        f"1. Subtract {b} from both sides: ${a}x = {rhs} - ({b}) = {rhs - b}$\n"
        f"2. Divide both sides by {a}: $x = \\frac{{{rhs - b}}}{{{a}}} = {x:.4g}$\n\n"
        f"$$\\boxed{{x = {x:.4g}}}$$"
        f"\n\n[MATH_CARD: formula: {a}x+{b}={rhs} | result: x={x:.4g} | style: violet]"
    )
    return _thinking_wrap(thinking, heading, body, mode)


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------

def _parse_number_list(query: str) -> list:
    """Extract a list of numbers from a query string."""
    return [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", query)]


def _statistics_response(query: str, mode: str) -> str:
    heading = "Statistics Calculator"
    thinking = (
        "- **Intent:** Descriptive Statistics.\n"
        "- **Method:** Direct computation on dataset."
    )

    numbers = _parse_number_list(query)
    if len(numbers) < 2:
        body = "Please provide a dataset, e.g. `mean of 4, 8, 6, 5, 3, 2, 8, 9, 2, 5`."
        return _thinking_wrap(thinking, heading, body, mode)

    n = len(numbers)
    mean = sum(numbers) / n
    sorted_nums = sorted(numbers)
    mid = n // 2
    median = sorted_nums[mid] if n % 2 else (sorted_nums[mid - 1] + sorted_nums[mid]) / 2

    from collections import Counter
    counts = Counter(numbers)
    max_count = max(counts.values())
    modes = [k for k, v in counts.items() if v == max_count]
    mode_str = ", ".join(str(m) for m in sorted(modes))

    variance = sum((x - mean) ** 2 for x in numbers) / n
    std_dev = math.sqrt(variance)

    q = query.lower()
    if "std" in q or "standard deviation" in q:
        result_label = f"std={std_dev:.4g}"
    elif "variance" in q:
        result_label = f"var={variance:.4g}"
    elif "median" in q:
        result_label = f"median={median:.4g}"
    elif "mode" in q:
        result_label = f"mode={mode_str}"
    else:
        result_label = f"mean={mean:.4g}"

    nums_str = ", ".join(str(x) for x in numbers)
    body = (
        f"**Dataset**: ${{{nums_str}}}$  (n = {n})\n\n"
        f"| Statistic | Value |\n"
        f"|-----------|-------|\n"
        f"| Mean (μ) | ${mean:.4g}$ |\n"
        f"| Median | ${median:.4g}$ |\n"
        f"| Mode | ${mode_str}$ |\n"
        f"| Variance (σ²) | ${variance:.4g}$ |\n"
        f"| Std Deviation (σ) | ${std_dev:.4g}$ |\n\n"
        f"$$\\mu = \\frac{{\\sum x_i}}{{n}} = \\frac{{{sum(numbers)}}}{{{n}}} = {mean:.4g}$$"
        f"\n\n[MATH_CARD: formula: stats({nums_str}) | result: {result_label} | style: violet]"
    )
    return _thinking_wrap(thinking, heading, body, mode)


def _combinations_response(query: str, mode: str) -> str:
    heading = "Combinations & Permutations"
    thinking = (
        "- **Intent:** Count arrangements.\n"
        "- **Method:** nCr / nPr formula."
    )

    m = re.search(r"(\d+)\s*[Cc]r?\s*(\d+)|[Cc](\d+)\s*,\s*(\d+)", query)
    pm = re.search(r"(\d+)\s*[Pp]r?\s*(\d+)|[Pp](\d+)\s*,\s*(\d+)", query)

    if pm:
        n = int(pm.group(1) or pm.group(3))
        r = int(pm.group(2) or pm.group(4))
        perm = math.perm(n, r)
        body = (
            f"**Permutations** $P({n}, {r})$:\n\n"
            "$$P(n,r) = \\frac{n!}{(n-r)!}$$\n\n"
            f"$$P({n},{r}) = \\frac{{{n}!}}{{{n-r}!}} = {perm}$$"
            f"\n\n[MATH_CARD: formula: P({n},{r}) | result: {perm} | style: violet]"
        )
    elif m:
        n = int(m.group(1) or m.group(3))
        r = int(m.group(2) or m.group(4))
        comb = math.comb(n, r)
        body = (
            f"**Combinations** $C({n}, {r})$:\n\n"
            "$$C(n,r) = \\binom{n}{r} = \\frac{n!}{r!(n-r)!}$$\n\n"
            f"$$C({n},{r}) = \\frac{{{n}!}}{{{r}! \\cdot {n-r}!}} = {comb}$$"
            f"\n\n[MATH_CARD: formula: C({n},{r}) | result: {comb} | style: violet]"
        )
    else:
        body = "Please use the form `5C2` (combinations) or `5P2` (permutations)."

    return _thinking_wrap(thinking, heading, body, mode)


# ---------------------------------------------------------------------------
# Geometry
# ---------------------------------------------------------------------------

def _geometry_response(query: str, mode: str) -> str:
    heading = "Geometry Calculator"
    thinking = (
        "- **Intent:** Geometric computation.\n"
        "- **Method:** Standard area/volume/perimeter formulas."
    )

    q = query.lower()
    nums = _parse_number_list(query)

    # Circle
    if "circle" in q:
        if not nums:
            body = "Please provide a radius, e.g. `area of circle with radius 5`."
            return _thinking_wrap(thinking, heading, body, mode)
        r = nums[0]
        area = math.pi * r ** 2
        perim = 2 * math.pi * r
        body = (
            f"**Circle** with radius $r = {r}$:\n\n"
            f"| Property | Formula | Value |\n"
            f"|----------|---------|-------|\n"
            f"| Area | $\\pi r^2$ | ${area:.4g}$ |\n"
            f"| Circumference | $2\\pi r$ | ${perim:.4g}$ |\n\n"
            f"$$A = \\pi ({r})^2 = {area:.4g}$$"
            f"\n\n[MATH_CARD: formula: circle r={r} | result: area={area:.4g} | style: violet]"
        )
        return _thinking_wrap(thinking, heading, body, mode)

    # Triangle
    if "triangle" in q:
        if "pythagorean" in q or "hypotenuse" in q:
            return _pythagorean_response(query, mode)
        if len(nums) >= 2:
            base, height = nums[0], nums[1]
            area = 0.5 * base * height
            body = (
                f"**Triangle** with base $b = {base}$, height $h = {height}$:\n\n"
                f"$$A = \\frac{{1}}{{2}} \\cdot b \\cdot h = \\frac{{1}}{{2}} \\cdot {base} \\cdot {height} = {area:.4g}$$"
                f"\n\n[MATH_CARD: formula: triangle b={base} h={height} | result: area={area:.4g} | style: violet]"
            )
            return _thinking_wrap(thinking, heading, body, mode)

    # Rectangle / Square
    if "rectangle" in q or "square" in q:
        if len(nums) >= 2:
            l, w = nums[0], nums[1]
        elif len(nums) == 1:
            l = w = nums[0]
        else:
            body = "Please provide dimensions, e.g. `area of rectangle 6 by 4`."
            return _thinking_wrap(thinking, heading, body, mode)
        area = l * w
        perim = 2 * (l + w)
        body = (
            f"**Rectangle** with length $l = {l}$, width $w = {w}$:\n\n"
            f"| Property | Formula | Value |\n"
            f"|----------|---------|-------|\n"
            f"| Area | $l \\times w$ | ${area:.4g}$ |\n"
            f"| Perimeter | $2(l + w)$ | ${perim:.4g}$ |\n\n"
            f"$$A = {l} \\times {w} = {area:.4g}$$"
            f"\n\n[MATH_CARD: formula: rect {l}x{w} | result: area={area:.4g} | style: violet]"
        )
        return _thinking_wrap(thinking, heading, body, mode)

    # Trapezoid
    if "trapezoid" in q or "trapezium" in q:
        if len(nums) >= 3:
            a, b, h = nums[0], nums[1], nums[2]
            area = 0.5 * (a + b) * h
            body = (
                f"**Trapezoid** with parallel sides $a = {a}$, $b = {b}$, height $h = {h}$:\n\n"
                f"$$A = \\frac{{(a+b)}}{{2}} \\cdot h = \\frac{{({a}+{b})}}{{2}} \\cdot {h} = {area:.4g}$$"
                f"\n\n[MATH_CARD: formula: trapezoid a={a} b={b} h={h} | result: area={area:.4g} | style: violet]"
            )
            return _thinking_wrap(thinking, heading, body, mode)

    # Sphere
    if "sphere" in q:
        if not nums:
            body = "Please provide a radius, e.g. `volume of sphere with radius 3`."
            return _thinking_wrap(thinking, heading, body, mode)
        r = nums[0]
        vol = (4 / 3) * math.pi * r ** 3
        sa = 4 * math.pi * r ** 2
        body = (
            f"**Sphere** with radius $r = {r}$:\n\n"
            f"| Property | Formula | Value |\n"
            f"|----------|---------|-------|\n"
            f"| Volume | $\\frac{{4}}{{3}}\\pi r^3$ | ${vol:.4g}$ |\n"
            f"| Surface Area | $4\\pi r^2$ | ${sa:.4g}$ |\n\n"
            f"$$V = \\frac{{4}}{{3}}\\pi ({r})^3 = {vol:.4g}$$"
            f"\n\n[MATH_CARD: formula: sphere r={r} | result: vol={vol:.4g} | style: violet]"
        )
        return _thinking_wrap(thinking, heading, body, mode)

    # Cylinder
    if "cylinder" in q:
        if len(nums) >= 2:
            r, h = nums[0], nums[1]
            vol = math.pi * r ** 2 * h
            sa = 2 * math.pi * r * (r + h)
            body = (
                f"**Cylinder** with radius $r = {r}$, height $h = {h}$:\n\n"
                f"| Property | Formula | Value |\n"
                f"|----------|---------|-------|\n"
                f"| Volume | $\\pi r^2 h$ | ${vol:.4g}$ |\n"
                f"| Surface Area | $2\\pi r(r+h)$ | ${sa:.4g}$ |\n\n"
                f"$$V = \\pi ({r})^2 ({h}) = {vol:.4g}$$"
                f"\n\n[MATH_CARD: formula: cylinder r={r} h={h} | result: vol={vol:.4g} | style: violet]"
            )
            return _thinking_wrap(thinking, heading, body, mode)

    # Cone
    if "cone" in q:
        if len(nums) >= 2:
            r, h = nums[0], nums[1]
            vol = (1 / 3) * math.pi * r ** 2 * h
            slant = math.sqrt(r ** 2 + h ** 2)
            sa = math.pi * r * (r + slant)
            body = (
                f"**Cone** with radius $r = {r}$, height $h = {h}$:\n\n"
                f"| Property | Formula | Value |\n"
                f"|----------|---------|-------|\n"
                f"| Volume | $\\frac{{1}}{{3}}\\pi r^2 h$ | ${vol:.4g}$ |\n"
                f"| Surface Area | $\\pi r(r+l)$ | ${sa:.4g}$ |\n"
                f"| Slant Height | $\\sqrt{{r^2+h^2}}$ | ${slant:.4g}$ |\n\n"
                f"$$V = \\frac{{1}}{{3}}\\pi ({r})^2({h}) = {vol:.4g}$$"
                f"\n\n[MATH_CARD: formula: cone r={r} h={h} | result: vol={vol:.4g} | style: violet]"
            )
            return _thinking_wrap(thinking, heading, body, mode)

    # Cube
    if "cube" in q:
        if nums:
            s = nums[0]
            vol = s ** 3
            sa = 6 * s ** 2
            body = (
                f"**Cube** with side $s = {s}$:\n\n"
                f"| Property | Formula | Value |\n"
                f"|----------|---------|-------|\n"
                f"| Volume | $s^3$ | ${vol:.4g}$ |\n"
                f"| Surface Area | $6s^2$ | ${sa:.4g}$ |\n\n"
                f"$$V = ({s})^3 = {vol:.4g}$$"
                f"\n\n[MATH_CARD: formula: cube s={s} | result: vol={vol:.4g} | style: violet]"
            )
            return _thinking_wrap(thinking, heading, body, mode)

    body = "Could not identify the geometric shape or parameters. Try `area of circle radius 5` or `volume of sphere radius 3`."
    return _thinking_wrap(thinking, heading, body, mode)


def _pythagorean_response(query: str, mode: str) -> str:
    heading = "Pythagorean Theorem Solver"
    thinking = (
        "- **Intent:** Solve right triangle sides.\n"
        "- **Method:** a² + b² = c²."
    )

    nums = _parse_number_list(query)
    q = query.lower()

    if len(nums) >= 2:
        if "hypotenuse" in q or "c" in q:
            a, b = nums[0], nums[1]
            c = math.sqrt(a ** 2 + b ** 2)
            body = (
                f"Finding hypotenuse with legs $a = {a}$, $b = {b}$:\n\n"
                "$$c = \\sqrt{a^2 + b^2}$$\n\n"
                f"$$c = \\sqrt{{({a})^2 + ({b})^2}} = \\sqrt{{{a**2} + {b**2}}} = \\sqrt{{{a**2 + b**2}}} = {c:.4g}$$"
                f"\n\n[MATH_CARD: formula: a²+b²=c² | result: c={c:.4g} | style: violet]"
            )
        else:
            # Assume largest is hypotenuse, find missing leg
            nums_sorted = sorted(nums[:2])
            leg, hyp = nums_sorted[0], nums_sorted[1]
            if hyp <= leg:
                body = "Hypotenuse must be larger than the leg."
                return _thinking_wrap(thinking, heading, body, mode)
            missing = math.sqrt(hyp ** 2 - leg ** 2)
            body = (
                f"Finding missing leg with known leg $a = {leg}$ and hypotenuse $c = {hyp}$:\n\n"
                "$$b = \\sqrt{c^2 - a^2}$$\n\n"
                f"$$b = \\sqrt{{({hyp})^2 - ({leg})^2}} = \\sqrt{{{hyp**2} - {leg**2}}} = {missing:.4g}$$"
                f"\n\n[MATH_CARD: formula: a²+b²=c² | result: b={missing:.4g} | style: violet]"
            )
    else:
        body = "Please provide two sides, e.g. `Pythagorean theorem with a=3, b=4` or `hypotenuse with legs 3 and 4`."

    return _thinking_wrap(thinking, heading, body, mode)


# ---------------------------------------------------------------------------
# Number Theory
# ---------------------------------------------------------------------------

def _is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True


def _prime_response(query: str, mode: str) -> str:
    heading = "Prime Number Checker"
    thinking = (
        "- **Intent:** Primality test.\n"
        "- **Method:** Trial division."
    )

    nums = _parse_number_list(query)
    if not nums:
        body = "Please specify a number, e.g. `is 97 prime?`."
        return _thinking_wrap(thinking, heading, body, mode)

    n = int(nums[0])
    prime = _is_prime(n)

    if prime:
        body = (
            f"**{n}** is a **prime number**.\n\n"
            f"It has no divisors other than 1 and {n} itself.\n\n"
            f"[MATH_CARD: formula: is {n} prime? | result: YES | style: violet]"
        )
    else:
        factors = [i for i in range(2, n + 1) if n % i == 0 and i != n]
        factors_str = ", ".join(str(f) for f in factors)
        body = (
            f"**{n}** is **not prime**.\n\n"
            f"Divisors: {factors_str} (among others)\n\n"
            f"[MATH_CARD: formula: is {n} prime? | result: NO (factors: {factors_str}) | style: violet]"
        )

    return _thinking_wrap(thinking, heading, body, mode)


def _gcd_lcm_response(query: str, mode: str) -> str:
    heading = "GCD & LCM Calculator"
    thinking = (
        "- **Intent:** Greatest Common Divisor / Least Common Multiple.\n"
        "- **Method:** Euclidean algorithm."
    )

    nums = [int(x) for x in re.findall(r"\d+", query)]
    if len(nums) < 2:
        body = "Please provide at least two numbers, e.g. `GCD of 48 and 18`."
        return _thinking_wrap(thinking, heading, body, mode)

    a, b = nums[0], nums[1]
    gcd = math.gcd(a, b)
    lcm = abs(a * b) // gcd

    q = query.lower()
    if "lcm" in q or "least common" in q:
        result_label = f"LCM={lcm}"
    else:
        result_label = f"GCD={gcd}"

    body = (
        f"For **{a}** and **{b}**:\n\n"
        f"**GCD** (using Euclidean algorithm):\n"
        f"$$\\gcd({a}, {b}) = {gcd}$$\n\n"
        f"**LCM** (using relationship $\\text{{lcm}}(a,b) = \\frac{{|a \\cdot b|}}{{\\gcd(a,b)}}$):\n"
        f"$$\\text{{lcm}}({a}, {b}) = \\frac{{{a} \\cdot {b}}}{{{gcd}}} = {lcm}$$"
        f"\n\n[MATH_CARD: formula: GCD/LCM({a},{b}) | result: {result_label} | style: violet]"
    )
    return _thinking_wrap(thinking, heading, body, mode)


def _fibonacci_response(query: str, mode: str) -> str:
    heading = "Fibonacci Sequence"
    thinking = (
        "- **Intent:** Generate Fibonacci numbers.\n"
        "- **Method:** Iterative computation."
    )

    nums = _parse_number_list(query)
    n = int(nums[0]) if nums else 10
    n = min(n, 50)  # cap at 50 for safety

    fibs = [0, 1]
    while len(fibs) < n:
        fibs.append(fibs[-1] + fibs[-2])
    fibs = fibs[:n]

    seq_str = ", ".join(str(f) for f in fibs)
    body = (
        f"**First {n} Fibonacci numbers:**\n\n"
        "$$F(n) = F(n-1) + F(n-2), \\quad F(0)=0, F(1)=1$$\n\n"
        f"$${seq_str}$$"
        f"\n\n[MATH_CARD: formula: Fibonacci({n}) | result: F({n-1})={fibs[-1]} | style: violet]"
    )
    return _thinking_wrap(thinking, heading, body, mode)


def _factorial_response(query: str, mode: str) -> str:
    heading = "Factorial Calculator"
    thinking = (
        "- **Intent:** Compute factorial.\n"
        "- **Method:** n! = n × (n-1) × … × 1."
    )

    nums = _parse_number_list(query)
    if not nums:
        body = "Please specify a number, e.g. `5 factorial` or `what is 7!`."
        return _thinking_wrap(thinking, heading, body, mode)

    n = int(nums[0])
    if n < 0:
        body = "Factorial is not defined for negative numbers."
        return _thinking_wrap(thinking, heading, body, mode)
    if n > 20:
        body = f"Factorial of {n} is a very large number. Limiting computation to n ≤ 20."
        return _thinking_wrap(thinking, heading, body, mode)

    result = math.factorial(n)
    steps = " × ".join(str(i) for i in range(n, 0, -1)) if n > 0 else "1"
    body = (
        f"Computing **${n}!$**:\n\n"
        "$$n! = n \\times (n-1) \\times \\cdots \\times 1$$\n\n"
        f"$${n}! = {steps} = {result}$$"
        f"\n\n[MATH_CARD: formula: {n}! | result: {result} | style: violet]"
    )
    return _thinking_wrap(thinking, heading, body, mode)


# ---------------------------------------------------------------------------
# Unit Conversion
# ---------------------------------------------------------------------------

_UNIT_CONVERSIONS = {
    # Length
    ("km", "miles"): (0.621371, "km × 0.621371 = miles"),
    ("miles", "km"): (1.60934, "miles × 1.60934 = km"),
    ("meters", "feet"): (3.28084, "m × 3.28084 = ft"),
    ("feet", "meters"): (0.3048, "ft × 0.3048 = m"),
    ("cm", "inches"): (0.393701, "cm × 0.393701 = in"),
    ("inches", "cm"): (2.54, "in × 2.54 = cm"),
    # Mass
    ("kg", "pounds"): (2.20462, "kg × 2.20462 = lb"),
    ("pounds", "kg"): (0.453592, "lb × 0.453592 = kg"),
    ("grams", "ounces"): (0.035274, "g × 0.035274 = oz"),
    ("ounces", "grams"): (28.3495, "oz × 28.3495 = g"),
    # Volume
    ("liters", "gallons"): (0.264172, "L × 0.264172 = gal"),
    ("gallons", "liters"): (3.78541, "gal × 3.78541 = L"),
}

_TEMP_PATTERNS = [
    (r"celsius", r"fahrenheit", lambda c: c * 9 / 5 + 32, "°C × 9/5 + 32 = °F"),
    (r"fahrenheit", r"celsius", lambda f: (f - 32) * 5 / 9, "(°F - 32) × 5/9 = °C"),
    (r"celsius", r"kelvin", lambda c: c + 273.15, "°C + 273.15 = K"),
    (r"kelvin", r"celsius", lambda k: k - 273.15, "K - 273.15 = °C"),
]


def _unit_conversion_response(query: str, mode: str) -> str:
    heading = "Unit Converter"
    thinking = (
        "- **Intent:** Unit conversion.\n"
        "- **Method:** Multiplication factor or formula."
    )

    q = query.lower()
    nums = _parse_number_list(query)
    if not nums:
        body = "Please specify a value, e.g. `convert 100 km to miles`."
        return _thinking_wrap(thinking, heading, body, mode)

    value = nums[0]

    # Temperature (special formulas)
    for from_pat, to_pat, fn, formula in _TEMP_PATTERNS:
        if re.search(from_pat, q) and re.search(to_pat, q):
            result = fn(value)
            body = (
                f"**Temperature Conversion**: ${value}$ {from_pat.title()} → {to_pat.title()}\n\n"
                f"**Formula**: {formula}\n\n"
                f"$${value} \\rightarrow {result:.4g}$$"
                f"\n\n[MATH_CARD: formula: {value} {from_pat[:1].upper()} to {to_pat[:1].upper()} | result: {result:.4g} | style: violet]"
            )
            return _thinking_wrap(thinking, heading, body, mode)

    # Factor-based conversions
    for (from_u, to_u), (factor, formula) in _UNIT_CONVERSIONS.items():
        if from_u in q and to_u in q:
            result = value * factor
            body = (
                f"**Unit Conversion**: ${value}$ {from_u} → {to_u}\n\n"
                f"**Formula**: {formula}\n\n"
                f"$${value} \\times {factor} = {result:.4g}$$"
                f"\n\n[MATH_CARD: formula: {value} {from_u} to {to_u} | result: {result:.4g} | style: violet]"
            )
            return _thinking_wrap(thinking, heading, body, mode)

    body = (
        "Could not identify the unit conversion. "
        "Try `convert 100 km to miles`, `convert 50 celsius to fahrenheit`, or `convert 1 kg to pounds`."
    )
    return _thinking_wrap(thinking, heading, body, mode)


# ---------------------------------------------------------------------------
# Improved arithmetic evaluator
# ---------------------------------------------------------------------------

def _arithmetic_response(query: str, mode: str) -> str:
    heading = "Arithmetic Evaluator"
    thinking = (
        "- **Intent:** Arithmetic Reduction.\n"
        "- **Method:** Safe expression evaluation."
    )

    q = query.lower().strip()

    # Percentage: "15% of 340"
    pct_m = re.search(r"(\d+(?:\.\d+)?)\s*%\s*of\s*(\d+(?:\.\d+)?)", q)
    if pct_m:
        pct, of_val = float(pct_m.group(1)), float(pct_m.group(2))
        result = pct / 100 * of_val
        body = (
            f"**{pct}% of {of_val}**:\n\n"
            f"$$\\frac{{{pct}}}{{100}} \\times {of_val} = {result:.4g}$$"
            f"\n\n[MATH_CARD: formula: {pct}% of {of_val} | result: {result:.4g} | style: violet]"
        )
        return _thinking_wrap(thinking, heading, body, mode)

    # Factorial: "3 factorial" or "4!"
    fact_m = re.search(r"(\d+)\s*(?:factorial|!)", q)
    if fact_m:
        return _factorial_response(q, mode)

    # Build safe eval expression
    clean = (
        q
        .replace("plus", "+").replace("minus", "-")
        .replace("times", "*").replace("divided by", "/")
        .replace("÷", "/").replace("x", "*")
    )

    # Replace ^ with ** for power
    clean = re.sub(r"\^", "**", clean)

    # Replace sqrt(...)
    clean = re.sub(r"sqrt\s*\(([^)]+)\)", lambda mm: f"({mm.group(1)})**0.5", clean)
    clean = re.sub(r"\bsqrt\s+(\d+(?:\.\d+)?)\b", lambda mm: f"({mm.group(1)})**0.5", clean)

    # Replace log(...) -> log10, ln(...) -> ln
    safe_env = {
        "__builtins__": {},
        "sqrt": math.sqrt,
        "log": math.log10,
        "ln": math.log,
        "pi": math.pi,
        "e": math.e,
        "abs": abs,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
    }

    # Strip non-safe chars but keep function names and parens
    safe = re.sub(r"[^0-9+\-*/().\s*a-z_]", "", clean)

    try:
        result = eval(safe, safe_env)  # noqa: S307
        if not isinstance(result, (int, float)) or not math.isfinite(result):
            raise ValueError
        body = (
            f"Evaluating **`{query.strip()}`**:\n\n"
            f"1. **Expression**: `{safe.strip()}`\n"
            f"2. **Result**: ${result:.6g}$"
            f"\n\n[MATH_CARD: formula: {safe.strip()} | result: {result:.6g} | style: violet]"
        )
    except Exception:
        body = f"Could not safely evaluate **\"{query}\"**. Please enter a valid arithmetic expression."

    return _thinking_wrap(thinking, heading, body, mode)


# ---------------------------------------------------------------------------
# Main dispatcher
# ---------------------------------------------------------------------------

def generate_math_response(query: str, mode: str) -> str:
    q = query.lower().strip()
    q = re.sub(
        r"^(what is|whats|what's|calculate|solve|evaluate|compute|find|value of)\s+", "", q
    )
    q = q.rstrip("?")

    # Unit conversion
    if re.search(r"\bconvert\b", q) or (
        re.search(r"\b(km|miles|celsius|fahrenheit|kelvin|kg|pounds|liters|gallons|feet|meters|cm|inches|ounces|grams)\b", q)
        and re.search(r"\bto\b", q)
    ):
        return _unit_conversion_response(q, mode)

    # Calculus
    if "derivative" in q or "d/dx" in q:
        expr = re.sub(r"derivative of|d/dx", "", q).strip()
        return _derivative_response(expr, mode)

    if any(w in q for w in ("integral", "integrate", "antiderivative")):
        expr = re.sub(r"integral of|integrate|antiderivative of", "", q).strip()
        return _integral_response(expr, mode)

    # Trig
    if re.search(r"(sin|cos|tan|csc|sec|cot)\s*\(?\d", q, re.IGNORECASE):
        return _trig_response(q, mode)

    # Quadratic
    if re.search(r"quadratic|x\^?2|x\s*\*\s*\*\s*2", q):
        return _quadratic_response(q, mode)

    # Linear equation (has "=" but not quadratic)
    if re.search(r"\d\s*x.*=|\bx\s*[+-].*=", q):
        return _linear_equation_response(q, mode)

    # Statistics
    if re.search(r"\b(mean|median|mode|average|std|standard deviation|variance)\b", q):
        return _statistics_response(q, mode)

    # Combinations / Permutations
    if re.search(r"\b(\d+[Cc]r?\d+|\d+[Pp]r?\d+|combination|permutation|ncr|npr)\b", q):
        return _combinations_response(q, mode)

    # Geometry
    if re.search(r"\b(circle|sphere|cylinder|cone|cube|rectangle|square|triangle|trapezoid|trapezium|area|volume|perimeter|circumference)\b", q):
        # Pythagorean special case
        if re.search(r"pythagorean|hypotenuse", q):
            return _pythagorean_response(q, mode)
        return _geometry_response(q, mode)

    # Pythagorean (standalone)
    if re.search(r"pythagorean|hypotenuse", q):
        return _pythagorean_response(q, mode)

    # Number theory
    if re.search(r"\bis\s+\d+\s+prime\b|prime\s+(number|check|test)", q):
        return _prime_response(q, mode)

    if re.search(r"\b(gcd|lcm|greatest common|least common)\b", q):
        return _gcd_lcm_response(q, mode)

    if re.search(r"\bfibonacci\b", q):
        return _fibonacci_response(q, mode)

    if re.search(r"\b(\d+\s*factorial|\d+\s*!)\b", q):
        return _factorial_response(q, mode)

    # Percentage
    if re.search(r"\d+%\s*of\s*\d+", q):
        return _arithmetic_response(q, mode)

    # Fallback: arithmetic
    return _arithmetic_response(q, mode)
