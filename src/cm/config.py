import os

class Config:
    def __init__(self):
        self.corpus_files = {"Phon-SUBTLEX-DE": os.curdir + "/data/corpora/Phon-SUBTLEX-DE.txt"}