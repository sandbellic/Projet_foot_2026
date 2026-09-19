from pathlib import Path
import shutil
import subprocess
import sys
import tomllib

from matplotlib.pylab import rint

#---------------------------------------------------------------------------
#Configuration
#---------------------------------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parent.parent

SRC_DIR = ROOT_DIR / "src"
MAIN_FILE = SRC_DIR / "projet_foot" / "main.py"

DIST_DIR = ROOT_DIR / "dist"
BUILD_DIR = ROOT_DIR / "build"

INSTALLER_DIR = ROOT_DIR / "installer"
ISS_FILE = INSTALLER_DIR / "projet-foot.iss"

PYPROJECT_FILE = ROOT_DIR / "pyproject.toml"       #va servir à récupérer le numéro de version qu’on ajoutera à l’exécutable
#INNO_SETUP = Path(r"C:\Users\sandb\AppData\Local\Programs\Inno Setup 7\ISCC.exe")

#---------------------------------------------------------------------------
# Gestion des versions
#tomllib ?
#C'est le lecteur TOML intégré à Python depuis Python 3.11.
#Comme ton projet nécessite : python = ">=3.13", on peut donc l'utiliser directement, sans #installer de bibliothèque supplémentaire.
# la version est dans le « chapitre » project
#---------------------------------------------------------------------------
def get_version() -> str:
#"""on Récupère la version depuis pyproject.toml."""

    with PYPROJECT_FILE.open("rb") as file:
        pyproject = tomllib.load(file)

    try:
        version = pyproject["project"]["version"]
    except KeyError:
        print("ERREUR : impossible de trouver project.version dans pyproject.toml")
        sys.exit(1)

    return version

#---------------------------------------------------------------------------
# Recherche du répertoire d'installation d'Inno Setup, il peut être installer à
#différents endroits, et 2 versions possibles, on teste les chemins potentiels
#---------------------------------------------------------------------------
def find_inno_setup() -> Path:
#"""Recherche automatiquement ISCC.exe."""

    possible_paths = [
        Path(r"C:\Program Files\Inno Setup 7\ISCC.exe"),
        Path(r"C:\Program Files (x86)\Inno Setup 7\ISCC.exe"),
        Path.home() / r"AppData\Local\Programs\Inno Setup 7\ISCC.exe",

        Path(r"C:\Program Files\Inno Setup 6\ISCC.exe"),
        Path(r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"),
        Path.home() / r"AppData\Local\Programs\Inno Setup 6\ISCC.exe",
    ]

    for path in possible_paths:
        if path.exists():
            return path

    print()
    print("ERREUR : impossible de trouver ISCC.exe.")
    print()
    print("Vérifie que Inno Setup est installé.")
    print()
    print("Emplacements recherchés :")

    for path in possible_paths:
        print(f"  - {path}")

    sys.exit(1)

#---------------------------------------------------------------------------
#Fonctions utilitaires
#---------------------------------------------------------------------------

def run_command(command: list[str]) -> None:
#"""Execute une commande et arrête le build en cas d'erreur."""
    print()
    print(">>>", " ".join(command))
    print()

    result = subprocess.run(command)

    if result.returncode != 0:
        print(f"Erreur : la commande a échoué ({result.returncode}).")
        sys.exit(result.returncode)

def clean() -> None:
#"""Supprime les anciens fichiers de build."""

    print("=== Nettoyage ===")

    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)

    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)

    DIST_DIR.mkdir(parents=True)

#---------------------------------------------------------------------------
#PyInstaller
##---------------------------------------------------------------------------

def build_executable() -> None:
#"""Construit l'exécutable Windows avec PyInstaller."""

    print("=== Construction de l'exécutable ===")

    command = [
    "uv",
    "run",
    "pyinstaller",
    "--onefile",
    "--name",
    "projet-foot",
    "--distpath",
    str(DIST_DIR),
    "--workpath",
    str(BUILD_DIR),
    str(MAIN_FILE),
]

    run_command(command)

#---------------------------------------------------------------------------
#Inno Setup
#dans l'installateur, la version est toujours transmise à Inno Setup par :
#f"/DMyAppVersion={version}"

#---------------------------------------------------------------------------

def build_installer(version: str) -> None:
#"""Construit l'installateur Windows avec Inno Setup."""

    inno_setup = find_inno_setup()

    print(f"Inno Setup trouvé : {inno_setup}")

    command = [
        str(inno_setup),
        f"/DMyAppVersion={sys.version}",
        str(ISS_FILE),
    ]

    run_command(command)

    # Inno Setup vient de créer ProjetFoot-Setup.exe
    generated_installer = DIST_DIR / "ProjetFoot-Setup.exe"
    final_installer = DIST_DIR / f"ProjetFoot-Setup-{version}.exe"

    if not generated_installer.exists():
        print()
        print("ERREUR : l'installateur Inno Setup n'a pas été généré.")
        sys.exit(1)

    generated_installer.rename(final_installer)

    print(f"Installateur final : {final_installer}")

#---------------------------------------------------------------------------
#Main
#---------------------------------------------------------------------------

def main() -> None:
    print()
    print("==============================")
    print(" BUILD PROJET FOOT")
    print("==============================")

    version = get_version()

    print(f"Version : {version}")
    print()

    clean()
    build_executable()
    build_installer(version)

    print()
    print("==============================")
    print("  BUILD TERMINE")
    print("==============================")
    print()
    print(f"Version       : {version}")
    print(f"Installateur  : {DIST_DIR / f'ProjetFoot-Setup-{sys.version}.exe'}")
    print()

if __name__ == "__main__":
    main()
