import ast
import os
import csv
import sys
import bs4 as bs
import nltk

maxInt = sys.maxsize

while True:
    # decrease the maxInt value by factor 10 
    # as long as the OverflowError occurs.

    try:
        csv.field_size_limit(maxInt)
        break
    except OverflowError:
        maxInt = int(maxInt/10)

global_dir = 'D:\\KGP\\'

zip_words = set()
with open(global_dir + 'zip_words.txt','r') as csv_file:
    csv_reader = csv.reader(csv_file)
    for word in csv_reader:
        zip_words.add(word[0])
zip_len = len(zip_words)

def get_set(set_string):
    if set_string == 'set()':
        return set()
    else:
        return ast.literal_eval(set_string)
    
def is_title(name):
    if len(name) >= 3 and name[-3] == '(' and name[-2].isdigit() and name[-1] == ')':
        return True
    else:
        return False

def valid_entity(name):
    if is_title(name) and (len(name) == 3 or name[-4] in string.punctuation):
        return False
    return True

ent_index = {}

length = 0
with open(global_dir + 'Extractions\\ent_index.txt','r') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter = '\t') 
        for entity in csv_reader:
            ent_index[entity['name']] = int(entity['index'])
            length = max([length, int(entity['index'])])
length += 1 
            
ent_name = [0] * length
with open(global_dir + 'Extractions\\ent_index.txt','r') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter = '\t') 
        for entity in csv_reader:
            ent_name[int(entity['index'])] = entity['name']

entities = [0] * length
with open(global_dir + 'Extractions\\index_merged_extractions.txt','r') as csv_file:

        csv_reader = csv.DictReader(csv_file, delimiter = '\t') 

        for entity in csv_reader:
            _index = int(entity['index'])
            entities[_index] = {}
            entities[_index]['type'] = get_set(entity['type'])
            entities[_index]['context_dict'] = ast.literal_eval(entity['context_dict'])
            entities[_index]['co_occ'] = get_set(entity['co_occ'])
            #entities[entity['name']]['zipf'] = get_set(entity['zipf_vector'])

# 1a Manpage title entity -> entity
# One way relation

file_name = '1a.txt'
with open(global_dir + 'Extractions\\Graph\\' + file_name, 'w') as file_int:
    fieldnames = ['ent1','ent2']
    csv_writer = csv.DictWriter(file_int, fieldnames=fieldnames, delimiter = '\t')
    csv_writer.writeheader()

    for section in range(1, 10):

        directory = global_dir + 'Extractions\\man' + str(section) + '\\'
        anc_directory = global_dir + 'Extractions\\Anchors\\man' + str(section) + '\\'
        all_files = os.listdir(directory)
        n = 1

        for file in all_files:

            sys.stdout.flush()
            sys.stdout.write("Section : %d Progress: %d / %d \r" % (section, n, len(all_files)))
            
            title_set = set()
            with open(anc_directory + file,'r') as csv_file:
                csv_reader = csv.DictReader(csv_file, delimiter = '\t') 
                for line in csv_reader:
                    title_set.add(line['title'])

            with open(directory + file,'r') as csv_file:
                csv_reader = csv.DictReader(csv_file, delimiter = '\t') 
                for entity in csv_reader:
                    name = entity['name']
                    if name not in title_set:
                        for title in title_set:
                            new_dict = {'ent1' : ent_index[title], 'ent2' : ent_index[name]}
                            csv_writer.writerow(new_dict)
            n += 1

# 1b +- k window
# One way relation

file_name = '1b.txt'
with open(global_dir + 'Extractions\\Graph\\' + file_name, 'w') as file_int:
    fieldnames = ['ent1','ent2']
    csv_writer = csv.DictWriter(file_int, fieldnames=fieldnames, delimiter = '\t')
    csv_writer.writeheader()
    for index1 in range(length):
        for index2 in entities[index1]['co_occ']:
            new_dict = {'ent1' : index1, 'ent2' : index2}
            csv_writer.writerow(new_dict)

# 2 Anchor link
# One way relation

bad = 0

file_name = '2.txt'
with open(global_dir + '\\Extractions\\Graph\\' + file_name, 'w') as file_int:
    fieldnames = ['ent1','ent2']
    csv_writer = csv.DictWriter(file_int, fieldnames=fieldnames, delimiter = '\t')
    csv_writer.writeheader()

    for section in range(1, 10):

        directory = global_dir + 'Extractions\\Anchors\\man' + str(section) + '\\'
        all_files = os.listdir(directory)
        n = 1

        for file in all_files:

            sys.stdout.flush()
            sys.stdout.write("Section : %d Progress: %d / %d \r" % (section, n, len(all_files)))

            with open(directory + file,'r') as csv_file:
                csv_reader = csv.DictReader(csv_file, delimiter = '\t') 
                for line in csv_reader:
                    for link in get_set(line['links']):
                        new_dict = {'ent1' : ent_index[line['title']], 'ent2' : ent_index[link]}
                        csv_writer.writerow(new_dict)

            n += 1

# 3 Similar context_dict link from holling
# Two way relation

cont_list = [0] * length

for i in range(length):
    cont_list[i] = entities[i]['context_dict']
        
num = len(cont_list)

import random
random.seed(30)
random.shuffle(cont_list)

# Calculate occurence_count for all entities
occ_count = {}
for index in range(length):
    entity = entities[index]
    occ_count[index] = 0
    for context in entity['context_dict']:
        occ_count[index] += entity['context_dict'][context]

file_name = '3.txt'
with open(global_dir + 'Extractions\\Graph\\' + file_name, 'a', newline = '') as file_int:
    
    fieldnames = ['ent1','ent2']
    csv_writer = csv.DictWriter(file_int, fieldnames=fieldnames, delimiter = '\t')
    csv_writer.writeheader()
    
    threshold = 0.9 # 2 entities will be connected by an edge if no of common contexts > threshold * no of contexts for both entities
    lim1 = 0
    lim2 = num
    for i in range(lim1, lim2):

        sys.stdout.flush()
        sys.stdout.write("%d / %d \r" % (i - lim1 + 1, lim2 - lim1))

        cont1 = cont_list[i]

        for j in range(i + 1, num):

            cont2 = cont_list[j]

            n1 = 0 # No of common contexts of entity1
            n2 = 0 # No of common contexts of entity2

            for context in cont1:
                if context in cont2:
                    n1 += cont1[context]
                    n2 += cont2[context]


            if (n1 >= threshold * occ_count[i]) and (n2 >= threshold * occ_count[j]):
                new_dict = {'ent1' : i, 'ent2' : j}
                csv_writer.writerow(new_dict)

# 4 zipf based relation
# Two way relation

window_size = 5

four_ent_set = set()
four_index = {}

max_ent_len = 0
for name in ent_name:
    cand = name.replace(' ', '')
    four_ent_set.add(cand)
    four_index[cand] = ent_index[name]
    max_ent_len = max([max_ent_len, len(nltk.word_tokenize(name))])

# Find entity pairs between +- window_size
# word_list is list of [entity_index, start_word_index, entity_length]
# Remove pairs between the same words in the end

def find_pairs(word_list):
    n = len(word_list)
    pairs = []
    for i in range(n):
        start_limit_up = word_list[i][1] + word_list[i][2] + window_size
        start_limit_down = word_list[i][1] + word_list[i][2]
        j = i + 1
        while j < n and word_list[j][1] <= start_limit_up and word_list[j][1] >= start_limit_down:
            pairs.append([i, j])
            j += 1
    
    for ind, pair in enumerate(pairs):
        if word_list[pair[0]][0] == word_list[pair[1]][0]:
            pairs[ind] = None
            
    return pairs

file_name = '4.txt'
with open(global_dir + '\\Extractions\\Graph\\' + file_name, 'w') as file_int:
    fieldnames = ['ent1','relation', 'ent2']
    csv_writer = csv.DictWriter(file_int, fieldnames=fieldnames, delimiter = '\t')
    csv_writer.writeheader()

    for section in range(1, 10):
        directory = global_dir + 'man' + str(section) + '\\'
        all_files = os.listdir(directory)
        n = 1
        for file in all_files:
            
            with open(directory + file, 'rb') as sauce:

                sys.stdout.flush()
                sys.stdout.write("Section : %d Progress: %d / %d \r" % (section, n, len(all_files)))

                soup = bs.BeautifulSoup(sauce, 'lxml')

                sentences = nltk.sent_tokenize(soup.get_text())

                for sentence in sentences:

                    word_list = []
                    words = nltk.word_tokenize(sentence)

                    for start in range(len(words)):
                        for length in range(1, min(len(words) - start, max_ent_len) + 1):

                            candidate = ''.join(words[start: start + length])

                            if candidate in four_ent_set:
                                word_list.append([four_index[candidate], start, length])

                            if is_title(candidate):
                                cand = candidate[:-3]
                                if cand in four_ent_set:
                                    word_list.append([four_index[cand], start, length])
                            else:
                                cand = candidate + '(' + str(section) + ')'
                                if cand in four_ent_set:
                                    word_list.append([four_index[cand], start, length])
                    
                    pairs = find_pairs(word_list)
                    
                    for pair in pairs:
                        
                        if pair == None:
                            continue
                        
                        list0 = word_list[pair[0]]
                        list1 = word_list[pair[1]]
                        
                        start_ind = list0[1] + list0[2]
                        end_in = list1[1]
                        relation = set(words[start_ind : end_in]) & zip_words
                        
                        try:
                            #new_dict = {'file' : words, 'ent1' : ent_name[list0[0]], 'relation' : relation, 'ent2' : ent_name[list1[0]]}
                            new_dict = {'ent1' : list0[0], 'relation' : relation, 'ent2' : list1[0]}
                            csv_writer.writerow(new_dict)
                        except:
                            pass
                n += 1



