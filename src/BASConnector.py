import io
import requests

class BASConnector:
    """
    provides methods to call the BAS-API and convert orthographic WOs to phons
    """
    def __init__(self, lang, calc):
        self.base_url = "https://clarin.phonetik.uni-muenchen.de/BASWebServices/services/runG2P"
        self.ping_url = "https://clarin.phonetik.uni-muenchen.de/BASWebServices/services/getLoadIndicator"
        self.params = {"com": "no","align": "no","outsym": "sampa","stress": "no","lng": lang,"syl": "no",
                        "embed": "no","iform": "list","nrm": "no","oform": "tab","map": "no","featset": "standard"}
        self.calc = calc
    def ping(self):
        """
        checks the server load of the BAS
        """
        request = requests.get(url=self.ping_url)
        return request.text

    def get_single_phon(self, orth):
        """
        pretends to send a file containing only one orth and converting it
        """
        file = {'i': ('temp.txt', io.StringIO(orth))}

        request = requests.post(url=self.base_url, data=self.params, files=file)
        link = request.text.split("<downloadLink>")[1].split("</downloadLink>")[0]
        result = requests.get(link)
        result.encoding = "utf-8"

        for word in result.text.split("\n"):
            if ";" in word:
                if self.calc == "CHARACTER":
                    phon = word.split(";")[1].replace(" ", "")
                else:
                    phon = word.split(";")[1].split(" ")
                return phon
        return None

    def get_phons_from_list(self, orths):
        """
        converts a list of orths to phons via BAS
        """
        file = {'i': ('temp.txt', io.StringIO(orths))}

        request = requests.post(url=self.base_url, data=self.params, files=file)
        link = request.text.split("<downloadLink>")[1].split("</downloadLink>")[0]
        result = requests.get(link)
        result.encoding = "utf-8"

        # needs to be read in as a corpus
        return result.text

    def get_phons_from_file(self, path):
        """
        converts a file of orths to phons via BAS
        """
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