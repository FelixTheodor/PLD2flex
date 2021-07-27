import io
import requests
import xml.etree.ElementTree as ET

class BASConnector:
    def __init__(self, lang):
        self.base_url = "https://clarin.phonetik.uni-muenchen.de/BASWebServices/services/runG2P"
        self.ping_url = "https://clarin.phonetik.uni-muenchen.de/BASWebServices/services/getLoadIndicator"
        self.params = {"com": "no","align": "no","outsym": "sampa","stress": "no","lng": lang,"syl": "no",
                        "embed": "no","iform": "list","nrm": "no","oform": "tab","map": "no","featset": "standard"}
    
    def ping(self):
        request = requests.get(url=self.ping_url)
        return request.text

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
        fi = open(path)
        f = {'i': fi}
        request = requests.post(self.base_url, data=self.params, files=f)
        fi.close()
        root = ET.fromstring(request.text)
        link = root.find("downloadLink").text
        result = requests.get(link)
        result.encoding = "utf-8"
        
        # needs to be read in as a corpus
        return result.text