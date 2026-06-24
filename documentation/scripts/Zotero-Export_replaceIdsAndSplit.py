"""
Author: Research and Infrastructure Support, University of Basel
Date created: 15/02/2023
Python Version: 3.9
Description:
Take the XML/TEI export from Zotero and replace the xml:id attribute with a new
value based on the Zotero item id in @corresp. Then split the file into single
biblStruct files, one per bibliographic entry.

Additionally, repair common TEI ordering issues in <monogr> elements from the
Zotero export, especially cases where:
- <author> appears after <extent> or <imprint>
- <extent> appears before <imprint>

License: GPLv3
"""

from xml.etree import ElementTree as ET
from pathlib import Path

TEI_NS = "http://www.tei-c.org/ns/1.0"
XML_NS = "http://www.w3.org/XML/1998/namespace"
NS = {"tei": TEI_NS}

# Eingabedatei
INPUT_FILE = Path("BEBB.xml")

# Zielordner
OUTPUT_DIR = Path(
    "/Users/l-gehsul00/Documents/BEBB-Github/BEBB_Data_WIP/data/register/bibliography"
)


def localname(tag):
    """Gibt den lokalen Namen eines XML-Tags ohne Namespace zurück."""
    return tag.split("}", 1)[-1] if "}" in tag else tag


def repair_monogr_order(root):
    """
    Bringt direkte Kindelemente von <monogr> in eine stabile, für TEI-validierung
    geeignete Reihenfolge.

    Diese Funktion ist bewusst pragmatisch gehalten und zielt auf typische
    Zotero-Export-Probleme ab, nicht auf eine vollständige Modellierung aller
    möglichen TEI-Sonderfälle.
    """
    preferred_order = {
        "author": 10,
        "editor": 20,
        "respStmt": 30,
        "title": 40,
        "idno": 50,
        "edition": 60,
        "imprint": 70,
        "extent": 80,
        "biblScope": 90,
        "note": 100,
    }

    for monogr in root.findall(".//tei:monogr", NS):
        children = list(monogr)

        if len(children) < 2:
            continue

        indexed_children = list(enumerate(children))
        sorted_children = sorted(
            indexed_children,
            key=lambda item: (
                preferred_order.get(localname(item[1].tag), 999),
                item[0],  # erhält Originalreihenfolge bei gleichem Rang
            ),
        )

        # Nur umbauen, wenn sich tatsächlich etwas ändert
        original_tags = [child.tag for child in children]
        new_tags = [child.tag for _, child in sorted_children]

        if original_tags != new_tags:
            for child in children:
                monogr.remove(child)

            for _, child in sorted_children:
                monogr.append(child)


def replace_ids_and_repair(infile):
    """
    Parst die Zotero-Exportdatei, repariert problematische <monogr>-Reihenfolgen
    und setzt für jedes <biblStruct> ein neues xml:id im Format biblio_<Zotero-ID>.
    """
    ET.register_namespace("", TEI_NS)
    ET.register_namespace("xml", XML_NS)

    tree = ET.parse(infile)
    root = tree.getroot()

    repair_monogr_order(root)

    for bs in root.findall(".//tei:biblStruct", NS):
        corresp = bs.attrib.get("corresp")
        if not corresp:
            print("Warnung: biblStruct ohne @corresp übersprungen")
            continue

        zotero_id = corresp.rstrip("/").split("/")[-1]
        new_xml_id = f"biblio_{zotero_id}"

        # vorhandenes xml:id entfernen
        bs.attrib.pop(f"{{{XML_NS}}}id", None)

        # korrekt namespaced wieder setzen
        bs.set(f"{{{XML_NS}}}id", new_xml_id)

    return tree


def split_into_single_bibl_items(tree):
    """
    Schreibt jedes <biblStruct> als eigene XML-Datei in den Zielordner.
    Der Dateiname entspricht dem xml:id.
    """
    root = tree.getroot()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    count = 0

    for bs in root.findall(".//tei:biblStruct", NS):
        xml_id = bs.attrib.get(f"{{{XML_NS}}}id")
        if not xml_id:
            print("Warnung: biblStruct ohne xml:id übersprungen")
            continue

        outfile = OUTPUT_DIR / f"{xml_id}.xml"

        with open(outfile, "wb") as f:
            ET.ElementTree(bs).write(
                f,
                xml_declaration=True,
                encoding="utf-8",
                method="xml",
            )

        count += 1

    print(f"Fertig. {count} Dateien wurden nach {OUTPUT_DIR} geschrieben.")


def main():
    tree = replace_ids_and_repair(INPUT_FILE)
    split_into_single_bibl_items(tree)


if __name__ == "__main__":
    main()