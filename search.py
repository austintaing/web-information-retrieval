# Austin Taing
# CS 585 Digital Assets
# HW5 - Search

import json
import math
import time

# build tf-idf vectors for corpus
def init(in_file):
    f = open(in_file, 'r')
    content = json.load(f)
    f.close()
    
    term_list = []
    
    # incomplete stopword list
    stops = ['a', 'an', 'the', 'of', 'and', 'for', 'not', 'but', 'so', 'or', 'yet',
             'in', 'out', 'to', 'nor', 'on', 'if', 'then', 'is', 'are', 'were',
             'he', 'him', 'she', 'her', 'it', 'its', 'they', 'their', 'we', 'us']
    
    # Use string-split to tokenize text from each page
    # and create list of terms, filtering non-alphabetic strings
    for i in content:
        content[i]['text'] = content[i]['text'].split()
        content[i]['text'] = [v.lower() for v in content[i]['text'] if v.isalpha() and v not in stops]
        for term in content[i]['text']:
            if term not in term_list:
                term_list.append(term)
    
    # sort term list (probably unnecessary)
    term_list = sorted(term_list)
    
    # Generate term frequency vector for each document
    tfidf = {}
    for i in content:
        tf = {}
        for term in content[i]['text']:
            if term in tf:
                tf[term] += 1
            else:
                tf[term] = 1
        for term in tf:
            tf[term] /= len(content[i]['text'])
        tfidf[i] = tf
        
    # calculate inverse codument frequency for each term, then multiply across 
    # each tf vector to make tf-idf values
    for term in term_list:
        df = 0
        for page in tfidf:
            if term in tfidf[page]:
                df += 1
        idf = math.log(len(term_list) / df)
        for page in tfidf:
            if term in tfidf[page]:
                tfidf[page][term] *= idf
            
    out_data = {'terms' : term_list, 'TF-IDF' : tfidf}
    out_file = open('TFIDF data.json', 'w')
    json.dump(out_data, out_file, indent=4, sort_keys = True)
    #return tfidf, term_index

# 2-norm of vector in program format
def norm(vec):
    sqsum = 0
    for i in vec:
        sqsum += vec[i] ** 2
    n = sqsum ** 0.5
    return n

# dot product of vectors in program format
def dot(a,b):
    d=0
    for term in a:
        if term in b:
            d += a[term]*b[term]
    if norm(a) == 0 or norm(b) == 0:
        return -1
    d /= (norm(a) * norm(b))
    return d

# runs the search queryon the pre-generated data set
def search(q):
    tfidf = open("TFIDF data.json", 'r')
    data = json.load(tfidf)
    tfidf.close()

    query = {}
    for term in q.split():
        if term not in data['terms']:
            print('Query term', term, 'not in corpus and will be ignored')
        else:
            if term in query:
                query[term] += 1
            else:
                query[term] = 1
                
    if len(query) == 0:
        print("No results found")
        return
    
    for term in query:
        query[term] /= len(query)    
    
    results = {}
    for page in data['TF-IDF']:
        dp = dot(query, data['TF-IDF'][page])
        if dp > 0:
            results[page] = dp
            
    ranks = open('Ranks.json','r')
    rank_data = json.load(ranks)
    ranks.close()
    
    for page in results:
        results[page] *= rank_data[page]
    
    ranked_search_result = sorted(results.items(), key=lambda x: x[1], reverse=True)
    
    num_results = 20
    if len(results) < 20:
        num_results = len(results)
    for i in range(num_results):
        print(ranked_search_result[i][0])

def main():
    if input("Enter INIT to re-initialize TF-IDF vectors, or press ENTER to continue to search ") == 'INIT':
        init_file = input("Data file (JSON): ")
        init(init_file)
    
    query = input("\nEnter search query or QUIT to exit: ")
    while query != 'QUIT':
        start = time.time()
        search(query)
        print("Search completed in", time.time()-start, "seconds.")
        query = input("\nEnter search query or QUIT to exit: ")
    
main()