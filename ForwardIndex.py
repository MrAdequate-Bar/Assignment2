import sys
import re
import operator
import os

class Word_Freq:
    def __init__(self):
        self.word_dict = {}
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
    # def add_index(self):
    # 	f = open('D:/RL/Desktop/CS121/Index.txt', 'w')
    # 	for (k,v) in self.word_dict.items():
    # 		f.write(k, v)
    # 	f.write("\n")
    # 	f.close
    def iterate_directories(self, d):
        with open('D:/RL/Desktop/CS121/Index.txt', 'a') as f:
            for subdir, dirs, files in os.walk(d):
                for file in files:
                    self.open_f(os.path.join(subdir, file))
                    f.write(str(subdir) + "/" + str(file) + " - ")
                    for (k,v) in self.word_dict.items():
                        f.write(k + " " + str(v))
                    f.write("\n")
                    #add_index()
                    self.clear_dict()


if __name__ == "__main__":
    try:
    	rootdir = 'D:/RL/Desktop/CS121/M1'
        w = Word_Freq()
        w.iterate_directories(rootdir)
        #w.open_file(sys.argv[1])
        #w.print_word_dict()
        print("Done")
    except IndexError:
        print("No file was entered.")
