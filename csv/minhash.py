from datasketch import MinHash, MinHashLSH


def create_minhash(text, ngram_range=(1, 1)):
    tokens = text.lower().split()
    ngrams = []
    for n in range(ngram_range[0], ngram_range[1] + 1):
        ngrams.extend(zip(*[tokens[i:] for i in range(n)]))
    minhash = MinHash()
    for gram in ngrams:
        minhash.update(' '.join(gram).encode('utf-8'))
    return minhash


def create_lsh_index(documents, threshold=0.8, num_perm=128, ngram_range=(1, 1)):
    lsh = MinHashLSH(threshold=threshold, num_perm=num_perm)
    for idx, doc in documents.items():
        minhash = create_minhash(doc, ngram_range=ngram_range)
        lsh.insert(str(idx), minhash)
    return lsh


# Query similar documents and return the one with the highest score
def query_similar_documents(query_text, lsh_index, documents, ngram_range=(1, 1)):
    query_minhash = create_minhash(query_text, ngram_range=ngram_range)
    result = lsh_index.query(query_minhash)
    if not result:
        return None
    best_match = None
    highest_score = 0
    for doc_id in result:
        doc_id = int(doc_id)
        similarity_score = query_minhash.jaccard(create_minhash(documents[doc_id], ngram_range=ngram_range))
        if similarity_score > highest_score:
            highest_score = similarity_score
            best_match = (doc_id, similarity_score)
    return best_match
