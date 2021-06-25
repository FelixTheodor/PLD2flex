import io
import requests
import xml.etree.ElementTree as ET

class BASConnector:
    def __init__(self):
        self.base_url = "https://clarin.phonetik.uni-muenchen.de/BASWebServices/services/runG2P"
        self.params = {"com": "no","align": "no","outsym": "sampa","stress": "no","lng": "deu-DE","syl": "no",
                        "embed": "no","iform": "list","nrm": "no","oform": "tab","map": "no","featset": "standard"}
    
    def ping(self):
        pass

    def get_single_phon(self, orth):
        file = {'i': ('temp.txt', io.StringIO(orth))}

        request = requests.post(url=self.base_url, data=self.params, files=file)
        root = ET.fromstring(request.text)
        link = root.find("downloadLink").text
        result = requests.get(link)
        result.encoding = "utf-8"

        for word in result.text.split("\n"):
            if ";" in word:
                phon = word.split(";")[1].replace(" ", "")
                return phon

        return None

    def get_phons_from_list(self, orths):
        file = {'i': ('temp.txt', io.StringIO(orths))}

        request = requests.post(url=self.base_url, data=self.params, files=file)
        root = ET.fromstring(request.text)
        link = root.find("downloadLink").text
        result = requests.get(link)
        result.encoding = "utf-8"

        return result.text

    def get_phons_from_file(self, path):
        file = {'i': open(path)}
        request = requests.post(self.base_url, data=self.params, files=file)
        root = ET.fromstring(request.text)
        link = root.find("downloadLink").text
        result = requests.get(link).text
        result.encoding = "utf-8"
        
        # needs to be read in as a corpus
        return result.text