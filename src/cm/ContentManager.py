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
        # creating files to save the results
        self.filePro = open(os.curdir + "/data/protocols/protocol_" + str(datetime.now().isoformat(timespec='minutes')) + ".csv", mode="w", encoding="utf-8")
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
            self.log("no target specified (...)")
            return
        
        corpus_name = self.ui.chooseDatabase.currentText()
        # should be done on start-up
        with open(self.config.corpus_files[corpus_name], encoding = "utf-8", mode = "r") as file:
            content = file.read().split("\n")
        corpus = self.PLD20.read_corpus(content)

        return self.target_compare(t_orth, corpus)

    def push_file(self):
        """
        Function reacts to the user clicking on "Compare with file/list" calculates the levenshtein-distances and prints the output
        :return: levenshtein-distances
        """
        if (self.ui.input.toPlainText() == ""):
            self.log("No list or file provided.")
            return

        file_mode = self.ui.fileType.currentText()
        input_text = self.ui.input.toPlainText()
        target_text = self.ui.target.text()
        target_provided = target_text != ""
        path_provided = "file://" in str(input_text)

        if path_provided and file_mode == "Two columns":
            self.log("comparing columns in " + input_text +":\n")
            return self.columns_compare(input_text.replace("file://", ""))
        
        # create phonlist
        if path_provided and file_mode == "One column":
            to_log = "file " + input_text
            phon_list = self.connector.get_phons_from_file(input_text.replace("file://", ""))
        else:
            to_log = "the provided list"
            phon_list = self.connector.get_phons_from_list(input_text)

        corpus = self.PLD20.read_corpus(phon_list.split("\n"))
        
        if target_provided:
            self.log("compare target to " + to_log + ":\n")
            t_orth = target_text.replace(" ", "")
            return self.target_compare(t_orth, corpus)
        
        self.log("cross compare " + to_log + ":\n")
        return self.cross_compare(corpus)

    def push_close(self):
        """
        Function closes the running process
        """
        self.filePro.close()
        sys.exit()

    def push_help(self):
        """
        No function yet: Function should open the User Manual
        """
        self.log("Not available")

    def cross_compare(self, corpus):
        result = self.PLD20.compare_corpus(corpus)
        self.log(str(result))
    
    def target_compare(self, t_orth, corpus):
        t_phon = self.connector.get_single_phon(t_orth)
        target = WordObject(t_orth, phon=t_phon)
        # compare target with corpus
        mean, corpus = self.PLD20.compare_to_target(target, corpus)
        
        self.log("mean: " + str(mean))
        self.log(self.divider)

        for entry in corpus:
            self.log(str(entry))
        
        self.log(self.divider)
    
    def columns_compare(self, path):
        pass

    def log(self, msg):
        """
        The function log(msg) prints a string into the protocol field
        :param string: Output
        """
        self.ui.protocol.insertPlainText(msg + "\n")

    def save(self, string):
        """
        The function save(string) prints a string into the result filed and file
        :param string: Output
        """
        print(string + "\nTarget: ;" + self.ui.target.text() + "\nInput: ;" + " ;".join(self.ui.input.toPlainText().split("\n")) + "\n", file= self.fileRes)

    def connectSeq(self):
        """
        Function connects function with the developed GUI
        :return:
        """
        self.ui.setupUi(self.window)

        for corpus in self.config.corpus_files.keys():
            self.ui.chooseDatabase.addItem(corpus)
    
        self.ui.compareList.clicked.connect(self.push_file)
        self.ui.compareCel.clicked.connect(self.push_database)
        self.ui.actionClose.triggered.connect(self.push_close)
        self.ui.actionHelp.triggered.connect(self.push_help)

        self.window.show()
        sys.exit(self.app.exec_())
        self.filePro.close()
        self.fileRes.close()