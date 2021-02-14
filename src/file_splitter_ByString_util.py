import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"file_splitter_ByString",['os','io','shutil'])==False:
    sys.exit(0)

import io
import os
import shutil

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 12 21:04:52 2020

@author: claude
"""

# target: the substring used to identify the start of a subfile
# spot_one & spot_two: range where the target appear in the starting line
# inclusion: if that substring appear in any line, that line will be the start of a new subfile
# run (inputFilename, outputPath, 'pp.', -7, -5, True)
# a = '6) pp. 884'
# print(a[-7:-5+1])
def splitDocument_byStrings(inputFilename, outputPath, target, spot_one, spot_two, inclusion = False):
    newOutputPath = os.path.join(outputPath, 'split_files')
    if not os.path.exists(newOutputPath):
        os.mkdir(newOutputPath)
    else:
        # remove/delete and recreate directory
        shutil.rmtree(newOutputPath)
        os.mkdir(newOutputPath)

    # print("target, spot_one, spot_two",target, spot_one, spot_two)

    f = open(inputFilename, 'r', encoding='utf-8',errors='ignore')
    content = f.readlines()
    content = [x.strip() for x in content] 

    #print(len(content))
    loc = []
    for c in content:
        if inclusion == True:
            if target in c:
                loc.append(True)
            else:
                loc.append(False)
        else:    
            if len(c) < spot_two or type(spot_two) != int or type(spot_one) != int:
                loc.append(False)
            else: 
                if spot_one == spot_two: 
                    if c[spot_one - 1] == target:
                        loc.append(True)
                    else:
                        loc.append(False)
                elif spot_one < 0 and spot_two == -1:
                    s = spot_one * -1
                    t = c[s:]
                    if t == target:
                        loc.append(True)
                    else:
                        loc.append(False)
    
                else:
                    t = c[spot_one : spot_two + 1]
                    if t == target:
                        loc.append(True)
                    else:
                        loc.append(False)

    i = 1
    if loc[0] != True:
        p = open(newOutputPath+'/subfile'+str(i)+'.txt', 'w', encoding='utf-8',errors='ignore')
        i = i+1
    for d in range(len(loc)):
        if loc[d] == True:
            p = open(newOutputPath+'/subfile'+str(i)+'.txt', 'w', encoding='utf-8',errors='ignore')
            i = i+1
            p.write("{}\n".format(content[d]))
        else:
            p.write("{}\n".format(content[d]))
            
#this function only split txt files whose contents are nicely split by lines without characters
def split_by_blanks(inputFilename, outputPath):
    docname = os.path.split(inputFilename)[1]
    title = docname.partition('.')[0]
    lines = []#list of each line in the txt files
    with open(inputFilename, 'r', encoding='utf-8',errors='ignore') as iptf: #read each line
        line = iptf.readline()
        while line: #read each line of the  input txt file
            lines.append(line)
            line = iptf.readline()
    subfileIndex = 1
    subfilename = subfilename = outputPath+"/"+title+"_splited_"+str(subfileIndex)+".txt"
    subfile = open(subfilename, 'w',encoding='utf-8',errors='ignore')#first split file
    for l in lines: 
        if len(l.strip()) == 0:#a line without character --> a new subfile
            subfileIndex += 1
            subfilename = subfilename = outputPath+"/"+title+"_splited_"+str(subfileIndex)+".txt"
            subfile = open(subfilename, 'w',encoding='utf-8',errors='ignore')
        else: 
           subfile.write(l + '\n')

