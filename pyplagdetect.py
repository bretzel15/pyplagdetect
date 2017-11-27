#! /usr/bin/python3

# edit directories for existing and new reports, relative to script folder
existing_dir = "../existing_reports"
test_dir = "../to_be_tested"

## change length of string sequence to be detected, 7 is a good value
tuple_length = 7
min_copies = 3


## script requires following modules, which can be installed by typing "pip3 install YYY" in command line,
## YYY = os, numpy, hashlib, pdftotext



###############################################
####                                       ####
####      !!! DO NOT EDIT BELOW !!!        ####
####                                       ####
###############################################

import os
import re
import numpy as np
import hashlib
import time
import pdftotext

def generate_hashes(pdf_text, tuple_length, hash_list, string_list):
    # combine single pages into one big string
    whole_text = "\n\n".join(pdf_text)
    # merge two words around a hyphen "-" together to handle hyphenation
    whole_text = whole_text.replace('-\n','')
    # replace newlines with spaces and then split text at points
    text_by_sentences = whole_text.replace('\n',' ').split('.')
    # iterate through each sentence
    for sentence in text_by_sentences:
        # split each sentence into its single words
        sentence_split = re.findall('\w+',sentence)
        # only evaluate if sentence is longer than "tuple_length" words
        if len(sentence_split) >= tuple_length:
            # go through each 7-word combination in each sentence (4 times for 10 words)
            for k in range(0,len(sentence_split)-tuple_length+1):
                # join seven words into one string, with spaces in between each word
                seven_strings = " ".join(sentence_split[k:k+tuple_length])
                # store string in separat list for later printing to output
                string_list.append(seven_strings)
                # hash each string with md5 for faster comparison
                hash_object = hashlib.md5(seven_strings.encode())
                # add each hash to one big list with all hashes of all existing documents
                hash_list.append(hash_object.hexdigest())
                # hash each six-word tuple of each seven-word tuple as well
                seven_strings_split = seven_strings.split()
                for m in range(0,tuple_length):
                    six_strings =  seven_strings_split[0:m] + seven_strings_split[m+1:tuple_length]
                    six_strings = " ".join(six_strings)
                    string_list.append(six_strings)
                    # hash each string with md5 for faster comparison
                    hash_object = hashlib.md5(six_strings.encode())
                    # add each hash to one big list with all hashes of all existing documents
                    hash_list.append(hash_object.hexdigest())
    return [hash_list, string_list]



# scan through existing pdf files, extract text, split it at each sentence
# take each sentence equal or longer than 7 words and generate a hash
# save hashes in hash_existing

hash_existing = []
string_existing = []
doc_backlink = []
ref_doc_count = 0

start_time = time.time()
hash_time = 0
for root, subdir, filename in os.walk(existing_dir):
    # scan each file in directory
    for one_file in filename:
        # only evaluate "pdf" files
        if os.path.splitext(one_file)[1] == ".pdf":
            # open file and store all text in "pdf_text"
            #hash_start = time.time()
            with open(os.path.join(root, one_file), "rb") as f:
                pdf_text = pdftotext.PDF(f)
            #hash_time += time.time() - hash_start
            # increase reference document counter by 1
            ref_doc_count += 1
            # store current length of hash_existing for later backtracking of document
            begin_hash = len(hash_existing)
            # generate hashes and string list from text
            [hash_existing, string_existing] = generate_hashes(pdf_text, tuple_length, hash_existing, string_existing)
            # store last hast for later backtracking of document
            end_hash = np.size(hash_existing) - 1
            # store first and last hash line together with document name
            doc_backlink.append( [os.path.join(root, one_file), begin_hash, end_hash] )
import_time = time.time() - start_time
# print('  reference documents analyzed in %.2f seconds\n' % import_time)

# scan through new pdf files, extract text, split it at each sentence
# take each sentence equal or longer than 7 words and generate a hash
# save hashes in hash_new
for root, subdir, filename in os.walk(test_dir):
    # scan each file in directory
    for one_file in filename:
        # reset hashes and strings for each new document
        hash_new = []
        string_new = []
        # only evaluate "pdf" files
        if os.path.splitext(one_file)[1] == ".pdf":
            # open file and store all text in "pdf_text"
            with open(os.path.join(root, one_file), "rb") as f:
                pdf_text = pdftotext.PDF(f)
            # generate hashes and string list from text
            [hash_new, string_new] = generate_hashes(pdf_text, tuple_length, hash_new, string_new)

            # find all hashes that exists in both old pdfs and the new document
            hash_matches = set(hash_existing).intersection(hash_new)
            # create empty list
            existing_hash_line_prelim = []
            # collect all line numbers of hashes in both old and new pdfs
            for match in hash_matches:
                existing_hash_line_prelim.append(hash_existing.index(match))
            # sort hashes in ascending order
            existing_hash_line_prelim = np.sort(existing_hash_line_prelim)
            # delete following seven numbers if string is already a seven word match
            existing_hash_line = []
            for n in existing_hash_line_prelim:
                # print(string_existing[n])
                if n % (tuple_length + 1) == 0:
                    existing_hash_line.append(n)
                elif (n - (n % (tuple_length + 1))) in existing_hash_line_prelim:
                    continue
                else:
                    existing_hash_line.append(n)

            # sort hashes in ascending order
            existing_hash_line = np.sort(existing_hash_line)



            # create text file with same name as new pdf document and open it
            save_name = os.path.join(os.path.splitext(one_file)[0] + "." + "txt")
            with open(os.path.join(root, save_name), "w") as f:
                # write title of file in first line
                f.write("Tested File: %s\n" % os.path.join(root, one_file))
                f.write("  tuple length: %s  -" % tuple_length)
                f.write("  min hits  : %s\n" % min_copies)
                f.write("  reference documents scanned: %s" % ref_doc_count)
                f.write(" in %.2f seconds" % import_time)
                f.write(" (%.0f docs/sec)" % (ref_doc_count/import_time))
                f.write("\n  :: means a seven word hit")
                f.write("\n  :* means a six word hit, so there is one word in between missing")
                #f.write(" - opening: %.2f seconds \n" % hash_time)
                # iterate through all documents with found similarities
                for document in doc_backlink:
                    # count number of copies, if smaller than XXX, omit document
                    b = existing_hash_line < document[2]
                    c = document[1] < existing_hash_line
                    mask = [all(tup) for tup in zip(b,c)]
                    if np.sum(mask) >= min_copies:
                        # set switch for file name writing to True
                        header_write = True
                        prev = 0
                        # go through each line in the duplicate hash entries
                        for l in existing_hash_line:
                            # write to the file if the hash belongs to the current old pdf ("document")
                            if document[1] <= l <= document[2]:
                                # write header if this is the first line of this document
                                if header_write:
                                    # f.write('\nFound %s' % np.sum(mask))
                                    f.write('\n\nFound duplicates in: %s' % document[0])
                                    header_write = False
                                # write all similar lines to output file
                                if ( l % (tuple_length+1) ):
                                    if string_existing[prev].split()[-5:] ==  string_existing[l].split()[:5]:
                                        f.write(' ' + string_existing[l].split()[-1])
                                    else:
                                        f.write('\n :* ' + string_existing[l])
                                else:
                                    if string_existing[prev].split()[-6:] ==  string_existing[l].split()[:6]:
                                        f.write(' ' + string_existing[l].split()[-1])
                                    else:
                                        f.write('\n :: ' + string_existing[l])
                                prev = l
                        f.write('\n')
                        header_write = True

            # print('  %s finished' % one_file)
