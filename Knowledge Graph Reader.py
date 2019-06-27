import ast
import os
import csv
import sys
import bs4 as bs
import nltk
import networkx as nx

maxInt = sys.maxsize

while True:
    # decrease the maxInt value by factor 10 
    # as long as the OverflowError occurs.

    try:
        csv.field_size_limit(maxInt)
        break
    except OverflowError:
        maxInt = int(maxInt/10)


global_dir = 'C:\\Users\\shash\\Desktop\\'
directory = 'Extractions\\Graph\\'

def get_set(set_string):
    if set_string == 'set()':
        return set()
    else:
        return ast.literal_eval(set_string)

ent_name = {}
with open(global_dir + 'Extractions\\ent_index.txt','r') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter = '\t') 
        for entity in csv_reader:
            ent_name[int(entity['index'])] = entity['name']

G = nx.MultiDiGraph()

# Read 1a
# One way relation

def graph_has_1a_edge(G, v1, v2):
    try:
        x = G[v1][v2]
    except:
        return False
    
    for r in x:
        if x[r] == {'reln' : '1a'}:
            return True
    return False

with open(global_dir + directory + '1a.txt', 'r') as csv_file:
    csv_reader = csv.DictReader(csv_file, delimiter = '\t') 
    
    n = 0
    for line in csv_reader:
        if n % 10000 == 0:
            sys.stdout.flush()
            sys.stdout.write("Line / 10,000 : %d / 2380 \r" % (n / 10000))
        v1 = int(line['ent1'])
        v2 = int(line['ent2'])
        if not graph_has_1a_edge(G, v1, v2):
            G.add_edge(v1, v2, reln = '1a')
        n += 1
        
# Read 1b
# One way relation

with open(global_dir + directory + '1b.txt', 'r') as csv_file:
    csv_reader = csv.DictReader(csv_file, delimiter = '\t') 
    
    n = 0
    for line in csv_reader:
        if n % 10000 == 0:
            sys.stdout.flush()
            sys.stdout.write("Line / 10,000 : %d / 246 \r" % (n / 10000))
        G.add_edge(int(line['ent1']), int(line['ent2']), reln = '1b')
        n += 1

# Read 2
# One way relation

with open(global_dir + directory + '2.txt', 'r') as csv_file:
    csv_reader = csv.DictReader(csv_file, delimiter = '\t') 
    
    n = 0
    for line in csv_reader:
        if n % 10000 == 0:
            sys.stdout.flush()
            sys.stdout.write("Line / 10,000 : %d / 20 \r" % (n / 10000))
        G.add_edge(int(line['ent1']), int(line['ent2']), reln = '2')
        n += 1

# Read 3
# Two way relation

with open(global_dir + directory + '3.txt', 'r') as csv_file:
    csv_reader = csv.DictReader(csv_file, delimiter = '\t') 
    
    n = 0
    for line in csv_reader:
        if n % 10000 == 0:
            sys.stdout.flush()
            sys.stdout.write("Line / 10,000 : %d / 88628 \r" % (n / 10000))
        v1 = line['ent1']
        v2 = line['ent2']
        if v1.isnumeric() and v2.isnumeric():
            v1 = int(v1)
            v2 = int(v2)
            G.add_edge(v1, v2, reln = '3')
            G.add_edge(v2, v1, reln = '3')
            n += 1

# Read 4
# Two way relation
# For 4, check if that reln and zipf label is already present. Add new only if not present

def graph_has_edge(G, v1, v2, label):
    try:
        x = G[v1][v2]
    except:
        return False
    
    for r in x:
        if x[r] == {'reln' : '4', 'label' : label}:
            return True
    return False

with open(global_dir + directory + '4.txt', 'r') as csv_file:
    csv_reader = csv.DictReader(csv_file, delimiter = '\t') 
    
    n = 0
    for line in csv_reader:
        if n % 10000 == 0:
            sys.stdout.flush()
            sys.stdout.write("Line / 10,000 : %d / 88628 \r" % (n / 10000))
        
        v1 = line['ent1']
        v2 = line['ent2']
        if v1.isnumeric() and v2.isnumeric():
            v1 = int(v1)
            v2 = int(v2)
            edge_label = get_set(line['relation'])
            if not graph_has_edge(G, v1, v2, edge_label):
                G.add_edge(v1, v2, reln = '4', label = edge_label)
            if not graph_has_edge(G, v2, v1, edge_label):
                G.add_edge(v2, v1, reln = '4', label = edge_label)
            n += 1

# Sanity check: 
# for every edge G[x][y]:
#     Initialize count for '1a', '1b', '2', '3' to 0
#     Initialize list for reln '4' to a empty list
#     for r in G[x][y]:
#         Update count for reln based on value of G[x][y][r]['reln']
#         For reln of type 4, keep list of labels instead of count
#     Now, count for relns 1a, 1b, 2, 3 should be one or zero
#     List for reln 4 should have no duplicates

def duplicates(set_list):
    for i in range(len(set_list)):
        for j in range(i + 1, len(set_list)):
            if set_list[i] == set_list[j]:
                return True
    return False

for x in G:
    for y in G[x]:
        count = {'1a' : 0, '1b' : 0, '2' : 0, '3' : 0}
        label_list = []
        for r in G[x][y]:
            reln = G[x][y][r]['reln'] 
            if reln != '4':
                count[reln] += 1
            else:
                label_list.append(G[x][y][r]['label'])
        if  duplicates(label_list) or count['1a'] > 1 or count['1b'] > 1 or count['2'] > 1 or count['3'] > 1:
            print('Error in graph edge: ', x, y, G[x][y])

