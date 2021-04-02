import xml.etree.ElementTree as ET
import sys


class KannadaLitmusEngine:

    def __init__(self):
        pass

    def parse_xml(self, f):
        root = ET.parse(f)
        docs = root.findall('./doc')
        return docs

    def get_candidates(self, doc):
        return doc.findall('./title')


if __name__ == "__main__":
    f = sys.argv[1]
    e = KannadaLitmusEngine()
    docs = e.parse_xml(f)
    for doc in docs:
        for c in e.get_candidates(doc):
            print(c.text)
