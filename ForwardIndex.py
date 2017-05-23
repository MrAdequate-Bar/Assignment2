import sys
import re
import operator
import os
import math
from sys import argv

class Word_Freq:
    def __init__(self):
        self.word_dict = {}
        self.doc_dict = {}
        self.doc_count = 0
        self.word_count = 0
        
    # opens file and tokenizes it, adding it into a dictionary
    def open_f(self, f):
        try:
            with open(f, 'r') as file:
                if os.stat(f).st_size == 0:
                    print("This file is empty: {0}".format(f))
                    return
                for i in file:
                    i = i.lower()
                    i = re.sub(r'\\n+', ' ', i)
                    i = re.sub(r'\W+|_+', ' ', i)
                    i = i.split()
                    for j in i:
                        if j not in self.word_dict:
                            self.word_dict[j] = 1
                        else:
                            self.word_dict[j] += 1
        except IOError:
            print("This file does not exist: {0}".format(f))

    #sorts the dict in descending order and prints it
    def print_word_dict(self, dir):
        for k, v in sorted(self.word_dict.items(), key=operator.itemgetter(1), reverse=True):
            print("{0} - {1}".format(k, v))
            
    def clear_dict(self):
        self.word_dict.clear()
    
    def iterate_directories(self, d):
        #Open each file within a directory and make a forward index of the tokens
        with open('Index.txt', 'a') as f:
            for subdir, dirs, files in os.walk(d):
                for file in files:
                    if file == 'bookkeeping.json' or file == 'bookkeeping.tsv':
                        continue
                    self.open_f(os.path.join(subdir, file))
                    
                    #This nabs the beginning of the directory for URL lookup in the jsons
                    fileNumber = str(subdir)
                    while "\\" in fileNumber:
                        fileNumber = fileNumber[fileNumber.rfind("\\")+1:]
                    
                    #This loop creates the inverted index
                    for (k,tf) in self.word_dict.items():
                        if k not in self.doc_dict:
                            self.doc_dict[k] = [[fileNumber + "/" + str(file), tf]]
                        else:
                            self.doc_dict[k].append([fileNumber + "/" + str(file), tf])
                    self.doc_count += 1
                    self.clear_dict()

            #Exchange the tf out with the tf-idf of the token
            for (k,v) in self.doc_dict.items():
                tmpCount = 0
                for e in v:
                    tf = e[1]
                    N = self.doc_count
                    df = len(self.doc_dict[k])
                    idf = math.log10(N / df)
                    self.doc_dict[k][tmpCount].append(float(format(idf,'.2f')))
                    tf_idf = math.log10(1 + int(tf)) * idf
                    self.doc_dict[k][tmpCount].append(float(format(tf_idf, '.2f')))
                    tmpCount += 1

            #Printing out the inverted index to a text file for testing
            #for (k,v) in self.doc_dict.items():
                #print(str(k) + " - " + str(v) + "\n")
                #f.write(str(k) + " - " + str(v) + "\n")

        #This is simply statistics output
        self.word_count = len(self.doc_dict)
        print("Document Count: " + str(self.doc_count))
        print("Word Count: " + str(self.word_count))
        return self.doc_dict


def query_parse(argv):
    new_query = []
    if len(argv) == 1:
        print "No search terms"
        return
    else:
        for x in argv[1:]:
            new_query.append(x)
        return new_query

def find_docs(token, index_dict):
    if token not in index_dict:
        return 'No results'
    else:
        docs = []
        for e in index_dict[token]:
            docs.append(e[0])
        return docs

def make_url_dict(d):
    url_dict = {}
    for subdir, dirs, files in os.walk(d):
        for file in files:
            if file == 'bookkeeping.json' or file == 'bookkeeping.tsv':
                f = os.path.join(subdir, file)
                with open(f, 'r') as document:
                    if os.stat(f).st_size == 0:
                        print("This file is empty: {0}".format(f))
                        return
                    for i in document: #for each line in the document
                        '''
                        "0/0": "www.ics.uci.edu/~rickl/courses/cs-171/2016-smrq-cs171/StudentResources/StudentResources_tournament/Wumpus_World_tournament/Worlds_20160712/TestWorld5x5_787.txt",
                        '''
                        i = i.split(':')
                        if len(i) > 1:
                            s1 = i[0].strip(' "\'\t\r\n')
                            s2 = i[1].strip(' "\'\t\r\n')
                            url_dict[s1] = s2
    return url_dict

def find_urls(url_dict, docIDs):
    results = []
    for e in docIDs:
        if e in url_dict:
            results.append(url_dict[e])
            
    return results
        
if __name__ == "__main__":
    try:
        #We store all data, such a tf, idf, tf-idf, type (e.g. title, bold, h1, h2, h3)
        #We still need to append types
        
        #Accepts a query of any length
        query = query_parse(sys.argv)
        print(query[0])

    	rootdir = 'WEBPAGES_CLEAN'
        w = Word_Freq()
        index = w.iterate_directories(rootdir)
        
        #We need to return all docIDs for the first word in the query M1 not M2
        docIDs = find_docs(query[0], index)
        print(docIDs)
        
        #We need to use those docIDs to find the URLs and give them to the user
        url_dict = make_url_dict(rootdir)
        results = find_urls(url_dict, docIDs)
        print("Search Results \n")
        for e in results:
            print(str(e) + "\n")
        
        print("Search Completed")

    except IndexError:
        print("No file was entered.")
