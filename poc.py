from threading import Event
from myCustomThread import CustomThread
from time import sleep





def main():
	ev = Event()
	t1 = CustomThread(ev)
	t1.start()
	print("Main sleeping for 3s")
	sleep(4)
	ev.set()

if __name__ == '__main__':
	main()