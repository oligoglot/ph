import xml.etree.ElementTree as ET
import sys
import re
from io import StringIO

class KannadaLitmusEngine:

    def __init__(self):
        self.noise_pattern = re.compile(r'===?[^=]+=?==')
        self.nonword_pattern = re.compile(r'\W')
        self.p_initials = re.compile('^(ಪ|ಪಾ|ಪಿ|ಪೀ|ಪು|ಪೂ|ಪೆ|ಪೇ|ಪೈ|ಪೊ|ಪೋ|ಪೌ)')
        self.h_initials = re.compile('^(ಹ|ಹಾ|ಹಿ|ಹೀ|ಹು|ಹೂ|ಹೆ|ಹೇ|ಹೈ|ಹೊ|ಹೋ|ಹೌ)')
        #self.load_titles()

    def load_titles(self):
        with open ("data/knwiktionary-20210401-all-titles-in-ns0", "r") as title_f:
            self.titles = set(title_f.read().split('\n'))

    def parse_xml(self, f):
        xml = open(f).read()
        it = ET.iterparse(StringIO(xml))
        for _, el in it:
            prefix, has_namespace, postfix = el.tag.partition('}')
            if has_namespace:
                el.tag = postfix  # strip all namespaces
        root = it.root
        for page in root.findall(".//page/[ns='0']"):
            yield page

    def get_candidates(self, doc):
        title = doc.findall('./title')
        text = doc.findall('.//text')
        return (title, text)

    def get_synonyms(self, title, text):
        if text:
            text = text[0].text
            if text:
                if title:
                    title = title[0].text
                    #text = title + ' ' + text
                text = self.noise_pattern.sub(' ', text, re.MULTILINE | re.DOTALL)
                text = re.sub(r'\W+', ' ', text)
                pwords = set(list(filter(lambda w: self.p_initials.match(w), re.split('[\s\n]+', text))))
                hwords = set(list(filter(lambda w: self.h_initials.match(w), re.split('[\s\n]+', text))))
                words = set.union(pwords, hwords)
                words.add(title)
                return words
        return []


if __name__ == "__main__":
    f = "data/knwiktionary-20210401-pages-articles.xml"
    e = KannadaLitmusEngine()
    for doc in e.parse_xml(f):
        title, text = e.get_candidates(doc)
        syns = e.get_synonyms(title, text)
        if len(syns) > 0:
            print(syns)
