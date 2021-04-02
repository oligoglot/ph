import xml.etree.ElementTree as ET
import sys
import re


class KannadaLitmusEngine:

    def __init__(self):
        self.noise_pattern = re.compile(r'\=\=\=?[^\=]+\=?\=\=')
        self.p_initials = re.compile(r'^\u0caa[\u0CBE-\u0ce3]')

    def parse_xml(self, f):
        root = ET.parse(f)
        for doc in root.findall('./doc'):
            yield doc

    def get_candidates(self, doc):
        title = doc.findall('./title')
        abstract = doc.findall('./abstract')
        return abstract

    def get_synonyms(self, abstract):
        if abstract:
            abstract = self.noise_pattern.sub(' ', abstract)
            words = list(filter(lambda w: self.p_initials.match(w), re.split(r'\W+', abstract)))
            return words
        return []


if __name__ == "__main__":
    f = sys.argv[1]
    e = KannadaLitmusEngine()
    for doc in e.parse_xml(f):
        for abstract in e.get_candidates(doc):
            syns = e.get_synonyms(abstract.text)
            if len(syns) > 0:
                print(syns)
