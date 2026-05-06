#!/usr/bin/env python3
from pathlib import Path
import xml.etree.ElementTree as ET
import sys

# Pfade anpassen, falls nötig
LETTERS_DIR = Path("/Users/l-gehsul00/Documents/BEBB-Github/BEBB_Data_Test/data/edited_texts/letters")
FIGURES_DIR = Path("/Users/l-gehsul00/Documents/BEBB-Github/BEBB_Data_Test/data/images/figures")

OUTPUT_FILE = Path("missing_facs.txt")

def collect_image_filenames(figures_dir: Path) -> set[str]:
    """Sammelt alle Dateinamen (ohne Pfad) im figures-Verzeichnis (rekursiv)."""
    image_files = set()
    for p in figures_dir.rglob("*"):
        if p.is_file():
            image_files.add(p.name)
    return image_files

def find_missing_facs_references(letters_dir: Path, image_filenames: set[str]) -> list[tuple[Path, str, str]]:
    """
    Durchsucht alle XML-Dateien in letters_dir und findet figure/facs,
    deren referenzierte Bilddatei nicht existiert.
    
    Rückgabe: Liste von Tupeln (xml_path, facs_value, filename)
    """
    missing = []

    for xml_path in letters_dir.rglob("*.xml"):
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
        except ET.ParseError as e:
            print(f"Fehler beim Parsen von {xml_path}: {e}", file=sys.stderr)
            continue

        for elem in root.iter():
            if elem.tag.endswith("figure"):
                facs_val = elem.get("facs")
                if not facs_val:
                    continue

                filename = Path(facs_val).name

                if filename and filename not in image_filenames:
                    missing.append((xml_path, facs_val, filename))

    return missing

def write_missing_to_file(missing_refs, output_file: Path):
    with open(output_file, "w", encoding="utf-8") as f:
        if not missing_refs:
            f.write("Keine fehlenden Bildreferenzen gefunden.\n")
            return

        f.write("Fehlende Bildreferenzen:\n\n")
        for xml_path, facs_val, filename in missing_refs:
            f.write(f"XML-Datei : {xml_path}\n")
            f.write(f"facs      : {facs_val}\n")
            f.write(f"Dateiname : {filename}\n\n")

        f.write(f"Summe fehlender Referenzen: {len(missing_refs)}\n")

def main():
    if not LETTERS_DIR.exists():
        print(f"Letters-Verzeichnis existiert nicht: {LETTERS_DIR}", file=sys.stderr)
        sys.exit(1)
    if not FIGURES_DIR.exists():
        print(f"Figures-Verzeichnis existiert nicht: {FIGURES_DIR}", file=sys.stderr)
        sys.exit(1)

    image_filenames = collect_image_filenames(FIGURES_DIR)
    missing_refs = find_missing_facs_references(LETTERS_DIR, image_filenames)

    # Ausgabe auf der Konsole
    if not missing_refs:
        print("Keine fehlenden Bildreferenzen gefunden ✔️")
    else:
        print("Fehlende Bilddateien für facs-Attribute:\n")
        for xml_path, facs_val, filename in missing_refs:
            print(f"- XML-Datei : {xml_path}")
            print(f"  facs      : {facs_val}")
            print(f"  Dateiname : {filename}\n")
        print(f"Summe fehlender Referenzen: {len(missing_refs)}")

    # In Datei schreiben
    write_missing_to_file(missing_refs, OUTPUT_FILE)
    print(f"\nErgebnis wurde auch geschrieben nach: {OUTPUT_FILE.resolve()}")

if __name__ == "__main__":
    main()
