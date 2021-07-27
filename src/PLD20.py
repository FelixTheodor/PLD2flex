import requests
import os
import xml.etree.ElementTree as ET
import numpy as np

from Levenshtein import distance # pylint: disable=no-name-in-module
from src.WordObject import WordObject # pylint: disable=import-error


class PLD20:
    def compare_to_target(self, target, corpus):
        """
        Function compares a target word with a corpus
        :return: Function returns the 20 nearest words
        """
        corpus = self.lev(target, corpus)
        self.sort_corpus(corpus)
        mean, sd = self.get_mean_20(corpus)

        return mean, sd, corpus
    
    def compare_corpus(self, corpus):
        count_all_levi = []
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
                count_all_levi.append(cur_levi)
            self.sort_corpus(cl)
            entry.levi = self.get_mean_20(cl)
            entry.comp_levis = cl
        mean = np.mean(count_all_levi)
        sd = np.std(count_all_levi)
        self.sort_corpus(corpus)

        return mean, sd, corpus
    
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
        return distance(w1, w2)
    
    def get_mean_20(self, corpus):
        c20 = []
        for word in corpus[0:20]:
            c20.append(word.levi)
        mean = np.mean(c20)
        std = np.std(c20)
        return mean, std

    def sort_corpus(self, corpus):
        corpus.sort(key=lambda x: x.levi)
        return
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