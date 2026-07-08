import argparse
import os
import shutil
import zipapp

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _versao() -> str:
    import re
    with open(os.path.join(REPO, "src", "koine", "_version.py"), encoding="utf-8") as f:
        return re.search(r'__version__ = "([^"]+)"', f.read()).group(1)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(REPO, "dist"))
    ap.add_argument("--zip", action="store_true",
                    help="também monta dist/koine-<versao>.zip (pyz + vault/ na raiz)")
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
    if ns.zip:
        import zipfile
        zpath = os.path.join(ns.out, f"koine-{_versao()}.zip")
        if os.path.exists(zpath):
            os.remove(zpath)
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
            z.write(pyz, "koine.pyz")
            for raiz, _, arqs in os.walk(payload):
                for a in arqs:
                    p = os.path.join(raiz, a)
                    z.write(p, "vault/" + os.path.relpath(p, payload).replace(os.sep, "/"))
        print(f"zip: {zpath}")
    print(f"pyz: {pyz}")
    print(f"payload: {payload}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
