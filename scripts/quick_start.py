import puzzlekit
import time
import os
import logging

# Script-only logging configuration:
# - Library code never calls `basicConfig`.
# - Enable logs by setting `PUZZLEKIT_LOG_LEVEL` (e.g. DEBUG/INFO/WARNING).
_level_name = os.getenv("PUZZLEKIT_LOG_LEVEL", "").strip().upper()
if _level_name:
    _level = getattr(logging, _level_name, None)
    if isinstance(_level, int):
        logging.basicConfig(
            level=_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

# Raw input data
start_time = time.time()
problem_str = """
10 10\n6 5 - - - - - - - -\n- - - - - - - - - -\n- - - - - 2 - - - -\n1 - - - - - 9 - - -\n- - - - - - - - - -\n- - - - - - - - - -\n3 - - - - - 8 - - -\n- 4 - - - - - - - -\n- - - - - - - - - -\n- - 7 - - - - - - -\n1 4 4 4 4 4 4 4 4 4\n1 1 1 4 4 4 8 4 4 4\n1 1 1 1 4 8 8 8 8 4\n2 2 2 7 7 7 9 9 9 9\n2 3 3 3 7 7 7 9 9 9\n2 3 3 3 7 7 7 10 9 9\n3 3 5 3 7 6 10 10 9 9\n3 5 5 5 5 6 10 10 10 10\n3 5 5 6 6 6 6 10 10 10\n3 5 6 6 6 6 6 10 10 10
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="shimaguni")

# Print solution grid
print(res.solution_data.get('solution_grid', []))
print(res.solution_data.get('cpu_time', "Not available"))
print(res.solution_data.get('build_time', "Not available"))
end_time = time.time()
print(f"Time taken: {end_time - start_time} seconds")
# Visualize (optional)
# res.show()


# URL -> IR
ir = puzzlekit.decode("https://puzz.link/p?slither/10/10/g188227cl1dg367bdcg3ddgbhdgd1agbd760dg2cl633661d")
# IR -> puzz.link URL
print(puzzlekit.encode(ir, "puzzlink"))
