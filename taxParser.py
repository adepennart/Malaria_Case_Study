#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title: taxParser.py
Date: March 4th, 2022
Author: Auguste de Pennart

Description:
    based on database information and blast information remove scaffolds in file that have best blast id matches that 
    are birds 

List of functions:
    No user defined functions are used in the program.

List of "non standard modules"
    No "non standard modules" are used in the program.

Procedure:
    1. for loop through taxonomy database and pull out aves taxonomy ids
    2. for loop through uniport database and pull out bird species ids
    3. for loop through the blast output file and find the genes with the best match is a bird gene
    4. for loop through fna file to find scaffold for matching bird id
    5. for loop through genome file and remove scaffolds that contain bird genes

Usage:
    python taxParser.py Ht.blastp taxonomy.dat uniprot_sprot.dat gffParse.fna Haemoproteus_tartakovskyi_clean.genome Haemoproteus_no_bird.fna
known error:
    1.

 """

# import packages
import re
import random
import sys
from pathlib import Path

# allows for different file names to be adjusted easily for user
# inputfile = 'Ht.blastp'
inputfile = 'Ht.blastout'
inputfile2 = 'taxonomy.dat'
inputfile3 = 'uniprot_sprot.dat'
inputfile4 = 'gffParse.fna'
inputfile5 = 'Haemoproteus_tartakovskyi_clean.genome'
outputfile = 'Haemoproteus_no_bird.fna'

# uses the files specified by user
if len(sys.argv) == 7:
    inputfile = sys.argv[1]
    inputfile2 = sys.argv[2]
    inputfile3 = sys.argv[3]
    inputfile4 = sys.argv[4]
    inputfile5 = sys.argv[5]
    outputfile = sys.argv[6]

# uses the files specified above in the script
elif len(sys.argv) == 1:
    inputfile = inputfile
    inputfile2 = inputfile2
    inputfile3 = inputfile3
    inputfile4 = inputfile4
    inputfile5 = inputfile5
    outputfile = outputfile

# exits script if unexpected arguments in commandline.
else:
    try:
        raise ArithmeticError
    except:
        print("wrong number of arguments, try again")
        exit()

# assigned variables
inaves = False
aves_set = set()
aves_dict = {}
hitset = set()
foundhit = False
scaffold_find = set()
# opening inputfile and outputfyile
inputted = open(inputfile, 'r')
inputted2 = open(inputfile2, 'r')
inputted3 = open(inputfile3, 'r')
inputted4 = open(inputfile4, 'r')
inputted5 = open(inputfile5, 'r')
output = open(outputfile, 'w')

#find aves in taxonomy file
for line in inputted2:
    if re.search('RANK\s+:\sclass', line):  # finds line if fasta header
        # print("found class")
        inaves = False
        next(inputted2)
        next(inputted2)
        isaves = next(inputted2)
        # print(isaves)
        if re.search('Aves', isaves):  # finds line if fasta header
            print("found Aves")
            inaves = True
        else:
            pass
    elif re.search('^ID', line):
        if inaves == True:
            # print(line)
            match = re.search(r':\s(\d+)', line).group(1)
            # print(match)
            aves_set.add(match.strip())
        elif inaves == False:
            pass
    elif re.search('SCIENTIFIC NAME', line):
        if inaves == True:
            # print(line)
            if re.search('Podilymbus podiceps', line):  # temporary fix
                inaves = False
                print("found podiceps")
print(f"number of birds in the taxonomy file: {len(aves_set)}")
# print(aves_set)

#find bird gene names
for line in inputted3:
    if re.search('^ID', line):
        match = re.search(r'\_([\dA-Za-z]+)\s', line).group(1)
        # match=re.search(r'^ID\s+([\dA-Za-z\_]+)\s', line).group(1)
        Id = match
    elif re.search('^OX', line):
        # match=re.search(r'NCBI_TaxID=(\d+)[\s;]', line).group(1)
        match = re.search(r'=(\d+)', line).group(1)
        taxid = match
        # print(taxid)
        if taxid.strip() in aves_set:
            # print("found bird in aves_set")
            aves_dict[taxid] = Id
print(f"number of birds in Uniprot file: {len(aves_dict)}")
# print(aves_dict)

#find gene ids were best match is bird
for line in inputted:
    if re.search('^Query=', line):
        match = re.search(r'=\s+([\dA-Za-z\_]+)\s', line).group(1)
        header = match
        next(inputted)
        next(inputted)
        next(inputted)
        next(inputted)
        next(inputted)
        bestmatch = next(inputted)
        # print(bestmatch)
        if bestmatch.strip():
            bird = re.search(r'\|[\dA-Za-z]+\_([\dA-Za-z]+)\s', bestmatch).group(1)
            # print(bestmatch)
            # print(bird)
            if bird in aves_dict.values():
                # print("found bird in aves_dict")
                hitset.add(header)
            else:
                pass
    else:
        pass
print(f"number of best matches in blast that are birds: {len(hitset)}")

#find scaffold with bird gene
# for loop through each line in inputted
for line in inputted4:
    if re.search('^>[^?*]+$', line):  # finds line if fasta header
        # print(line)
        match = re.search(r'>([\dA-Za-z\_]+)\s', line).group(1)
        if match in hitset:
            print("found bird in hitset")
            scaffold = re.search(r'=(scaffold\d+)', line).group(1)
            scaffold_find.add(scaffold)
        elif not match in hitset:
            pass
    elif not re.search('^>[^?*]+$', line):  # finds line if not fasta header
        # print(line)
        if foundhit:
            pass
        elif not foundhit:
            pass
    else:
        print("something went wrong")  # prints if some else goes wrong
        pass

print(f"number of scaffolds to remove: {len(scaffold_find)}")

#remove scaffold with bird gene from genome file
# for loop through each line in inputted
for line in inputted5:
    if re.search('^>[^?*]+$', line):  # finds line if fasta header
        # print(line)
        match = re.search(r'>([\dA-Za-z\_]+)\s', line).group(1)
        if match in scaffold_find:
            print("removing bird scaffold")
            foundhit = True
        elif not match in hitset:
            foundhit = False
            print(line.strip(), file=output)
    elif not re.search('^>[^?*]+$', line):  # finds line if not fasta header
        # print(line)
        if foundhit:
            pass
        elif not foundhit:
            print(line.strip(), file=output)
    else:
        print("something went wrong")  # prints if some else goes wrong
        pass

print("done")

inputted.close()  # closing
inputted2.close()  # closing
inputted3.close()  # closing
inputted4.close()  # closing
inputted5.close()  # closing
output.close()  # closing
