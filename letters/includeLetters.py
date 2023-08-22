import os

output_file = "output.txt"
corpus_directory = '/Users/l-gehsul00/Documents/BEBB-Github/Ueberarbeitung_Editionsrichtlinien/teiCorpus/letters'

with open(output_file, "a") as a:
    for path, subdirs, files in os.walk(corpus_directory):
        for filename in files:
            if filename.endswith(".xml"):
                f = os.path.join(path, filename)
                f_relative = f.split("letters/")[1]  # Entferne alles vor "letters/"
                f_relative_with_letters = "letters/" + f_relative  # Füge "letters/" wieder hinzu
                line = f'<include xmlns="http://www.w3.org/2001/XInclude" href="{f_relative_with_letters}"/>'
                a.write(line + os.linesep)