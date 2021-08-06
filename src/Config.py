import os

class Config:
    def __init__(self):
        self.corpus_folder = {}
        self.corpus_files = {}
        self.lang = "deu-DE"
        self.neighbours = 20
        self.result_path = os.getcwd() + "/data/results/"
        self.log_path = os.getcwd() + "/data/logs/"
        self.path = os.getcwd() + "/config.txt"
        self.read_from_file()
        self.init_corpus_files()
        
    def read_from_file(self):
        if not os.path.isfile(self.path):
            return
        f = open(self.path)
        for line in f.readlines():
            spline = line.replace("\n", "").split("=")
            if len(spline) == 2:
                cat, val = spline
                if cat == "DBFOLDER":
                    self.corpus_folder = val
                elif cat == "LANGUAGE":
                    self.lang = val
                elif cat == "NEIGHBOURS":
                    try:
                        self.neighbours = int(val)
                    except ValueError:
                        print("value for neighbours is not an int!")
                elif cat == "RESULTS_PATH":
                    self.result_path = val
                elif cat == "LOGS_PATH":
                    self.log_path = val
        f.close()
    
    def init_corpus_files(self):
        if len(self.corpus_folder) == 0 or not os.path.isdir(self.corpus_folder):
            return
        self.corpus_files = {}
        for name in os.listdir(self.corpus_folder):
            self.corpus_files[name.split(".")[0]] = self.corpus_folder + "/" + name
