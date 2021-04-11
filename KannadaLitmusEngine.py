import xml.etree.ElementTree as ET
import sys
import re


class KannadaLitmusEngine:

    def __init__(self):
        self.noise_pattern = re.compile(r'\=\=\=?[^\=]+\=?\=\=')
        self.p_initials = re.compile('^(ಪ|ಪಾ|ಪಿ|ಪೀ|ಪು|ಪೂ|ಪೆ|ಪೇ|ಪೈ|ಪೊ|ಪೋ|ಪೌ)')
        self.h_initials = re.compile('^(ಹ|ಹಾ|ಹಿ|ಹೀ|ಹು|ಹೂ|ಹೆ|ಹೇ|ಹೈ|ಹೊ|ಹೋ|ಹೌ)')

    def parse_xml(self, f):
        root = ET.parse(f)
        for doc in root.findall('./doc'):
            yield doc

    def get_candidates(self, doc):
        title = doc.findall('./title')
        abstract = doc.findall('./abstract')
        return (title, abstract)

    def get_synonyms(self, title, abstract):
        if abstract:
            abstract = abstract[0].text
            if abstract:
                if title:
                    title = title[0].text
                    #abstract = title + ' ' + abstract
                abstract = self.noise_pattern.sub(' ', abstract, re.MULTILINE|re.DOTALL)
                #print(abstract)
                #sys.exit()
                pwords = set(list(filter(lambda w: self.p_initials.match(w), re.split('[\s\n]+', abstract, re.MULTILINE|re.DOTALL))))
                hwords = set(list(filter(lambda w: self.h_initials.match(w), re.split('\s+', abstract))))
                words = set.union(pwords, hwords)
        return []


if __name__ == "__main__":
    f = sys.argv[1]
    e = KannadaLitmusEngine()
    for doc in e.parse_xml(f):
        title, abstract = e.get_candidates(doc)
        syns = e.get_synonyms(title, abstract)
        if len(syns) > 0:
            print(syns)
