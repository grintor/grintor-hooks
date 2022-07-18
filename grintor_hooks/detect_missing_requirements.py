import ast
import sys
import os
import types

import pip_api # pip install pip_api
import isort.stdlibs # pip install isort


def main():
    all_imports = {}
    for filename in sys.argv[1:]:
        for key, val in find_imports(filename).items():
            all_imports[key] = val

    external_imports = extract_external_imports(all_imports.keys())

    missing_external_imports = []
    for requirements_file in ["requirements.txt", "requirements.in"]:
        if os.path.exists(requirements_file):
            requirements = pip_api.parse_requirements(requirements_file).keys()
            for external_import in external_imports:
                if external_import not in requirements:
                    missing_external_import = {
                        "name": external_import,
                        "line": all_imports[external_import]["line"],
                        "file": all_imports[external_import]["file"],
                        "requirements_file": requirements_file,
                    }
                    missing_external_imports.append(
                        types.SimpleNamespace(**missing_external_import)
                    )

    if missing_external_imports:
        for imp in missing_external_imports:
            print(f'File "{imp.file}", line {imp.line}: "{imp.name}" not found in {imp.requirements_file}')
        sys.exit(2)


def extract_external_imports(all_imports):
    # given a list of modules, return a list of those not found in the python std lib
    external_imports = []

    if sys.version_info >= (3, 10):
        std_lib = sys.stdlib_module_names
    else:
        std_lib = getattr(isort.stdlibs, f"py{sys.version_info.major}{sys.version_info.minor}").stdlib

    for import_item in all_imports:
        if import_item not in std_lib:
            external_imports.append(import_item)

    return external_imports


def find_imports(filename):
    # given a filename, parse the file and extract information about all of the module imports within
    found_imports = {}

    with open(filename, "r", encoding="utf-8") as f:
        src = f.read()

    try:
        file_ast = ast.parse(src, filename=filename, mode="exec")
    except:  # skip unparsable files by supplying an empty ast
        file_ast = ast.parse("", mode="exec")

    for node in ast.walk(file_ast):
        if isinstance(node, ast.Import):
            for name in node.names:
                found_imports[name.name] = {
                    "name": name.name,
                    "line": node.lineno,
                    "file": filename,
                }

        if isinstance(node, ast.ImportFrom):
            found_imports[node.module] = {
                "name": node.module,
                "line": node.lineno,
                "file": filename,
            }

    return found_imports


if __name__ == "__main__":
    main()
