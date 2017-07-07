#coding:utf-8
import sys
import os
import random

def former():
	former = []
	file = open("./male.txt")  
	for line in file:
		former.append(line)
	file.close()
	file1 = open("./female.txt")
	for line1 in file1:
		former.append(line1)
	file1.close()
	return former

def latter():
	latter = []
	file = open("./male.txt")  
	for line in file:
		latter.append(line)
	file.close()
	return latter

if __name__ == '__main__':
	file_dst = open('./name.txt','w')
	former = former()
	latter = latter()
	for i in range(len(former)):
		for j in range(len(latter)):
			name = former[i].strip('\n') + '·' + latter[j]
			#print name
			file_dst.write(name)
	file_dst.close()


