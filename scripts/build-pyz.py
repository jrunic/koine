import argparse
import os
import shutil
import zipapp

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(REPO, "dist"))
    ns = ap.parse_args()
    os.makedirs(ns.out, exist_ok=True)

    # staging = cópia de src/koine (o zipapp precisa do pacote na raiz do zip)
    stage = os.path.join(ns.out, "_stage")
    if os.path.isdir(stage):
        shutil.rmtree(stage)
    shutil.copytree(os.path.join(REPO, "src", "koine"), os.path.join(stage, "koine"),
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyd", "*.so", "*.dll"))
    # entry point na raiz do zip
    with open(os.path.join(stage, "__main__.py"), "w", encoding="utf-8") as f:
        f.write("from koine.cli import main\nraise SystemExit(main())\n")

    pyz = os.path.join(ns.out, "koine.pyz")
    zipapp.create_archive(stage, target=pyz, interpreter="/usr/bin/env python3")

    # payload solto do vault, AO LADO do pyz (o instalar localiza aqui)
    payload = os.path.join(ns.out, "vault")
    if os.path.isdir(payload):
        shutil.rmtree(payload)
    shutil.copytree(os.path.join(REPO, "vault"), payload,
                    ignore=shutil.ignore_patterns(".gitkeep"))
    shutil.rmtree(stage)
    print(f"pyz: {pyz}")
    print(f"payload: {payload}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
