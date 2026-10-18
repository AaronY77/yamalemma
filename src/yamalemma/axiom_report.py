import re


def find_axiom_report(
    stdout: str,
    theorem_name: str,
) -> str | None:
    prefix = f"'{theorem_name}'"
    matches: list[str] = []

    for line in stdout.splitlines():
        clean_line = line.strip()

        if clean_line.startswith(prefix):
            matches.append(clean_line)

    if len(matches) == 1:
        return matches[0]

    return None


def parse_axiom_report(
    stdout: str,
    theorem_name: str,
) -> tuple[str, ...] | None:
    report = find_axiom_report(stdout, theorem_name)

    if report is None:
        return None

    empty_report = f"'{theorem_name}' does not depend on any axioms"
    if report == empty_report:
        return ()

    prefix = f"'{theorem_name}' depends on axioms: ["
    if not report.startswith(prefix) or not report.endswith("]"):
        return None

    contents = report[len(prefix):-1].strip()

    if not contents:
        return ()

    names = tuple(name.strip() for name in contents.split(","))

    name_pattern = r"[A-Za-z_][A-Za-z0-9_']*(?:\.[A-Za-z_][A-Za-z0-9_']*)*"

    for name in names:
        if re.fullmatch(name_pattern, name) is None:
            return None

    return names
