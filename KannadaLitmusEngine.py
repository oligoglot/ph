import xml.etree.ElementTree as ET
import sys
import re
from io import StringIO


class KannadaLitmusEngine:

    def __init__(self):
        self.noise_pattern = re.compile(r'===?[^=]+=?==')
        self.nonword_pattern = re.compile(r'\W')
        self.p_initials = re.compile('^(ಪ|ಪಾ|ಪಿ|ಪೀ|ಪು|ಪೂ|ಪೆ|ಪೇ|ಪೈ|ಪೊ|ಪೋ|ಪೌ)')
        self.pa = re.compile('^ಪ')
        self.h_initials = re.compile('^(ಹ|ಹಾ|ಹಿ|ಹೀ|ಹು|ಹೂ|ಹೆ|ಹೇ|ಹೈ|ಹೊ|ಹೋ|ಹೌ)')
        self.ha = re.compile('^ಹ')
        self.pertinent_words = set()
        self.hertinent_words = set()
        self.psuffixes = set()
        self.hsuffixes = set()
        # self.load_titles()

    def load_titles(self):
        with open("data/knwiktionary-20210401-all-titles-in-ns0", "r") as title_f:
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
                    text = title + ' ' + text
                text = self.noise_pattern.sub(
                    ' ', text, re.MULTILINE | re.DOTALL)
                text = re.sub(
                    r'([a-z]|[\{\}\<\>\[\]\|\-\:\'\;\)\(])+', ' ', text.lower())
                words = re.split('[\s\n]+', text)
                pwords = set()
                hwords = set()
                for word in words:
                    if self.p_initials.match(word):
                        self.pertinent_words.add(word)
                        word = re.sub(self.pa, '', word, 1)
                        pwords.add(word)
                    elif self.h_initials.match(word):
                        self.hertinent_words.add(word)
                        word = re.sub(self.ha, '', word, 1)
                        hwords.add(word)
                self.psuffixes.update(pwords)
                self.hsuffixes.update(hwords)
                phsynonyms = list(map(lambda suffix: (
                    'ಪ' + suffix, 'ಹ' + suffix), set.intersection(pwords, hwords)))
                return phsynonyms
        return []


if __name__ == "__main__":
    f = "data/knwiktionary-20210401-pages-articles.xml"
    e = KannadaLitmusEngine()
    pairs = set()
    pairedwords = set()
    for doc in e.parse_xml(f):
        title, text = e.get_candidates(doc)
        syns = e.get_synonyms(title, text)
        if len(syns) > 0:
            for pair in syns:
                pairs.add(",".join(pair))
                pairedwords.add(pair[0])
                pairedwords.add(pair[1])
    with open("phsynonyms.csv", "w") as synf:
        for pair in pairs:
            print(pair, file=synf)
    with open("presumable_synonyms.csv", "w") as psynf:
        presumable_synonyms = e.psuffixes.intersection(e.hsuffixes)
        for suffix in presumable_synonyms:
            print('ಪ' + suffix + ',' + 'ಹ' + suffix, file=psynf)
    with open("puniverse.csv", "w") as punif, open("huniverse.csv", "w") as hunif, open("unpaired.csv", "w") as unpairedf:
        for word in e.pertinent_words:
            suffix = re.sub(e.pa, '', word)
            print(word + ',' + suffix, file=punif)
            if word not in pairedwords and suffix not in presumable_synonyms:
                print(word, file=unpairedf)
        for word in e.hertinent_words:
            suffix = re.sub(e.ha, '', word)
            print(word + ',' + suffix, file=hunif)
            if word not in pairedwords and suffix not in presumable_synonyms:
                print(word, file=unpairedf)
