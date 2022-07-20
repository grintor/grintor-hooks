import ast
import sys
import os
import types
import subprocess
import pathlib
import shutil
from zipfile import ZipFile
import hashlib
import json

def main():
    all_imports = {}
    for filename in sys.argv[1:]:
        for key, val in find_imports(filename).items():
            all_imports[key] = val

    external_imports = extract_external_imports(all_imports.keys())

    missing_external_imports = []
    for requirements_file in ["requirements.in", "requirements.txt"]:
        if os.path.exists(requirements_file):
            pip_modules = extract_pip_modules(requirements_file)
            for external_import in external_imports:
                if external_import not in pip_modules:
                    missing_external_import = {
                        "module": external_import,
                        "line": all_imports[external_import]["line"],
                        "file": all_imports[external_import]["file"],
                        "requirements_file": requirements_file,
                    }
                    missing_external_imports.append(
                        types.SimpleNamespace(**missing_external_import)
                    )

    if missing_external_imports:
        for imp in missing_external_imports:
            print(f'{imp.file}:{imp.line}, imported "{imp.module}" missing from {imp.requirements_file}')
        sys.exit(2)

def extract_pip_modules(requirements_file):
    # given a requirements file, determine all the modules that would be installed (by downloading and inspecting them)
    
    pip_modules = get_cached_pip_module_info(requirements_file)
    
    if not pip_modules:
        whl_cache_dir = str((pathlib.Path(os.environ['VIRTUAL_ENV']) / 'whl_cache_tmp').resolve())
        if os.path.exists(whl_cache_dir):
            shutil.rmtree(whl_cache_dir, ignore_errors=True)

        subprocess.run(
            ["pip", "download", "--no-deps", "-r", requirements_file, "-d", whl_cache_dir],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        pip_modules = []
        for item in os.listdir(whl_cache_dir):
            if item.endswith('.whl'):
                for pip_module in get_modules_from_wheel(str((pathlib.Path(whl_cache_dir) / item).resolve())):
                    pip_modules.append(pip_module)

        shutil.rmtree(whl_cache_dir, ignore_errors=True)
        save_cached_pip_module_info(requirements_file, pip_modules)

    return pip_modules

def save_cached_pip_module_info(requirements_file, to_save):
    sha1 = hashlib.sha1()
    with open(requirements_file, 'rb') as f:
        sha1.update(f.read())

    whl_cache = str((pathlib.Path(os.environ['VIRTUAL_ENV']) / f'cache_val_{sha1.hexdigest()}.json').resolve())
    with open(whl_cache, 'w') as f:
        f.write(json.dumps(to_save))
    

def get_cached_pip_module_info(requirements_file):
    sha1 = hashlib.sha1()
    with open(requirements_file, 'rb') as f:
        sha1.update(f.read())
    
    whl_cache = str((pathlib.Path(os.environ['VIRTUAL_ENV']) / f'cache_val_{sha1.hexdigest()}.json').resolve())
    if os.path.exists(whl_cache):
        with open(whl_cache, 'r') as f:
            return json.loads(f.read())
    else:
        return None

def extract_external_imports(all_imports):
    # given a list of modules, return a list of those not found in the python std lib or sys.path
    external_imports = []

    builtin_modules = sys.builtin_module_names
    
    sys_modules = []
    for import_item in all_imports:
        for sys_path in sys.path:
            p1 = pathlib.Path(sys_path) / f"{import_item}.py"
            p2 = pathlib.Path(sys_path) / import_item / '__init__.py'
            if p1.exists() or p2.exists():
                sys_modules.append(import_item)


    for import_item in all_imports:
        if import_item not in builtin_modules and import_item not in sys_modules:
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


def get_modules_from_wheel(wheel_filename):
    top_level = []
    pth_file = []
    with ZipFile(wheel_filename) as wheel:
        for filename in wheel.namelist():
            if filename.endswith('.dist-info/top_level.txt') and filename.count('/') == 1:
                with wheel.open(filename) as f:
                    top_level = f.read().decode('utf-8').splitlines()
            if filename.endswith('.pth') and filename.count('/') == 0:
                with wheel.open(filename) as f:
                    pth_file = f.read().decode('utf-8').splitlines()

    top_level_norm = []
    for line in top_level:
        strip_line = line.strip()
        if not strip_line.startswith('#'):
            top_level_norm.append(strip_line.replace('\\', '/')) # normalize windows/linux

    pth_entries = []
    for line in pth_file:
        strip_line = line.strip()
        if not strip_line.startswith('#'):
            pth_entries.append(strip_line.replace('\\', '/')) # normalize windows/linux


    real_exposed_modules = []

    for file in top_level_norm:
        real_exposed_modules.append(file)

    for file in top_level_norm:
        for pth_entry in pth_entries:
            if file.startswith(f"{pth_entry}/"):
                real_exposed_modules.append(file[len(f"{pth_entry}/"):])

    importable_modules = []
    for file in real_exposed_modules:
        importable_modules.append(file.replace('/', '.'))
    return list(set(importable_modules))

if __name__ == "__main__":
    main()
