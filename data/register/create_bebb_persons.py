import os
import glob
import xml.etree.ElementTree as ET

# Eingabe- und Ausgabeordner
input_folder = "/Users/l-gehsul00/Documents/BEBB-Github/BEBB_Persons/XML_files"
output_file = "/Users/l-gehsul00/Documents/BEBB-Github/BEBB_Persons/combined_persList.xml"

# XML-Namespace definieren
namespace = {"tei": "http://www.tei-c.org/ns/1.0"}
ET.register_namespace("", namespace["tei"])  # Registriere Namespace für korrekte Ausgabe

# Root-Element für die kombinierte Datei erstellen
pers_list = ET.Element("persList")

# Alle XML-Dateien im Ordner durchsuchen
xml_files = glob.glob(os.path.join(input_folder, "*.xml"))

for file in xml_files:
    try:
        # XML-Datei parsen
        tree = ET.parse(file)
        root = tree.getroot()

        # Prüfen, ob das Root-Element <person> ist
        if root.tag.endswith("person"):
            # Füge das <person>-Element zur persList hinzu (mit Kopie)
            pers_list.append(root)
    except Exception as e:
        print(f"Fehler beim Verarbeiten von {file}: {e}")

# Ausgabe in Datei speichern
tree = ET.ElementTree(pers_list)
tree.write(output_file, encoding="UTF-8", xml_declaration=True)

print(f"Zusammengeführte Datei gespeichert unter: {output_file}")
