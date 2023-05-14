import threading
import hashlib
from threading import Lock
from multiprocessing.dummy import Pool
from multiprocessing import cpu_count
import time
import random
import os
import shutil

def GetCPUcount():
	#print(cpu_count())
	return cpu_count()

# ---- POC 1 ----

def task(subD):
	print("subD", subD)
	print("Thread :", threading.get_ident())
	time.sleep(1 + random.randint(1, 10))


def test(d):
	lock = [False]
	step = 4
	keys = list(d.keys())
	pool = Pool()
	for i in range(0, len(d), step):
		subD = {k: d[k] for k in keys[i: i+step]}
		#print(subD)
		a = pool.imap(task, {k: d[k] for k in keys[i: i+step]})
	for i in a:
		print(i)


# ---- POC 2 ----

def watchList(tl, plck, cpt, tsk):
	while True:
		plck.acquire()
		print(f"Tlist = ", len(tl), tl, "cpt:", cpt)
		if(cpt == tsk):
			break
		plck.release()
		time.sleep(1)


def work(subdict, plck, cpt):
	plck.acquire()
	print(f"Thread :", threading.get_ident(), ", sub-dict :", subdict)
	cpt[0] += 1
	plck.release()
	time.sleep(1 + random.randint(1, 10))


def dummyPool(d):
	step = 2
	printLock = Lock()
	tlist = [None] * GetCPUcount()
	cpt = [0]
	#print(tlist)
	keys = list(d.keys())
	threading.Thread(target=watchList, args=(tlist, printLock, cpt, len(d))).start()
	for i in range(0, len(d), step):
		while(len(tlist) == GetCPUcount()):
			printLock.acquire()
			print(f"All threads working sleeping while waiting...zzZz")
			printLock.release()
			time.sleep(0.3)
			t = threading.Thread(target=work, args=({k: d[k] for k in keys[i: i+step]}, printLock, cpt))
			tlist.append(t)
			t.start()
		#print(tlist)
	print("Done")

# ---- POC 3 ----

def printSet(setPath):
	res = "{"
	for i in setPath:
		res += str(i)+", "
	res = res[0:-2]+'}'
	return res


def copy(src, dest):
	#print(f"Comparing files HASH (skipping if same or copy/replace if different or file dest not exist)")
	time.sleep(0.5)


def mainWatcher(pathSet, printLock):
	initSize = len(pathSet)
	while True:
		if(len(pathSet) == 0):
			#printLock.acquire()
			print(f"Updating loading bar", initSize - len(pathSet))
			#printLock.release()
			break
		#printLock.acquire()
		print(f"Updating loading bar", initSize - len(pathSet))
		print(pathSet)
		#printLock.release()


def task(pathSet, elements, dest, pathSetLock, printLock):
	tmpList = []
	pathSetLock.acquire()
	for i in range(elements):
		tmpList.append(pathSet.pop())
	pathSetLock.release()
	printLock.acquire()
	print(f"Thread:", threading.get_ident(), tmpList)
	printLock.release()
	for p in tmpList:
		printLock.acquire()
		#copy(p, dest)
		print(f"Thread:", threading.get_ident(), ", copying:", p, "to destination", printSet(pathSet))
		printLock.release()
	#time.sleep(0.5 + random.randint(1, 10))
	

def Poool(pathSet):
	pool = Pool()
	PSL = Lock()
	PL = Lock()
	threading.Thread(target=mainWatcher, args=(pathSet, PL,)).start()
	while True:
		pool.apply_async(task, args=(pathSet, 4, "./test", PSL, PL))
		if(len(pathSet) == 0):
			break
	PL.acquire()
	print(f"Done")
	#print(type(printSet(pathSet)))
	PL.release()




def calculateHashFile(f1):
	BUF_SIZE = 65536
	sha1 = hashlib.sha1()
	with open(f1, 'rb') as f:
		while True:
			data = f.read(BUF_SIZE)
			if not data:
				break
			sha1.update(data)
	return sha1.hexdigest()


def hasFileChanged(f1,f2):
	if(os.path.exists(f1) and os.path.exists(f2)):
		return calculateHashFile(f1) != calculateHashFile(f2)

# --------------------------------------


if __name__ == '__main__':
	d = {i: i for i in range(100)}
	#test(d)

	#dummyPool(d)

	S = {0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15}
	#Poool(S)
	#print(printSet(S))

	#print(os.path.isfile('c:/otherproject/save-3000/in/a1/a3/data.docx'))
	#print(os.path.isfile('c:/otherproject/save-3000/in/a1/a2'))
	#print(os.path.isdir('c:/otherproject/save-3000/in/a1/a2'))
	#print(os.path.isdir('c:/otherproject/save-3000/in/a1/a3/data.docx'))

	src = 'c:/otherproject/save-3000/in/A1/A3/data.docx'
	#print('c:/otherproject/save-3000/in/a1/a3/data.docx'.split('/')[-2])
	parent_path = os.path.dirname(os.path.splitdrive('c:/otherproject/save-3000/in/A1/A3/data.docx')[1])
	file_name = os.path.basename(os.path.splitdrive('c:/otherproject/save-3000/in/a1/a3/data.docx')[1])
	destination = 'G:/save'
	print(destination+parent_path+'/'+file_name)

	if(os.path.exists(destination+parent_path+'/'+file_name)):
		if(hasFileChanged(src, destination+parent_path+'/'+file_name)):
			print("File changed !")
			shutil.copy2(src, destination+parent_path+'/'+file_name)
	else:
		if(not os.path.exists(destination+parent_path+'/'+file_name)):
			os.makedirs(destination+parent_path, exist_ok=True)
			shutil.copy2(src, destination+parent_path+'/'+file_name)
		#try:
		#	shutil.copy2()

