import pygame
import time
import numpy as np
import os
import re
import random
import math
import threading
from collections import deque
import wave
import pyaudio
import struct
from copy import deepcopy

random.seed()

pygame.init()
size = 500, 500
bgcolor = 100, 200, 255
objs = []
screen = pygame.display.set_mode(size)
imgs = {}
tickrate = 128

mfrate = 44100

def readWav(name):
	wf = wave.open(name, 'rb')
	return wf.readframes(wf.getnframes())

ohno = readWav('Error_441.wav')
succ = readWav('Success_441.wav')
dogBark = readWav('dog_bark.wav')
chickDead = readWav('deadchick.wav')

def importimgs():
	#imports all images in the imgs subfolder in the project directory and loads them into a dict with appropriate names. 
	#Failure to load or missing images will cause a runtime exception, if not now, then later.
	global imgs
	for root, dirs, files in os.walk(os.getcwd()):
		for file in files:
			if re.match('.+?\.png', file, re.IGNORECASE):
				imgs[re.match(r'(.+?)\.', file).groups(1)[0]] = pygame.image.load(file).convert_alpha()
	
importimgs()

class buf(deque):
	def put(self, iterable):
		for i in iterable:
			self.append(i)
	def peek(self, how_many):
		return([self[i] for i in range(how_many)])
	def get(self, how_many):
		return([self.popleft() for i in range(how_many)])
	def add(self, ite, sf = 0):
		for n in range(len(ite)):
			i = n+sf
			try:
				self[i] += ite[n]
			except:
				self.append(ite[n])
	def cl(self):
		self = b''

class nthread (threading.Thread):
	def __init__(self, func, arg = None):
		threading.Thread.__init__(self)
		self.f = func
		self.a = arg
	def run(self):
		if self.a:
			self.f(self.a)
		else:
			self.f()	
	
bg = pygame.Surface(size)
bg.fill(bgcolor) 
def play(tp):  
	chunk = 1024
	p = pyaudio.PyAudio()  
	stream = p.open(format = 8, channels = 1, rate = mfrate, output = True)
	 
	stream.write(tp)
	
	stream.stop_stream()  
	stream.close()  
	p.terminate()
	
def playSound(sound):
	pt = nthread(play, sound)
	pt.start()
	
class bobj:
	#Base objekt
	imgn = 'NoImageName'
	def __init__(self, **kwargs):
		#self.imgn = kwargs.get('imgn', 'NoImageName')		#Dicionary name of image
		self.img = imgs[self.imgn]							#Current sprite
		self.rec = None										#Current rectangel for drawing sprite
		self.rpos = kwargs.get('rpos', [0, 0])				#Obejcts real position
		self.gpos = np.floor(self.rpos)						#Obejcts graphical position
		self.dir = kwargs.get('dir', 0)						#Direction obejct is facing, 0 is up, 360 degrees
		self.skaldoe = kwargs.get('skaldoe', False)			#True hvis object skal slettes
		self.tps = kwargs.get('tps', [])					#List arbitrary object types
		self.align = kwargs.get('align', 'NEUTRAL')
		self.nm = kwargs.get('nm', 'NONAME')
	def istp(self, **kwargs):
		#Tjeks if object is type
		tp = kwargs.get('tp', 'NONETYPE')
		for ele in self.tps:
			if ele==tp:
				return(True)
		return(False)
	def updtimgp(self):
		#Move drawing rectangel to current graphical position
		self.gpos = np.floor(self.rpos)
		reh = self.img.get_rect()
		reh = reh.move(self.gpos[0]-reh[2]/2, self.gpos[1]-reh[3]/2)
		self.rec = reh
	def updtimg(self):
		#Update sprite and drawing rectangel to current position and direction
		self.img = pygame.transform.rotate(imgs[self.imgn], self.dir)
		self.updtimgp()
	def rotate(self, amnt = 0, to = False, updt = True):
		#Rotates object an amount of degrees. A True to value sets the angle.
		if to:
			self.dir = amnt
		else:
			self.dir+=amnt
		if updt:
			self.updtimg()
	def move(self, *agrs, **kwargs):
		#Move object
		movamnt = kwargs.get('amnt', [0, 0])
		for i in range(2):
			self.rpos[i]+=moveamnt[i]
		self.gpos = funclst(self.rpos, math.floor)
	def draw(self):
		#Draw object
		if self.rec and self.img:
			screen.blit(self.img, self.rec)
	def tick(self, **kwargs):
		#Is here to be inherited
		pass	

class Coin(bobj):
	imgn = 'coin'
	def __init__(self, **kwargs):
		super(Coin, self).__init__(**kwargs)
		self.speed = kwargs.get('speed', 256)		
	def tick(self):
		self.rpos[1] += self.speed/tickrate
		if self.rpos[1]>size[1]:
			self.skaldoe = True
			ascore_()
		self.updtimgp()
		
class Paddle(bobj):
	imgn = 'paddle'
	def __init__(self, **kwargs):
		super(Paddle, self).__init__(**kwargs)
		self.speed = kwargs.get('speed', 360)
	def tick(self):
		for event in pygame.event.get():
			if event.type==pygame.KEYDOWN and event.key==pygame.K_SPACE:
				objs.append(Bullet(rpos=[self.rpos[0], size[1]-50]))
		key=pygame.key.get_pressed()
		if key[pygame.K_RIGHT]:
			self.rpos[0] += self.speed/tickrate
		if key[pygame.K_LEFT]:
			self.rpos[0] -= self.speed/tickrate
		if self.rpos[0]>size[0]:
			self.rpos[0] = size[0]
		elif self.rpos[0]<0:
			self.rpos[0] = 0
		self.updtimgp()
		for obj in objs:
			if obj!=self and obj.rpos[1]>(size[1]-40) and math.fabs(obj.rpos[0]-self.rpos[0])<50:
				obj.skaldoe = True
				score_()
	
def gdis(o1, o2):
	return math.sqrt((o1.rpos[0]-o2.rpos[0])**2+(o1.rpos[1]-o2.rpos[1])**2)
		
class Fugl(bobj):
	imgn = 'fugl_lille'
	def __init__(self, **kwargs):
		super(Fugl, self).__init__(**kwargs)
		self.speed = kwargs.get('speed', 500)		
	def tick(self):
		self.rpos[0] -= self.speed/tickrate
		if self.rpos[0]<0:
			self.skaldoe = True
		for obj in objs:
			if type(obj)==Coin and gdis(self, obj)<50:
				obj.skaldoe = True
				ascore_()
		self.updtimgp()
		
class Bullet(bobj):
	imgn = 'hund'
	def __init__(self, **kwargs):
		super(Bullet, self).__init__(**kwargs)
		self.speed = kwargs.get('speed', 700)
		playSound(dogBark)
	def tick(self):
		self.rpos[1] -= self.speed/tickrate
		if self.rpos[1]<0:
			self.skaldoe = True
		for obj in objs:
			if type(obj)==Fugl and gdis(self, obj)<50:
				obj.skaldoe = True
				playSound(chickDead)
		self.updtimgp()
		
coinSpawnRate = 1
birdSpawnRate = 1
		
score = 0
antiscore = 0
def score_(val = 1):
	global score
	score += val
	playSound(succ)

def ascore_(val = 1):
	global antiscore
	antiscore += val
	playSound(ohno)
	
fonto = pygame.font.SysFont(pygame.font.get_default_font(), 18)
glsize = (10, 10)
def tick():
	#for event in pygame.event.get():
	#	if event.type==pygame.QUIT:
	#		return 'quitting'
	if random.random()<coinSpawnRate/tickrate:
		objs.append(Coin(rpos=np.asarray([random.random()*size[0], 0])))
	if random.random()<birdSpawnRate/tickrate:
		objs.append(Fugl(rpos=np.asarray([size[0], random.random()*size[1]])))
	i = 0
	while i<len(objs):
		if objs[i].skaldoe:
			del objs[i]
		else:	
			objs[i].tick()
			i+=1
	if ctick%tickrate==0:
		bg.scroll(-5, 0)
		bg.fill((0, 0, 0), (size[0]-glsize[0]*2, int(size[1]-((score)/(score+antiscore+1)*size[1])), glsize[0], glsize[1]))
	screen.blit(bg, (0, 0))
	for obj in objs:
		obj.draw()
	fimg = fonto.render('SUCCESSFUL SPECULATIONS: '+str(score), 1, (255, 255, 0))
	screen.blit(fimg, fimg.get_rect().move([100, 33]))
	fimg = fonto.render('FAILED MINING: '+str(antiscore)+' :(((', 1, (255, 0, 0))
	screen.blit(fimg, fimg.get_rect().move([100, 66]))
		
	pygame.display.flip()

ctick = 0
def main():
	ntick = 0
	global ctick
	inter = 1/tickrate
	ori_time = time.time()
	next_call = time.time()
	objs.append(Paddle(rpos=np.asarray([100, size[1]-10], dtype=np.float)))
	while True:
		ntick += inter
		ctick += 1
		if ori_time-next_call+ntick>0:
			time.sleep(ori_time-next_call+ntick)
		if not tick()==None: break
		next_call = time.time()

if __name__=='__main__':	
	main()