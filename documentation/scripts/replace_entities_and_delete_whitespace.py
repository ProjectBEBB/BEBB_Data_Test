# -*- coding: utf-8 -*-
"""
Created on Sat Jul 1 20:38:06 2023
@author: marga
"""

import os
import re
import urllib.request
import ssl

# Unsichere SSL-Verbindung erlauben (Umgehung für Zertifikatsfehler)
ssl._create_default_https_context = ssl._create_unverified_context

entities_dict = {}
url = 'https://raw.githubusercontent.com/ProjectBEBB/BEBB_Data_Prod/main/Documentation/Technical_documentation/ODD_XMLschemas/entities.txt'

# Entitäten-Datei direkt von GitHub laden
response = urllib.request.urlopen(url)
lines = [line.decode('utf-8').strip() for line in response.readlines()]

for line in lines:
    if line.startswith('<!ENTITY') and '<choice>' in line:
        line = line.replace('<!ENTITY ', '')
        choice_start_index = line.index('<choice>')
        entity_str = line[:choice_start_index - 2]
        entity_str = '&' + entity_str + ';'
        choice_str = line[choice_start_index:-3]
        entities_dict[entity_str] = choice_str

doctype_str_old = '<!DOCTYPE TEI [<!ENTITY % entities SYSTEM "../../entities.txt"> %entities; ]>'
doctype_str_new = ''


# <del/> durch <del><gap/></del> ersetzen
def replace_del_tag(content):
    return content.replace('<del/>', '<del><gap/></del>')


# Funktion zum Bearbeiten einer Datei
def process_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    modified_content = content

    # 1. Trennzeichen am Zeilenende:
    #
    # d’admi<pc type="hyphenation">-</pc>
    #   <lb break="no"/>ration
    #
    # wird zu:
    #
    # d’admi<pc type="hyphenation">-</pc><lb break="no"/>ration
    pattern_1 = r'(<pc type="hyphenation">-</pc>)\s+(<lb break="no"/>)'
    modified_content = re.sub(pattern_1, r'\1\2', modified_content)

    # 1b. Leeres pc-Element am Zeilenende:
    #
    # d’admi<pc type="hyphenation"></pc>
    #   <lb break="no"/>ration
    #
    # wird zu:
    #
    # d’admi<pc type="hyphenation"></pc><lb break="no"/>ration
    #
    # Dieser Fall wird nur vor <lb break="no"/> behandelt,
    # nicht nach <lb break="no"/>.
    pattern_1b = r'(<pc type="hyphenation"></pc>)\s+(<lb break="no"/>)'
    modified_content = re.sub(pattern_1b, r'\1\2', modified_content)

    # 2. Trennzeichen am Zeilenbeginn:
    #
    # d’admi<lb break="no"/>
    #   <pc type="hyphenation">-</pc>ration
    #
    # wird zu:
    #
    # d’admi<lb break="no"/><pc type="hyphenation">-</pc>ration
    pattern_2 = r'(<lb break="no"/>)\s+(<pc type="hyphenation">-</pc>)'
    modified_content = re.sub(pattern_2, r'\1\2', modified_content)

    # 3. Fall mit Trennzeichen am Zeilenende und am Zeilenbeginn:
    #
    # d’admi<pc type="hyphenation">-</pc>
    #   <lb break="no"/>
    #   <pc type="hyphenation">-</pc>ration
    #
    # wird durch pattern_1 und pattern_2 automatisch zu:
    #
    # d’admi<pc type="hyphenation">-</pc><lb break="no"/><pc type="hyphenation">-</pc>ration
    #
    # Deshalb ist kein drittes separates Pattern nötig.

    # <del/> ersetzen
    modified_content = replace_del_tag(modified_content)

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(modified_content)


# Funktion zum Bearbeiten von Dateien in Ordnern und Unterordnern
def process_files_in_folder(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)

        if os.path.isfile(file_path) and filename.endswith(".xml"):
            process_file(file_path)
            print(f"Datei '{filename}' wurde erfolgreich bearbeitet.")

        elif os.path.isdir(file_path):
            process_files_in_folder(file_path)


def main():
    # Angepasster Pfad zum Ordner mit den XML-Dateien
    folder_path = '/Users/l-gehsul00/Documents/BEBB-Github/BEBB_Data_Test/data/edited_texts'

    # Erster Teil des Skripts:
    # DOCTYPE entfernen und Entitäten ersetzen
    files = []
    allowed_extensions = ['.xml', '.XML']

    for dirName, subdirList, fileList in os.walk(folder_path):
        for fname in fileList:
            root, extension = os.path.splitext(fname)

            if extension.lower() in allowed_extensions:
                print(fname)
                entry = [dirName, fname]
                files.append(entry)

                outfile_content = ''

                with open(os.path.join(dirName, fname), encoding='utf-8', mode='r') as f:
                    for line in f:
                        if doctype_str_old in line:
                            line = line.replace(doctype_str_old, doctype_str_new)

                        for key in entities_dict.keys():
                            if key in line:
                                line = line.replace(key, entities_dict[key])

                        outfile_content = outfile_content + line

                with open(os.path.join(dirName, fname), encoding='utf-8', mode='w') as output_file:
                    output_file.write(outfile_content)

    print(files)

    # Zweiter Teil des Skripts:
    # Whitespaces zwischen hyphenation-pc und lb break="no" bereinigen
    process_files_in_folder(folder_path)


if __name__ == "__main__":
    main()