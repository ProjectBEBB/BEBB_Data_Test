
import os

a = open("output.txt", "a")
for path, subdirs, files in os.walk(r'/Users/l-gehsul00/Documents/BEBB-Github/Ueberarbeitung_Editionsrichtlinien/teiCorpus/index/persons'):
   for filename in files:
     f = os.path.join(path, filename)
     a.write(str(f) + os.linesep) 