import requests
import os
import xml.etree.ElementTree as ET


def lev20(w1, l2):
    """
    The function lev20(w1, l2) calls the function which calculates the levenshtein-distance and afterwards calculates the mean of the values.
    :param transcripted target word:
    :param transcripted list of words which should be compared to the target word:
    """
    # variable sum will save the sum of the calculated levenshtein-distances
    sum = 0
    # length saves the length of the list of words (to calculate the mean)
    length = len(l2)
    # for each word the function calculates the levenshtein-distance and saves the word and its value in the list
    # furthermore the value will be added to the sum
    for w2 in range(len(l2)):
        if len(l2[w2].split("\t")) != 2 and l2[w2] != "":
            l2[w2] = l2[w2] + "\t" + str(levenshtein(w1,l2[w2]))
        if len(l2[w2].split("\t")) == 2:
            sum += int(l2[w2].split("\t")[1])
        elif l2[w2] != "":
            sum += levenshtein(w1,l2[w2])
        else:
            length -= 1
    return sum/length, l2


def levenshtein(w1,w2):
    """
    The function levenshtein(w1,w2) calculates the levenshtein-distance of two words
    :param target word:
    :param word that will be compared to the target word:
    :return: levenshtein-distance
    """
    # Longer word will be compared to the shorter the shorter one
    if len(w1) >= len(w2):
        word1,word2 = w1,w2
    else:
        word1,word2 = w2,w1

    # Filling the Dummy-table distance (length1xlength2)
    distance = []
    for i in range(len(word1)+1):
        distance.append([])
        for j in range(len(word2)+1):
            distance[i].append(0)

    # Filling the first row and column of the table with the indices (value1 and value2)
    for value1 in range(len(word2)+1):
        distance[0][value1] = value1
    for value2 in range(len(word1)+1):
       distance[value2][0] = value2

    # Calculating the Levenshtein-distance by comparing the letters and saving the biggest neighbour value
    for i in range(1,(len(word1)+1)):
        letter1 = word1[i-1]
        for j in range(1,(len(word2)+1)):
            letter2 = word2[j-1]
            neighbours = [distance[i-1][j],distance[i][j-1],distance[i-1][j-1]]
            neighbours.sort()
            if letter1 == letter2:
                distance[i][j] = neighbours[0]
            elif letter1 != letter2:
                distance[i][j] = neighbours[0] +1
    return distance[len(word1)][len(word2)]


def getInfos(file = "noFile", liste = [], w1 = ""):
    """
    The function getInfos(file, liste, w1) gathers the information and controls the process.
    :param file: File that contains the list of word to which the target word should be compared (default: noFile)
    :param liste: list of words to which the target word should be compared (default: empty list)
    :param w1: target word (default: empty string)
    :return: tuple of mean distance and strings containing a word and its individual levenshtein-distance
    """
    # variable self controls the possibilty of cross validated files
    self = False
    # variable translated determines if the file and/or the list of words is already transcripted
    translated = False
    # variable sum saves the sum of the levenshtein-distances to print the mean of the cross validated levenshtein-distances
    result = 0

    #if the user wants to read a file, the function opens the file and reads in the words
    if file != "noFile":
        with open(file, mode = "r", encoding = "utf-8") as file:
            liste = file.read().split("\n")
        try:
            # if the file has to columns (of which one has only a digit) the digit will be ignored here
            if len(liste[0].split("\t")) == 2:
                for element in range(len(liste)):
                    liste[element] = liste[element].split("\t")[0]
                    translated = True
        except:
            self = False

        # if the user has not given a target word the function will begin to cross validate the given words
        if w1 == "":
            cross = []
            if translated == False:
                for index in range(len(liste)):
                    liste[index] = translate(w1 = liste[index])

            for word in liste:
                for word2 in liste:
                    if word != "" and word2 != "":
                        lev = levenshtein(word, word2)
                        if (word, word2, lev) not in cross and (word2, word, lev) not in cross and word != word2:
                            cross.append((word, word2, lev))
            self = True

    # if the user has typed in a target word the function will now calculate the levenshtein distance
    if self == False:
        if translated == False:
            for word in range(len(liste)):
                liste[word] = translate(w1 = liste[word])
        result, liste = lev20(translate(w1=w1), liste)

    # if the file was cross validated the mean will be calculated here
    else:
        summe = 0
        for number in cross:
            summe += number[2]
        result = summe/len(cross)
        liste = cross

    return (result, liste)



def getFile(w1, files):
    """
    The function getFile(w1, files) reads in  a corpus and the target word. It transcripts the target word,
    calculates the levenshtein-distance of the whole corpus and creates a file which contains the 20 nearest words.
    :param w1: target word
    :param files: list of files
    :return: path of the file which contains the 20 nearest words
    """
    # w contains the transcripted target word
    w = translate(w1 = w1)
    # set_dis inhibits tupels of the levenshtein-distance and the compared word
    set_dis = set()
    # for each file of the corpus the function reads in the needed word and calls the function to calculate the distance
    for file in files:
        with open(file, encoding = "utf-8", mode = "r") as file:
            content = file.read().split("\n")
        for line in content:
            if ";" in line:
                word = line.split(";")[1].replace(" ","")
                if word != w:
                    set_dis.add((levenshtein(w, word), word))
    # function prints the 20 nearest words in a file named target-lev20.txt
    with open(os.curdir + "/results/" + w1 + "-lev20.txt", mode = "w", encoding = "utf-8") as output:
        for w2 in sorted(set_dis)[:20]:
            print(w2[1] + "\t" + str(w2[0]), file = output)
    return os.curdir + "/results/" + w1 + "-lev20.txt"




def automatic(w1, files):
    """
    The function automatic(w1, files) calls getFile and afterwards calls getInfos to evaluate the result of getFile
    :param w1: target word
    :param files: list of files (corpus)
    :return: tuple of mean distance and strings containing a word and its individual levenshtein-distance
    """
    file = getFile(w1, files)
    return (getInfos(file = file, w1 = w1))




def translate(file = "", w1 = ""):
    """
    The function translate(file,w1) transcripts the given file or word by using the web service of G2P
    :param file: file that contains the words which have to be transcripted
    :param w1: word that needs to be transcripted
    :return: transcripted string
    """

    # if a file needs to be transcripted the function calls the web service and saves the result in a string
    if file != "":
        url = "https://clarin.phonetik.uni-muenchen.de/BASWebServices/services/runG2P"
        file = {"i": open(file)}
        data = {"com": "no",
                    "align": "no",
                    "outsym": "sampa",
                    "stress": "no",
                    "lng": "deu-DE",
                    "syl": "no",
                    "embed": "no",
                    "iform": "list",
                    "nrm": "no",
                    "oform": "tab",
                    "map": "no",
                    "featset": "standard"}
        request = requests.post(url, data=data, files=file)
        root = ET.fromstring(request.text)
        link = root.find("downloadLink").text
        result = requests.get(link)
        result.encoding = "utf-8"

        text = ""
        for word in result.text.split("\n"):
            if ";" in word:
                w1 = word.split(";")[1]
                text += w1 + "\n"

        return text.replace(" ","")

    # if only one word should be transcripted the function creates a temporaty file and starts the function again to transcript the file via the web service
    if w1 != "":
        temp = open("temp.txt", encoding = "utf-8", mode = "w")
        print(w1, file = temp)
        temp.close()
        result = translate(file = "temp.txt").replace("\n","")
        try:
            os.remove("temp.txt")
        except:
            pass
        return result
