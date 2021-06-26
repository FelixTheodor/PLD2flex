class WordObject:
    def __init__(self, o, p=str(), l=str(), cl=list()):
        self.orth = o
        self.phon = p
        self.levi = l
        self.comp_levis = cl
    
    def __repr__(self):
        r_str = ""
        if len(self.comp_levis) != 0:
            for key in self.comp_levis:
                rep = f"{self.orth}/{self.phon}\t{key.orth}/{key.phon}\t{key.levi}\n"
                r_str += rep
        else:
            r_str = f"{self.orth}\t{self.phon}\t{self.levi}"
        return r_str
    
    def copy(self):
        return WordObject(self.orth, p=self.phon, l=self.levi, cl=[])