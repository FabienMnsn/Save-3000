from threading import Event
from myCustomThread import CustomThread
from myCustomThread import CustomThreadPool
from time import sleep
from multiprocessing import cpu_count




def main():
	#c_set = {"1", "2", "3", "4", "5", "6", "7", "8"}
	c_set = {x for x in range(1000)}
	print(c_set)
	ev = Event()
	#t1 = CustomThread(ev, c_set)
	#t1.start()
	#t2 = CustomThreadPool(ev, c_set, cpu_count(), 2)
	#t2.start()
	print("Main sleeping")
	#sleep(5)
	ev.set()
	print(c_set)

	c = {1}
	print(c.pop())

	try:
		c.pop()
	except Exception as e:
		if("pop from an empty set" in str(e)):
			print("SAME")
		else:
			print("DIFFERENT")
	finally:
		print("finally")
if __name__ == '__main__':
	main()