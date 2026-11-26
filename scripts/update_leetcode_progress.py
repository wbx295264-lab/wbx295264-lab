"""Update the profile's LeetCode section from verified public totals."""

import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path
import re


START = "<!-- leetcode-progress:start -->"
END = "<!-- leetcode-progress:end -->"
BEIJING_TIME = timezone(timedelta(hours=8))
COUNTS = re.compile(
    r"^\*\*已解 (\d+) 题\*\*$.*?^\| (\d+) \| (\d+) \| (\d+) \|$",
    re.MULTILINE | re.DOTALL,
)


def refresh_readme(readme: Path, total: int, easy: int, medium: int, hard: int) -> bool:
    counts = (total, easy, medium, hard)
    if any(count < 0 for count in counts) or total != easy + medium + hard:
        raise ValueError("The total must match the three nonnegative difficulty counts.")

    before = readme.read_text(encoding="utf-8")
    if before.count(START) != 1 or before.count(END) != 1:
        raise ValueError("Expected exactly one pair of LeetCode section markers.")

    prefix, remainder = before.split(START, 1)
    block, marker, suffix = remainder.partition(END)
    if not marker:
        raise ValueError("The LeetCode section markers are out of order.")
    previous = COUNTS.search(block)
    if previous is None:
        raise ValueError("Could not read the existing LeetCode totals.")
    if tuple(map(int, previous.groups())) == counts:
        return False

    today = datetime.now(BEIJING_TIME).date().isoformat()
    updated = (
        f"\n**已解 {total} 题**\n\n"
        "| 简单 | 中等 | 困难 |\n"
        "| :---: | :---: | :---: |\n"
        f"| {easy} | {medium} | {hard} |\n\n"
        f"<sub>更新于 {today}（北京时间）</sub>\n"
    )
    readme.write_text(prefix + START + updated + END + suffix, encoding="utf-8", newline="\n")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--total", required=True, type=int)
    parser.add_argument("--easy", required=True, type=int)
    parser.add_argument("--medium", required=True, type=int)
    parser.add_argument("--hard", required=True, type=int)
    args = parser.parse_args()
    readme = Path(__file__).resolve().parents[1] / "README.md"
    try:
        changed = refresh_readme(readme, args.total, args.easy, args.medium, args.hard)
    except ValueError as error:
        parser.error(str(error))
    print("LeetCode totals updated." if changed else "LeetCode totals are unchanged.")


if __name__ == "__main__":
    main()
