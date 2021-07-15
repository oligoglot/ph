import xml.etree.ElementTree as ET
import sys
import re
import gzip
from io import StringIO
from collections import Counter


class KannadaLitmusEngine:

    def __init__(self):
        self.noise_pattern = re.compile(r'===?[^=]+=?==')
        self.nonword_pattern = re.compile(r'\W')
        self.p_initials = re.compile('^(ಪ|ಪಾ|ಪಿ|ಪೀ|ಪು|ಪೂ|ಪೆ|ಪೇ|ಪೈ|ಪೊ|ಪೋ|ಪೌ)')
        self.pa = re.compile('^ಪ')
        self.h_initials = re.compile('^(ಹ|ಹಾ|ಹಿ|ಹೀ|ಹು|ಹೂ|ಹೆ|ಹೇ|ಹೈ|ಹೊ|ಹೋ|ಹೌ)')
        self.ha = re.compile('^ಹ')
        self.pertinent_words = Counter()
        self.hertinent_words = Counter()
        self.psuffixes = Counter()
        self.hsuffixes = Counter()
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
                text = self.preprocess_text(text)
                pwords, hwords = self.get_phwords(text)
                phsynonyms = list(map(lambda suffix: (
                    'ಪ' + suffix, 'ಹ' + suffix), pwords & hwords))
                return phsynonyms
        return []

    def get_phwords(self, text):
        words = text.split()
        psuffixes = Counter()
        hsuffixes = Counter()
        for word in words:
            if self.p_initials.match(word):
                self.pertinent_words[word] += 1
                suffix = re.sub(self.pa, '', word, 1)
                psuffixes[suffix] += 1
            elif self.h_initials.match(word):
                self.hertinent_words[word] += 1
                suffix = re.sub(self.ha, '', word, 1)
                hsuffixes[suffix] += 1
        self.psuffixes.update(psuffixes)
        self.hsuffixes.update(hsuffixes)
        return psuffixes,hsuffixes

    def preprocess_text(self, text):
        text = self.noise_pattern.sub(
                    ' ', text, re.MULTILINE | re.DOTALL)
        text = re.sub(
                    r'([a-z]|[\{\}\<\>\[\]\|\-\:\'\;\)\(\.\,])+', ' ', text.lower())
            
        return text


def process_kn_wiktionary(e, f=r"data/knwiktionary-20210401-pages-articles.xml"):
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
    return pairs,pairedwords

if __name__ == "__main__":
    e = KannadaLitmusEngine()
    infile, corpus = sys.argv[1:3]
    pairs, pairedwords = process_kn_wiktionary(e)
    with open(r"out/phsynonyms.csv", "w") as synf:
        for pair in pairs:
            print(pair, file=synf)
    if corpus!="wikt":
        with gzip.open(infile, 'rt') as corpus_f:
            for doc in corpus_f:
                text = e.preprocess_text(doc)
                e.get_phwords(text)
    with open(r"out/presumable_synonyms.csv", "w") as psynf:
        presumable_synonyms = e.psuffixes & e.hsuffixes
        for suffix in presumable_synonyms:
            pcount = e.psuffixes[suffix]
            hcount = e.hsuffixes[suffix]
            print(','.join(('ಪ' + suffix, str(pcount), 'ಹ' + suffix, str(hcount), str(round((pcount-hcount)/(pcount+hcount),5)))), file=psynf)
    with open(r"out/puniverse.csv", "w") as punif, open(r"out/huniverse.csv", "w") as hunif, open(r"out/unpaired.csv", "w") as unpairedf:
        for word, count in e.pertinent_words.most_common():
            suffix = re.sub(e.pa, '', word)
            print(word + ',' + suffix + ',' + str(count), file=punif)
            if word not in pairedwords and suffix not in presumable_synonyms:
                print(word + ',' + str(count), file=unpairedf)
        for word, count in e.hertinent_words.most_common():
            suffix = re.sub(e.ha, '', word)
            print(word + ',' + suffix + ',' + str(count), file=hunif)
            if word not in pairedwords and suffix not in presumable_synonyms:
                print(word + ',' + str(count), file=unpairedf)
