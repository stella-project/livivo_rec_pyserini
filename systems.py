import os
from pyserini.index.__main__ import JIndexCollection
from pyserini.search import SimpleSearcher
import jsonlines


class Ranker(object):

    def __init__(self):
        self.idx = None

    def index(self):
        pass

    def rank_publications(self, query, page, rpp):

        itemlist = []

        return {
            'page': page,
            'rpp': rpp,
            'query': query,
            'itemlist': itemlist,
            'num_found': len(itemlist)
        }


class Recommender(object):

    def __init__(self):
        self.idx = None
        self.searcher = None
        self.title_lookup = {}

    def index(self):

        data = []
        for file in os.listdir('./data/livivo/documents/'):
            if file.endswith(".jsonl"):
                with jsonlines.open(os.path.join('./data/livivo/documents', file)) as reader:
                    for obj in reader:
                        title = obj.get('TITLE') or ''
                        title = title[0] if type(title) is list else title
                        abstract = obj.get('ABSTRACT') or ''
                        abstract = abstract[0] if type(abstract) is list else abstract
                        try:
                            data.append({'id': obj.get('DBRECORDID'),
                                         'contents': ' '.join([title, abstract])})
                        except Exception as e:
                            print(e)

        try:
            os.mkdir('./convert/')
        except OSError as error:
            print(error)

        with jsonlines.open('./convert/output.jsonl', mode='w') as writer:
            for doc in data:
                writer.write(doc)

        try:
            os.mkdir('./index/')
        except OSError as error:
            print(error)

        args = ["-collection", "JsonCollection",
                "-generator", "DefaultLuceneDocumentGenerator",
                "-threads", "1",
                "-input", "./convert",
                "-index", "./index/",
                "-storePositions",
                "-storeDocvectors",
                "-storeRaw"]

        JIndexCollection.main(args)
        self.searcher = SimpleSearcher('./index/')
        for file in os.listdir('./data/livivo/documents/'):
            if file.endswith(".jsonl"):
                with jsonlines.open(os.path.join('./data/livivo/documents', file)) as reader:
                    for obj in reader:
                        self.title_lookup[obj.get('DBRECORDID')] = obj.get('TITLE')


    def recommend_publications(self, item_id, page, rpp):

        itemlist = []

        doc_title = self.title_lookup.get(item_id)

        if doc_title is not None:
            hits = self.searcher.search(doc_title[0])

            itemlist = [hit.docid for hit in hits[page*rpp:(page+1)*rpp]]

        return {
            'page': page,
            'rpp': rpp,
            'item_id': item_id,
            'itemlist': itemlist,
            'num_found': len(itemlist)
        }

    def recommend_datasets(self, item_id, page, rpp):

        itemlist = []

        return {
            'page': page,
            'rpp': rpp,
            'item_id': item_id,
            'itemlist': itemlist,
            'num_found': len(itemlist)
        }
