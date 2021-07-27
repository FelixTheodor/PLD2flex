import sys
import os
import requests

from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import QApplication, QMainWindow # pylint: disable=no-name-in-module
from PyQt5 import QtCore
from datetime import datetime
import playsound
import numpy as np
import copy

from src.Config import Config # pylint: disable=import-error
from src.WordObject import WordObject # pylint: disable=import-error
from src.PLD20 import PLD20 # pylint: disable=import-error
from src.BASConnector import BASConnector # pylint: disable=import-error
from src.GUI import Ui_MainWindow # pylint: disable=import-error
from src.CommandData import CommandData # pylint: disable=import-error

class ContentManager:
    def __init__(self):
        #self.appctxt = ApplicationContext()
        self.app = QApplication(sys.argv)
        self.window = QMainWindow()
        self.ui = Ui_MainWindow()

        self.config = Config()
        self.PLD20 = PLD20()
        self.connector = BASConnector(self.config.lang)

        self.corpora = {}

        self.divider = "####################################"
        # creating file to save the results
        self.fileRes = open(os.getcwd() + "/data/results/result" + str(datetime.now().isoformat(timespec='minutes')) + ".csv", mode="w", encoding="utf-8")
        self.fileLog = open(os.getcwd() + "/data/logs/log" + str(datetime.now().isoformat(timespec='minutes')) + ".csv", mode="w", encoding="utf-8")
        


    #################################################################
    # methods reacting to button push                               #
    #################################################################
    def push_database(self):
        """
        Function reacts to the user clicking on "Compare with Database"
        (Corpus has to be in the same directory in the folder "corpora")
        :return: Function prints the 20 nearest words into the output and the protocol text fields
        """
        cd = CommandData()
        t_orth = str(self.ui.target.text().replace(" ", ""))
        input_text = str(self.ui.input.toPlainText())
        if t_orth == "" and input_text == "":
            self.error("no data in target or input field", cd)
            return
        if t_orth != "" and input_text != "":
            self.error("data in target and input field", cd)
            return
        
        corpus_name = self.ui.chooseDatabase.currentText()
        if corpus_name == "":
            self.error("no corpus provided", cd)
            return
        corpus = copy.deepcopy(self.corpora[corpus_name])

        cd.corpus = corpus
        cd.input = "corpus"
        cd.path_word = corpus_name
        if t_orth != "":
            self.protocol("comparing target to " + corpus_name + "\n")   
            self.target_compare(t_orth, cd)
        else:
            self.database_list_compare(cd, input_text, corpus_name)

        self.play_sound()

    def push_input(self):
        """
        Function reacts to the user clicking on "Compare with file/list" calculates the levenshtein-distances and prints the output
        :return: levenshtein-distances
        """
        cd = CommandData()
        if (self.ui.input.toPlainText() == ""):
            self.error("no list or file in input", cd)
            return

        input_mode = self.ui.fileType.currentText()
        input_text = self.ui.input.toPlainText()
        target_text = self.ui.target.text()
        target_provided = target_text != ""
        path_provided = "file://" in str(input_text)

        # for two columns, the process works differently
        if input_mode == "Two columns":
            if target_provided:
                self.error("comparing two columns is not possible with given target", cd)
                return
            self.columns_compare(path_provided, input_text, cd)
        elif input_mode == "One column":
            self.one_compare(path_provided, input_text, target_text, target_provided, cd) 
        else:
            self.protocol("something went wrong, invalid input mode!")
            return
        self.play_sound()

    def push_close(self):
        """
        Function closes the running process
        """
        self.fileRes.close()
        self.fileLog.close()
        sys.exit()

    def push_help(self):
        """
        No function yet: Function should open the User Manual
        """
        self.protocol("Not available")



    #################################################################
    # methods doing the comparisons                                 #
    #################################################################
    def database_list_compare(self, cd, input_text, corpus_name):
        if "file://" not in input_text:
            self.protocol("comparing list to " + corpus_name + "\n") 
            cd.input = "gui"
            phon_list = self.connector.get_phons_from_list(input_text)
        else: 
            path = input_text.replace("file://", "").replace("\n", "")
            self.protocol("comparing "+path+" to " + corpus_name + "\n")
            cd.input = "file"
            cd.path_word = path
            if os.path.isfile(path):
                f = open(path)
                for line in f.readlines():
                    if " " in line or "\t" in line:
                        self.error("too many columns in input file", cd)
                        return
                f.close()
                try:
                    phon_list = self.connector.get_phons_from_file(path)
                except requests.exceptions.RequestException:
                    self.error("connection to BAS refused", cd)
                    return
            else:
                self.error("cannot read file: " + path, cd)
                return
        all_words = self.PLD20.read_corpus(phon_list.split("\n"))
        all_levi = []
        for word in all_words:
            new_cd = CommandData()
            new_cd.target = word
            new_cd.method = "mul-one-to-many"
            new_cd.input = cd.input
            new_cd.path_word = corpus_name
            # compare target with corpus
            new_cd.pld20, new_cd.sd, new_cd.corpus = self.PLD20.compare_to_target(word, cd.corpus)
            all_levi.append(new_cd.pld20)
    
            self.protocol("tested target:\t" + str(word))
            self.print_results(new_cd, log=False)
        cd.pld20, cd.sd = np.mean(all_levi), np.std(all_levi)
        cd.method = "mul-one-to-many"
        self.log(cd.log())
        self.protocol(self.divider)

    def one_compare(self, path_provided, input_text, target_text, target_provided, cd):
        for line in input_text.split("\n"):
            if " " in line or "\t" in line:
                self.error("too many columns in input", cd)
                return
        if path_provided:
            path = input_text.replace("file://", "").replace("\n", "")
            cd.input = "file"
            cd.path_word = path
            to_log = "file " + path.split("/")[-1]
            if os.path.isfile(path):
                f = open(path)
                for line in f.readlines():
                    if " " in line or "\t" in line:
                        self.error("too many columns in input file", cd)
                        return
                f.close()
                try:
                    phon_list = self.connector.get_phons_from_file(path)
                except requests.exceptions.RequestException:
                    self.error("connection to BAS refused", cd)
                    return
            else:
                self.error("cannot read file: " + path, cd)
                return
        else:
            cd.input = "gui"
            cd.path_word = "list"
            to_log = "the provided list"
            try:
                phon_list = self.connector.get_phons_from_list(input_text)
            except requests.exceptions.RequestException:
                self.error("connection to BAS refused", cd)
                return
        corpus = self.PLD20.read_corpus(phon_list.split("\n"))
        cd.corpus = corpus

        if len(corpus) < 20:
            self.warn("these are less than 20 words!", cd)
        
        if target_provided:
            self.protocol("compare target to " + to_log + ":\n")
            t_orth = target_text.replace(" ", "")
            return self.target_compare(t_orth, cd)
        else:
            self.protocol("cross compare " + to_log + ":\n")
            return self.cross_compare(cd)

    def cross_compare(self, cd):
        cd.method= "many-to-many"
        if len(cd.corpus) < 21:
            self.error("cross compare only possible with more than 20 entrys",cd)
            return
        cd.pld20, cd.sd, cd.corpus = self.PLD20.compare_corpus(cd.corpus)
        for entry in cd.corpus:
            self.protocol(entry.orth + " mean:\t" + str(entry.levi))
        self.protocol("")
        self.print_results(cd)
    
    def target_compare(self, t_orth, cd):
        cd.method = "one-to-many "
        try:
            t_phon = self.connector.get_single_phon(t_orth)
        except requests.exceptions.RequestException:
            self.error("connection to BAS refused", cd)
            return
        target = WordObject(t_orth, p=t_phon)
        cd.target = target
        # compare target with corpus
        cd.pld20, cd.sd, cd.corpus = self.PLD20.compare_to_target(cd.target, cd.corpus)
        
        self.protocol("tested target:\t" + str(target))
        self.print_results(cd)
    
    def columns_compare(self, path_provided, input_text, cd):
        cd.method = "one-to-one  "
        msgs = []
        lines = []

        if path_provided:
            cd.input = "file"
            cd.path_word = path
            path = input_text.replace("file://", "").replace("\n", "")
            if os.path.isfile(path): 
                self.protocol("comparing columns in " + path.split("/")[-1] +":\n")
                f = open(path)
                for line in f.readlines():
                    lines.append(line.replace("\n", ""))
                f.close()
            else:
                self.error("file not found: " + path, cd)
                return    
        else:
            cd.input = "gui"
            cd.path_word = "list"
            self.protocol("comparing columns in input field" + ":\n")
            for line in input_text.split("\n"):
                lines.append(line)

        for line in lines:
            if line in ["\n", "", " "]:
                continue
            pair = line.split("\t") if "\t" in line else line.split(" ") 
            if len(pair) != 2:
                self.error("not every line has two columns", cd)
                return
            try:
                p1 = self.connector.get_single_phon(pair[0])
                p2 = self.connector.get_single_phon(pair[1])
            except requests.exceptions.RequestException:
                self.error("connection to BAS refused", cd)
                return
            levi = self.PLD20.levenshtein(p1, p2)
            msgs.append(f"{pair[0]}\t{p1}\t{pair[1]}\t{p2}\t{levi}")

        self.msgs = msgs
        self.protocol(f"count corpus:\t{len(msgs)}")
        self.protocol(self.divider)
        
        for msg in msgs:
            self.save(cd.save(msg))
        self.save("#########")
        self.log(cd.log())
        self.protocol(self.divider)



    #################################################################
    # methods handling the logging and saving of results            #
    #################################################################
    def protocol(self, msg):
        """
        The function protocol(msg) prints a string into the protocol field
        :param string: msg
        """
        self.ui.protocol.insertPlainText(msg + "\n")
    
    def save(self, msg):
        """
        The function save(msg) prints a string into the result file and output field
        :param string: msg
        """
        self.ui.output.insertPlainText(msg + "\n")
        self.fileRes.write(msg + "\n")
    
    def log(self, msg):
        """
        The function log(msg) prints a string into the log file
        :param string: msg
        """
        self.fileLog.write(msg + "\n")
    
    def error(self, msg, cd):
        """
        The function error(msg) prints an error string into the protocol field
        :param string: msg
        """
        self.protocol("ERROR: " + msg)
        self.protocol(self.divider)
        self.protocol(self.divider)
        cd.err = msg
        self.log(cd.log())

    def warn(self, msg, cd):
        """
        The function warn(msg) prints an warn string into the protocol field
        :param string: msg
        """
        self.protocol("WARN: " + msg)
        cd.warn = msg

    def print_results(self, cd, log=True):
        """
        The function save(string) prints a string into the result filed and file
        :param string: Output
        """
        self.protocol("mean-distance:\t" + str(cd.pld20))
        self.protocol("std-deviation:\t" + str(cd.sd))
        self.protocol(f"count corpus: \t{len(cd.corpus)}")
        self.protocol(self.divider)

        if len(cd.corpus) > 20:
            cd.corpus = cd.corpus[0:20]

        for entry in cd.corpus:
            self.save(cd.save(str(entry)))
        self.save("#####")
        if log:
            self.log(cd.log())
            self.protocol(self.divider)

    

    #################################################################
    # methods for the init process                                  #
    #################################################################
    def read_corpora(self):
        """
        Function reads in all the corpora that are in the specified folder
        :return:
        """
        for key in self.config.corpus_files.keys():
            path = self.config.corpus_files[key]
            with open(path, encoding = "utf-8", mode = "r") as file:
                content = file.read().split("\n")
            corpus = self.PLD20.read_corpus(content)
            if corpus != None and len(corpus) != 0:
                self.corpora[key] = corpus
            else:
                self.protocol(f"WARN: file {key} is not a valid corpus")
            

        for corpus in self.corpora.keys():
            self.ui.chooseDatabase.addItem(corpus)
    
    def play_sound(self):
        try:
            playsound.playsound("data/sounds/bell.mp3")
        except playsound.PlaysoundException:
            print(playsound.PlaysoundException)

    def report_config(self):
        """
        Function shows the user the current configuration
        :return:
        """
        self.protocol(f"path to config: {self.config.path}")
        self.protocol("---------------------------------------")
        self.protocol(f"current configuration:\ncorpora:\t{len(self.corpora)} initialized")
        self.protocol(f"language:\t{self.config.lang}\nuse old20:\t{self.config.old}")
        self.protocol("---------------------------------------")
        self.log(f"configuration: {len(self.corpora)} corpora initialized, language: {self.config.lang}, use old20: {self.config.old}")

    def ping(self):
        """
        Function pings BAS-Server and reports the status
        :return:
        """
        try:
            status = self.connector.ping()
        except requests.exceptions.RequestException:
            self.protocol("ERROR: connection to BAS refused")
        if status in ["0", "1", "2"]:
            if status == "0":
                status = "low"
            elif status == "1":
                status = "medium"
            else:
                status = "high"
            self.protocol("current server load of BAS is: " + status)
        else:
            self.protocol("BAS-Server load is unkown!")
        self.protocol(self.divider)
        self.protocol(self.divider)

    def init_process(self):
        self.ui.setupUi(self.window)
        self.ui.compareList.clicked.connect(self.push_input)
        self.ui.compareCel.clicked.connect(self.push_database)
        self.ui.actionClose.triggered.connect(self.push_close)
        self.ui.actionHelp.triggered.connect(self.push_help)

        self.read_corpora()
        self.report_config()
        self.ping()
        self.log("method\tinput_type\tinput_source\tmean_pld\tsd\terrors\twarnings")
        self.save("target_orth\ttarget_phon\tcomp_orth\tcomp_phon\tlevenshtein\tmethod\tinput_type\tinput_source")
        
    def connectSeq(self):
        """
        Function connects function with the developed GUI
        :return:
        """
        self.window.show()
        exit_code = self.app.exec()
        self.fileRes.close()
        self.fileLog.close()
        return exit_code