#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title: cleaning.py
Date: March 4th, 2022
Author: Auguste de Pennart

Description:
    removes all scaffolds that are unwanted based on scaffold length and GC content

List of functions:
    No user defined functions are used in the program.

List of "non standard modules"
    No "non standard modules" are used in the program.

Procedure:
    1. open input file
    2. make dictionary of header and sequence
    3. find headers that are above a certain length
    4. find sequences that are below a certain GC content
    5. output these to a new file

Usage:
    python cleaning.py Haemoproteus_tartakovskyi.genome Haemoproteus_tartakovskyi_clean.genome

known error:
    1.

 """

#import packages
import re
import random
import sys
from pathlib import Path
#from functions import *

# allows for different file names/inputs to be adjusted easily for user
inputfile = 'Haemoproteus_tartakovskyi.genome'
outputfile = 'Haemoproteus_tartakovskyi_clean.genome'
cutout=30
minscaffold=3000
# Here we are looking for 3 arguments (script, input file[1],outputfile[2]) placed in the command line.
# we are also making sure the input is valid
if len(sys.argv) == 3 and Path(sys.argv[1]).is_file():
    # here we are making sure that the file is not being overwritten
    if Path(sys.argv[2]).is_file():
        # asking user if they want to overwrite file or not
        while 1:
            reasonlen2 = input("Output file already exists would you like to overwrite(Y/N)?\n")
            try:
                # if they answer yes to overwrite, file is overwritten
                if reasonlen2.upper() == 'Y' or reasonlen2.upper() == 'YES':
                    # print('y')
                    inputfile = sys.argv[1]
                    outputfile = sys.argv[2]
                    break
                # if not script is ended and user is asked for new input
                elif reasonlen2.upper() == 'N' or reasonlen2.upper() == 'NO':
                    raise NameError
                # if neither yes or no given, user must resubmit answer
                else:
                    raise ArithmeticError
            except NameError:
                print("please resubmit code with a different output file")
                exit()
            except ArithmeticError:
                print('Not a Yes or No, please try again')
    inputfile = sys.argv[1]
    outputfile = sys.argv[2]
# here the line accounts for missing input file
elif len(sys.argv) == 3 and not Path(sys.argv[1]).is_file():
    try:
        # this line raises an error if no file exists
        if len(sys.argv) == 3 and not Path(sys.argv[1]).is_file():
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
    outputfile = outputfile


# exits script if unexpected arguments in commandline.
else:
    try:
        raise ArithmeticError
    except:
        print("Looking for 3 argument, try again")
        exit()
#assigned variables
main_dict={}
modified_dict={}
GCcount=0
totalcount=0
sequence=""
# opening inputfile and outputfile
inputted = open(inputfile, 'r')
output = open(outputfile, 'w')
#for loop through each line in inputted
for line in inputted:
    if re.search('^>[^?*]+$', line): #finds line if fasta header
        #print(line)
        header=line
        main_dict[header]=''#put fasta file in dictionary
        pass
    elif not re.search('^>[^?*]+$', line): #finds line if not fasta header
        #print(line)
        sequence=line
        main_dict[header]+=sequence
        pass
    else:
        print("something went wrong") # prints if some else goes wrong
        exit()
inputted.close()  # closing


#print(len(main_dict))
for key,value in main_dict.items():
    #find length of sequence
    if re.search('^>[^?*]+$', key): #finds line if fasta header
        #print(key)
        match=re.findall('\S+', key)
        #print(match)
        #print(match[2])
        matched=match[1]
        matched=re.findall('[^=]+', matched)
        #print(match[2])
        length=int(matched[1])
        #see if sequence is above certain threshold
        if length >= minscaffold:
            # print(key.strip())
            #find seqeucnes below certain GC content
            for nuc in value:
                #print(nuc)
                if nuc.upper() == "G" or nuc.upper() == "C":
                    GCcount+=1
                    totalcount+=1
                elif not nuc.upper() == "G" or nuc.upper() == "C":
                    totalcount+=1
                else:
                    print("something went wrong")
                    exit()
            #print(f"the gc content is {100*(GCcount/totalcount):.2f}%")
            #print(totalcount)
            gccontent= float(f"{100*(GCcount/totalcount):.2f}")
            if gccontent <= cutout:
                #print(value) 
                modified_dict[key.strip()]=value.strip()
                #add to output
                #print(key.strip())
                print(key.strip(), file=output)
                #print(value.strip())
                print(value.strip(),file=output)
            else:
                pass
            GCcount=0
            totalcount=0
#print(len(modified_dict))
print(f"kept {len(modified_dict)} of {len(main_dict)} scaffolds")
output.close()  # closing
