#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#Created on Fri May 12 10:43:40 2017

#@author: xiuxiuzhang


import random
import cv2
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont 
from PIL import ImageFilter
import pygame
import numpy
import shutil
import sys
import os
import threading
import time
from compiler.ast import flatten

#存储每行信息所放位置      #加载文字的位置随机化          
position_new = [(random.gauss(245,5),random.gauss(85,2)),    
                (random.gauss(95,5),random.gauss(118,2)),
                (random.gauss(314,5),random.gauss(131,2)),
                (random.gauss(474,5),random.gauss(128,2)),
                [(102,163),(95,198)],
                (random.gauss(259,5),random.gauss(236,2)),
                (random.gauss(288,5),random.gauss(274,2)),
                (random.gauss(302,5),random.gauss(308,2)),
                (random.gauss(136,5),random.gauss(356,2)),
                (random.gauss(284,5),random.gauss(356,2))]

#旧版每行位置               
position_old = [(random.gauss(245,5),random.gauss(90,2)),    
                (random.gauss(91,5),random.gauss(118,2)),
                (random.gauss(317,5),random.gauss(131,2)),
                (random.gauss(477,5),random.gauss(128,2)),
                [(100,162),(92,198)],
                (random.gauss(245,5),random.gauss(237,2)),
                (random.gauss(279,5),random.gauss(276,2)),
                (random.gauss(304,5),random.gauss(308,2)),
                (random.gauss(156,5),random.gauss(355,2)),
                (random.gauss(367,5),random.gauss(353,2))]    

#自定义高斯模糊
class MyGaussianBlur(ImageFilter.Filter):
    name = "GaussianBlur"

    def __init__(self, radius=2.0,bounds=None,sigma=2.0):
        self.radius = radius
        #self.bounds = bounds
        self.sigma  = sigma
        
    def filter(self, background):
        return background.gaussian_blur(self.radius,self.sigma)

#将文本每行分割出十个信息
def split(line):      
    allWords = []     
    list = line.split(',')  
    for word in list:  
        if word[-1]=='\n':  
           allWords.append(word[:-1])  #去掉行末的'\n'  
        else:  
           allWords.append(word)     
    return allWords

#将地址分成两行，输入为‘unicode’，输出为’unicode‘
def addressprocess(address,version, theFont2):  
        for j in range(len(address)):
                [w_tmp,h_tmp] = theFont2.size(address[0:j]) 
                #默认值一行
                address1 = address
                address2 = ''
                #两行处理
                if version == 'new':         
                        if w_tmp > 575 - position_new[4][0][0]:
                                address1 = address[0:j]
                                address2 = address[j:]
                                break
                elif version == 'old':         
                        if w_tmp > 575 - position_old[4][0][0]:
                                address1 = address[0:j]
                                address2 = address[j:]
                                break
                else:
                        print("version error")
        return [address1,address2]

#获得透视变换矩阵
def perspective_data(dst):
    src = numpy.array([[0,0],[620,0],[620,420],[0,420]], numpy.float32)
    M_perspective = cv2.getPerspectiveTransform(src, dst)
    tmp = M_perspective.tolist()
    data = flatten(tmp)[0:8]
    return data

#创建一个黑白图像找到变换后坐标
def dualimage(function,(x,y,w,h),angel,dst):
    x = int(x)       #将位置转换成整型，便于后续处理
    y = int(y)
    w = int(w)
    h = int(h)
    #创建一个和原图一样大的黑色图像
    temp = Image.new("RGB",(620,420),(0,0,0))
    #创建一个和抠图一样大的白色图像
    region = Image.new("RGB",(w,h),(255,255,255))
    temp.paste(region,(x,y,x+w,y+h))

    if function == 'rotate':      #旋转
        temp1 = temp.rotate(angel)
    elif function == 'perspective':   #仿射变换
        temp1 = temp.transform((620,420),Image.PERSPECTIVE,perspective_data(dst))
    else:
        pass

    #将PIL库处理的图像转换为opencv处理形式
    tempcv = numpy.array(temp1) 
    # Convert RGB to BGR 
    tempcv = tempcv[:, :, ::-1].copy()

    #转化为灰度图像，寻找轮廓，最小外接矩形和正的矩形框
    img = cv2.cvtColor(tempcv,cv2.COLOR_BGR2GRAY)
    ret1, th1 = cv2.threshold(img, 0, 255, cv2.THRESH_OTSU)

     #在opencv 2中为第一个参数，opencv 3中为第二个参数，本机配置为2，GPU配置为3
    contours = cv2.findContours(th1, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[1]   
    for i in range(min(len(contours), 4)):
        c = sorted(contours, key=cv2.contourArea, reverse=True)[i]
        g_dConArea = cv2.contourArea(c, False)
        x1, y1, w1, h1 = cv2.boundingRect(c)
        return [x1, int(random.gauss(y1,2)), x1 + w1, int(random.gauss(y1+h1,2))]  #截取的位置高斯随机变动

#旋转
def rotate_process(word, angel, result, boxs, background, version, i, theFont2):
    img_rotate = background.rotate(angel)
    img_rotate.save(result + '/wholeImage/'+str(i) + '_rotate_' + str(angel) + '_' + version + '.jpg')
    for j in range(len(boxs)):
        if j == 4:
            if boxs[j][1][2] == 0:
                region = dualimage('rotate',boxs[j][0],angel,0)
                region_tmp = list(region)
                w = region_tmp[2]-region_tmp[0]
                h = region_tmp[3]-region_tmp[1]
                region_img = img_rotate.crop(region).resize((28*w/h,28))    #图片高度统一成28
                region_img.save(result + '/regionImage/' + str(i) + '_rotate_' + str(angel) + '_' + version + '_' + str(j) +'.jpg')
                region_txt = open(result + '/regionImage/' + str(i) + '_rotate_' + str(angel) + '_' + version + '_' + str(j) +'.txt','w')
                region_txt.write(word[j])
                region_txt.close()
            else:
                [address1,address2] = addressprocess((unicode(word[j],'utf-8')),version,theFont2)
                region1 = dualimage('rotate',boxs[j][0],angel,0)
                region_tmp1 = list(region1)
                w1 = region_tmp1[2]-region_tmp1[0]
                h1 = region_tmp1[3]-region_tmp1[1]
                region2 = dualimage('rotate',boxs[j][1],angel,0)
                region_tmp2 = list(region2)
                w2 = region_tmp2[2]-region_tmp2[0]
                h2 = region_tmp2[3]-region_tmp2[1]
                region_img1 = img_rotate.crop(region1).resize((28*w1/h1,28))   #图片高度统一成28
                region_img2 = img_rotate.crop(region2).resize((28*w2/h2,28))    #图片高度统一成28
                region_img1.save(result + '/regionImage/' + str(i) + '_rotate_' + str(angel) + '_' + version + '_' + str(j) +'_1.jpg')
                region_img2.save(result + '/regionImage/' + str(i) + '_rotate_' + str(angel) + '_' + version + '_' + str(j) +'_2.jpg')
                region_txt1 = open(result + '/regionImage/' + str(i) + '_rotate_' + str(angel) + '_' + version + '_' + str(j) +'_1.txt','w')
                region_txt2 = open(result + '/regionImage/' + str(i) + '_rotate_' + str(angel) + '_' + version + '_' + str(j) +'_2.txt','w')
                region_txt1.write(address1.encode('utf-8'))
                region_txt1.close()
                region_txt2.write(address2.encode('utf-8'))
                region_txt2.close()
        else:
            region = dualimage('rotate',boxs[j],angel,0)
            region_tmp = list(region)
            w = region_tmp[2]-region_tmp[0]
            h = region_tmp[3]-region_tmp[1]
            region_img = img_rotate.crop(region).resize((28*w/h,28))   #图片高度统一成28
            region_img.save(result + '/regionImage/' + str(i) + '_rotate_' + str(angel) + '_' + version + '_' + str(j) +'.jpg')
            region_txt = open(result + '/regionImage/' + str(i) + '_rotate_' + str(angel) + '_' + version + '_' + str(j) +'.txt','w')
            region_txt.write(word[j])
            region_txt.close()

#透视变换            
def perspective_process(word, dst, result, boxs, background, version, perspective_index, i, theFont2):
    data = perspective_data(dst)
    img_perspective = background.transform((620,420),Image.PERSPECTIVE,data)
    img_perspective.save(result + '/wholeImage/'+str(i) + '_perspective_' + str(perspective_index) + '_' + version + '.jpg')
    for j in range(len(boxs)):
        if j == 4:
            if boxs[j][1][2] == 0:
                region = dualimage('perspective',boxs[j][0],0,dst)

                region_tmp = list(region)  #将数组转换成列表进行处理
                w = region_tmp[2]-region_tmp[0]
                h = region_tmp[3]-region_tmp[1]
                region_img = img_perspective.crop(region).resize((28*w/h,28))    #图片高度统一成28
                region_img.save(result + '/regionImage/' + str(i) + '_perspective_' + str(perspective_index) + '_' + version + '_' + str(j) +'.jpg')
                region_txt = open(result + '/regionImage/' + str(i) + '_perspective_' + str(perspective_index) + '_' + version + '_' + str(j) +'.txt','w')
                region_txt.write(word[j])
                region_txt.close()
            else:
                [address1,address2] = addressprocess((unicode(word[j],'utf-8')),version,theFont2)

                region1 = dualimage('perspective',boxs[j][0],0,dst)
                region_tmp1 = list(region1)
                w1 = region_tmp1[2]-region_tmp1[0]
                h1 = region_tmp1[3]-region_tmp1[1]

                region2 = dualimage('perspective',boxs[j][1],0,dst)
                region_tmp2 = list(region2)
                w2 = region_tmp2[2]-region_tmp2[0]
                h2 = region_tmp2[3]-region_tmp2[1]
                region_img1 = img_perspective.crop(region1).resize((28*w1/h1,28))    #图片高度统一成28
                region_img2 = img_perspective.crop(region2).resize((28*w2/h2,28))    #图片高度统一成28

                region_img1.save(result + '/regionImage/' + str(i) + '_perspective_' + str(perspective_index) + '_' + version + '_' + str(j) +'_1.jpg')
                region_img2.save(result + '/regionImage/' + str(i) + '_perspective_' + str(perspective_index) + '_' + version + '_' + str(j) +'_2.jpg')
                region_txt1 = open(result + '/regionImage/' + str(i) + '_perspective_' + str(perspective_index) + '_' + version + '_' + str(j) +'_1.txt','w')
                region_txt2 = open(result + '/regionImage/' + str(i) + '_perspective_' + str(perspective_index) + '_' + version + '_' + str(j) +'_2.txt','w')
                region_txt1.write(address1.encode('utf-8'))
                region_txt1.close()
                region_txt2.write(address2.encode('utf-8'))
                region_txt2.close()
        else:
            region = dualimage('perspective',boxs[j],0,dst)

            region_tmp = list(region)
            w = region_tmp[2]-region_tmp[0]
            h = region_tmp[3]-region_tmp[1]
            region_img = img_perspective.crop(region).resize((28*w/h,28))    #图片高度统一成28
            region_img.save(result + '/regionImage/' + str(i) + '_perspective_' + str(perspective_index) + '_' + version + '_' + str(j) +'.jpg')
            region_txt = open(result + '/regionImage/' + str(i) + '_perspective_' + str(perspective_index) + '_' + version + '_' + str(j) +'.txt','w')
            region_txt.write(word[j])
            region_txt.close()

#模糊
def filter_process(word, result, boxs, background, version, radius, sigma, i, theFont2):
    img_filter = background.filter(MyGaussianBlur(radius = radius,sigma = sigma))
    img_filter.save(result + '/wholeImage/'+str(i) + '_filter_' + str(radius+sigma) + '_' + version + '.jpg')
    for j in range(len(boxs)):
        if j == 4:
            if boxs[j][1][2] == 0:

                region = []   #(x,y,w,h)
                for index in range(len(boxs[j][0])):     #对坐标取整
                    region.append(int(boxs[j][0][index])) 
                region_tmp = list(region)  #将数组转换成列表进行处理
                w = region_tmp[2]
                h = region_tmp[3]
                box = [region_tmp[0],region_tmp[1],region_tmp[0]+w,region_tmp[1]+h]
                region_img = img_filter.crop(box).resize((28*w/h,28))    #图片高度统一成28
                region_img.save(result + '/regionImage/' + str(i) + '_filter_' + str(radius+sigma) + '_' + version + '_' + str(j) +'.jpg')
                region_txt = open(result + '/regionImage/' + str(i) + '_filter_' + str(radius+sigma) + '_' + version + '_' + str(j) +'.txt','w')
                region_txt.write(word[j])
                region_txt.close()
            else:
                [address1,address2] = addressprocess((unicode(word[j],'utf-8')),version,theFont2)

                region1 = []        #(x,y,w,h)
                for index in range(len(boxs[j][0])):     #对坐标取整
                    region1.append(int(boxs[j][0][index]))
                region_tmp1 = list(region1)
                w1 = region_tmp1[2]
                h1 = region_tmp1[3]
                box1 = [region_tmp1[0],region_tmp1[1],region_tmp1[0]+w1,region_tmp1[1]+h1]

                region2 = []
                for index in range(len(boxs[j][1])):     #对坐标取整
                    region2.append(int(boxs[j][1][index]))
                region_tmp2 = list(region2)
                w2 = region_tmp2[2]
                h2 = region_tmp2[3]
                box2 = [region_tmp2[0],region_tmp2[1],region_tmp2[0]+w2,region_tmp2[1]+h2]
                
                region_img1 = img_filter.crop(box1).resize((28*w1/h1,28))    #图片高度统一成28
                region_img2 = img_filter.crop(box2).resize((28*w2/h2,28))    #图片高度统一成28
                region_img1.save(result + '/regionImage/' + str(i) + '_filter_' + str(radius+sigma) + '_' + version + '_' + str(j) +'_1.jpg')
                region_img2.save(result + '/regionImage/' + str(i) + '_filter_' + str(radius+sigma) + '_' + version + '_' + str(j) +'_2.jpg')
                region_txt1 = open(result + '/regionImage/' + str(i) + '_filter_' + str(radius+sigma) + '_' + version + '_' + str(j) +'_1.txt','w')
                region_txt2 = open(result + '/regionImage/' + str(i) + '_filter_' + str(radius+sigma) + '_' + version + '_' + str(j) +'_2.txt','w')
                region_txt1.write(address1.encode('utf-8'))
                region_txt1.close()
                region_txt2.write(address2.encode('utf-8'))
                region_txt2.close()
        else:
            region = []
            for index in range(len(boxs[j])):
                region.append(int(boxs[j][index]))

            region_tmp = list(region)  #将数组转换成列表进行处理
            w = region_tmp[2]
            h = region_tmp[3]
            box = [region_tmp[0],region_tmp[1],region_tmp[0]+w,region_tmp[1]+h]
            region_img = img_filter.crop(box).resize((28*w/h,28))    #图片高度统一成28
            region_img.save(result + '/regionImage/' + str(i) + '_filter_' + str(radius+sigma) + '_' + version + '_' + str(j) +'.jpg')
            region_txt = open(result + '/regionImage/' + str(i) + '_filter_' + str(radius+sigma) + '_' + version + '_' + str(j) +'.txt','w')
            region_txt.write(word[j])
            region_txt.close()

#旋转加载每行字体，每行旋转角度保持一致
def drawline(image, region, myFont, theFont, s, pixel):       #s为每行文字信息‘unicode’
    angel = random.gauss(0,1)     #旋转角度
    rangel = numpy.deg2rad(angel)
    for letter in s:              
        image.text(region,letter,pixel,myFont)                    
        [width,height] = theFont.size(letter)
        region[0] = int(region[0] + width)
        region[1] = int(region[1] - numpy.tan(rangel)*width)

#生成并存储图片                
def drawtext(text,result,i,version):
        #模拟不同字体
        #字体     #不同的框字体大小不一致   #利用自造字体，黑体以及宋体来模拟字体   #一张图片使用一种字体
        pygame.init()
        n = random.random()
        if n < 0.6:        #自造字体
                #regular
                theFont1 = pygame.font.Font("../fonts/STSongti-SC-Black.ttf", 19)     
                myFont1 = ImageFont.truetype("../fonts/STSongti-SC-Black.ttf", 19)
                #住址
                theFont2 = pygame.font.Font("../fonts/STSongti-SC-Black.ttf", 21)     
                myFont2 = ImageFont.truetype("../fonts/STSongti-SC-Black.ttf", 21)
                #姓名和准驾车型
                theFont3 = pygame.font.Font("../fonts/STSongti-SC-Black.ttf", 29)     
                myFont3 = ImageFont.truetype("../fonts/STSongti-SC-Black.ttf", 29)
        elif n < 0.8:     #宋体--黑体
                #regular
                theFont1 = pygame.font.Font("../fonts/Songti.ttc", 19)     
                myFont1 = ImageFont.truetype("../fonts/Songti.ttc", 19)
                #住址
                theFont2 = pygame.font.Font("../fonts/Songti.ttc", 21)     
                myFont2 = ImageFont.truetype("../fonts/Songti.ttc", 21)
                #姓名和准驾车型
                theFont3 = pygame.font.Font("../fonts/Songti.ttc", 29)     
                myFont3 = ImageFont.truetype("../fonts/Songti.ttc", 29)
        else:          #黑体--中等
                #regular
                theFont1 = pygame.font.Font("../fonts/STHeiti Medium.ttc", 19)     
                myFont1 = ImageFont.truetype("../fonts/STHeiti Medium.ttc", 19)
                #住址
                theFont2 = pygame.font.Font("../fonts/STHeiti Medium.ttc", 21)     
                myFont2 = ImageFont.truetype("../fonts/STHeiti Medium.ttc", 21)
                #姓名和准驾车型
                theFont3 = pygame.font.Font("../fonts/STHeiti Medium.ttc", 29)     
                myFont3 = ImageFont.truetype("../fonts/STHeiti Medium.ttc", 29)

        #模拟字体颜色深浅
        pixel_tmp = random.randint(0,200)
        pixel = (pixel_tmp,)*3

        word = split(text)   #获取每小格信息

        boxs = []    #存储原始小框信息
        #背景图片
        backgroundName = '../assets/drive license template/' + version + '/' + str(random.randint(1,8)) + '.jpg'    #多种背景
        background = Image.open(backgroundName)
        image = ImageDraw.Draw(background)

        for index in range(len(word)):              #每行
                # angel = random.gauss(0,1)     #旋转角度
                # rangel = numpy.deg2rad(angel)
                s = unicode(word[index],'utf-8')

                #姓名和准驾车型
                if index == 1 or index == 7:
                        if version == 'new':
                                #image.text(position_new[index],s,pixel,font = myFont3)
                                position_temp = list(position_new[index])
                                region = position_temp
                                drawline(image, region, myFont3, theFont3, s, pixel)
                                
                        else:
                                #image.text(position_old[index],s,pixel,font = myFont3)
                                position_temp = list(position_old[index])
                                region = position_temp
                                drawline(image, region, myFont3, theFont3, s, pixel)
                        [w,h] = theFont3.size(s)
                        box = [position_temp[0],position_temp[1],w,h-3]
                        boxs.append(box)
                #地址
                elif index == 4:
                        [address1,address2] = addressprocess(s,version,theFont2)
                        if version == 'new':
                                #image.text(position_new[index][0],address1,pixel,font = myFont2)
                                [w1,h1] = theFont2.size(address1) 
                                position_temp1 = list(position_new[index][0])
                                region = position_temp1
                                drawline(image, region, myFont2, theFont2, address1, pixel)

                                #image.text(position_new[index][1],address2,pixel,font = myFont2)
                                [w2,h2] = theFont2.size(address2) 
                                position_temp2 = list(position_new[index][1])
                                region = position_temp2
                                drawline(image, region, myFont2, theFont2, address2, pixel)
                        else:
                                #image.text(position_old[index][0],address1,pixel,font = myFont2)
                                [w1,h1] = theFont2.size(address1) 
                                position_temp1 = list(position_old[index][0]) 
                                region = position_temp1
                                drawline(image, region, myFont2, theFont2, address1, pixel)

                                #image.text(position_old[index][1],address2,pixel,font = myFont2)
                                [w2,h2] = theFont2.size(address2) 
                                position_temp2 = list(position_old[index][1])
                                region = position_temp2
                                drawline(image, region, myFont2, theFont2, address2, pixel)

                        box1 = [position_temp1[0],position_temp1[1],w1,h1-3]
                        box2 = [position_temp2[0],position_temp2[1],w2,h2-3]
                        box = [box1,box2]
                        boxs.append(box)
                #正常行
                else:
                        if version == 'new':
                                #image.text(position_new[index],s,pixel,font = myFont1)
                                position_temp = list(position_new[index])
                                region = position_temp
                                drawline(image, region, myFont1, theFont1, s, pixel)
                                
                        else:
                                #image.text(position_old[index],s,pixel,font = myFont1)
                                position_temp = list(position_old[index])
                                region = position_temp
                                drawline(image, region, myFont1, theFont1, s, pixel)
                                
                        [w,h] = theFont1.size(s) 
                        box = [position_temp[0],position_temp[1],w,h-3]
                        boxs.append(box)

        #存储未处理整图
        background.save(result + '/wholeImage/'+str(i) + '_' + version + '.jpg')

        #旋转
        rotate_process(word, 2, result, boxs, background, version, i, theFont2)
        rotate_process(word, -2, result, boxs, background, version, i, theFont2)
        rotate_process(word, 1, result, boxs, background, version, i, theFont2)
        rotate_process(word, -1, result, boxs, background, version, i, theFont2)
        rotate_process(word, 0.5, result, boxs, background, version, i, theFont2)
        rotate_process(word, -0.5, result, boxs, background, version, i, theFont2)

        #透视
        #上方压缩
        dst_1 = numpy.array([[random.randint(-150,0),0],[random.randint(620,800),0],[620,420],[0,420]], numpy.float32)
        perspective_process(word, dst_1, result, boxs, background, version, 1, i, theFont2)
        #下方压缩
        dst_2 = numpy.array([[0,0],[620,0],[random.randint(620,800),420],[random.randint(-150,0),420]], numpy.float32)
        perspective_process(word, dst_2, result, boxs, background, version, 2, i, theFont2)
        #垂直压缩
        dst_3 = numpy.array([[0,0],[620,0],[620,520],[0,520]], numpy.float32)
        perspective_process(word, dst_3, result, boxs, background, version, 3, i, theFont2)
        #水平压缩
        dst_4 = numpy.array([[-100,0],[620,0],[620,420],[-100,420]], numpy.float32)
        perspective_process(word, dst_4, result, boxs, background, version, 4, i, theFont2)

        #模糊
        filter_process(word, result, boxs, background, version, 2, 150, i, theFont2)
        filter_process(word, result, boxs, background, version, 2, 250, i, theFont2)

def generateImage(texts, result, start_index):
    i = start_index
    for text in texts:
        word = split(text)
        if "-" in word[9]:
            version = 'new'
        else:
            version = 'old'
        i += 1
        drawtext(text,result,i,version)

        if i % 100 == 0:
            print("Thread: {0} generate {1}".format(start_index, i))

if __name__ == '__main__':
    isGPU = True

    #结果存放路径
    if isGPU:
        result = '/data/linkface/DriverLicense'  
    else:
        result = '/Users/xiuxiuzhang/Downloads/dldata_artificial'  

    #清空文件夹
    if os.path.exists(result + '/wholeImage/') == False:
        os.makedirs(result + '/wholeImage/')
    else:
        shutil.rmtree(result + '/wholeImage/')
        os.makedirs(result + '/wholeImage/')

    if os.path.exists(result + '/regionImage/') == False:
        os.makedirs(result + '/regionImage/')
    else:
        shutil.rmtree(result + '/regionImage/')
        os.makedirs(result + '/regionImage/')

    file = open('../assets/list.txt')   #输入信息
    #for line in file:
        #print line
    i = 0
    
    tsk = []
    texts = []
    for line in file:
        #print line
        i += 1             #生成第i个文件
        texts.append(line)
        word = split(line)
        #根据最后一个字符串判断版本
        if "-" in word[9]:
            version = 'new'
        else:
            version = 'old'

        #drawtext(line,result,i,version)


        if i % 5000 == 0:
            thread = threading.Thread(target = generateImage, args = (texts, result, i))
            thread.start()
            tsk.append(thread)
            texts = []

    if i % 5000 != 0:
            thread = threading.Thread(target = generateImage, args = (texts, result, i))
            thread.start()
            tsk.append(thread)

    for tt in tsk:
        tt.join()
    file.close()
    
        


       
