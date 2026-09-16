import json
import traceback

from app.examples import EXAMPLES
from app.solvers.dispatcher import dispatch

failures = []
for category, problems in EXAMPLES.items():
    for problem in problems:
        try:
            result = dispatch(category, problem)
            has_plot = result["plot"] is not None
            print(f"OK  [{category}] '{problem}' -> {result['summary']}  (plot={has_plot})")
        except Exception as e:
            failures.append((category, problem, str(e)))
            print(f"FAIL [{category}] '{problem}' -> {e}")
            traceback.print_exc()

print("\n=== SUMMARY ===")
print(f"Total: {sum(len(v) for v in EXAMPLES.values())}, Failures: {len(failures)}")
for f in failures:
    print(f)
