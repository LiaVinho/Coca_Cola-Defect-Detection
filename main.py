import skimage.io as skio
import matplotlib.pyplot as plt
import glob, os
import numpy as np
import  skimage.filters as skf
import pprint       #printing list 
from skimage.color import rgb2gray
from skimage.morphology import square,erosion

def check_bottle_cap(img):
    img = rgb2gray(img)
    thresh = skf.threshold_mean(img)
    binary = img > thresh
    # nfig, ax = skf.try_all_threshold(img, figsize=(10, 6), verbose=False)
    cropped = binary[0:-1,100:255]
    bottle_cap=cropped[0:50,0:-1]
    cap=erosion(bottle_cap,square(30))
    x= cap.sum()
    if x>3900 and x <6500:
        return "bottle cap is missing"
    return "No defects"

def check_label_misprint(img):
    edges=skf.sobel(img)
    img = rgb2gray(img)
    thresh = skf.threshold_mean(img)
    binary = img > thresh
    
    # nfig, ax = skf.try_all_threshold(img, figsize=(10, 6), verbose=False)
    cropped = binary[0:-1,100:255]
    label= cropped[170:-1,0:150]
    x=erosion(label, square(30))
    if x.sum()>6000 and x.sum()<7000:
        return "bottle has label but label printing has failed"
    return "No defects"

def check_bottle_Missing(img):
    img = rgb2gray(img)
    thresh = skf.threshold_mean(img)
    binary = img > thresh
    cropped = binary[0:-1,100:255]
    x=cropped[0:-1,50:80]
    c=x.sum()
    if c>=8580:
        return "Bottle Missing"
    return "No defects"

def check_bottle_underfilled(img):
     img = rgb2gray(img)
     thresh = skf.threshold_mean(img)
     binary = img > thresh
     cropped = binary[0:-1,100:255]
     x=cropped[70:-1,80:110]
     x=erosion(x, square(30))
     # print_(x,cropped)
     c=x.sum()
     if c<300:
         return "bottle over-filled" 
     if c>2400 and c<3100:
         return "bottle under-filled or not filled at all"
     return "No defects"
    
def check_bottle_label(img):
    img = rgb2gray(img)
    thresh = skf.threshold_mean(img)
    binary = img > thresh
    cropped = binary[240:280,115:175]
    # print_(binary,cropped)
    black = cropped.sum()
    total_pixels=np.shape(cropped)[1]*np.shape(cropped)[0]
    x=100*((total_pixels-black)/total_pixels)
    if x >95:
        return "bottle has label missing"
    return "No defects"
def check_label_straight(img):
    if check_bottle_Missing(img)=="No Fault":
        img = rgb2gray(img)
        thresh = skf.threshold_mean(img)
        binary = img > thresh
        cropped = binary[240:280,115:175]
        label = binary[180:330,110:250]
        c=label.sum()
        if c>2600 and c<3700:
            return "bottle label is not straight"
    return "No defects"
def print_(before,after):
    f, ax = plt.subplots(1,2)
    ax[0].imshow(before,cmap="gray") #first image
    ax[0].text(3,2,"Before")
    ax[1].imshow(after,cmap="gray") #second image
    ax[1].text(3,2,"After")
    # print(before.sum())
    plt.show()

def processImage(img):
    faults=[1,0,0,0,0,
            0,0,0,0,0]
    
    fl=False
    x=""    
    c=check_bottle_cap(img)
    if ( c != "No defects"):
        fl=True
        faults[1]=1
        x+=c
    c=check_label_misprint(img)
    if (c!="No defects"):    
        fl=True
        faults[2]=1
        x+=c
    c=check_bottle_Missing(img)
    if (c!="No defects"):    
        faults[3]=1
        fl=True
        x+=c
    c=check_bottle_underfilled(img)
    if (c!="No defects"):
        if(c=="bottle under-filled or not filled at all"):
            faults[4]=1
            fl=True
            x+=c
        if(c=="bottle over-filled"):
            faults[5]=1
            fl=True    
            x+=c
            
        
    c=check_bottle_label(img)
    if (c!="No defects"):    
        faults[6]=1
        fl=True
        x+=c
    c=check_label_straight(img)
    if(c!="No defects"):
        faults[7]=1
        fl=True
        x+=c
        
    if(fl==False):
        xcs=bottle_deformed(img)
        if (xcs=="Bottle Deformed"):
            fl=True
            faults[8]=1
            x+=xcs
            return faults,x
        faults[9]=1
        x+=c    
        # print (fName,x) 
    return faults,x
def processDirectory(dirName):
    os.chdir(dirName)
    fault = [["BC","LM","BM","OF","UN","LF","LS","BD","NF"]]
    #BC BOTTLECAP           2
    #LM LABELMISSING        2
    #BM BOTTLE MISSING      2
    #OF OVER FILLED         2
    #UF UNDER FILLED        2
    #LF LABEL PRINTINT FAILDE  2
    #LS LABEL NOT STRAIGH  3
    #BD BOTTLEDEFORME      3
    #NF NORMAL   3
    for fName in glob.glob("*.jpg"):
        fPath = dirName + fName
        img = skio.imread(fPath)
        faults,x = processImage(img)
        plt.figure()
        plt.imshow(img)
        plt.title(x)
        faults[0]=fName
        fault+=[faults]
        print(fName + " : " + x)
    
    c=[0,0,0,0,0
        ,0,0,0,0,0]
    
    for i in range(1,22):
        for j in range(1,10):   
            # print (i,j,fault[i][j])
            c[j]+=fault[i][j]
            
    
    # print(c)
    pprint.pprint(fault)
    print("Missing Bottle Cap=",c[1])
    print("Missing Label =",c[2])
    print("Bottle Missing=",c[3])
    print("OverFilled=",c[4])
    print("Under FIlled=",c[5])
    print("Label Print Failure=",c[6])
    print("Label Not Straigt=",c[7])
    print("Deformed Bottles =",c[8])
    print("Normal Bottles =",c[9])
def bottle_deformed(img):
    
    bottle=img[:,:,1]
    cimg=bottle[170:200,100:260]
    # dimg=equalize(cimg)
    border=skf.sobel_h(cimg)
    border=skf.laplace(cimg)
    
    thresh = skf.threshold_mean(border)
    nex = border > thresh
    nex= nex- border
    b=nex.sum()
    
    c=np.shape(cimg)[1]*np.shape(cimg)[0]
    xcs=100*((c-b)/c)
    if (xcs>=51.0 and xcs<=52.0):
        return "Bottle Deformed"
    return "No defects"

if __name__ == '__main__':
    myDir = ''
    processDirectory(myDir)



def equalize(img):
    unique,count=np.unique(img,return_counts=True)
    freq=np.asarray((unique,count))
    fmin=freq[0].min()
    fmax=freq[0].max()
    new_intensity=((img-fmin)/(fmax-fmin))*255
    new_intensity=new_intensity.astype(np.uint8)
    return new_intensity

def f1(a1,img):
    return img*a1
def f2(s1,img,r1,a2):
    return (s1+(img-r1)*a2)
def piecewiseTransform(img, anchors, functions):
    new_img=np.where(
            (img<anchors[2][0]) ,
                eval(functions[0]+'(anchors[0][0],img)'),
            np.where(
            ((img>anchors[2][0])&(img<anchors[2][1])) ,
                eval(functions[1]+'(anchors[1][0],img,anchors[2][0],anchors[0][1])'),
            np.where(
            ((img>anchors[2][1])&(img<anchors[2][2])) ,
                eval(functions[1]+'(anchors[1][1],img,anchors[2][1],anchors[0][2])'),
                img)))
    return new_img


def normalize(img):
    new_=np.array(img)
    r,c=img.shape
    #frequency of gray levelss
    freq=np.zeros(256)
    for i in range(0,r):
        for j in range(0,c):
            freq[img[i][j]]=freq[img[i][j]]+1
    ##########################pmf##########################
    total_pixels=freq.sum()
    pmf=freq/total_pixels
    ##########################pmf##########################
    
    ##########################CDF##########################
    # cdf=np.cumsum(pmf)
    cdf=pmf
    # pmf.shape
    for i in range(1,255):
          cdf[i]=cdf[i]+cdf[i-1]
          # print(cdf[i],pmf[i],pmf[i-1])
    ##########################CDF##########################
    
    ##########################New Level##########################
    new_level=cdf*(256-1)
    new_level=new_level.astype(np.uint8)
    # img=img.astype(np.uint8)
    # ##########################New Level##########################
    
    for i in range(0,r):
        for j in range(0,j):
            new_[i][j]=new_level[img[i][j]]
    return new_






