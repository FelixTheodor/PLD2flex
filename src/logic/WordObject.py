class WordObject:
    def __init__(self, orth, phon="", levi=""):
        self.orth = orth
        self.phon = phon
        self.levi = levi
    
    def __repr__(self):
        return f"{self.orth}\t{self.phon}\t{self.levi}"
