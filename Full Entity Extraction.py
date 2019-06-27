import bs4 as bs
import urllib.request
import regex
import nltk
from nltk.corpus import stopwords
import csv
import os
import sys
import traceback
import re
import ast
import string

global_dir = 'D:\\KGP\\'

def rem_beg(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text

def rem_end(text, suffix):
    if text.endswith(suffix):
        return text[:-len(suffix)]
    return text

def rem_both(text, pattern):
    return rem_suffix(rem_prefix(text,pattern),pattern)

def removeNonAscii(text):
    out = ''
    for c in text:
        if ord(c) in range(128):
            out += c
    return out

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
    
def post_process(entities, type_dict = None):
    
    for each in entities.copy():
        
        entity = ' '.join(each.split()) # Change multiple space to single space and remove \n
        entity = removeNonAscii(entity) # Remove non ascii chars
        if len(entity) >= 4 and entity[-4] == ' ' and entity[-3] == '(' and entity[-2].isdigit() and entity[-1] == ')':
            entity = entity[:-4] + entity[-3:] # Change grep (1) to grep(1)
        if len(entity) <= 1 or (not valid_entity(entity)): # Remove entities with length 1 or 0 and invalid entities
            entities.discard(each)
            if type_dict != None:
                type_dict.pop(each, None)
            continue
        
        if entity != each:
            entities.discard(each)
            entities.add(entity)
            if type_dict != None:
                type_dict[entity] = type_dict[each]
                del type_dict[each]
        
        
    # Remove stopwords 
    del_words = stopwords.words("english")
    for word in del_words:
        entities.discard(word)
        entities.discard(word[0].upper() + word[1:])
        entities.discard(word.upper())   
    if type_dict != None:
        for word in del_words:
            type_dict.pop(word, None)
            type_dict.pop(word[0].upper() + word[1:], None)
            type_dict.pop(word.upper(), None)
        

    # Remove grep if grep(1) is already present
    for each in entities.copy():
        if len(each) >= 3 and each[-3] == '(' and each[-2].isdigit() and each[-1] == ')':
            del_entity = each[:-3]
            entities.discard(del_entity)
            if type_dict != None:
                type_dict.pop(del_entity, None)

not_man_page = []

for section in range(1,10):
    directory = global_dir + "man" + str(section) + "\\"
    
    file_no = 1

    all_files = os.listdir(directory)
    
    for file in all_files:
            
        sys.stdout.flush()
        sys.stdout.write("Section : %d Progress: %d / %d \r" % (section, file_no, len(all_files)))

        #----------------------------------------------------------------------------------------------------------------------

        # Find the title entities

        sauce = open(directory + file, 'rb') 
        soup = bs.BeautifulSoup(sauce, 'lxml')
        name_code = re.search(r'<b> *((NAME)|(Name)) *</b>([\s\S]*?)<pre>([\s\S]*?)</pre>', str(soup))
        desc_code =  re.search('((<b> *DESCRIPTION *</b>)|(<b> *Description *</b>)|(<b> *Detailed *</b> <b> *Description *</b>))([\s\S]*?)<pre>([\s\S]*?)</pre>', str(soup))

        if desc_code == None and name_code == None:
            not_man_page.append(directory + file)
            continue

        # Find the code for the NAME section
        if name_code == None:
            name_code = soup.title.text
        else:
            name_code = name_code.group(5)

        # Extract the title from the name code
        title = name_code.replace('\n','').strip()

        title = regex.search(r'(.*?)[ ]+([\p{Pd}]|(<b>[\p{Pd}]</b>))', title)
        if title == None:
            title = re.search(r'[^.]+', file).group(0).replace('_COLON_',':')
        else:
            title = title.group(1)

        all_title = title.split(', ')

        # Append '(section id)' to the title
        for idx, title in enumerate(all_title):
            all_title[idx] = all_title[idx].replace('<b>','').replace('</b>','').strip()
            all_title[idx] = all_title[idx] + '(' + str(section) + ')'

        all_title = set(all_title)

        #----------------------------------------------------------------------------------------------------------------------

        # Find all href words/phrases

        all_href = set()
        for url in soup.find_all('a'):
            if url.text != '' and '\n' not in url.text:
                all_href.add(url.text)

        #----------------------------------------------------------------------------------------------------------------------

        all_b = set()
        all_i = set()

        if (desc_code != None):

            desc_code = desc_code.group(6)

            #----------------------------------------------------------------------------------------------------------------------

            # Find all boldface words from the description

            for met in re.findall(r'((<b>(.*?)</b>\s?)+)', str(desc_code)):
                word = (''.join(''.join(met[0].split('<b>')).split('</b>'))).replace('\n',' ').strip()
                if (len(word) > 1):
                    all_b.add(word)

            #----------------------------------------------------------------------------------------------------------------------

            # Find all italics words from the description

            for met in re.findall(r'((<i>(.*?)</i>\s?)+)', str(desc_code)):
                word = (''.join(''.join(met[0].split('<i>')).split('</i>'))).replace('\n',' ').strip()
                if (len(word) > 1):
                    all_i.add(word) 

            #----------------------------------------------------------------------------------------------------------------------

        # Find manpage mentions 

        all_mentions = re.findall(r'[^ \n]+[ \n]+\([0-9]\)', soup.get_text())
        all_mentions = {v.replace(' ','').replace('\n','') for v in all_mentions}

        #----------------------------------------------------------------------------------------------------------------------

        # Find all system file mentions

        all_sys_files = set()
        for match in re.findall(r'([ \n=]|^)((/[^/ ,]{2,})+/?)', str(soup.get_text())):
            all_sys_files.add(match[1].replace('\n',''))

        #----------------------------------------------------------------------------------------------------------------------

        # All caps continuous words

        all_caps = set()
        for met in re.findall(r'[ \n]+(([A-Z_]{2,}\s)+)', str(soup.get_text())):
            all_caps.add(met[0].strip().replace('\n',' ')) 

        #----------------------------------------------------------------------------------------------------------------------

        # All first letter cap mid sentence words 
        # !!!! Currently includes all mid sentence all caps continous words (it is a necessity)

        all_first_caps = set()
        for met in re.findall(r'([A-Za-z0-9\,][ ]+)(([A-Z]([A-Za-z0-9]|[.-][A-Za-z0-9])+[ ]+)*([A-Z][A-Za-z0-9\.-]+([, \n\.]|$)))', str(soup.get_text())):
            all_first_caps.add(met[1].strip().replace('\n',' ').strip('.').strip(','))

        #----------------------------------------------------------------------------------------------------------------------

        # List of proper nouns

        sentences = nltk.sent_tokenize(soup.get_text())

        sent_words = []
        sent_tagged = []

        for sentence in sentences:
            words = nltk.word_tokenize(sentence)
            sent_words.append(words)
            sent_tagged.append(nltk.pos_tag(words))

        chunkGram = '''Chunk: {(<NNP>(<,>|<CC>))+<NNP>}'''
        chunkParser = nltk.RegexpParser(chunkGram)
        all_NP_list = set()

        for idx, sentence in enumerate(sentences):
            chunked = chunkParser.parse(sent_tagged[idx])
            for tree in chunked.subtrees(filter=lambda t: t.label() == 'Chunk'):
                for ind in range(0, len(tree.leaves()), 2):
                    all_NP_list.add(tree.leaves()[ind][0])

        #----------------------------------------------------------------------------------------------------------------------

        # Find anchor entities

        # Find the 'SEE ALSO' section's html code 
        see_also_code = re.search(r'<b>SEE</b> <b>ALSO</b>([\s\S]*?)<pre>([\s\S]*?)</pre>', str(soup))
        all_anchor = set()

        if (see_also_code != None):

            see_also_code = see_also_code.group(2)

            # Find the entities corresponding to href tags
            all_anchor = [each[1] + each[2] for each in re.findall(r'<a(.*?)>(.*?)</a></u>(\([0-9]\))', see_also_code)]
            all_anchor = set(all_anchor)

        #----------------------------------------------------------------------------------------------------------------------

        # A dictionary that will store the type of each entity
        # The dict will have a 9 dim binary vector corresponding to each entity with indices indicating the following:

        # 0 title
        # 1 href
        # 2 bold
        # 3 italics
        # 4 manpage mention
        # 5 system file mention
        # 6 All Caps continuous words
        # 7 First letter cap mid sentence words
        # 8 List of NNP
        # 9 Anchor

        type_dict = {}

        # Add one entity to the type_dict
        def add_type(entity, entity_type):
            if entity not in type_dict:
                type_dict[entity] = set()
            type_dict[entity].add(entity_type)

        # Add an entire section of entities to the type_dict
        def add_section(entity_list, section_id):
            for entity in entity_list:
                add_type(entity, section_id)

        # Populate the type_dict
        add_section(all_title, 0)
        add_section(all_href, 1)
        add_section(all_b, 2)
        add_section(all_i, 3)
        add_section(all_mentions, 4)
        add_section(all_sys_files, 5)
        add_section(all_caps, 6)
        add_section(all_first_caps, 7)
        add_section(all_NP_list, 8)
        add_section(all_anchor, 9)

        #----------------------------------------------------------------------------------------------------------------------

        # Build the full entity list

        # ???????????????????
        # Should grep -e like commands be grep -e(1)

        entities = all_title | all_href | all_b | all_i | all_mentions | all_sys_files | all_caps | all_first_caps | all_NP_list | all_anchor
        post_process(entities, type_dict)

        #----------------------------------------------------------------------------------------------------------------------

        # Find out which entities occur in a +- k window (but in the same sentence) for all entities

        k = 2

        co_occ_dict = {}
        for entity in entities:
            co_occ_dict[entity] = set()

        # word_list is list of [orig_entity, start_word_index, entity_length]
        # Remove pairs between the same words in the end

        def find_pairs(word_list):
            n = len(word_list)

            for i in range(n):
                start_limit_up = word_list[i][1] + word_list[i][2] + k
                start_limit_down = word_list[i][1] + word_list[i][2]
                j = i + 1
                while j < n and word_list[j][1] <= start_limit_up and word_list[j][1] >= start_limit_down:
                    if word_list[i][0] != word_list[j][0]:
                        co_occ_dict[word_list[i][0]].add(word_list[j][0])
                        co_occ_dict[word_list[j][0]].add(word_list[i][0])
                    j += 1

        #------------------------------------------------------------------------------------------------

        # Holling Algo Implementation

        context_dict = {}
        context_word_dict = {}

        holl_ent_set = set()
        holl_index = {}

        max_ent_len = 0
        for name in entities:
            cand = name.replace(' ', '')
            holl_ent_set.add(cand)
            holl_index[cand] = name
            max_ent_len = max([max_ent_len, len(nltk.word_tokenize(name))])
            context_dict[name] = {}
            context_word_dict[name] = {}

        for index, sentence in enumerate(sentences):

            word_list = []

            words = sent_words[index]
            tagged = sent_tagged[index]

            for start in range(len(words)):
                for length in range(1, min(len(words) - start, max_ent_len) + 1):

                    candidate = ''.join(words[start: start + length])

                    if candidate in holl_ent_set:
                        word_list.append([holl_index[candidate], start, length])

                    if is_title(candidate):
                        cand = candidate[:-3]
                        if cand in holl_ent_set:
                            word_list.append([holl_index[cand], start, length])
                    else:
                        cand = candidate + '(' + str(section) + ')'
                        if cand in holl_ent_set:
                            word_list.append([holl_index[cand], start, length])

            c = 2
            # context_dict[entity] is a list of tuples of the form [context, count] where context is a list and count is the no of 
            # occurences of that context


            for word_ind in range(len(word_list)):

                orig_entity = word_list[word_ind][0]
                start = word_list[word_ind][1]
                end = start + word_list[word_ind][2] - 1

                context = ""
                word_context = ""

                for i in range(start - c, 0):
                    context += '$ '
                    word_context += '$ '

                for i in range(max(start - c, 0), start):
                    context += tagged[i][1] + ' '
                    word_context += words[i] + ' '

                context += '@@'
                word_context += '@@'

                for i in range(end + 1, min(len(words) - 1, end + c) + 1):
                    context += ' ' + tagged[i][1]
                    word_context += ' ' + words[i]

                for i in range(len(words), end + c + 1):
                    context += ' $'
                    word_context += ' $'

                if context in context_dict[orig_entity]: # if context is already present in the context list, just increment count
                    context_dict[orig_entity][context] += 1
                else: # Add new context
                    context_dict[orig_entity][context] = 1

                if word_context in context_word_dict[orig_entity]: # if context is already present in the context list, just increment count
                    context_word_dict[orig_entity][word_context] += 1
                else: # Add new context
                    context_word_dict[orig_entity][word_context] = 1

            find_pairs(word_list)

        #----------------------------------------------------------------------------------------------------------------------

        # Calculate occurence_count for all entities
        occ_count = {}
        for entity in entities:
            occ_count[entity] = 0
            for context in context_dict[entity]:
                occ_count[entity] += context_dict[entity][context]

        # Check if any context_count is 0 for any entity(which means an error)
        # Also, delete also those from the entity list for now 

        for entity in entities.copy():
            if occ_count[entity] == 0:
                entities.discard(entity)

        #--------------------------------------------------------------------------------------------------------------

        # Clear the context dict of non ascii terms

        for entity in entities:
            context_dict[entity] = {removeNonAscii(u):v for u,v in context_dict[entity].items()}

        #----------------------------------------------------------------------------------------------------------------------

        # Write the extractions of this manpage to a file

        file_name = rem_end(file,'.html') + '.txt'

        with open(global_dir + 'Extractions\\man' + str(section) + '\\' + file_name, 'w') as file_int:
            fieldnames = ['name','type','context_dict','co_occ']
            csv_writer = csv.DictWriter(file_int, fieldnames=fieldnames, delimiter = '\t')
            csv_writer.writeheader()
            for entity in entities:
                new_dict = {}
                new_dict['name'] = entity
                new_dict['type'] = type_dict[entity]
                new_dict['context_dict'] = context_dict[entity]
                new_dict['co_occ'] = co_occ_dict[entity]
                csv_writer.writerow(new_dict)

        # Recalculate all_title entities
        all_title = set()
        for entity in entities:
            if 0 in type_dict[entity]:
                all_title.add(entity)
                
        # Recalculate all_anchor entities
        all_anchor = set()
        for entity in entities:
            if 9 in type_dict[entity]:
                all_anchor.add(entity)

        with open(global_dir + 'Extractions\\Anchors\\man' + str(section) + '\\' + file_name, 'w') as file_int:
            fieldnames = ['title','links']
            csv_writer = csv.DictWriter(file_int, fieldnames=fieldnames, delimiter = '\t')
            csv_writer.writeheader()

            for title in all_title:
                new_dict = {}
                new_dict['title'] = title
                new_dict['links'] = all_anchor
                csv_writer.writerow(new_dict)

        #----------------------------------------------------------------------------------------------------------------------

        file_no += 1


