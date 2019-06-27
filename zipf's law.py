import re
from operator import itemgetter
import matplotlib.pyplot as plt
from scipy import special
import numpy as np
import os
import sys
import bs4 as bs
import nltk

global_dir = 'D:\\KGP\\'

def removeNonAscii(text):
    out = ''
    for c in text:
        if ord(c) in range(128):
            out += c
    return out

def stripper(word, strip_list):
    for item in strip_list:
        word = word.strip(item)
    return word

#strip_list = ['.',',']

frequency = {}
bad_files = []

for index in range(1,10):
    directory = global_dir + "man" + str(index) + "\\"
    all_files = os.listdir(directory)
    n = 0
    for file in all_files:
        with open(directory + file, 'rb') as sauce:
            try:
                soup = bs.BeautifulSoup(sauce, 'lxml')
                #words = [stripper(each) for each in re.findall(r'(\b[^\b]{2,9}\b)', soup.get_text())]
                words = nltk.word_tokenize(soup.get_text())
                for word in words:
                    count = frequency.get(word,0)
                    frequency[word] = count + 1
                n += 1
                sys.stdout.flush()
                sys.stdout.write("Index : %d Progress: %d / %d / %d  \r" % (index, n, len(all_files), len(bad_files)) )
            except:
                bad_files.append(directory + file)

import csv
bad_words = []
with open(global_dir + 'word_freq.txt','w') as csv_file:
    fieldnames = ['word','freq']
    csv_writer = csv.DictWriter(csv_file, fieldnames = fieldnames, delimiter = '\t')
    csv_writer.writeheader()

    for word in frequency:
        try:
            new_dict = {'word': word, 'freq' : frequency[word]}
            csv_writer.writerow(new_dict)
        except:
            bad_words.append(word)

frequency = {}
import csv
with open(global_dir + 'word_freq.txt','r') as csv_file:
    csv_reader = csv.DictReader(csv_file, delimiter = '\t')
    for word in csv_reader:
        frequency[word['word']] = word['freq']

for key, value in frequency.items():
    frequency[key] = int(value)

import collections
sorted_frequency = sorted(frequency.items(), key=lambda kv: kv[1], reverse=True)
sorted_frequency

sorted_frequency_dict = {}

for each in sorted_frequency:
    sorted_frequency_dict[each[0]] = each[1]

s = [sorted_frequency_dict[each]  for each in sorted_frequency_dict]

# Take only the words from index lim1 to index lim2 in the sorted frequency dict as the zipf words

lim1 = 1000
lim2 = 30000
print(s[lim1])
print(s[lim2])
plt.plot(range(len(s))[lim1:lim2], s[lim1:lim2])
plt.show()

zip_list =  list(sorted_frequency_dict.items())[lim1:lim2]

zip_words = [each[0] for each in zip_list]

with open(global_dir + 'zip_words.txt','w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)

    for word in zip_words:
        csv_writer.writerow([word])



