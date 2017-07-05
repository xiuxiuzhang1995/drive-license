#coding:utf-8

import os
import sys
import random
import argparse
import time
import datetime
import re

reload(sys)
sys.setdefaultencoding('utf8')  # 2.7

Multiday=random.randint(0,365*17)


def parse_args():
  """
  Parse input arguments
  """
  parser = argparse.ArgumentParser(description='Train ID Data')
  parser.add_argument('--new',
                      help='the number of New ID Data',
                      type=int)
  parser.add_argument('--old',
                      help='the number of Old ID Data',
                      type=int)
  if len(sys.argv) == 1:
      parser.print_help()
      sys.exit(1)

  args = parser.parse_args()
  return args

def random_pick(some_list, probabilities):
    x = random.uniform(0, 1)
    cumulative_probability = 0.0
    for item, item_probability in zip(some_list, probabilities):
        cumulative_probability += item_probability
        if x < cumulative_probability: break
    return item

def zoom():
    with open('../dicts/zoom.txt') as file:
        name = []
        for line in file:
            temp = line.strip('\n')
            if len(temp)>0:
                temp=re.split(',',temp)[0]
                name.append(temp)
        return name
#身份证生成
def  Idgenerate(name):
    days = random.randint(365 * 18, 365 * 70)
    date = (datetime.datetime.now() - datetime.timedelta(days))
    m_brith_time = date.strftime("%Y-%m-%d")
    m_issue_time = date.strftime("%Y%m%d")
    m_issue_time = m_issue_time + str(random.randint(100,300))
    #print(m_issue_time)
    f=random.randint(0, len(name)-1)
    id=str(name[f])+m_issue_time
    count = 0
    weight = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]  # 权重项
    checkcode = {'0': '1', '1': '0', '2': 'X', '3': '9', '4': '8', '5': '7',
                 '6': '6', '7': '5', '8': '5', '9': '3','10': '2'}  # 校验码映射
    for i in range(0, len(id)):
        count = count + int(id[i]) * weight[i]
    id = id + checkcode[str(count % 11)]  # 算出校验码
    if int(id[-2])%2==0:
        Male = 0 #女
    else:
        Male = 1
    return id,Male,m_brith_time,days


#姓名：
def random_name():
    try:
        with open(r'../dicts/Name.txt') as file:
            num=0
            name=[]
            for line in file:
                temp = line.strip('\n')
                name.append(temp)
                #name[num]=temp
                num+=1
                #print(temp)
    except:
        print('the Name.txt is not find')
    return name


#k=random.randint(1,len(m_name))
#print(m_name[k])
#地址：
def random_Address():
    with open(r'../dicts/Address.txt') as file:
        num=0
        Address=[]
        for line in file:
            temp = line.strip('\n')
            Address.append(temp)
            #name[num]=temp
            num+=1
            #print(temp)
    return Address

#k=random.randint(1,len(m_address))
#print(m_address[k])


#准驾车型
mclass = ['A1','A2','A3','B1','B2','B3','C1','C2','C3','C4', 'D',
         'E','F','M','N','P','C1E','C1D','B1E','A2D','A1A2D','A2E','B1F']
def random_class(mclass):
    probabilities=[0.05,0.05,0.05,0.05,0.05,0.05,0.2,0.15,0.05,0.05,0.05,  #0.8
        0.02,0.01,0.001,0.001,0.001,0.054,0.05,0.02,0.02,0.005,0.009,0.009]
    #m_class = "".join(random.sample(mclass,1))
    m_class = random_pick(mclass,probabilities)
    return m_class


#注册日期 2009-09-03
def random_regist_time(day):
    #先获得时间数组格式的日期
    SomeDayAgo = (datetime.datetime.now() - datetime.timedelta(days = random.randint(0,day-365*18)))
    #转换为时间戳:
    timeStamp = int(time.mktime(SomeDayAgo.timetuple()))
    #转换为其他字符串格式:
    m_regist_time = SomeDayAgo.strftime("%Y-%m-%d")
    return m_regist_time
#print(random_regist_time())

#发证日期 2014-12-29
def random_vaildtime_start(date):
    time = re.split('-',date)
    if int(time[0])<2005:
        vaildyears = "".join(random.sample(['0','6','10'], 1))
    elif int(time[0])<2011:
        vaildyears = "".join(random.sample(['0', '6'], 1))
    else:
        vaildyears = '0'
    time = str(int(time[0])+int(vaildyears))+'-'+time[1]+'-'+time[2]
    return time


def random_vaildtime_end(date):
    time = re.split('-',date)
    vaildyears = "".join(random.sample(['6','10','20'], 1))
    time = str(int(time[0])+int(vaildyears))+'-'+time[1]+'-'+time[2]
    return time

def random_vaildtime_end_old(date):
    time = re.split('-',date)
    mclass = ['6年','10年','20年']

    probabilities = [0.9, 0.08, 0.02]
    vaildyears = random_pick(mclass, probabilities)
    return vaildyears

def generatedata(args):
    m_address = random_Address()
    m_name = random_name()
    m_class = random_class(mclass)
    name=zoom()

    file = open('list.txt','w')

    for i in range(1,args.new+1): #new data
        try:
            ID,Male,m_brith_time,days=Idgenerate(name)
            if Male==0:
                Male='女'
            else:
                Male='男'
            k = random.randint(0, len(m_name)-1)
            k1 = random.randint(0,len(m_address)-1)
            start = random_regist_time(int(days))
            vaildtimestart = random_vaildtime_start(start)
            vaildtimeend = random_vaildtime_end(vaildtimestart)
            text = ID + ',' + m_name[k]+','+Male+',中国'+','+m_address[k1]+','+m_brith_time+','+\
                   start+','+random_class(mclass)+',' +vaildtimestart+','+vaildtimeend

            file.write(text+'\n')
            if i==1:
                print ('The new ID data number:\n'),
            elif i % (args.new/10)==0:
                print(i),
        except:
            print('Error')

    for i in range(1,args.old+1): #old data
        try:
            ID,Male,m_brith_time,days=Idgenerate(name)
            if Male==1:
                Male='女'
            else:
                Male='男'
            k = random.randint(0, len(m_name)-1)
            k1 = random.randint(0,len(m_address)-1)
            start = random_regist_time(int(days))
            vaildtimestart = random_vaildtime_start(start)
            vaildtimeend = random_vaildtime_end_old(vaildtimestart)
            text = ID + ',' + m_name[k]+','+Male+',中国'+','+m_address[k1]+','+m_brith_time+','+\
                   start+','+random_class(mclass)+',' +vaildtimestart+','+vaildtimeend

            file.write(text+'\n')
            if i==1:
                print ('\nThe old ID data number:\n'),
            elif i % (args.old/10)==0:
                print(i),
        except:
            print('Error')

    file.close()

if __name__ == '__main__':
    args = parse_args()
    print('start generate data...')
    generatedata(args)
    print('\ndone!')
