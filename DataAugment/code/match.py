#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
from os import listdir

filepath='/data/linkface/DriverLicense/artificial_data/regionImage/'
filename_list=listdir(filepath)

txt = []
jpg = []
num = 0

#找到txt与jpg匹配项
for filename in filename_list:
    if filename[-4:]=='.jpg':
        jpg.append(filename[:-4])
    elif filename[-4:]=='.txt':
        txt.append(filename[:-4])
    else:
    	pass

diff = set(txt).difference(set(jpg))	#txt中有的而jpg中没有的
print len(diff)
for line in diff:
	os.remove(filepath + line+'.txt')
	print line + '.txt'
	num += 1
	print num

diff1 = set(jpg).difference(set(txt))	#jpg中有的而txt中没有的
print len(diff1)
for line in diff1:
	print line
	os.remove(filepath + line + '.jpg')
	num += 1
	print num
