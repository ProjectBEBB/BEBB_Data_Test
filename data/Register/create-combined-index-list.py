import os
from lxml import etree

# Funktion zur Erstellung der kombinierten TEI-Datei mit allen Indizes
def create_combined_tei(output_file, input_folders):
    # XML-Namespace für das Ergebnisdokument
    namespace = "http://www.tei-c.org/ns/1.0"
    xi_namespace = "http://www.w3.org/2001/XInclude"
    xml_namespace = "http://www.w3.org/XML/1998/namespace"

    # XML-Header und Model-Definition erstellen
    xml_header = (
        b'<?xml version="1.0" encoding="UTF-8"?>\n'
        b'<?xml-model href="https://raw.githubusercontent.com/ProjectBEBB/BEBB_Data_Prod/refs/heads/main/Documentation/Technical_documentation/ODD_XMLschemas/BEBB_schema.rng" '
        b'type="application/xml" schematypens="http://relaxng.org/ns/structure/1.0"?>\n'
    )

    # TEI-Root-Element erstellen
    tei_root = etree.Element("TEI", xmlns=namespace)
    tei_root.set(f"{{{xml_namespace}}}id", "combined-indices")

    # teiHeader-Element erstellen
    tei_header = etree.SubElement(tei_root, "teiHeader")
    file_desc = etree.SubElement(tei_header, "fileDesc")

    # titleStmt hinzufügen
    title_stmt = etree.SubElement(file_desc, "titleStmt")
    etree.SubElement(title_stmt, "title")  # Leeres <title/>-Element

    # publicationStmt hinzufügen
    publication_stmt = etree.SubElement(file_desc, "publicationStmt")
    etree.SubElement(publication_stmt, "publisher").text = "Bernoulli-Euler-Zentrum"
    etree.SubElement(publication_stmt, "pubPlace").text = "Basel"
    availability = etree.SubElement(publication_stmt, "availability")
    etree.SubElement(availability, "licence", target="https://creativecommons.org/licenses/by/4.0/deed.de").text = "(CC BY 4.0)"

    # sourceDesc hinzufügen
    source_desc = etree.SubElement(file_desc, "sourceDesc")
    etree.SubElement(source_desc, "p").text = "Born digital"

    # text-Element erstellen
    text = etree.SubElement(tei_root, "text")
    body = etree.SubElement(text, "body")

    # Listen hinzufügen
    for list_type, folder in input_folders.items():
        list_element = etree.SubElement(body, list_type)

        # Alle Dateien im jeweiligen Ordner durchgehen
        for filename in sorted(os.listdir(folder)):
            if filename.endswith(".xml"):
                file_path = os.path.join(folder, filename)
                etree.SubElement(list_element, f"{{{xi_namespace}}}include", href=file_path)

    # XML-Baum erstellen
    xml_tree = etree.ElementTree(tei_root)

    # XML-Datei schreiben
    with open(output_file, "wb") as file:
        file.write(xml_header)  # Header mit Schema hinzufügen
        xml_tree.write(file, pretty_print=True, xml_declaration=False, encoding="UTF-8")

    print(f"Kombinierte Datei '{output_file}' wurde erfolgreich erstellt.")

# Basispfad für die Register
base_path = os.path.expanduser("~/Documents/BEBB-Github/BEBB_Data_Test/data/Register")

# Ordner und Listentypen definieren
input_folders = {
    "listPlace": os.path.join(base_path, "Places"),
    "listPerson": os.path.join(base_path, "Persons"),
    "listBibl": os.path.join(base_path, "Bibliography"),
    "listOrg": os.path.join(base_path, "Organisations")
}

# Kombinierte Datei erstellen
create_combined_tei(os.path.join(base_path, "combined-indices.xml"), input_folders)
