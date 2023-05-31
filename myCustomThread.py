from threading import Thread
from threading import get_ident
from threading import Event
from time import sleep
from multiprocessing import cpu_count
from concurrent.futures import ThreadPoolExecutor



class CustomThread(Thread):
	def __init__(self, wk_ev, wk_lk, dataset, b_size):
		Thread.__init__(self)
		self.worker_event = wk_ev
		self.worker_lock = wk_lk
		self.dataset = dataset
		self.batch_size = b_size
		self.working_list = []
		signal.signal(signal.SIGSTOP, signal_handler)


	def run(self):
		#signal.signal(signal.SIGSTOP, signal_handler)
		while True:
			if(self.event.is_set()):
				self.signal_handler()
				break
			if(len(self.working_list) > 0):
				# do copy file
				for element in self.working_list:
					print("[%s] : Copying file %s" % get_ident(), element)
			else:
				if(len(self.dataset) > 0):
					for i in range(self.batch_size):
						try:
							print("[%s] : Acquire lock" % get_ident())
							self.worker_lock.acquire()
							self.working_list.append(self.dataset.pop())
						except KeyError:
							print("[%s] : Set is empty, breaking" % get_ident())
							break
						finally:
							print("[%s] : Release lock" % get_ident())
							self.worker_lock.release()
				else:
					print("[%s] : Quitting main loop" % get_ident())
					break


	def signal_handler(self):
		printprint("[%s] : Signal Received Quitting" % get_ident())
		exit(0)









class CustomThreadPool(Thread):
	def __init__(self, tp_ev, wk_ev, dataset, b_size):
		Thread.__init__(self)
		self.threadpool_event = tp_ev
		self.worker_event = wk_ev
		self.dataset = dataset
		self.workerList = []
		self.batch_size = b_size
		signal.signal(signal.SIGSTOP, signal_handler)


	def run(self):
		print("Start Worker Pool")
		for i in range(cpu_count()):
			self.workerList.append(CustomThread())

		while not self.threadpool_event.is_set():
			sleep(0.3)
	


	#def run(self):
	#	print("start pool")
	#	with ThreadPoolExecutor(self.pool_size) as self.threadPool:
	#		while len(self.dataset) > 0 or not self.threadPool._shutdown:
	#			if(self.event.is_set()):
	#				self.signal_handler()
	#			if(self.threadPool._work_queue.qsize() < self.pool_size):
	#				#print("Queue size : %s" % self.threadPool._work_queue.qsize())
	#				w = self.threadPool.submit(self.task)
	#				print(vars(w))
	#				w.cancel()
	#			#print(vars(self.threadPool))
	#			#print(self.threadPool._work_queue)
	#			#sleep(10)
	#			if(len(self.dataset) > 0):
	#				self.dataset.pop()
	#				print(self.dataset)
	#
	#
	#	print("Fin de la boucle")
	#	for r in self.threadPool._work_queue:
	#		print(type(r))
			#if(not r.cancelled()):
			#	r.result()


	def task(self):
		#print(" [Working:%s] " % self.submited)
		sleep(1)


	def signal_handler(self):
		print(vars(self.threadPool))
		print(self.threadPool._work_queue.qsize())
		for t in self.threadPool._threads:
			print(vars(t))
			t.cancel()
			print(vars(t))
		#for r in self.threadPool._work_queue:
		#	print(type(r))
		print("Receiving Signal -> Exiting Thread Pool")
		exit(0)