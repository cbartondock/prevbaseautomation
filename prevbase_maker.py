from PIL import Image
from PIL import ImageOps
from PIL import ImageDraw
from skimage import transform as tf
import os
import numpy as np
import math

# Helper Functions
def scalecrop(image, scaleheight, cropwidth):
    hpercent = float(scaleheight/float(image.size[1]))
    scalewidth = int(float(image.size[0])*hpercent)
    if scalewidth > cropwidth:
        scaled = image.resize((scalewidth,scaleheight),Image.BICUBIC)
        left = max((scalewidth-cropwidth)/2,0)
        right = min((scalewidth+cropwidth)/2,scalewidth)
        return scaled.crop((left,0,right,scaleheight))
    else:
        cropheight = int((float(image.size[0])/float(cropwidth))*scaleheight)
        top = max(0,(image.size[1]-cropheight)/2)
        bottom = min(image.size[1],(image.size[1]+cropheight)/2)
        cropped= image.crop((0,top,image.size[0],bottom))
        return cropped.resize((cropwidth,scaleheight),Image.BICUBIC)
def justwidth(image,scalewidth):
    if image.size[0]<scalewidth:
        return image
    wpercent = float(scalewidth/float(image.size[0]))
    scaleheight = int(float(image.size[1])*wpercent)
    return image.resize((scalewidth,scaleheight),Image.ANTIALIAS)
def justheight(image,scaleheight):
    if image.size[1]<scaleheight:
        return image
    hpercent = float(scaleheight/float(image.size[1]))
    scalewidth = int(float(image.size[0]*hpercent))
    return image.resize((scalewidth,scaleheight),Image.ANTIALIAS)
def maxdim(image, dim):
    dim = int(dim)
    return justwidth(image,dim) if image.size[0]>=image.size[1] else justheight(image,dim)
def opacity(image, frac):
    new = image.convert('RGBA')
    for i in range(0,image.size[0]):
        for j in range(0,image.size[1]):
            rgb=list(image.getpixel((i,j)))
            rgb[3]=int(frac*rgb[3])
            new.putpixel((i,j),tuple(rgb))
    return new
def shear(image, shearfrac):
    sheartf = tf.AffineTransform(shear=shearfrac)
    extended = Image.new("RGB",(int(image.size[0]*(1+abs(shearfrac))),image.size[1]))
    extended.paste(image,(0 if shearfrac>0 else extended.size[0]-image.size[0],0,image.size[0] if shearfrac>0 else extended.size[0],image.size[1]))
    result = tf.warp(extended, inverse_map=sheartf)
    resultim=Image.fromarray((result*255).astype(np.uint8))
    return resultim.resize(image.size,Image.ANTIALIAS)
def vline(image,x,y1,y2,width):
    draw = ImageDraw.Draw(image)
    draw.rectangle(((int(x-width*.5),int(min(y1,y2))),(int(x+width*.5),int(max(y1,y2)))), fill='black')
def hline(image,y,x1,x2,width):
    draw = ImageDraw.Draw(image)
    draw.rectangle(((int(min(x1,x2)),int(y-width*.5)),(int(max(x1,x2)),int(y+width*.5))), fill='black')
def buttonpositions(buttonlist,center,width):
    nb = len(buttonlist)
    sep = 0.7*max([b.size[0] for b in buttonlist])
    if nb==1:
        return [(
                math.floor(center[0]-buttonlist[0].size[0]/2.),
                math.floor(center[1]-buttonlist[0].size[1]/2.),
                math.floor(center[0]+buttonlist[0].size[0]/2.),
                math.floor(center[1]+buttonlist[0].size[1]/2.)
            )]
    elif nb==2:
        return [(
                math.floor(center[0]-buttonlist[0].size[0]),
                math.floor(center[1]-buttonlist[0].size[1]/2.),
                math.floor(center[0]),
                math.floor(center[1]+buttonlist[0].size[1]/2.)
        ),(
                math.floor(center[0]),
                math.floor(center[1]-buttonlist[1].size[1]/2.),
                math.floor(center[0]+buttonlist[1].size[0]),
                math.floor(center[1]+buttonlist[1].size[1]/2.)
        )]
    elif nb==3:
        return [(
                math.floor(center[0]-sep-buttonlist[0].size[0]/2.),
                math.floor(center[1]-buttonlist[0].size[1]/2.),
                math.floor(center[0]-sep+buttonlist[0].size[0]/2.),
                math.floor(center[1]+buttonlist[0].size[1]/2.)
        ),(
                math.floor(center[0]-buttonlist[1].size[0]/2.),
                math.floor(center[1]-buttonlist[1].size[1]/2.),
                math.floor(center[0]+buttonlist[1].size[0]/2.),
                math.floor(center[1]+buttonlist[1].size[1]/2.)
        ),(
                math.floor(center[0]+sep-buttonlist[2].size[0]/2.),
                math.floor(center[1]-buttonlist[2].size[1]/2.),
                math.floor(center[0]+sep+buttonlist[2].size[0]/2.),
                math.floor(center[1]+buttonlist[2].size[1]/2.)
        )]


# Function to build prevbase
def build_prevbase(base_im, sub_ims,subbuttons,buttonopacity=1.,buttonsizeboost=0.,borderwidth=-1):
    prevbase = Image.new("RGB", (480,480))
    nsubs=len(subbuttons)
    if nsubs == 0:
        base_im_component = scalecrop(base_im,480,480)
        prevbase.paste(base_im_component,(0,0,480,480))
    if nsubs == 1:
        base_im_component = scalecrop(base_im,240,480)
        singlesub = scalecrop(sub_ims[0], 240,480)
        prevbase.paste(base_im_component,(0,0,480,240))
        prevbase.paste(singlesub,(0,240,480,480))
        if borderwidth > 0:
            hline(prevbase,240,0,480,borderwidth)
        subbuttons[0] = [opacity(maxdim(b,60*(1+buttonsizeboost)),buttonopacity) for b in subbuttons[0]]
        poslist=buttonpositions(subbuttons[0],(240,240),480)
        for j in range(0,len(subbuttons[0])):
            prevbase.paste(subbuttons[0][j],poslist[j],subbuttons[0][j])

    if nsubs == 2:
        base_im_component = scalecrop(base_im,240,480)
        sub_im_components = [scalecrop(si,240,240) for si in sub_ims]
        prevbase.paste(base_im_component,(0,0,480,240))
        for i in range(0,nsubs):
            prevbase.paste(sub_im_components[i],(240*i,240,240*(i+1),480))
        if borderwidth > 0:
            hline(prevbase,240,0,480,borderwidth)
            vline(prevbase,240,240,480,borderwidth)
        for i in range(0,nsubs):
            subbuttons[i] = [opacity(maxdim(b,60*(1+buttonsizeboost)),buttonopacity) for b in subbuttons[i]]
            poslist=buttonpositions(subbuttons[i],(120*(2*i+1),240),240)
            for j in range(0,len(subbuttons[i])):
                prevbase.paste(subbuttons[i][j],poslist[j],subbuttons[i][j])
    if nsubs == 3:
        base_im_component = scalecrop(base_im,240,480)
        sub_im_components = [scalecrop(sub_ims[i],240,240) if i==0 else scalecrop(sub_ims[i],120,240) for i in range(0,nsubs)]
        prevbase.paste(base_im_component,(0,0,480,240))
        for i in range(0,nsubs):
            x, ydelt = (0,240) if i==0 else (240,120)
            y=240 if i<2 else 360
            prevbase.paste(sub_im_components[i],(x,y,x+240,y+ydelt))
        if borderwidth>0:
            hline(prevbase,240,0,480,borderwidth)
            vline(prevbase,240,240,480,borderwidth)
            hline(prevbase,360,240,480,borderwidth)
        for i in range(0,nsubs):
            subbuttons[i] = [opacity(maxdim(b,50*(1+buttonsizeboost)),buttonopacity) for b in subbuttons[i]]
            poslist=buttonpositions(subbuttons[i],([120,360,360][i],[240,240,360][i]),240)
            for j in range(0,len(subbuttons[i])):
                prevbase.paste(subbuttons[i][j],poslist[j],subbuttons[i][j])
    if nsubs == 4:
        base_im_component = scalecrop(base_im,240,480)
        sub_im_components = [scalecrop(si,120,240) for si in sub_ims]
        prevbase.paste(base_im_component,(0,0,480,240))
        for i in range(0,nsubs):
            x, y = 240*(i%2), 240+(i//2)*120
            prevbase.paste(sub_im_components[i],(x,y,x+240,y+120))
        if borderwidth>0:
            hline(prevbase,240,0,480,borderwidth)
            vline(prevbase,240,240,480,borderwidth)
            hline(prevbase,360,0,480,borderwidth)
        for i in range(0,nsubs):
            subbuttons[i] = [opacity(maxdim(b,50*(1+buttonsizeboost)),buttonopacity) for b in subbuttons[i]]
            poslist=buttonpositions(subbuttons[i],([120,360,120,360][i],[240,240,360,360][i]),240)
            for j in range(0,len(subbuttons[i])):
                prevbase.paste(subbuttons[i][j],poslist[j],subbuttons[i][j])
    if nsubs == 5:
        base_im_component = scalecrop(base_im,240,360)
        prevbase.paste(base_im_component,(0,0,360,240))
        for i in range(0,nsubs):
            subcomp = scalecrop(sub_ims[i],120,120) if i<2 else scalecrop(sub_ims[i],240 if i==2 else 120,240)
            x=360 if i<2 else ((i-2)>=1)*240
            y=120*i if i<2 else 240+120*((i-2)//2)
            xdelt = 120 if i<2 else 240
            ydelt = 120 if i!=2 else 240
            prevbase.paste(subcomp,(x,y,x+xdelt,y+ydelt))
        if borderwidth>0:
            hline(prevbase,240,0,480,borderwidth)
            vline(prevbase,360,0,240,borderwidth)
            hline(prevbase,120,360,480,borderwidth)
            vline(prevbase,240,240,480,borderwidth)
            hline(prevbase,360,240,480,borderwidth)
        for i in range(0,nsubs):
            subbuttons[i] = [opacity(maxdim(b,50*(1+buttonsizeboost)),buttonopacity) for b in subbuttons[i]]
            poslist=buttonpositions(subbuttons[i],([420,420,120,360,360][i],[20,120,240,240,360][i]),120 if i<2 else 240)
            for j in range(0,len(subbuttons[i])):
                prevbase.paste(subbuttons[i][j],poslist[j],subbuttons[i][j])
    if nsubs == 6:
        base_im_component = scalecrop(base_im,240,360)
        prevbase.paste(base_im_component,(0,0,360,240))
        for i in range(0,nsubs):
            subcomp=scalecrop(sub_ims[i],120,120) if i<2 else scalecrop(sub_ims[i],120,240)
            x=360 if i<2 else ((i-2)%2)*240
            y=120*i if i<2 else 240+((i-2)//2)*120
            xdelt= 120 if i<2 else 240
            prevbase.paste(subcomp,(x,y,x+xdelt,y+120))
        if borderwidth>0:
            hline(prevbase,240,0,480,borderwidth)
            vline(prevbase,360,0,240,borderwidth)
            hline(prevbase,120,360,480,borderwidth)
            hline(prevbase,360,0,480,borderwidth)
            vline(prevbase,240,240,480,borderwidth)
        for i in range(0,nsubs):
            subbuttons[i] = [opacity(maxdim(b,50*(1+buttonsizeboost)),buttonopacity) for b in subbuttons[i]]
            poslist=buttonpositions(subbuttons[i],([420,420,120,360,120,360][i],[20,120,240,240,360,360][i]),120 if i<2 else 240)
            for j in range(0,len(subbuttons[i])):
                prevbase.paste(subbuttons[i][j],poslist[j],subbuttons[i][j])
    if nsubs == 7:
        base_im_component = scalecrop(base_im,240,360)
        prevbase.paste(base_im_component,(0,0,360,240))
        for i in range(0,nsubs):
            subcomp=scalecrop(sub_ims[i],120,120 if i in [0,1,3,4] else 240)
            x=[360,360,0,240,360,0,240][i]
            y=[0,120,240,240,240,360,360][i]
            xdelt=120 if i in [0,1,3,4] else 240
            prevbase.paste(subcomp,(x,y,x+xdelt,y+120))
        if borderwidth>0:
            hline(prevbase,240,0,480,borderwidth)
            vline(prevbase,360,0,360,borderwidth)
            hline(prevbase,120,360,480,borderwidth)
            hline(prevbase,360,0,480,borderwidth)
            vline(prevbase,240,240,480,borderwidth)
        for i in range(0,nsubs):
            subbuttons[i] = [opacity(maxdim(b,50*(1+buttonsizeboost)),buttonopacity) for b in subbuttons[i]]
            poslist=buttonpositions(subbuttons[i],([420,420,120,300,420,120,360][i],[20,120,240,240,240,360,360][i]),120 if i in [0,1,3,4] else 240)
            for j in range(0,len(subbuttons[i])):
                prevbase.paste(subbuttons[i][j],poslist[j],subbuttons[i][j])
    if nsubs == 8:
        base_im_component = scalecrop(base_im,240,360)
        prevbase.paste(base_im_component,(0,0,360,240))
        for i in range(0,nsubs):
            subcomp=scalecrop(sub_ims[i],120,240 if i in [2,3] else 120)
            x=[360,360,0,0,240,360,240,360][i]
            y=[0,120,240,360,240,240,360,360][i]
            xdelt=240 if i in [2,3] else 120
            prevbase.paste(subcomp,(x,y,x+xdelt,y+120))
        if borderwidth>0:
            hline(prevbase,240,0,480,borderwidth)
            vline(prevbase,360,0,480,borderwidth)
            hline(prevbase,120,360,480,borderwidth)
            hline(prevbase,360,0,480,borderwidth)
            vline(prevbase,240,240,480,borderwidth)
        for i in range(0,nsubs):
            subbuttons[i] = [opacity(maxdim(b,50*(1+buttonsizeboost)),buttonopacity) for b in subbuttons[i]]
            poslist=buttonpositions(subbuttons[i],([420,420,120,120,300,420,300,420][i],[20,120,240,360,240,240,360,360][i]),240 if i in [2,3] else 120)
            for j in range(0,len(subbuttons[i])):
                prevbase.paste(subbuttons[i][j],poslist[j],subbuttons[i][j])
    if nsubs == 9:
        base_im_component = scalecrop(base_im,240,360)
        prevbase.paste(base_im_component,(0,0,360,240))
        for i in range(0,nsubs):
            subcomp=scalecrop(sub_ims[i],120,240 if i==2 else 120)
            x=[360,360,0,240,360,0,120,240,360][i]
            y=[0,120,240,240,240,360,360,360,360][i]
            xdelt=240 if i==2 else 120
            prevbase.paste(subcomp,(x,y,x+xdelt,y+120))
        if borderwidth>0:
            hline(prevbase,240,0,480,borderwidth)
            vline(prevbase,360,0,480,borderwidth)
            hline(prevbase,120,360,480,borderwidth)
            hline(prevbase,360,0,480,borderwidth)
            vline(prevbase,240,240,480,borderwidth)
            vline(prevbase,120,360,480,borderwidth)
        for i in range(0,nsubs):
            subbuttons[i] = [opacity(maxdim(b,50*(1+buttonsizeboost)),buttonopacity) for b in subbuttons[i]]
            poslist=buttonpositions(subbuttons[i],([420,420,120,300,420,60,180,300,420][i],[20,120,240,240,240,360,360,360,360][i]),240 if i==2 else 120)
            for j in range(0,len(subbuttons[i])):
                prevbase.paste(subbuttons[i][j],poslist[j],subbuttons[i][j])
    if nsubs == 10:
        base_im_component = scalecrop(base_im,240,360)
        sub_im_components = [scalecrop(si, 120,120) for si in sub_ims]
        prevbase.paste(base_im_component,(0,0,360,240))
        for i in range(0,nsubs):
            x=360 if i<2 else ((i-2)%4)*120
            y=120*i if i<2 else (((i-2)//4)*120+240)
            prevbase.paste(sub_im_components[i],(x,y,x+120,y+120))
        if borderwidth>0:
            hline(prevbase,240,0,480,borderwidth)
            vline(prevbase,360,0,480,borderwidth)
            hline(prevbase,120,360,480,borderwidth)
            hline(prevbase,360,0,480,borderwidth)
            vline(prevbase,240,240,480,borderwidth)
            vline(prevbase,120,240,480,borderwidth)
        for i in range(0,nsubs):
            subbuttons[i] = [opacity(maxdim(b,50*(1+buttonsizeboost)),buttonopacity) for b in subbuttons[i]]
            poslist=buttonpositions(subbuttons[i],([420,420,60,180,300,420,60,180,300,420][i],[20,120,240,240,240,240,360,360,360,360][i]),120)
            for j in range(0,len(subbuttons[i])):
                prevbase.paste(subbuttons[i][j],poslist[j],subbuttons[i][j])
    return prevbase


# Load in configuration
conf={}
with open('config.txt','r') as conf_file:
    conf_a,conf_b = zip(*[line.split('//')[0].split('=') for line in filter(lambda l: len(l)>0,conf_file.read().split('\n'))])
    conf_a = map(lambda s: s.strip(), conf_a)
    conf_b = map(lambda s: float(s.strip()), conf_b)
    conf = dict(zip(conf_a,conf_b))
conf['buttonopacity'] = max(min(conf['buttonopacity'],1.),0.)
conf['buttonsizeboost'] = max(min(conf['buttonsizeboost'],1.),-1.)
conf['shear'] = max(min(conf['shear'],1.),-1.)
conf['posterize'] = max(min(int(conf['posterize']),8),0) if conf['posterize']>0 else -1
conf['solarize'] = max(min(int(conf['solarize']),256),0) if conf['solarize']>0 else -1
conf['borderwidth'] = max(min(int(conf['borderwidth']),20),0) if conf['borderwidth']>0 else -1


# Load in images and make the prevbases
idir='inputs/'
odir='outputs/'
buttondir='buttons/'
butt_f_list = [f for f in os.listdir(buttondir) if os.path.isfile(buttondir+f)]
buttons = [Image.open(buttondir+butt_f) for butt_f in butt_f_list]
buttondict = {butt_f.split('.')[0]:Image.open(buttondir+butt_f) for butt_f in butt_f_list}
for stage in [d for d in os.listdir(idir) if os.path.isdir(idir+d)]:
    base_f_list = [f for f in os.listdir(idir+stage) if os.path.isfile(idir+stage+'/'+f)]
    sub_f_list = [f for f in os.listdir(idir+stage+'/subimages/') if os.path.isfile(idir+stage+'/subimages/'+f)]
    nsubs = len(sub_f_list)
    if len(base_f_list)==0:
        print("To make a Prevbase at least the base image is required.")
        print("Your stage "+stage+" is missing a base image. Just plop a screenshot in that directory.")
        exit()
    base_f= base_f_list[0]
    base_image = Image.open(idir+stage+'/'+base_f)
    sub_images = [Image.open(idir+stage+'/subimages/'+sub_f) for sub_f in sub_f_list]
    if conf['posterize'] > 0:
        base_image = ImageOps.posterize(base_image.convert('RGB'),conf['posterize'])
        sub_images = [ImageOps.posterize(si.convert('RGB'),conf['posterize']) for si in sub_images]
    if conf['solarize'] > 0:
        base_image = ImageOps.solarize(base_image.convert('RGB'),conf['solarize'])
        sub_images = [ImageOps.solarize(si.convert('RGB'),conf['solarize']) for si in sub_images]
    sub_buttons= [[buttondict[b] for b in sub_f_list[i].split('.')[0].split("_")] for i in range(0,nsubs)]
    if max([len(buttonlist) for buttonlist in sub_buttons])>3:
        print("At most three buttons can be used for a single stage.")
        print("Your stage "+stage+" has a subimage with too many buttons in its name.")
        exit()
    # Build Prevbase
    prevbase = build_prevbase(base_image,sub_images,sub_buttons,conf['buttonopacity'],conf['buttonsizeboost'],conf['borderwidth'])
    prevbase = shear(prevbase,conf['shear'])
    prevbase.save(odir+stage+'_preview.png',quality=100)
    # Build Icon
    icon = scalecrop(base_image,228,256)
    icon.save(odir+stage+'_icon.png',quality=100)
