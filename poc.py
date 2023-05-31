from threading import Event, Lock
from myCustomThread import CustomThread, WatcherThread
from myCustomThread import CustomThreadPool
from time import sleep
from multiprocessing import cpu_count




def main():
	#c_set = {"1", "2", "3", "4", "5", "6", "7", "8"}
	c_set = {x for x in range(1000)}
	#ev = Event()
	#t1 = CustomThread(ev, c_set)
	#t1.start()

	thread_pool_event = Event()

	print_lock = Lock()

	t1 = WatcherThread(thread_pool_event, c_set, print_lock)
	t1.start()

	t2 = CustomThreadPool(thread_pool_event, c_set, 10, print_lock)
	t2.start()
	#sleep(5)
	#ev.set()

	#sleep(5)
	#print("SENDING EVENT")
	#thread_pool_event.set()
	#c = {1}
	#print(c.pop())
	#
	#try:
	#	c.pop()
	#except Exception as e:
	#	if("pop from an empty set" in str(e)):
	#		print("SAME")
	#	else:
	#		print("DIFFERENT")
	#finally:
	#	print("finally")
if __name__ == '__main__':
	main()