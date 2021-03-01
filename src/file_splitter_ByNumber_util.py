#!/usr/bin/env Python
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 29 00:00:31 2020

@author: claude
"""
import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"file_splitter_ByNumber_util",['os'])==False:
    sys.exit(0)

import os
    
#This function split a txt file by recognizing number sequence in lines, and naming subfiles by the number recognized
def run(inputFilename, outputPath, post_number_string = ''):
    #post_number_string is the string behind each number
    #(if the numbers in the txt are in the form of "1. ", "2. ", then the post_number_string should be ". ")
    docname = os.path.split(inputFilename)[1]
    title = docname.partition('.')[0]
    lines = []#list of each line in the txt files
    with open(inputFilename, 'r', encoding='utf-8',errors='ignore') as iptf: #read each line
        line = iptf.readline()
        while line: 
            lines.append(line)
            line = iptf.readline()
    subfilename = outputPath+"/"+title+"_prenumber"+".txt"#first splitfile: the contents before the first number at the head of one line
    subfile = open(subfilename, 'w',encoding='utf-8',errors='ignore')
    j = len(post_number_string)
    for l in lines: 
        spaceless = l.lstrip()#get rid of spaces at the head of one line
        recognized = True
        if len(spaceless) > 0 and spaceless[0].isdigit():#not a blank line and the head character is a number
            num = ''#string of number
            i = 0
            while spaceless[i].isdigit():#colect all digits of the number
                num += l.lstrip()[i]
                i += 1
                
            if len(post_number_string) > 0 and spaceless[i: i + j] != post_number_string:#if the number has post_number_string behind it
                recognized = False         
        else: 
            recognized = False  
        
        if recognized: 
            subfilename = outputPath+"/"+title+"_"+num+".txt"#split file with the number in its title
            i = 1
            while os.path.exists(subfilename):
                subfilename = outputPath+"/"+title+"_"+num+"_"+str(i)+".txt"
                i += 1
            subfile = open(subfilename, 'w',encoding='utf-8',errors='ignore')
            subfile.write(l + '\n')
        else: #no number at the head or the number not followed by the post_number_string
            subfile.write(l + '\n')