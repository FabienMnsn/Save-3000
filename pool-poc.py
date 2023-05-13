import threading
from threading import Lock
from multiprocessing.dummy import Pool
from multiprocessing import cpu_count
import time
import random

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
	res = res[0:-2]
	return res+"}"


def copy(src, dest):
	#print(f"Comparing files HASH (skipping if same or copy/replace if different or file dest not exist)")
	time.sleep(0.5)


def mainWatcher(pathSet, printLock):
	initSize = len(pathSet)
	while True:
		if(len(pathSet) == 0):
			printLock.acquire()
			print(f"Updating loading bar", initSize - len(pathSet))
			printLock.release()
			break
		printLock.acquire()
		print(f"Updating loading bar", initSize - len(pathSet))
		#print(pathSet)
		printLock.release()


def task(pathSet, elements, dest, pathSetLock, printLock):
	tmpList = []
	pathSetLock.acquire()
	for i in range(elements):
		tmpList.append(pathSet.pop())
	pathSetLock.release()
	for p in tmpList:
		printLock.acquire()
		copy(p, dest)
		print(f"Thread:", threading.get_ident(), ", copying:", p, "to destination", printSet(pathSet))
		printLock.release()
	#time.sleep(0.5 + random.randint(1, 10))
	

def Poool(pathSet):
	pool = Pool()
	PSL = Lock()
	PL = Lock()
	threading.Thread(target=mainWatcher, args=(pathSet, PL,)).start()
	while True:
		pool.apply_async(task, args=(pathSet, 1, "./test", PSL, PL))
		if(len(pathSet) == 0):
			break
	PL.acquire()
	print(f"Done")
	print(printSet(pathSet))
	PL.release()


# --------------------------------------


if __name__ == '__main__':
	d = {i: i for i in range(100)}
	#test(d)

	#dummyPool(d)

	S = {0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15}
	Poool(S)