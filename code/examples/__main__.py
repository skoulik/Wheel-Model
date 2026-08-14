"""Run every worked example, or check every case.

    python -m examples --list        what exists, and what it backs
    python -m examples --check       every case, against the article
    python -m examples --run         every example's CLI output at defaults

From `code/`, or anywhere with `code/` on the path.  `verify_examples.py`
calls the same machinery; this is the shortcut for working on one module.
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples import _harness as H                            # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--coverage", action="store_true",
                    help="every {#eq:} in sections/ has a script, and vice versa")
    ap.add_argument("--references", action="store_true",
                    help="every #ref: cited in sections/ is a bibliography entry")
    ap.add_argument("--registers", action="store_true",
                    help="section 00's anchor registers match what sections declare")
    ap.add_argument("--derivations", action="store_true",
                    help="every #drv: linked in sections/ is a derivations entry")
    ap.add_argument("--appendix", action="store_true",
                    help="print the reproduction appendix as markdown")
    ap.add_argument("--only", default=None,
                    help="restrict to modules whose name contains this")
    ap.add_argument("--quiet", action="store_true", help="failures only")
    args = ap.parse_args()
    if not (args.list or args.check or args.run or args.coverage
            or args.references or args.registers or args.derivations
            or args.appendix):
        args.check = True

    mods = H.discover()
    if args.only:
        mods = [m for m in mods if args.only in m.__name__]
    if not mods:
        print("no example modules found")
        return 1

    if args.list:
        width = max(len(m.__name__.rsplit(".", 1)[-1]) for m in mods)
        for m in mods:
            name = m.__name__.rsplit(".", 1)[-1]
            print(f"  {name:<{width}}  {m.SECTION:<16} {', '.join(m.EQ)}")
        print(f"\n{len(mods)} modules, "
              f"{sum(len(m.EQ) for m in mods)} formulas, "
              f"{sum(len(m.CASES) for m in mods)} cases")

    if args.run:
        ctx = H.solve_all(H.collect_needs(mods))
        for m in mods:
            print(f"\n{m.TITLE}")
            print(H.render(m, m.compute(**H.params_from(m, ""), ctx=ctx)))

    if args.appendix:
        from examples import _report
        print(_report.appendix(mods))

    if args.coverage:
        from examples import _report
        gaps = _report.coverage(mods)
        for g in gaps:
            print(f"  {g}")
        return 1 if gaps else 0

    if args.references:
        from examples import _report
        gaps = _report.references()
        for g in gaps:
            print(f"  {g}")
        return 1 if gaps else 0

    if args.registers:
        from examples import _report
        gaps = _report.registers()
        for g in gaps:
            print(f"  {g}")
        return 1 if gaps else 0

    if args.derivations:
        from examples import _report
        gaps = _report.derivations()
        for g in gaps:
            print(f"  {g}")
        return 1 if gaps else 0

    if args.check:
        ctx = H.solve_all(H.collect_needs(mods))
        failures = H.report_cases(mods, ctx, quiet=args.quiet)
        print(f"\n{len(failures)} failure(s)" if failures else "\nall cases pass")
        for f in failures:
            print(f"  {f}")
        return 1 if failures else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
