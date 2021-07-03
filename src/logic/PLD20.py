import requests
import os
import xml.etree.ElementTree as ET

from src.logic.WordObject import WordObject # pylint: disable=import-error

class PLD20:
    def compare_to_target(self, target, corpus):
        """
        Function compares a target word with a corpus
        :return: Function returns the 20 nearest words
        """
        corpus = self.lev(target, corpus)
        self.sort_corpus(corpus)
        mean = self.get_mean_20(corpus)
        return mean, corpus
    
    def compare_corpus(self, corpus):
        count_all_levi = 0
        count_all_corpus = 0
        for entry in corpus:
            cl = []
            for comp in corpus:
                if comp.orth == entry.orth:
                    continue
                cur_levi = 0
                already = [x for x in comp.comp_levis if x.phon == entry.phon]
                if len(already) != 0:
                    cur_levi = already[0].levi
                else:
                    cur_levi = self.levenshtein(entry.phon, comp.phon)
                ncomp = comp.copy()
                ncomp.levi = cur_levi
                cl.append(ncomp)
                count_all_levi += cur_levi
                count_all_corpus += 1
            self.sort_corpus(cl)
            entry.levi = self.get_mean_20(cl)
            entry.comp_levis = cl
        mean = count_all_levi/count_all_corpus
        self.sort_corpus(corpus)

        return mean, corpus
    
    def lev(self, target, corpus):
        """
        The function lev calculates the levenshtein-distance  between target and each word in corpus
        :param target word object:
        :param transcripted corpus word objects:
        :return mean of calculation and corpus with added levenshtein-distances:
        """
        for entry in corpus:
            cur_levi = self.levenshtein(target.phon, entry.phon)
            entry.levi = cur_levi

        return corpus

    def levenshtein(self, w1,w2):
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
    
    def get_mean_20(self, corpus):
        count = 0
        for word in corpus[0:20]:
            count += word.levi
        return count/20

    def sort_corpus(self, corpus):
        corpus.sort(key=lambda x: x.levi)
        zero_entrys = []
        for entry in corpus:
            if entry.levi == 0:
                zero_entrys.append(entry)
            else:
                break
        for entry in zero_entrys:
            corpus.remove(entry)

    
    def read_corpus(self, content):
        corpus = []
        for line in content:
            if ";" in line:
                if len(line.split(";")) != 2:
                    continue
                orth = line.split(";")[0].replace(" ","")
                phon = line.split(";")[1].replace(" ","")
                if orth != None and phon != None:
                    wo = WordObject(orth, p=phon)
                    corpus.append(wo)
        return corpus