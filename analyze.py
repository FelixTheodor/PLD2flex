from src.Config import Config
from src.PLD2flex import PLD2flex
from src.BASConnector import BASConnector
from src.WordObject import WordObject
from os import sys
import requests

c = Config()
c.read_from_file()
c.init_corpus_files()

p = PLD2flex()
b = BASConnector(c.lang, c.calculation)

print("this script works with the same config file as the main program.")
print("these are the current values:")
print("config-path: "+c.path)
print("corpus-path: "+c.corpus_folder)
print("lang: "+c.lang)

print("corpora found in folder:\n")
count = 0
for k in c.corpus_files.keys():
    print(f"{count}:{k}")
    count += 1

i = input("\nplease enter ID of the corpus you want to check: ")
c_name = ""
try:
    c_name = list(c.corpus_files.keys())[int(i)]
except IndexError:
    print("index not valid!")
    sys.exit()
except ValueError:
    print("index is not an int!")
    sys.exit()

print(c_name)

path = c.corpus_files[c_name]
with open(path, encoding = "utf-8", mode = "r") as file:
    content = file.read().split("\n")

corpus = p.read_corpus(content,c.calculation)
if corpus != None and len(corpus) != 0:
    print("corpus initialized.")
else:
    print("corpus is not valid.")
    sys.exit()

targets_str = input("please enter your targets, seperate with comma and no spaces: ")
targets_str = targets_str.replace(",", "\n")

print("retrieving phons for targets...")
phons = ""
try:
    phons = b.get_phons_from_list(targets_str)
except requests.exceptions.RequestException:
    print("connection error!")
    sys.exit()

targets = []
for line in phons.split("\n"):
    if len(line.split(";")) != 2:
        continue
    line = line.split(";")
    wo = WordObject(line[0], p=line[1].replace(" ", ""))
    targets.append(wo)
    print(wo)

print("\nstarting analysis:\n##########################")
for target in targets:
    print("finding matches in corpus for word: " + target.orth)
    for comp in corpus:
        if comp.orth.lower() == target.orth.lower():
            if comp.phon == target.phon:
                print(f"O+P: {comp}")
            else:
                print(f"O : {comp}")
        elif comp.phon == target.phon:
            print(f"P : {comp}")
print("##########################")

print("done.")


