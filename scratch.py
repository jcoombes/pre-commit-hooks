import copy
from collections import OrderedDict
from pathlib import Path

import toml
from loguru import logger as log

BASE_DIR = Path(".")
pyproject_path = BASE_DIR / "pyproject.toml"

PASS, FAIL = 0, 1
EXIT_CODE = PASS


def insert_comment_line(filename, prod=True):
    # Inserts line saying
    # Everything after this should be sorted alphabetically
    # After the first dependency (python),
    # and before the first dev-dependency.
    # Inputs
    # filename: _OpenFile - e.g. pyproject_path string.
    # prod: bool = True
    # Returns None. Reads and writes the filename file.
    if prod:
        string_before_line = "[tool.poetry.dependencies]\n"
    if not prod:
        string_before_line = "[tool.poetry.dev-dependencies]\n"

    comment_line = "# Everything after this should be sorted alphabetically\n"
    with open(filename, "r") as f:
        contents = f.readlines()

    contents.insert(contents.index(string_before_line) + int(prod), comment_line)

    with open(filename, "w") as f:
        f.writelines(contents)

    return None


def main():
    pyp = toml.load(pyproject_path)
    unordered_deps = copy.deepcopy(pyp["tool"]["poetry"]["dependencies"])
    unordered_dev_deps = copy.deepcopy(pyp["tool"]["poetry"]["dev-dependencies"])
    u_deps, u_dev_deps = OrderedDict(unordered_deps), OrderedDict(unordered_dev_deps)

    ordered_deps = OrderedDict(sorted(unordered_deps.items())).move_to_end(
        "python", last=False
    )
    log.info(ordered_deps)

    ordered_dev_deps = OrderedDict(sorted(unordered_dev_deps.items()))
    log.info(ordered_dev_deps)

    pyp["tool"]["poetry"]["dependencies"] = ordered_deps
    pyp["tool"]["poetry"]["dev-dependencies"] = ordered_dev_deps

    if u_deps != ordered_deps and u_dev_deps != ordered_dev_deps:
        log.info("pyproject.toml modified - Both deps and dev-deps ordered")
        toml.dump(pyp, pyproject_path)
        insert_comment_line(pyproject_path, prod=True)
        insert_comment_line(pyproject_path, prod=False)
        EXIT_CODE = FAIL
    elif u_deps != ordered_deps and u_dev_deps == ordered_dev_deps:
        log.info("pyproject.toml modified - dependencies ordered")
        toml.dump(pyp, pyproject_path)
        insert_comment_line(pyproject_path, prod=True)
        EXIT_CODE = FAIL
    elif u_deps == ordered_deps and u_dev_deps != ordered_dev_deps:
        log.info("pyproject.toml modified - dev-dependencies ordered")
        toml.dump(pyp, pyproject_path)
        insert_comment_line(pyproject_path, prod=False)
        EXIT_CODE = FAIL
    else:
        log.info("dependencies and dev-dependencies left unchanged.")

    return EXIT_CODE


if __name__ == "__main__":
    main()
