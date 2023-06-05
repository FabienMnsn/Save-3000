import shutil
import logging
import os
import hashlib
import humanfriendly
from datetime import timedelta
from tkinter import *
from threading import Thread
from threading import get_ident
from threading import Event
from threading import Lock
from time import sleep, time
from multiprocessing import cpu_count


class CustomThread(Thread):
	def __init__(self, wk_ev, wk_lk, srcSet, dstList, b_size, logger, fileErrorList, cpt, cpt_lock):
		Thread.__init__(self)
		self.worker_event = wk_ev
		self.worker_lock = wk_lk
		self.srcSet = srcSet
		self.dstList = dstList
		self.batch_size = b_size
		self.working_list = []
		self.logger = logger
		self.permissionDeniedFiles = fileErrorList
		self.cpt = cpt
		self.cpt_lock = cpt_lock

	def run(self):
		while True:
			#self.logger.info(f"[THREAD_ID:%s] 1", get_ident())
			if(self.worker_event.is_set()):
				self.logger.info(f"[THREAD_ID:%s] Worker received quit signal", get_ident())
				self.signal_handler()
			#self.logger.info(f"[THREAD_ID:%s] 2", get_ident())
			if(len(self.working_list) > 0):
				#self.logger.info(f"[THREAD_ID:%s] 3", get_ident())
				# do copy file
				for d in self.dstList:
					for p in self.working_list:
						if(self.worker_event.is_set()):
							self.logger.info(f"[THREAD_ID:%s] Worker received quit signal", get_ident())
							self.signal_handler()
						parent_path = os.path.dirname(os.path.splitdrive(p)[1])
						file_name = os.path.basename(os.path.splitdrive(p)[1])
						if(os.path.exists(d+parent_path+'/'+file_name)):
							#self.logger.info(f"[THREAD_ID:%s] 4", get_ident())
							try:
								#self.logger.info(f"[THREAD_ID:%s] 4.1", get_ident())
								if(self.hasFileChanged(p, d+parent_path+'/'+file_name)):
									#self.logger.info(f"[THREAD_ID:%s] 4.2", get_ident())
									try:
										#self.logger.info(f"[THREAD_ID:%s] 5", get_ident())
										shutil.copy2(p, d+parent_path)
										self.working_list.remove(p)
										self.logger.info(f"[THREAD_ID:%s] File has changed or doesn't exist in last backup, copying new file %s to %s", get_ident(), p, d+parent_path)
									except Exception as e:
										#self.logger.info(f"[THREAD_ID:%s] 6", get_ident())
										self.logger.error(f"[THREAD_ID:%s] Exception occurred", get_ident(), exc_info=True)
										self.permissionDeniedFiles.append(p)
										self.working_list.remove(p)
										continue
								else:
									#self.logger.info(f"[THREAD_ID:%s] 4.3", get_ident())
									self.working_list.remove(p)
							except Exception as e:
								#self.logger.info(f"[THREAD_ID:%s] 7", get_ident())
								self.logger.error(f"[THREAD_ID:%s] Exception occurred", get_ident(), exc_info=True)
								self.permissionDeniedFiles.append(p)
								self.working_list.remove(p)
								continue
							self.cpt_lock.acquire()
							self.cpt.set(self.cpt.get()+1)
							self.cpt_lock.release()
						else:
							try:
								#self.logger.info(f"[THREAD_ID:%s] 8", get_ident())
								os.makedirs(d+parent_path, exist_ok=True)
							except Exception as e:
								#self.logger.info(f"[THREAD_ID:%s] 9", get_ident())
								self.logger.error(f"[THREAD_ID:%s] Exception occurred", get_ident(), exc_info=True)
							try:
								#self.logger.info(f"[THREAD_ID:%s] 10", get_ident())
								shutil.copy2(p, d+parent_path)
								self.working_list.remove(p)
								self.logger.info(f"[THREAD_ID:%s] File has changed since last backup, copying new file %s to %s", get_ident(), p, d+parent_path)
							except Exception as e:
								#self.logger.info(f"[THREAD_ID:%s] 11", get_ident())
								self.logger.error(f"[THREAD_ID:%s] Exception occurred", get_ident(), exc_info=True)
								self.permissionDeniedFiles.append(p)
								self.working_list.remove(p)
								continue
							self.cpt_lock.acquire()
							self.cpt.set(self.cpt.get()+1)
							self.cpt_lock.release()
			else:
				if(len(self.srcSet) > 0):
					#self.logger.info(f"[THREAD_ID:%s] 12", get_ident())
					self.logger.info(f"[THREAD_ID:%s] Grabbing data from srcSet", get_ident())
					for i in range(self.batch_size):
						try:
							#self.logger.info(f"[THREAD_ID:%s] 14", get_ident())
							self.worker_lock.acquire()
							self.working_list.append(self.srcSet.pop())
							if(self.worker_lock.locked()):
								self.worker_lock.release()
						except KeyError:
							#self.logger.info(f"[THREAD_ID:%s] 15", get_ident())
							self.logger.info(f"[THREAD_ID:%s] Set is empty, breaking", get_ident())
							break
				else:
					#self.logger.info(f"[THREAD_ID:%s] 17", get_ident())
					break
		self.logger.info(f"[THREAD_ID:%s] Worker's job completed", get_ident())

	def signal_handler(self):
		self.logger.info(f"[THREAD_ID:%s] Stopping worker thread", get_ident())
		exit(0)

	def calculateHashFile(self, file):
		BUF_SIZE = 1048576#65536
		sha1 = hashlib.sha1()
		with open(file, 'rb') as f:
			while True:
				data = f.read(BUF_SIZE)
				if not data:
					break
				sha1.update(data)
		return sha1.hexdigest()


	def hasFileChanged(self, file1, file2):
		if(os.path.exists(file1) and os.path.exists(file2)):
			return self.calculateHashFile(file1) != self.calculateHashFile(file2)




class CustomThreadPool(Thread):
	def __init__(self, root, tp_ev, srcSet, dstList, b_size, logger, fileErrorList, cpt):
		Thread.__init__(self)
		self.root = root # Tkinter root windows needed to unlock buttons when copy finished
		self.threadpool_event = tp_ev
		self.worker_event = Event()
		self.worker_lock = Lock()
		self.srcSet = srcSet
		self.dstList = dstList
		self.workerList = []
		self.batch_size = b_size
		self.logger = logger
		self.fileErrorList = fileErrorList
		self.cpt = cpt
		self.cpt_lock = Lock()

	def run(self):
		starttime = time()
		self.logger.info(f"[THREAD_ID:%s] : Starting threadpool thread", get_ident())
		for i in range(cpu_count()):
			w = CustomThread(self.worker_event, self.worker_lock, self.srcSet, self.dstList, self.batch_size, self.logger, self.fileErrorList, self.cpt, self.cpt_lock)
			w.start()
			self.workerList.append(w)

		while True:
			if(self.threadpool_event.is_set()):
				self.signal_handler()
				break
			if(len(self.srcSet) == 0):
				for w in self.workerList:
					w.join()
				break
		self.root.setExecTime(time() - starttime)

	def signal_handler(self):
		self.worker_event.set()
		for worker in self.workerList:
			worker.join()
		self.logger.info(f"[THREAD_ID:%s] : Stopping threadpool thread", get_ident())
		return




class CustomWatcherThread(Thread):
	def __init__(self, root, w_ev, srcSet, logger):
		Thread.__init__(self)
		self.root = root # Tkinter root windows needed to update progress bar and label
		self.worker_event = w_ev
		self.srcSet = srcSet
		self.logger = logger
		self.init_size = len(self.srcSet)
		self.root.setMaxProgress(self.init_size)
		self.root.setProgress(0)

	def run(self):
		self.logger.info(f"[THREAD_ID:%s] : Starting watcher thread", get_ident())
		while True:
			if(self.root.getCpt()) == self.init_size or self.worker_event.is_set():
				break
			self.root.setProgress(self.root.getCpt())
			self.root.setFileCounter(str(self.root.getCpt())+" / "+str(self.init_size)+" file(s)")
			sleep(0.05)

		self.root.setProgress(self.root.getCpt())
		self.root.setFileCounter(str(self.root.getCpt())+" / "+str(self.init_size)+" file(s)")
		self.root.showInfo("Information", "Sauvegarde effectuée en " + humanfriendly.format_timespan(timedelta(seconds=self.root.getExecTime())))
		self.root.resetCpt()
		self.root.setProgress(0)
		self.root.setFileCounter("0 / "+str(self.init_size)+" file(s)")
		self.root.unlockButtons()
		self.logger.info(f"[THREAD_ID:%s] : Watcher's job's done", get_ident())
		exit(0)

	def signal_handler(self):
		self.logger.info(f"[THREAD_ID:%s] : Watcher received quit signal", get_ident())
		exit(0)