"""Create a synthetic two-page PDF for a local parsing exercise."""

from pathlib import Path

import pymupdf


def main() -> None:
    destination = Path(__file__).resolve().parents[2] / ".runtime" / "cv-synthetique.pdf"
    destination.parent.mkdir(parents=True, exist_ok=True)
    with pymupdf.open() as document:
        page = document.new_page()
        page.insert_text((72, 72), "CV SYNTHETIQUE - AUCUNE PERSONNE REELLE", fontsize=14)
        page.insert_text((72, 120), "Profil fictif\nEtudiant ingénieur\nPython, SQL, FastAPI")
        page = document.new_page()
        page.insert_text((72, 72), "PROJETS\nAPI de catalogue avec FastAPI\nTests avec Pytest")
        # Exclusive creation prevents overwriting an existing document.
        with destination.open("xb") as output:
            output.write(document.tobytes())
    print(destination)


if __name__ == "__main__":
    main()
