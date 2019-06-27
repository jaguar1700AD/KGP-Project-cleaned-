# This program merges all the csv files to create a single csv file that conatins all the entities along with their
# various features

import csv
import os
import ast
import sys
import string

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

def Merge(dict1, dict2):
    for key in dict2:
        if key in dict1:
            dict1[key] += dict2[key]
        else:
            dict1[key] = dict2[key]

def bitwise_or(list1, list2):
    for i in range(len(list1)):
        list1[i] = list1[i] or list2[i]
        
def get_set(set_string):
    if set_string == 'set()':
        return set()
    else:
        return ast.literal_eval(set_string)
    
def rem_end(text, suffix):
    if text.endswith(suffix):
        return text[:-len(suffix)]
    return text

def is_title(name):
    if len(name) >= 3 and name[-3] == '(' and name[-2].isdigit() and name[-1] == ')':
        return True
    else:
        return False

def valid_entity(name):
    if is_title(name) and (len(name) == 3 or name[-4] in string.punctuation):
        return False
    return True

entities = {}
# Each entity will have 4 fields : type, context_dict, co_occ

for section in range(1, 10): 
    
    directory = global_dir + 'Extractions\\man' + str(section) + '\\'
    all_files = os.listdir(directory)
    n = 1

    for file in all_files:
        with open(directory + file,'r') as csv_file:

            sys.stdout.flush()
            sys.stdout.write("Section : %d Progress: %d / %d \r" % (section, n, len(all_files)))

            csv_reader = csv.DictReader(csv_file, delimiter = '\t') 

            for entity in csv_reader:

                _name = entity['name']
                
                if valid_entity(_name):
                    
                    _type = get_set((entity['type']))
                    _context_dict = ast.literal_eval(entity['context_dict'])
                    _co_occ = get_set((entity['co_occ']))

                    if _name not in entities:
                        entities[_name] = {}
                        entities[_name]['type'] = _type
                        entities[_name]['context_dict'] = _context_dict
                        entities[_name]['co_occ'] = _co_occ
                    else:
                        entities[_name]['type'] = entities[_name]['type'] | _type
                        Merge(entities[_name]['context_dict'], _context_dict)
                        entities[_name]['co_occ'] = entities[_name]['co_occ'] | _co_occ

            n += 1

# Assign index and write to file
file_name = 'ent_index.txt'
with open(global_dir + 'Extractions\\' + file_name, 'w') as write_file:
    fieldnames = ['index', 'name']
    writer = csv.DictWriter(write_file, fieldnames=fieldnames, delimiter = '\t')
    writer.writeheader()
    
    n = 0
    for name in entities:
        new_dict = {'index' : n, 'name' : name}
        writer.writerow(new_dict)
        n += 1

# Read the index
ent_dict = {}
with open(global_dir + 'Extractions\\ent_index.txt', 'r') as ent_file:
    reader = csv.DictReader(ent_file, delimiter = '\t')
    for entity in reader:
        ent_dict[entity['name']] = int(entity['index'])

with open(global_dir + 'Extractions\\index_merged_extractions.txt', 'w') as write_file:
    fieldnames = ['index', 'type', 'context_dict', 'co_occ']
    writer = csv.DictWriter(write_file, fieldnames=fieldnames, delimiter = '\t')
    writer.writeheader()
    
    for name, entity in entities.items():

        new_dict = {}
        new_dict['index'] = ent_dict[name]
        new_dict['type'] = entity['type']
        new_dict['context_dict'] = entity['context_dict']
        new_dict['co_occ'] = set()
        for name in entity['co_occ']:
            if valid_entity(name):
                new_dict['co_occ'].add(ent_dict[name])

        writer.writerow(new_dict)

