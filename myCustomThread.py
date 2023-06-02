from threading import Thread
from threading import get_ident
from threading import Event
from threading import Lock
from time import sleep
from multiprocessing import cpu_count
from concurrent.futures import ThreadPoolExecutor


class CustomThread(Thread):
	def __init__(self, wk_ev, wk_lk, dataset, b_size, print_lock, cpt_sh):
		Thread.__init__(self)
		self.worker_event = wk_ev
		self.worker_lock = wk_lk
		self.dataset = dataset
		self.batch_size = b_size
		self.working_list = []
		self.print_lock = print_lock
		self.cpt_shared = cpt_sh


	def run(self):
		while True:
			#sleep(0.3)
			#self.print_lock.acquire()
			#print("[", get_ident(), "] : Working list :", self.working_list)
			#self.print_lock.release()

			if(self.worker_event.is_set()):
				self.signal_handler()

			if(len(self.working_list) > 0):
				# do copy file
				for element in self.working_list:
					if(self.worker_event.is_set()):
						#self.print_lock.acquire()
						#print("[", get_ident(), "] : Worker Received Signal")
						#self.print_lock.release()
						self.signal_handler()
					#sleep(0.3)
					self.print_lock.acquire()
					self.working_list.remove(element)
					self.cpt_shared[0] += 1
					#print("[", get_ident(), "] : Copying file", element)
					self.print_lock.release()
				self.print_lock.acquire()
				print("[", get_ident(), "] : List", self.working_list)
				self.print_lock.release()
			else:
				if(len(self.dataset) > 0):
					#self.print_lock.acquire()
					#print("[", get_ident(), "] : Grabbing data from dataset")
					#self.print_lock.release()
					for i in range(self.batch_size):
						try:
							#self.print_lock.acquire()
							#print("[", get_ident(), "] : Acquire lock")
							#self.print_lock.release()
							self.worker_lock.acquire()
							self.working_list.append(self.dataset.pop())
							if(self.worker_lock.locked()):
								self.worker_lock.release()
								#self.print_lock.acquire()
								#print("[", get_ident(), "] : Release lock")
								#self.print_lock.release()
						except KeyError:
							#self.print_lock.acquire()
							#print("[", get_ident(), "] : Set is empty, breaking")
							#self.print_lock.release()
							break
						finally:
							#self.print_lock.acquire()
							#print("[", get_ident(), "] : Release lock (finally)")
							#self.print_lock.release()
							if(self.worker_lock.locked()):
								self.worker_lock.release()
				else:
					self.print_lock.acquire()
					print("[", get_ident(), "] : Quitting main loop")
					self.print_lock.release()
					break
		self.print_lock.acquire()
		print("[", get_ident(), "] : Working list :", self.working_list)
		self.print_lock.release()
		self.print_lock.acquire()
		print("[", get_ident(), "] : ---------------- Worker's Job Completed")
		self.print_lock.release()
			


	def signal_handler(self):
		self.print_lock.acquire()
		print("[", get_ident(), "] : Signal Received Quitting")
		self.print_lock.release()
		exit(0)









class CustomThreadPool(Thread):
	def __init__(self, tp_ev, dataset, b_size, print_lock):
		Thread.__init__(self)
		self.threadpool_event = tp_ev
		self.worker_event = Event()
		self.worker_lock = Lock()
		self.dataset = dataset
		self.workerList = []
		self.batch_size = b_size
		self.print_lock = print_lock
		self.cpt = [0]
		#signal.signal(signal.SIGSTOP, signal_handler)


	def run(self):
		print("Start Worker Pool")
		for i in range(cpu_count()):
			# CustomThread(self, wk_ev, wk_lk, dataset, b_size)
			w = CustomThread(self.worker_event, self.worker_lock, self.dataset, self.batch_size, self.print_lock, self.cpt)
			w.start()
			self.workerList.append(w)

		while True:
			#print("--------------------------------> THREAD POOL EVENT :", self.threadpool_event.is_set())
			if(self.threadpool_event.is_set()):
				self.signal_handler()
				break
			if(len(self.dataset) == 0):
				for w in self.workerList:
					w.join()
				break
			#sleep(0.3)
		print("FILE COPIED :", self.cpt[0])
	


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
		self.worker_event.set()
		for worker in self.workerList:
			worker.join()
		return







class WatcherThread(Thread):
	def __init__(self, w_ev, dataset, print_lock):
		Thread.__init__(self)
		self.worker_event = w_ev
		self.dataset = dataset
		self.print_lock = print_lock


	def run(self):
		while True:
			if(len(self.dataset) == 0 or self.worker_event.is_set()):
				self.signal_handler()
				break
			self.print_lock.acquire()
			print("DATA_SET SIZE :", len(self.dataset))
			self.print_lock.release()
			sleep(1)


	def signal_handler(self):
		self.print_lock.acquire()
		print("[", get_ident(), "] : Signal Received Watcher Quitting")
		self.print_lock.release()
		exit(0)