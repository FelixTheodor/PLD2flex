class CommandData:
    """
    convenient way to store and print all the data of a command to the application
    """
    def __init__(self):
        self.corpus = None
        self.target = None
        self.pld20 = None
        self.sd = None
        self.method = "None"
        self.err = "None"
        self.warn = "None"
        self.input = "None"
        self.path_word = "None"
        self.msgs = None
    
    def save(self, msg):
        if "\n" not in msg and self.target != None:
            return str(self.target) + msg + f"\t{self.method}\t{self.input}\t{self.path_word}"
        elif "\n" not in msg:
            return msg + f"\t{self.method}\t{self.input}\t{self.path_word}"
        else:
            r_str = ""
            for line in msg.split("\n"):
                r_str += line + f"\t{self.method}\t{self.input}\t{self.path_word}\n"
            return r_str
    
    def log(self):
        return f"{self.method}\t{self.input}\t{self.path_word}\t{self.pld20}\t{self.sd}\t{self.err}\t{self.warn}\t"