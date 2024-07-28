import requests
import os
import numpy as np

import textdistance # pylint: disable=no-name-in-module
from src.WordObject import WordObject # pylint: disable=import-error


class PLD2flex:
    def compare_to_target(self, target, corpus, ncount):
        """
        compares a target word with a corpus
        returns the the mean, the sd and the corpus of the operation
        """
        corpus = self.lev(target, corpus)
        self.sort_corpus(corpus)
        mean, sd = self.get_mean_neighbours(corpus, ncount)

        return mean, sd, corpus
    
    def compare_corpus(self, corpus, ncount):
        """
        calculates the lev-distance for every entry in the given corpus
        compared to the whole corpus
        returns the sorted corpus and the mean and std or the operation
        """
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
            entry.levi = self.get_mean_neighbours(cl, ncount)
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
        via the imported distance function for better performance
        """
        return textdistance.damerau_levenshtein.distance(w1, w2)
    
    def get_mean_neighbours(self, corpus, ncount):
        """
        calculates the mean and std of the first ncount entrys of the corpus
        """
        c_neigh = []
        for word in corpus[0:ncount]:
            c_neigh.append(word.levi)
        mean = np.mean(c_neigh)
        std = np.std(c_neigh)
        return mean, std

    def sort_corpus(self, corpus):
        """
        sorts a corpus by the levi-distance
        """
        corpus.sort(key=lambda x: x.levi)
        return

    
    def read_corpus(self, content):
        """
        converts a content string by splitting on ';' to a list of WordObjects
        """
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