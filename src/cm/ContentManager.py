import sys
import os

from PyQt5.QtWidgets import QApplication, QMainWindow # pylint: disable=no-name-in-module
from PyQt5 import QtCore
from datetime import datetime

from src.cm.config import Config # pylint: disable=import-error
from src.logic.WordObject import WordObject # pylint: disable=import-error
from src.logic.PLD20 import PLD20 # pylint: disable=import-error
from src.logic.BASConnector import BASConnector # pylint: disable=import-error
from src.cqt.GUI import Ui_MainWindow # pylint: disable=import-error

class ContentManager:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = QMainWindow()
        self.ui = Ui_MainWindow()

        self.config = Config()
        self.PLD20 = PLD20()
        self.connector = BASConnector()

        self.divider = "######################"
        # creating file to save the results
        self.fileRes = open(os.curdir + "/data/results/result" + str(datetime.now().isoformat(timespec='minutes')) + ".csv", mode="w", encoding="utf-8")

    # benötigt target und output
    def push_database(self):
        """
        Function reacts to the user clicking on "Compare with Database"
        (Corpus has to be in the same directory in the folder "corpora")
        :return: Function prints the 20 nearest words into the output and the protocol text fields
        """
        t_orth = str(self.ui.target.text().replace(" ", ""))
        if t_orth == "":
            self.error("no data in target")
            return
        
        corpus_name = self.ui.chooseDatabase.currentText()
        # should be done on start-up
        with open(self.config.corpus_files[corpus_name], encoding = "utf-8", mode = "r") as file:
            content = file.read().split("\n")
        corpus = self.PLD20.read_corpus(content)

        self.log("comparing target to " + corpus_name + "\n")

        return self.target_compare(t_orth, corpus)

    def push_input(self):
        """
        Function reacts to the user clicking on "Compare with file/list" calculates the levenshtein-distances and prints the output
        :return: levenshtein-distances
        """
        if (self.ui.input.toPlainText() == ""):
            self.error("no list or file in input")
            return

        input_mode = self.ui.fileType.currentText()
        input_text = self.ui.input.toPlainText()
        target_text = self.ui.target.text()
        target_provided = target_text != ""
        path_provided = "file://" in str(input_text)

        # for two columns, the process works differently
        if input_mode == "Two columns":
            if target_provided:
                self.error("comparing two columns is not possible with given target")
                return
            return self.columns_compare(path_provided, input_text)
        elif input_mode == "One column":
            return self.one_compare(path_provided, input_text, target_text, target_provided) 
        else:
            self.log("something went wrong, invalid input mode!")
            return

    def push_close(self):
        """
        Function closes the running process
        """
        self.fileRes.close()
        sys.exit()

    def push_help(self):
        """
        No function yet: Function should open the User Manual
        """
        self.log("Not available")

    def one_compare(self, path_provided, input_text, target_text, target_provided):
        for line in input_text.split("\n"):
            if " " in line or "\t" in line:
                self.error("too many columns in input")
                return
        if path_provided:
            path = input_text.replace("file://", "").replace("\n", "")
            to_log = "file " + path.split("/")[-1]
            if os.path.isfile(path):
                f = open(path)
                for line in f.readlines():
                    if " " in line or "\t" in line:
                        self.error("too many columns in input file")
                        return
                f.close()
                phon_list = self.connector.get_phons_from_file(path)
            else:
                self.error("cannot read file: " + path)
                return
        else:
            to_log = "the provided list"
            phon_list = self.connector.get_phons_from_list(input_text)
        corpus = self.PLD20.read_corpus(phon_list.split("\n"))

        if len(corpus) < 20:
            self.log("WARN: these are less than 20 words!")
        
        if target_provided:
            self.log("compare target to " + to_log + ":\n")
            t_orth = target_text.replace(" ", "")
            return self.target_compare(t_orth, corpus)
        else:
            self.log("cross compare " + to_log + ":\n")
            return self.cross_compare(corpus)

    def cross_compare(self, corpus):
        if len(corpus) < 21:
            self.error("cross compare only possible with more than 20 entrys")
            return
        mean, corpus = self.PLD20.compare_corpus(corpus)
        for entry in corpus:
            self.log(entry.orth + " mean:\t" + str(entry.levi))
        self.print_results(mean, corpus)
    
    def target_compare(self, t_orth, corpus):
        t_phon = self.connector.get_single_phon(t_orth)
        target = WordObject(t_orth, p=t_phon)
        # compare target with corpus
        mean, corpus = self.PLD20.compare_to_target(target, corpus)
        
        self.log("tested target:\t" + str(target))
        self.print_results(mean, corpus)
    
    def columns_compare(self, path_provided, input_text):
        msgs = []
        lines = []

        if path_provided:
            path = input_text.replace("file://", "").replace("\n", "")
            if os.path.isfile(path): 
                self.log("comparing columns in " + path.split("/")[-1] +":\n")
                f = open(path)
                for line in f.readlines():
                    lines.append(line.replace("\n", ""))
                f.close()
            else:
                self.error("file not found: " + path)
                return    
        else:
            self.log("comparing columns in input field" + ":\n")
            for line in input_text.split("\n"):
                lines.append(line)

        for line in lines:
            if line in ["\n", "", " "]:
                continue
            pair = line.split("\t") if "\t" in line else line.split(" ") 
            if len(pair) != 2:
                self.error("not every line has two columns")
                return
            p1 = self.connector.get_single_phon(pair[0])
            p2 = self.connector.get_single_phon(pair[1])
            levi = self.PLD20.levenshtein(p1, p2)
            msgs.append(f"{pair[0]}/{p1}\t{pair[1]}/{p2}\t{levi}")

        self.log(f"count corpus:\t{len(msgs)}")
        self.log(self.divider)
        for msg in msgs:
            #self.log(msg)
            self.save(msg)
        self.log(self.divider)

    def log(self, msg):
        """
        The function log(msg) prints a string into the protocol field
        :param string: Output
        """
        self.ui.protocol.insertPlainText(msg + "\n")
    
    def save(self, msg):
        """
        The function log(msg) prints a string into the protocol field
        :param string: Output
        """
        self.ui.output.insertPlainText(msg + "\n")
        self.fileRes.write(msg + "\n")
    
    def error(self, msg):
        self.log("ERROR: " + msg)
        self.log(self.divider)
        self.log(self.divider)

    def print_results(self, mean, corpus):
        """
        The function save(string) prints a string into the result filed and file
        :param string: Output
        """
        self.log("mean-distance:\t" + str(mean))
        self.log(f"count corpus: \t{len(corpus)}")
        self.log(self.divider)

        if len(corpus) > 20:
            corpus = corpus[0:20]

        for entry in corpus:
            #self.log(str(entry))
            self.save(str(entry))
        
        self.log(self.divider)


    def connectSeq(self):
        """
        Function connects function with the developed GUI
        :return:
        """
        self.ui.setupUi(self.window)

        for corpus in self.config.corpus_files.keys():
            self.ui.chooseDatabase.addItem(corpus)
    
        self.ui.compareList.clicked.connect(self.push_input)
        self.ui.compareCel.clicked.connect(self.push_database)
        self.ui.actionClose.triggered.connect(self.push_close)
        self.ui.actionHelp.triggered.connect(self.push_help)

        self.window.show()
        sys.exit(self.app.exec_())
        self.fileRes.close()