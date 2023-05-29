from threading import Thread
from threading import Event
from time import sleep
from concurrent.futures import ThreadPoolExecutor



class CustomThread(Thread):
	def __init__(self, ev, dataset):
		Thread.__init__(self)
		self.event = ev
		self.dataset = dataset


	def run(self):
		i = 0
		#signal.signal(signal.SIGSTOP, signal_handler)
		while i < len(self.dataset):
			if(self.event.is_set()):
				self.signal_handler()
			print("Value : [" + self.dataset.pop() + "] , sleeping for 1s")
			#print("%s, then sleeping for 1s\n" % i)
			sleep(10)
			i += 1


	def signal_handler(self):
		print("Receiving Signal -> Exiting Thread")
		exit(0)









class CustomThreadPool(Thread):
	def __init__(self, ev, dataset, pool_size, batch_size):
		Thread.__init__(self)
		self.event = ev
		self.dataset = dataset
		self.threadPool = None
		self.pool_size = pool_size
		self.batch_size = batch_size
		self.submited = 0

	def run(self):
		print("start pool")
		with ThreadPoolExecutor(self.pool_size) as self.threadPool:
			while len(self.dataset) > 0 or not self.threadPool._shutdown:
				if(self.event.is_set()):
					self.signal_handler()
				if(self.threadPool._work_queue.qsize() < self.pool_size):
					#print("Queue size : %s" % self.threadPool._work_queue.qsize())
					w = self.threadPool.submit(self.task)
					print(vars(w))
					w.cancel()
				#print(vars(self.threadPool))
				#print(self.threadPool._work_queue)
				#sleep(10)
				if(len(self.dataset) > 0):
					self.dataset.pop()
					print(self.dataset)


		print("Fin de la boucle")
		for r in self.threadPool._work_queue:
			print(type(r))
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