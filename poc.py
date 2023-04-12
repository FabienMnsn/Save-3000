import threading
import os
import random
import time
import distutils
import multiprocessing


def GetCPUcount():
	return multiprocessing.cpu_count()


def carre(number):
	for n in number:
		print('[', threading.get_ident(),'] : ', n, '^ 2 = ', n*n)
		time.sleep(1)


def cube(number):
	for n in number:
		print('[', threading.get_ident(),'] : ', n, '^ 3 = ', n*n*n)
		time.sleep(0.5)


if __name__ == '__main__':
    num = [i for i in range(1)]
    #num = [1, 2, 3, 4, 5, 6, 7]
    print('[PP] : ', os.getpid())
    plist = []
    for i in range(2):
    	if(i%2 == 0):
    		p = threading.Thread(target=carre, args=(num,))
    	else:
    		p = threading.Thread(target=cube, args=(num,))
    	plist.append(p)
    
    for i in range(len(plist)):
    	plist[i].start()

    try:
    	distutils.file_util.copy_file("./test.txt", "./test/test.txt", update=1)
    except:
    	print("Error distutils")
    print("CPU : ", GetCPUcount())






"""

Faire une première itération avec un thread en parallèle qui calcule le nombre total de fichiers à copier.
Pour chaque répertoire rajouté à la liste des répertoires à sauvegarder est associé un nombre de fichiers a copier
la valeur est obtenue en additionnant toutes les valeurs des répertoires à sauvegarder. Le nombre de fichier à sauvegarder est utilisé pour donner un état d'avancement global fiable.
Lors de la réouverture du logiciel la configuration de sauvegarde par défaut est chargée, le calcul du nombre de fichier à copier est relancé dans un thread.

Un fois le calcul effectué, la sauvegarde se fait en utilisant un thread par répertoire à sauvegarder.
La meilleure idée (je ne sais pas si c'est possible de le faire) en gros créer autant de thread que de core cpu dispo sur la machine. Chaque thread consomme un répertoire de sauvegarde dans la liste des sauvegardes.

"""