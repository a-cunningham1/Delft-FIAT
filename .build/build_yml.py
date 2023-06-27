import argparse
import tomli
from pathlib import Path

MAIN_DIR = Path(__file__).parent.parent

parser = argparse.ArgumentParser()

parser.add_argument(
    "profile", choices=["build", "dev", "docs", "min", "test"], default="dev", nargs="?"
)
parser.add_argument("--output", "-o", default="environment.yml")
parser.add_argument("--channel", "-c", default="conda-forge")

args = parser.parse_args()

# will sadly have to maintian this manually :(
deps_not_in_conda = ["sphinx_autosummary_accessors", "sphinx_design"]
with open(Path(MAIN_DIR, "pyproject.toml"), "rb") as f:
    toml = tomli.load(f)

PYTHON_V = "python" + toml["project"]["requires-python"]

deps = toml["project"]["dependencies"]
conda_deps = []
conda_deps.extend(["pip", PYTHON_V])
pip_deps = []

if args.profile == "build":
    pip_deps.extend(toml["project"]["optional-dependencies"]["all"])
    pip_deps.extend(toml["project"]["optional-dependencies"]["build"])
    deps.remove([item for item in deps if "gdal" in item.lower()][0])
    conda_deps[1] = "python==3.11.*"
    pip_deps.extend(deps + ["-e ."])
elif args.profile == "dev":
    conda_deps.extend(toml["project"]["optional-dependencies"]["all"])
    conda_deps.extend(toml["project"]["optional-dependencies"]["dev"])
    conda_deps.extend(toml["project"]["optional-dependencies"]["docs"])
    conda_deps.extend(toml["project"]["optional-dependencies"]["test"])
    conda_deps.extend(deps)
elif args.profile == "docs":
    conda_deps.extend(toml["project"]["optional-dependencies"]["all"])
    conda_deps.extend(toml["project"]["optional-dependencies"]["docs"])
    conda_deps.extend(deps)
elif args.profile == "min":
    conda_deps.extend(toml["project"]["optional-dependencies"]["all"])
    conda_deps.extend(deps)
elif args.profile == "test":
    conda_deps.extend(toml["project"]["optional-dependencies"]["all"])
    conda_deps.extend(toml["project"]["optional-dependencies"]["test"])
    conda_deps.extend(deps)
else:
    raise RuntimeWarning(f"Unknown profile: {args.profile}")

conda_deps_final = conda_deps.copy()

for dep in conda_deps:
    if dep in deps_not_in_conda:
        pip_deps.append(dep)
        conda_deps_final.remove(dep)

for dep in pip_deps:
    if "@" in dep:
        new_dep = dep.split("@")[1].strip()
        idx = pip_deps.index(dep)
        pip_deps.remove(dep)
        pip_deps.insert(idx, new_dep)

conda_deps_to_install_string = "\n  - ".join(conda_deps_final)
pip_deps_to_install_string = "\n    - ".join(pip_deps)
env_spec = f"""name: fiat_{args.profile}

channels:
  - {args.channel}

dependencies:
  - {conda_deps_to_install_string}
"""

if pip_deps:
    env_spec += f"""  - pip:
    - {pip_deps_to_install_string}
"""

with open(Path(MAIN_DIR, args.output), "w") as out:
    out.write(env_spec)
