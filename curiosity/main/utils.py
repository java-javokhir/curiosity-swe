from collections import defaultdict
from gensim import corpora
import webvtt
import nltk

nltk.download('punkt')
from nltk.tokenize import sent_tokenize
from gensim import models
from gensim import similarities
import os

def dict_corp(file):
    episode = webvtt.read(file)

    documents = ''

    for caption in episode:
        documents += caption.text

    documents = sent_tokenize(documents)

    # remove common words and tokenize
    stoplist = set('for a of the and to in you that is i this so it we have'.split())
    texts = [
        [word for word in document.lower().split() if word not in stoplist]
        for document in documents
    ]

    # remove words that appear only once
    frequency = defaultdict(int)
    for text in texts:
        for token in text:
            frequency[token] += 1

    texts = [
        [token for token in text if frequency[token] > 1]
        for text in texts
    ]

    dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]

    return dictionary, corpus, documents


def meta_dict_corp():
    dictionary = corpora.Dictionary()
    corpus = []
    meta_documents = []
    cnt = 0

    for file in os.scandir('/Users/javohir/Documents/vttt/'):
        if '.vtt' in file.name:
            small_dictionary, small_corpus, documents = dict_corp(file)

            dictionary.merge_with(small_dictionary)
            corpus += small_corpus
            # meta_documents += documents
            meta_documents.append(
                {'episode_num': file.name, 'content': documents, 'doc_num_range': (cnt, cnt + len(documents))})

            cnt += len(documents)

    corpora.MmCorpus.serialize('/tmp/deerwester.mm', corpus)  # store to disk, for later use
    dictionary.save('/tmp/dictionary')

    return meta_documents


def train_model():
    corpus = corpora.MmCorpus('/tmp/deerwester.mm')
    meta_dictionary = corpora.Dictionary.load('/tmp/dictionary')

    lsi = models.LsiModel(corpus, id2word=meta_dictionary, num_topics=70)

    lsi.save('/tmp/lsi.model')


def query_result(query):
    doc = query

    corpus = corpora.MmCorpus('/tmp/deerwester.mm')
    meta_dictionary = corpora.Dictionary.load('/tmp/dictionary')
    meta_documents = meta_dict_corp()

    lsi = models.LsiModel.load('/tmp/lsi.model')

    doc = doc.lower().split()
    vec_bow = meta_dictionary.doc2bow(doc)
    vec_lsi = lsi[vec_bow]  # convert the query to LSI space

    index = similarities.MatrixSimilarity(lsi[corpus])  # transform corpus to LSI space and index it

    index.save('/tmp/deerwester.index')
    index = similarities.MatrixSimilarity.load('/tmp/deerwester.index')

    sims = index[vec_lsi]  # perform a similarity query against the corpus
    #print(list(enumerate(sims)))  # print (document_number, document_similarity) 2-tuples

    sims = sorted(enumerate(sims), key=lambda item: -item[1])

    for doc_position, doc_score in sims:
        for episode in meta_documents:
            if doc_position in range(episode['doc_num_range'][0], episode['doc_num_range'][1]):
                episode_vtt = webvtt.read('/Users/javohir/Documents/vttt/' + episode['episode_num'])
                for caption in episode_vtt:
                    if episode['content'][doc_position - episode['doc_num_range'][0]] in caption.text:
                        timestamp = [int(x) for x in caption.start.replace('.', ':').split(':')[:-1]]
                        timestamp = timestamp[0] * 3600 + timestamp[1] * 60 + timestamp[-1]
                        return [s for s in episode['episode_num'].split('_') if s.isdigit()][0], timestamp

