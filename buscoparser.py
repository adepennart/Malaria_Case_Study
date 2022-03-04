#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title: buscoparser.py
Date: March 4th, 2022
Author: Auguste de Pennart

Description:
    create a file for each busco id containing orthologous sequences for a list of specified species of interest 

List of functions:
    No user defined functions are used in the program.

List of "non standard modules"
    No "non standard modules" are used in the program.

Procedure:
    1. input busco id file (this is determined by bash script)
    2. create set of busco ids
    3. input file of busco hmmer_output (determines gene_id for each busco id)
    4. for loop through each busco id
    5. for loop through each species
    6. for loop through each busco hmmer_output
    7. create dictionary of busco ids with values a dictionary of species and gene id
    8. for loop open file for each busco gene 
    7. in faa file fine gene id and print out respective species and sequence of gene id to output
    7. print to output

Usage:
    python buscoparser.py busco_list.txt

known error:
    1. consider making dictionary for each faa file

 """

# import packages
import re
import random
import sys
from pathlib import Path


# allows for different file names to be adjusted easily for user
#list of busco ids
inputfile = 'busco_list.txt'
#path to output folder
outputfiletree ='../9_busco/Python_output/'
#with busco output, path to gene_id
gene_idpath = '/run_apicomplexa_odb10/hmmer_output/initial_run_results/'
#set of species
spe_set={'Ht','Pb','Pc','Pf','Pk','Pv','Py','Tg'}
# Here we are looking for 2 arguments (script, input file[1]) placed in the command line.
# we are also making sure the input is valid
if len(sys.argv) == 2 and Path(sys.argv[1]).is_file():
    inputfile = sys.argv[1]
# here the line accounts for missing input file
elif len(sys.argv) == 2 and not Path(sys.argv[1]).is_file():
    try:
        # this line raises an error if no file exists
        if len(sys.argv) == 2 and not Path(sys.argv[1]).is_file():
            raise FileExistsError
        # for some reason something else goes wrong this error is raised
        else:
            raise FileNotFoundError
    except FileExistsError:
        print("Input file does not exist in directory or mispelled")
        exit()
    except FileNotFoundError:
        print("some other error")
        exit()


# uses the files specified above in the script
elif len(sys.argv) == 1:
    inputfile = inputfile
#    outputfile = outputfile

# exits script if unexpected arguments in commandline.
else:
    try:
        raise ArithmeticError
    except:
        print("Looking for 2 argument, try again")
        exit()

# assigned variables
buscoid_set = set()
id_dict={}
geneid_dict={}
#faadict={}
#headseq=""
flag=False
# opening inputfile and outputfile
inputted = open(inputfile, 'r')
# output = open(outputfile, 'w')
# for loop to create busco id set
for line in inputted:
    buscoid_set.add(line.strip())

#print(buscoid_set)
#for loop for create nested dictionary with busco id, species name and gene id
for id in buscoid_set:
    for species in spe_set:
        #specifies gene id file, far down tree path
        path = f'{species}{gene_idpath}{id}.out'
        gene_find = open(path, 'r')
        for line in gene_find:
            if re.search('^#', line):
                pass
            elif not re.search('^#', line):
                gene_id = re.search(r'([\dA-Za-z\_]+)\s', line).group(1)
                print(gene_id)
                geneid_dict[species]=f'>{gene_id}\s'
    id_dict[id]=geneid_dict
    geneid_dict={}
#print(id_dict)

#does not work
# for species in spe_set:
#     faa=f'{species}.faa'
#     faafile = open(faa, 'r')
#     for line in faafile:
#         if re.search('^>[^?*]+$', line):  # finds line if fasta header
# #            print(line)
#  #           print(headseq)
#             faadict[species]=headseq
#             headseq=""
#             header=line
#             headseq+=header
#         elif not re.search('^>[^?*]+$', line):  # finds line if not fasta header
#   #          print(line)
#             sequence=line
#             headseq+=sequence
#     faafile.close()
#print(faadict) 

# creates an output file for each busco gene
# adds line to file with species and corresponding busco gene sequence            
for key, value in id_dict.items():
    outputfile=f'{outputfiletree}{key}.faa'
    output = open(outputfile, 'w')
    print(f"creating file for {key} BUSCO gene")
    for species,gene_id in value.items():
        #print(species)
        #finds gene id in faa file
        faa=f'{species}.faa'
        faafile = open(faa, 'r')
        for line in faafile:
            if re.search('^>[^?*]+$', line):  # finds line if fasta header
                if re.search(gene_id, line):
                    #print(line.strip())
    #                print(f'{species}{line}')
                    print(f'>{species}', file=output)
                    flag= True
                else:
                    flag= False
            elif not re.search('^>[^?*]+$', line):  # finds line if not fasta header
                if flag:
                    #print(line.strip())
                    print(line.strip(), file=output)
                elif not flag:
                    #print("false")
                    pass
                else:
                    pass
    output.close()  # closing
inputted.close()  # closing

