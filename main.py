import src.logic.Levenshtein20 as LS
import sys
import os

from src.qt.GUI import Ui_MainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow
from datetime import datetime


app = QApplication(sys.argv)
window = QMainWindow()
ui = Ui_MainWindow()
# creating files to save the results
filePro = open(os.curdir + "/data/protocols/protocol_" + str(datetime.now().isoformat(timespec='minutes')) + ".csv", mode="w", encoding="utf-8")
fileRes = open(os.curdir + "/data/results/result" + str(datetime.now().isoformat(timespec='minutes')) + ".csv", mode="w", encoding="utf-8")

# benötigt target und output
def pushSUB():
    """
    Function reacts to the user clicking on "Compare with SUBTLEX"
    (SUBTLEX has to be in the same directory in the folder "corpora")
    :return: Function prints the 20 nearest words into the output and the protocol text fields
    """
    if str(ui.target.text()) != "":
        # function calls automatic(target word, file) which calculates the distances and extracts the 20 nearest words
        result = LS.automatic(str(ui.target.text()), [os.curdir + "/corpora/Phon-SUBTLEX-DE.txt"])
        # function prints the results
        addOutput(result[0], result[1])
        protocol("Tested " + str(ui.target.text()) + "  with SUBTLEX.\nLevenshtein-distance: ;" + str(result[0]) + "\n" + "\n".join(result[1]).replace("\t",";"),1)
    else:
        # error 6
        protocol("No data: target", 0)




def protocol(string, version):
    """
    The function protocol(string, version) prints a string into the protocol file
    If the version is 1 it also prints the result into the result file
    :param string: Output
    :param version: version == 0: only prints into protocol file; version == 1: prints also into the result file
    """
    ui.protocol.insertPlainText(string.replace(";", " ") + "\n")
    print(string + "\nTarget: ;" + ui.target.text() + "\nInput: ;" + " ;".join(ui.input.toPlainText().split("\n")) + "\n", file = filePro)
    if version == 1:
        print(string + "\nTarget: ;" + ui.target.text() + "\nInput: ;" + " ;".join(ui.input.toPlainText().split("\n")) + "\n", file=fileRes)



# braucht datei (corpus) und target
def pushData():
    """
    Function reacts to the user clicking on "Compare with Database"
    (Corpus has to be in the same directory in the folder "corpora")
    :return: Function prints the 20 nearest words into the output and the protocol text fields
    """
    if str(ui.target.text()) != "":
        # reading in file
        inputPath = str(ui.input.toPlainText())
        path = inputPath.replace("file://", "")
        with open(path, mode = "r") as file:
            # error 8
            if ";" not in file.readlines()[0]:
                protocol("No corpus found",0)
            else:
                # function calls automatic(target word, file) which calculates the distances and extracts the 20 nearest words
                result = LS.automatic(str(ui.target.text()), [path])
                # function prints the results
                addOutput(result[0], result[1])
                protocol("Tested " + str(ui.target.text()) + " with the given corpus.\nLevenshtein-distance: ;" + str(result[0]) + "\n" + "\n".join(result[1]).replace("\t",";"),1)
    else:
        # error 6
        protocol("No data: target", 0)



# braucht datei und target und list of words
def pushFile():
    """
    Function pushFile() reacts to the user clicking on "Compare with file/list" calculates the levenshtein-distances and prints the output
    :return: levenshtein-distances
    """
    result = ""
    # tests wether two checkboxes are activated
    if ui.fileOne.isChecked() and ui.fileTwo.isChecked():
        ui.protocol.insertPlainText("Please only use one Checkbox!")


    # if checkbox "One column" is activated the function will evaluate the file
    elif ui.fileOne.isChecked():
        # error 4
        if "file://" not in str(ui.input.toPlainText()):
            protocol("Found list not file", 0)
        else:
            try:
                # if the user typed in a target word, the function will calculate the distances in regard to this target
                if ui.target.text() != "":
                    inputPath = str(ui.input.toPlainText())
                    path = inputPath.replace("file://", "")
                    result = LS.getInfos(file=path, w1=str(ui.target.text()))
                # if the user did not give a target word the function will cross-validate the given words (of the file)
                else:
                    inputPath = str(ui.input.toPlainText())
                    path = inputPath.replace("file://", "")
                    lev, cross = LS.getInfos(file=path, w1="")
                    output = ""
                    # function prints the results
                    for tuple in cross:
                        output += tuple[0] + ";" + tuple[1] + ";" + str(tuple[2]) + "\n"
                        ui.output.insertPlainText(tuple[0] + "\t" + tuple[1] + "\tdistance: " + str(tuple[2]) + "\n")
                    protocol("Tested file " + path + "with cross validation. mean = " + str(lev) + "\n" + output,1)
            except:
                #error 1
                protocol("Cannot read file:" + path, 0)


    # if the checkbox "two columns" is activated the function will compare the words of one line
    elif ui.fileTwo.isChecked():
        if str(ui.target.text()) == "":
            # error 4
            if "file://" not in str(ui.input.toPlainText()):
                protocol("Found list not file", 0)
            else:
                try:
                    # calculating the levenshtein-distance for each line of the text file (two words)
                    error = True
                    inputPath = str(ui.input.toPlainText())
                    path = inputPath.replace("file://", "")
                    with open(path, mode = "r", encoding = "utf-8") as file:
                        liste = file.read().split("\n")
                    output = ""
                    for word in liste:
                        if "\t" in word:
                            error = False
                            word = word.split("\t")
                            word[0] = LS.translate(w1 = word[0])
                            word[1] = LS.translate(w1 = word[1])

                            lev = LS.levenshtein(word[0],word[1])
                            # function prints the results
                            ui.output.insertPlainText(word[0] + "\t" + word[1] + "\tdistance: " + str(lev) + "\n")
                            output += word[0] + ";" + word[1] + ";" + str(lev) + "\n"
                        # error 7
                        if error == True:
                            protocol("Only one column found!", 0)
                            break
                    protocol("Tested file " + path + ".\n" + output,1)
                # error 1
                except:
                    protocol("Cannot read file:" + path, 0)
        # error 2
        else:
            protocol("Comparing two columns not possible with target", 0)





    # If a list of words is given, the function calls getInfos to calculate the levenshtein-distance for each word
    if ui.fileOne.isChecked() == False and ui.fileTwo.isChecked() == False:
        # error 5
        if "file://" in str(ui.input.toPlainText()):
            protocol("Found file not list", 0)
            result = ""
        elif len(str(ui.input.toPlainText())) == 0:
            #error 7
            protocol("No data: input", 0)
            result = ""
        else:
            try:
                if str(ui.target.text()) != "":
                    liste = str(ui.input.toPlainText())
                    if "\n" in liste:
                        liste = liste.split("\n")
                    else:
                        liste = [liste]
                    if len(liste) < 20:
                        protocol("These are less than 20 words!", 0)
                    elif len(liste) > 20:
                        protocol("These are more than 20 words!", 0)
                    word = str(ui.target.text())
                    result = LS.getInfos(liste=liste, w1=word)
                else:
                    # error 6
                    protocol("No data: target", 0)
            except:
                protocol("Data not appropriate", 0)


    # function prints the results (if not done beforehand)
    if result != "":
        addOutput(result[0], result[1])
        protocol("Tested " + str(ui.target.text()) + ".\nLevenshtein-distance: ;" + str(result[0]) + "\n" + "\n".join(result[1]).replace("\t",";"),1)




def addOutput(word, liste):
    """
    Function prints the given strings into the text field "output"
    :param word: target word
    :param liste: list of words (which were compared to the target word)
    """
    ui.output.insertPlainText("levenshtein-distance: " + str(word) + "\n")
    for word in liste:
        ui.output.insertPlainText(word + "\n")


def pushClose():
    """
    Function closes the running process
    """
    filePro.close()
    sys.exit()


def pushHelp():
    """
    No function yet: Function should open the User Manual
    """
    protocol("Not available", 0)


def connectSeq():
    """
    Function connects function with the developed GUI
    :return:
    """
    ui.setupUi(window)

    ui.compareList.clicked.connect(pushFile)
    ui.compareCel.clicked.connect(pushData)
    ui.compareSub.clicked.connect(pushSUB)
    ui.actionClose.triggered.connect(pushClose)
    ui.actionHelp.triggered.connect(pushHelp)

    window.show()
    sys.exit(app.exec_())
    filePro.close()
    fileRes.close()

#starting the process
if __name__ == "__main__":
    connectSeq()
