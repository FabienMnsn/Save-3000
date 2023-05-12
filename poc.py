import threading
import os
import random
import time
import distutils
import multiprocessing
import subprocess
import sys
import hashlib


def GetCPUcount():
	return multiprocessing.cpu_count()


def carre(number, lock):
	for n in number:
		while(lock[0]):
			time.sleep(0.3)
		lock[0] = True
		print('[', threading.get_ident(),'] : ', n, '^ 2 = ', n*n)
		lock[0] = False
		time.sleep(0.7)


def cube(number, lock):
	for n in number:
		while(lock[0]):
			time.sleep(0.3)
		lock[0] = True
		print('[', threading.get_ident(),'] : ', n, '^ 3 = ', n*n*n)
		lock[0] = False
		time.sleep(0.5)


def systemCall(command):
	p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
	return str(p.stdout.read())[3:-1]


def listDiskID():
	diskID = {}
	r = []
	d = os.popen("fsutil fsinfo drives").readlines()
	if(len(d) > 1):
		d = d[1]
		for c in ['\\', '\n', ' ']:
			d = d.replace(c, "")
		for e in d.split(':'):
			if(len(e) == 1):
				r.append(e)
	else:
		return None
	for disk in r:
		res = systemCall("dir "+disk+":")
		res = res.split('\\r\\n')
		if(len(res) >= 2):
			res = res[1]
			if('-' in res):
				res = res.split(' ')[-1]
				diskID[disk] = res
		else:
			continue
	return diskID


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
	return calculateHashFile(f1) != calculateHashFile(f2)


def packSliceDict(d, slices):
	res = []
	for item in splitDict(d, slices):
		res.append(item)
	return res


def splitDict(d, s):
	# d : dict
	# s : number of batch to split the dict into, ex: s=20 will split d in 20 sub dict
	res = []
	keys = list(d.keys())
	q = len(d) // s
	r = len(d) % s
	R = 1
	c = 0
	if(r != 0):
		# split equally
		# NOT WORKING AT ALL
		for i in range(0, q*s, q + R):
			if(c == s):
				R = 0
			c+=1
			res.append({k: d[k] for k in keys[i: i+q+R]})
		# add reminder in the last dict (need a better repartition of the reminder on each dict)
		# for i in range(q*s, len(d)):
		#	res[-1][keys[i]] = d[keys[i]]

	else:
		for i in range(0, len(d), q):
			res.append({k: d[k] for k in keys[i: i+q]})
	return res


# --------------------------------------

if __name__ == '__main__':
	

	# Thread pool
	# fonction main qui donne un fichier à copier à chaque thread du pool
	# https://docs.python.org/3/library/concurrent.futures.html

	"""
	print(listDiskID())

	lock = [False]
	num = [i for i in range(3)]
	#num = [1, 2, 3, 4, 5, 6, 7]
	print('[PP] : ', os.getpid())
	plist = []
	for i in range(2):
		if(i%2 == 0):
			p = threading.Thread(target=carre, args=(num, lock,))
		else:
			p = threading.Thread(target=cube, args=(num, lock,))
		plist.append(p)
	
	# Starting all threads
	for i in range(len(plist)):
		plist[i].start()

	# Waiting for all threads to finish
	for p in plist:
		p.join()

	try:
		if(not(os.path.exists("./test/") and os.path.isdir("./test/"))):
			os.makedirs("./test/", exist_ok=True)
		distutils.file_util.copy_file("./test.txt", "./test/test.txt", update=1)
	except:
		print("Error distutils")
	print("CPU : ", GetCPUcount())

	start_time = time.time()
	r = calculateHashFile("./test.txt")
	print("Hash exec time :", time.time() - start_time)
	print(r)
	print(hasFileChanged("./test.txt", "./test1.txt"))

	d = {i: i for i in range(24)}
	print("Slices :", round(len(d)/GetCPUcount()), ", CPU :", GetCPUcount(), ", len(d) :", len(d))
	res = packSliceDict(d, round(len(d)//(GetCPUcount())) + len(d)%GetCPUcount())
	print(len(res))
	for i in res:
		print(i)

	"""
	d = {i: i for i in range(48)}
	res = splitDict(d, GetCPUcount())
	print(len(res))
	print(res)
# https://stackoverflow.com/questions/22878743/how-to-split-dictionary-into-multiple-dictionaries-fast


"""

Faire une première itération avec un thread en parallèle qui calcule le nombre total de fichiers à copier.
Pour chaque répertoire rajouté à la liste des répertoires à sauvegarder est associé un nombre de fichiers a copier
la valeur est obtenue en additionnant toutes les valeurs des répertoires à sauvegarder. Le nombre de fichier à sauvegarder est utilisé pour donner un état d'avancement global fiable.
Lors de la réouverture du logiciel la configuration de sauvegarde par défaut est chargée, le calcul du nombre de fichier à copier est relancé dans un thread.

Un fois le calcul effectué, la sauvegarde se fait en utilisant un thread par répertoire à sauvegarder.
La meilleure idée (je ne sais pas si c'est possible de le faire) en gros créer autant de thread que de core cpu dispo sur la machine. Chaque thread consomme un répertoire de sauvegarde dans la liste des sauvegardes.

"""