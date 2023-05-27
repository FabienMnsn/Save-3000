from threading import Thread
from threading import Event
from time import sleep

class CustomThread(Thread):
	def __init__(self, ev):
		Thread.__init__(self)
		self.event = ev

	def run(self):
		i = 0
		#signal.signal(signal.SIGSTOP, signal_handler)
		while i < 5:
			if(self.event.is_set()):
				self.signal_handler()
			print("%s, then sleeping for 3s\n" % i)
			sleep(3)
			i += 1

	def signal_handler(self):
		print("Receiving Signal -> Exiting")
		exit(0)