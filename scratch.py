import copy
from collections import OrderedDict
from pathlib import Path

import toml
from loguru import logger as log

BASE_DIR = Path(".")
pyproject_path = BASE_DIR / "pyproject5.toml"


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
        string_before_line = "[tool.poetry.dependencies]"
    if not prod:
        string_before_line = "[tool.poetry.dev-dependencies]"

    comment_line = "# Everything after this should be sorted alphabetically\n"
    with open(filename, "r") as f:
        contents = f.readlines()

    log.info(contents)

    line_index_gen = (
        idx + 1 for idx, line in enumerate(contents) if string_before_line in line
    )
    contents.insert(next(line_index_gen) + int(prod), comment_line)

    with open(filename, "w") as f:
        f.writelines(contents)

    return None


def main(pyproject_path):
    def fix_either_path(pyproject_path, prod=True):
        pyp = toml.load(pyproject_path)
        try:
            pyp["tool"]["poetry"]
        except KeyError:
            log.info("Not using poetry - no imports to sort")
            return False

        log.info(pyp)

        if prod:
            try:
                unordered_deps = copy.deepcopy(pyp["tool"]["poetry"]["dependencies"])
            except KeyError:
                log.info("No dependencies specified")
                return False

            ordered_deps = OrderedDict(sorted(unordered_deps.items())).move_to_end(
                "python", last=False
            )
            pyp["tool"]["poetry"]["dependencies"] = ordered_deps
            log.info(ordered_deps)
            if OrderedDict(unordered_deps) != ordered_deps:
                with open(pyproject_path, "w") as f:
                    toml.dump(pyp, f)
                insert_comment_line(pyproject_path, prod=True)
                log.info("Production dependencies sorted")
                return True
            else:
                log.info("Production dependencies unchanged")
                return False

        elif not prod:
            try:
                unordered_deps = copy.deepcopy(
                    pyp["tool"]["poetry"]["dev-dependencies"]
                )
            except KeyError:
                log.info("No dev dependencies specified")
                return False

            ordered_deps = OrderedDict(sorted(unordered_deps.items()))
            pyp["tool"]["poetry"]["dev-dependencies"] = ordered_deps
            log.info(ordered_deps)
            if OrderedDict(unordered_deps) != ordered_deps:
                with open(pyproject_path, "w") as f:
                    toml.dump(pyp, f)
                insert_comment_line(pyproject_path, prod=False)
                log.info("Development dependencies sorted")
                return True
            else:
                log.info("Development dependencies unchanged")
                return False

    # Force the logical OR not to short-circuit.
    left = fix_either_path(pyproject_path, prod=True)
    right = fix_either_path(pyproject_path, prod=False)

    # Note that True means the test failed
    return int(left or right)


if __name__ == "__main__":
    main(pyproject_path)
