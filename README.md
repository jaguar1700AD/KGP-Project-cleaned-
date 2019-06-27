# KGP-Project-cleaned-

Expected directory structure:\
\
global_dir
- man1 ... man9
- Extractions
  - man1 ... man9
  - Anchors
    - man1 ... man9
  - Graph
\
\
The global_dir variable is defined at the top of every script. It can be changed to any custom value. (Default is D:\KGP\)
The folders as shown in the directory structure above have to be created manually by the user

The various scripts are:
1. downloader: Downloads all the manpages to the local pc. wget can be used instead of this in Ubuntu OS. Files are downloaded to 
							 global_dir\man1...man9 according to their respective sections
2. Full Entity Extraction: Extracts entities from the downloaded files. Entities for each manpage are stored in a separate txt file in 
													 global_dir\Extractions\man(section)\. Anchor entities (from the SEE ALSO section of manpages) are stored in 
													 global_dir\Extractions\Anchors\man(section)\
3. Merger: Merges the entities from the txt files of all manpages to produce 2 files- ent_index that stores the index to entity mapping and 
					 index_merged_entities that stores the various features of the merged entities. Both files are saved at global_dir\Extractions\
4. Knowledge Graph Maker: Makes a knowledge graph out of the merged entities. The entity relations of each type are stored in a separate 														txt file in global_dir\Extractions\Graph\
5. Knowledge Graph Reader: Reads the knowledge graph made into an nx.MultiDiGraph python object
6. zipf's law: Finds and stores which words to use as zip words. The lim1 and lim2 parameter in the script can be adjusted to either 										 increase or decrease the no of zip words. The script makes 2 files- word_freq (stores the frequency of each word in the 									 ubuntu manpages'corpus) and zip_words (stores the extracted zip words).
7. Calculate rel 3 work distribution: Extracting relations of type 3 in the knowledge graph maker can take a lot of time, because for this
                                      we have to compare every pair of entities out of n entities to see if they are related, which takes                                         n^2 comparisons. So this script partitions the interval [1, n] into numerous parts so that each part 																			 has to perform the same number of comparisons. The partitons can be used to multithread the code in a 																			 multicore machine. In the Knowledge Graph Maker, lim1 and lim2 for relation 3 extraction have to be																				assigned the endpoints of the partitions described just now.
																		
Execution Order:
downloader -> Full Entity Extraction -> Merger -> zipf's law -> Calculate rel3 work distribution (optional) ->
Knowledge Graph Maker -> Knowledge Graph Reader\
