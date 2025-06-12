# -*- coding: utf-8 -*-
"""
Created on Sat Jul 1 20:38:06 2023
@author: marga
"""

import os
import re

# Korrigierter Pfad zur entities.txt-Datei
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

# Funktion zum Bearbeiten einer Datei
def process_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Entfernt Whitespace zwischen <pc>-Trennstrich und <lb break="no"/>
    pattern = r'<pc type="hyphenation">-</pc>\s+<lb break="no"/>'
    modified_content = re.sub(pattern, r'<pc type="hyphenation">-</pc><lb break="no"/>', content)

    # NEU: Entfernt Leerzeichen direkt vor <lb break="no"/> auch ohne <pc>
    pattern2 = r'(\S)\s+<lb break="no"/>'
    modified_content = re.sub(pattern2, r'\1<lb break="no"/>', modified_content)

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

    # Erster Teil des Skripts
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
                f.close()
                output_file = open(os.path.join(dirName, fname), encoding='utf-8', mode='w')
                output_file.write(outfile_content)
                output_file.close()

    print(files)

    # Zweiter Teil des Skripts
    process_files_in_folder(folder_path)

if __name__ == "__main__":
    main()
