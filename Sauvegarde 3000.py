import time
import json
import os
import shutil
import subprocess
import threading
import hashlib
import logging
from threading import Lock
from multiprocessing import cpu_count
from concurrent.futures import ThreadPoolExecutor
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter.ttk import Combobox
from tkinter.ttk import Progressbar
from tkinter import filedialog
from tkinter import font as tkFont


class App():
	def __init__(self):
		self.root = Tk()
		# theme and font color
		self.root.title("Sauvegarde 3000")
		self.root.minsize(664, 373)
		self.root.resizable(True, True)
		self.main_theme_light = "grey55"
		self.main_theme = "grey35"
		self.text_color = "white"
		self.main_button_color = "grey45"
		self.selected_button_color = "DarkOrange2"
		self.critical_button_color = "red4"
		self.safe_button_color = "dark green"
		self.main_font = tkFont.Font(size=11, weight="bold")
		self.root['bg'] = self.main_theme
		self.root.protocol("WM_DELETE_WINDOW", self.on_root_closing)
		# --------------------------------------------------------------------------------------------------
		# MENU BAR
		self.menubar = Menu(self.root, bg=self.main_theme, fg=self.text_color, activebackground="white", activeforeground='black')
		self.file = Menu(self.menubar, tearoff=0, bg=self.main_theme, fg=self.text_color, font=self.main_font)
		self.file.add_command(label="Réglages", command=self.openPreferencesWindow)
		self.file.add_separator()
		self.file.add_command(label="Quitter", command=self.on_root_closing)
		self.menubar.add_cascade(label="Fichier", menu=self.file)
		self.root.config(menu=self.menubar)

		# PRESET BAR
		self.presetbar = Menu(self.menubar, tearoff=0, bg=self.main_theme, fg=self.text_color, font=self.main_font)
		self.menubar.add_cascade(label="Préréglages", menu=self.presetbar)
		
		# MAIN FRAME
		self.main_frame = None

		# USER DATA
		self.user_data = None
		self.current_preset = None
		self.current_options = None

		# LOGGING CONFIGURATION
		logging.basicConfig(filename='Sauvegarde-3000.log', filemode='w', format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
		
		# BOOLEAN
		self.saveStarted = False

		# THREADS
		self.mainWatcherThread = None
		self.mainPoolThread = None
		self.poolThreadList = []
		self.threadPool = None
		self.onCloseLock = Lock()
		self.PATH_SET_LOCK = Lock()

		# DATA SET & LIST
		self.srcSet = None
		self.dstList = None
		self.permissionDeniedFiles = []



		# PRESET FRAME
		self.preset_frame = LabelFrame(self.main_frame, text="Préréglages", font=self.main_font, labelanchor="n", borderwidth=1, bg=self.main_theme, fg=self.text_color)
		self.preset_frame.pack(side=TOP, expand=False, fill=BOTH, padx=5, pady=5)
		
		self.preset_l = Label(self.preset_frame, text="Préréglage actuel :", font=self.main_font, height=1, bg=self.main_theme, fg=self.text_color, justify=LEFT)
		self.preset_l.pack(side=LEFT, fill=X, padx=(5,0), pady=(5,10))

		self.current_preset_label = Label(self.preset_frame, text=self.current_preset, font=self.main_font, height=1, bg=self.main_theme, fg=self.text_color, justify=LEFT)
		self.current_preset_label.pack(side=LEFT, fill=X, anchor=W, padx=(0,5), pady=(5,13))

		self.save_current_preset_button = Button(self.preset_frame, text="Sauvegarder préréglage", relief="raised", bg=self.main_button_color, fg="white")
		self.save_current_preset_button['command'] = self.openNameInputWindow
		self.save_current_preset_button.pack(side=RIGHT, padx=5, pady=(5,13))

		self.delete_current_preset_button = Button(self.preset_frame, text="Supprimer le préréglage courant", relief="raised", bg=self.critical_button_color, fg="white")
		self.delete_current_preset_button['command'] = self.deleteCurrentPreset
		self.delete_current_preset_button.pack(side=RIGHT, padx=5, pady=(5,13))


		# MAIN PANED FRAME
		self.folders_panedWindow = PanedWindow(self.main_frame, bg=self.main_theme, showhandle=True, handlesize=10, handlepad=100)
		self.folders_panedWindow.pack(side=TOP, expand=True, fill=BOTH, padx=(5,5), pady=0)


		# SRC FRAME
		self.src_frame = LabelFrame(self.folders_panedWindow, text="Dossiers à sauvegarder", font=self.main_font, labelanchor="n", borderwidth=1, bg=self.main_theme, fg=self.text_color)
		self.src_frame.pack(side=LEFT, expand=True, fill=BOTH)
		self.folders_panedWindow.add(self.src_frame)

		# SRC LISTBOX+SCROLLBARS FRAME
		self.src_listboxFrame = Frame(self.src_frame, bg=self.main_theme)
		self.src_listboxFrame.pack(side=TOP, expand=True, fill=BOTH, padx=0, pady=0)

		self.src_yscrollbar = Scrollbar(self.src_listboxFrame, bg=self.main_theme, orient=VERTICAL)
		self.src_yscrollbar.pack(side=RIGHT, padx=(0,5), pady=(5,5), fill=Y)

		self.src_xscrollbar = Scrollbar(self.src_listboxFrame, bg=self.main_theme, orient=HORIZONTAL)
		self.src_xscrollbar.pack(side=BOTTOM, padx=(5,5), pady=(0,5), fill=X)
		
		self.src_listbox = Listbox(self.src_listboxFrame, bg=self.main_theme, fg=self.text_color, width=65, height=1, selectmode=MULTIPLE, yscrollcommand=self.src_yscrollbar.set, xscrollcommand=self.src_xscrollbar.set)
		self.src_listbox.pack(side=TOP, expand=True, fill=BOTH, padx=(5,5), pady=(5,5))
		self.src_yscrollbar.config(command=self.src_listbox.yview)
		self.src_xscrollbar.config(command=self.src_listbox.xview)

		self.src_button_frame = Frame(self.src_frame, bg=self.main_theme)
		self.src_button_frame.pack(side=TOP, fill=X)

		self.delete_selected_SRC_button = Button(self.src_button_frame, text="Supprimer dossiers sélectionnés", relief="raised", bg=self.critical_button_color, fg="white")
		self.delete_selected_SRC_button['command'] = self.deleteSelectedSRC
		self.delete_selected_SRC_button.pack(side=LEFT, padx=(5,5), pady=(0,5))

		self.select_folder_SRC_button = Button(self.src_button_frame, text="Ajouter dossier", relief="raised", bg=self.main_button_color, fg="white")
		self.select_folder_SRC_button['command'] = self.addFolderSRC
		self.select_folder_SRC_button.pack(side=RIGHT, padx=(5,5), pady=(0,5))

		self.select_file_SRC_button = Button(self.src_button_frame, text="Ajouter fichier", relief="raised", bg=self.main_button_color, fg="white")
		self.select_file_SRC_button['command'] = self.addFileSRC
		self.select_file_SRC_button.pack(side=RIGHT, padx=(0,0), pady=(0,5))


		# DST FRAME
		self.dst_frame = LabelFrame(self.folders_panedWindow, text="Dossiers de sauvegarde", font=self.main_font, labelanchor="n", borderwidth=1, bg=self.main_theme, fg=self.text_color)
		self.dst_frame.pack(side=RIGHT, expand=True, fill=BOTH)
		self.folders_panedWindow.add(self.dst_frame)

		# SRC LISTBOX+SCROLLBARS FRAME
		self.dst_listboxFrame = Frame(self.dst_frame, bg=self.main_theme)
		self.dst_listboxFrame.pack(side=TOP, expand=True, fill=BOTH, padx=0, pady=0)

		self.dst_yscrollbar = Scrollbar(self.dst_listboxFrame, bg=self.main_theme, orient=VERTICAL)
		self.dst_yscrollbar.pack(side=RIGHT, padx=(0,5), pady=(5,5), fill=Y)

		self.dst_xscrollbar = Scrollbar(self.dst_listboxFrame, bg=self.main_theme, orient=HORIZONTAL)
		self.dst_xscrollbar.pack(side=BOTTOM, padx=(5,5), pady=(0,5), fill=X)

		self.dst_listbox = Listbox(self.dst_listboxFrame, bg=self.main_theme, fg=self.text_color, width=65, height=1, selectmode=MULTIPLE, yscrollcommand=self.dst_yscrollbar.set, xscrollcommand=self.dst_xscrollbar.set)
		self.dst_listbox.pack(side=TOP, expand=True, fill=BOTH, padx=(5,5), pady=(5,5))

		self.dst_button_frame = Frame(self.dst_frame, bg=self.main_theme)
		self.dst_button_frame.pack(side=TOP, fill=X)

		self.delete_selected_DST_button = Button(self.dst_button_frame, text="Supprimer dossiers sélectionnés", relief="raised", bg=self.critical_button_color, fg="white")
		self.delete_selected_DST_button['command'] = self.deleteSelectedDST
		self.delete_selected_DST_button.pack(side=LEFT, padx=(5,5), pady=(0,5))

		self.select_folder_DST_button = Button(self.dst_button_frame, text="Ajouter destination de sauvegarde", relief="raised", bg=self.main_button_color, fg="white")
		self.select_folder_DST_button['command'] = self.addFolderDST
		self.select_folder_DST_button.pack(side=RIGHT, padx=(5,5), pady=(0,5))


		# PROGRESS BAR FRAME
		self.progressBarFrame = Frame(self.main_frame, bg=self.main_theme)
		self.progressBarFrame.pack(side=BOTTOM, expand=False, fill=X, padx=0, pady=0)

		# PROGRESS BAR
		self.progress = Progressbar(self.progressBarFrame, orient=HORIZONTAL, maximum=100)
		self.progress.pack(side=TOP, expand=False, fill=X, padx=5, pady=5)

		# START SAVE BUTTON
		self.start_save = Button(self.progressBarFrame, text="Lancer la sauvegarde", font=self.main_font, relief="raised", bg=self.safe_button_color, fg="white", width=20, height=1)
		self.start_save['command'] = self.startThreadedSave
		self.start_save.pack(side=TOP, expand=True, fill=NONE, padx=(10,10), pady=(5,10))
		
		self.loadUserData()
		self.updatePresetMenu()
		self.loadLastPreset()




	def setMaxProgress(self, value):
		self.progress['maximum'] = value

	def resetProgress(self):
		self.progress['value'] = 0

	def incrementProgress(self):
		self.progress['value'] += 1

	def setProgress(self, value):
		self.progress['value'] = value


	def startThreadedSave(self):
		res = self.showYesNo("Attention", "Etes-vous sûr de vouloir\nlancer la sauvegarde?")
		if(res):
			self.startSave()

	# BACKUP			
	#def parseSRC(self, src_list):
	#	res = set()
	#	for src in src_list:
	#		for root, dirs, files in os.walk(src):
	#			if(len(files) == 0):
	#				res.add(os.path.normcase(root).replace('\\', '/'))
	#			for f in files:
	#				res.add(os.path.normcase(os.path.join(root, f)).replace('\\', '/'))
	#	return res

	def parseSRC(self, src_list):
		res = set()
		for src in src_list:
			for root, dirs, files in os.walk(src):
				for f in files:
					res.add(os.path.join(root, f).replace('\\', '/'))
		return res



	def calculateHashFile(self, f1):
		BUF_SIZE = 65536
		sha1 = hashlib.sha1()
		with open(f1, 'rb') as f:
			while True:
				data = f.read(BUF_SIZE)
				if not data:
					break
				sha1.update(data)
		return sha1.hexdigest()


	def hasFileChanged(self, f1, f2):
		if(os.path.exists(f1) and os.path.exists(f2)):
			return self.calculateHashFile(f1) != self.calculateHashFile(f2)



	def startSave(self):
		self.dstList = self.getAllDST()
		self.srcSet = self.parseSRC(self.getAllSRC())
		self.mainWatcherThread = threading.Thread(target=self.mainWatcher)
		self.mainWatcherThread.deamon = True
		self.mainWatcherThread.start()

		self.lockButtons()

		self.mainPoolThread = threading.Thread(target=self.mainPoolTask)
		self.mainPoolThread.deamon = True
		self.mainPoolThread.start()


	def mainWatcher(self):
		logging.info(f"[THREAD_ID:%s] Main watcher tread started", threading.get_ident())
		initSize = len(self.srcSet)
		self.setMaxProgress(initSize)
		while True:
			if(len(self.srcSet) == 0):
				self.setProgress(initSize - len(self.srcSet))
				break
			self.setProgress(initSize - len(self.srcSet))
		logging.info(f"[THREAD_ID:%s] Main watcher tread finished", threading.get_ident())


	def mainPoolTask(self):
		logging.info(f"[THREAD_ID:%s] Starting save (main thread pool loop)", threading.get_ident())
		starttime = time.time()
		with ThreadPoolExecutor(cpu_count()) as self.threadPool:
			while len(self.srcSet) > 0:
				if(self.threadPool._shutdown):
					logging.info(f"[THREAD_ID:%s] Aborting main thread pool loop (pool shutdown)", threading.get_ident())
					break
				if(self.threadPool._work_queue.qsize() < 5):
					self.onCloseLock.acquire()
					if(not self.threadPool._shutdown):
						w = self.threadPool.submit(self.task, 10)
						self.poolThreadList.append(w)
					self.onCloseLock.release()
		for r in self.poolThreadList:
			if(not r.cancelled()):
				r.result()
		logging.info(f"[THREAD_ID:%s] Execution time %ss:", threading.get_ident(), time.time() - starttime)
		self.threadPool.shutdown()
		logging.info(f"[THREAD_ID:%s] Save is done", threading.get_ident())
		self.showInfo("Sauvegarde", "Sauvegarde terminée !")
		self.resetProgress()
		self.unlockButtons()


	def task(self, nbElemPerTask):
		if(len(self.srcSet) == 0):
			return
		tmpList = []
		self.PATH_SET_LOCK.acquire()
		for i in range(nbElemPerTask):
			if(len(self.srcSet) > 0):
				tmpList.append(self.srcSet.pop())
			else:
				break
		self.PATH_SET_LOCK.release()
		if(len(tmpList) == 0):
			return
		for d in self.dstList:
			for p in tmpList:
				parent_path = os.path.dirname(os.path.splitdrive(p)[1])
				file_name = os.path.basename(os.path.splitdrive(p)[1])

				if(os.path.exists(d+parent_path+'/'+file_name)):
					try:
						if(self.hasFileChanged(p, d+parent_path+'/'+file_name)):
							try:
								shutil.copy2(p, d+parent_path)
								logging.info(f"[THREAD_ID:%s] File has changed since last backup, copying new file %s to %s", threading.get_ident(), p, d+parent_path)
							except Exception as e:
								logging.error(f"[THREAD_ID:%s] Exception occurred", threading.get_ident(), exc_info=True)
								self.permissionDeniedFiles.append(p)
								continue
					except Exception as e:
						logging.error(f"[THREAD_ID:%s] Exception occurred", threading.get_ident(), exc_info=True)
						self.permissionDeniedFiles.append(p)
						continue
				else:
					try:
						os.makedirs(d+parent_path, exist_ok=True)
					except Exception as e:
						logging.error(f"[THREAD_ID:%s] Exception occurred", threading.get_ident(), exc_info=True)
					try:
						shutil.copy2(p, d+parent_path)
						logging.info(f"[THREAD_ID:%s] File has changed since last backup, copying new file %s to %s", threading.get_ident(), p, d+parent_path)
					except Exception as e:
						logging.error(f"[THREAD_ID:%s] Exception occurred", threading.get_ident(), exc_info=True)
						self.permissionDeniedFiles.append(p)
						continue



	def optionsToString(self):
		opt = ""
		if(self.current_options != None):
			for key in self.current_options.keys():
				if(type(self.current_options[key]) == int):
					opt += "/"+key+":"+str(self.current_options[key])+" "
				else:
					if(self.current_options[key]):
						opt += "/"+key+" "
		return opt


	def loadLastPreset(self):
		if(self.user_data != None):
			if(self.user_data["LAST PRESET"] != ""):
				self.current_preset = self.user_data["LAST PRESET"]
				self.updateCurrentPresetLabel()
			if(self.user_data["PRESET"] != {}):
				if(self.user_data["PRESET"][self.current_preset]["OPTIONS"] != {}):
					self.loadOptions()
				if(self.user_data["PRESET"][self.current_preset]["SRC"] != []):
					self.loadSRC()
				if(self.user_data["PRESET"][self.current_preset]["DST"] != {}):
					self.loadDST()


	def on_root_closing(self):
		print(self.permissionDeniedFiles)
		res = self.showYesNo("Quitter", "Etes-vous sûr de vouloir quitter le programme avant la fin de la sauvegarde?\n La sauvegarde ne sera pas complète.")
		if(res):
			logging.info("User has closed main window")
			self.onCloseLock.acquire()
			if(self.threadPool != None):
				logging.info("Shutting down thread pool")
				self.threadPool.shutdown(wait=False, cancel_futures=True)
				logging.info("Canceling all running tasks in thread pool")
				for t in self.poolThreadList:
					if(t.running()):
						t.cancel()
			self.onCloseLock.release()
			
			if(self.current_preset != None and self.user_data != None):
				if(self.user_data["PRESET"] != {}):
					self.user_data["LAST PRESET"] = self.current_preset
				else:
					self.user_data["LAST PRESET"] = ""
				self.writeUserData()
			self.root.destroy()


	def openFolderDialog(self):
		return filedialog.askdirectory()


	def openFileDialog(self):
		return filedialog.askopenfilename()


	def saveCurrentPreset(self, name):
		if(self.user_data != None and self.current_options != None):
			self.user_data["PRESET"][name] = {"OPTIONS":self.current_options,"SRC":self.getAllSRC(),"DST":self.getDST()}
			self.current_preset = name
			self.updateCurrentPresetLabel()
			self.writeUserData()


	def deleteCurrentPreset(self):
		if(self.current_preset != None and self.user_data != None):
			res = self.showYesNo("Suppression", "Etes-vous sûr de vouloir\nsupprimer définitivement ce préréglage?")
			if(res):
				if(self.current_preset in list(self.user_data["PRESET"].keys())):
					self.user_data["PRESET"].pop(self.current_preset)
					self.current_preset = None
					self.updateCurrentPresetLabel()
					self.cleanSRCDST()
					self.updatePresetMenu()
					self.writeUserData()


	def updateCurrentPresetLabel(self):
		if(self.current_preset == None):
			self.current_preset_label["text"] = ""
		else:
			self.current_preset_label["text"] = self.current_preset


	def updatePresetMenu(self):
		if(self.user_data != None):
			self.presetbar.delete(0, 'end')
			for preset in self.user_data["PRESET"]:
				self.presetbar.add_command(label=preset, command=lambda name=preset:self.setCurrentPreset(name))


	def setCurrentPreset(self, name):
		self.current_preset = name
		self.updateCurrentPresetLabel()
		self.loadSRC()
		self.loadDST()


	def openNameInputWindow(self):
		self.pop_up = Toplevel(self.root)
		self.pop_up.resizable(False, False)
		self.pop_up.grab_set()
		frame_font = tkFont.Font(size=13, weight="bold")
		self.main_input_frame = LabelFrame(self.pop_up, text="Nom du préréglage", font=frame_font, labelanchor="n", borderwidth=0, bg=self.main_theme, fg="white")
		self.main_input_frame.pack(side=TOP)
		self.name_entry = Entry(self.main_input_frame, bg=self.main_theme_light, bd=0, width=25, font=self.main_font, fg=self.text_color)
		self.name_entry.pack(side=LEFT, padx=5, pady=5)
		self.save_button = Button(self.main_input_frame, text="Enregistrer et quitter", relief="raised", bg=self.main_button_color, fg="white")
		self.save_button['command'] = lambda window=self.pop_up:self.saveInputName(window)
		self.save_button.pack(side=LEFT, padx=5, pady=5)


	def saveInputName(self, window):
		self.saveCurrentPreset(self.name_entry.get())
		self.updatePresetMenu()
		window.destroy()


	def openPreferencesWindow(self):
		self.sub_win = Toplevel(self.root)
		self.sub_win.resizable(False, False)
		self.sub_win.grab_set()
		# main sub window frame
		frame_font = tkFont.Font(size=13, weight="bold")
		self.main_preference_frame = LabelFrame(self.sub_win, text="Options de sauvegarde", font=frame_font, labelanchor="n", borderwidth=0, bg=self.main_theme, fg="white")
		self.main_preference_frame.pack(side=TOP)
		# ROBOCOPY OPTIONS LIST
		# MT
		self.mt_frame = LabelFrame(self.main_preference_frame, bd=2, bg=self.main_theme)
		self.mt_frame.pack(side=TOP, fill=X, padx=10, pady=10)
		# mt label 
		self.mt_label = Label(self.mt_frame, text="Nombre de sous processus pour la copie :", font=self.main_font, height=1, bg=self.main_theme, fg=self.text_color, anchor=W)
		self.mt_label.pack(side=LEFT, fill=X, padx=2, pady=2)
		# mt value entry
		self.mt_entry = Entry(self.mt_frame, bg=self.main_theme_light, bd=0, width=6, font=self.main_font, fg=self.text_color)
		self.mt_entry.pack(side=LEFT, padx=2, pady=2)
		# PURGE
		self.purge_frame = LabelFrame(self.main_preference_frame, bd=2, bg=self.main_theme)
		self.purge_frame.pack(side=TOP, fill=X, padx=10, pady=10)
		# mt label 
		self.purge_label = Label(self.purge_frame, text="Supprimer les fichiers et dossiers de la\ndestination qui n'existent plus dans la source", font=self.main_font, height=2, bg=self.main_theme, fg=self.text_color, anchor=W, justify=LEFT)
		self.purge_label.pack(side=LEFT, fill=X, padx=2, pady=2)
		# mt value entry
		self.purge_ck_var = BooleanVar()
		self.purge_ck = Checkbutton(self.purge_frame, bg=self.main_theme, bd=2, variable=self.purge_ck_var, onvalue=True, offvalue=False)
		self.purge_ck.pack(side=LEFT, padx=2, pady=2)
		# EMPTY FOLDER COPY
		self.e_frame = LabelFrame(self.main_preference_frame, bd=2, bg=self.main_theme)
		self.e_frame.pack(side=TOP, fill=X, padx=10, pady=10)
		# mt label 
		self.e_label = Label(self.e_frame, text="Copier les sous dossiers vides", font=self.main_font, height=1, bg=self.main_theme, fg=self.text_color, anchor=W, justify=LEFT)
		self.e_label.pack(side=LEFT, fill=X, padx=2, pady=2)
		# mt value entry
		self.e_ck_var = BooleanVar()
		self.e_ck = Checkbutton(self.e_frame, bg=self.main_theme, bd=2, variable=self.e_ck_var, onvalue=True, offvalue=False)
		self.e_ck.pack(side=LEFT, padx=2, pady=2)
		# RETRIES
		self.r_frame = LabelFrame(self.main_preference_frame, bd=2, bg=self.main_theme)
		self.r_frame.pack(side=TOP, fill=X, padx=10, pady=10)
		# mt label 
		self.r_label = Label(self.r_frame, text="Nombre de tentative si la copie échoue :", font=self.main_font, height=1, bg=self.main_theme, fg=self.text_color, anchor=W)
		self.r_label.pack(side=LEFT, fill=X, padx=2, pady=2)
		# mt value entry
		self.r_entry = Entry(self.r_frame, bg=self.main_theme_light, bd=0, width=6, font=self.main_font, fg=self.text_color)
		self.r_entry.pack(side=LEFT, padx=2, pady=2)
		# WAIT TIME
		self.w_frame = LabelFrame(self.main_preference_frame, bd=2, bg=self.main_theme)
		self.w_frame.pack(side=TOP, fill=X, padx=10, pady=10)
		# mt label 
		self.w_label = Label(self.w_frame, text="Temps d'attente (secondes) entre chaque tentative :", font=self.main_font, height=1, bg=self.main_theme, fg=self.text_color, anchor=W)
		self.w_label.pack(side=LEFT, fill=X, padx=2, pady=2)
		# mt value entry
		self.w_entry = Entry(self.w_frame, bg=self.main_theme_light, bd=0, width=6, font=self.main_font, fg=self.text_color)
		self.w_entry.pack(side=LEFT, padx=2, pady=2)
		# OLD FOLDER COPY
		self.o_frame = LabelFrame(self.main_preference_frame, bd=2, bg=self.main_theme)
		self.o_frame.pack(side=TOP, fill=X, padx=10, pady=10)
		# mt label 
		self.o_label = Label(self.o_frame, text="Exclure les fichiers plus anciens", font=self.main_font, height=1, bg=self.main_theme, fg=self.text_color, anchor=W, justify=LEFT)
		self.o_label.pack(side=LEFT, fill=X, padx=2, pady=2)
		# mt value entry
		self.o_ck_var = BooleanVar()
		self.o_ck = Checkbutton(self.o_frame, bg=self.main_theme, bd=2, variable=self.o_ck_var, onvalue=True, offvalue=False)
		self.o_ck.pack(side=LEFT, padx=2, pady=2)

		self.validation_frame = Frame(self.main_preference_frame, borderwidth=0, bg=self.main_theme)
		self.validation_frame.pack(side=TOP, padx=10, pady=10)
		# validation button
		self.validate_button = Button(self.validation_frame, text="Enregistrer et quitter", relief="raised", bg=self.main_button_color, fg="white")
		self.validate_button['command'] = lambda window=self.sub_win:self.saveAndExitPreferences(window)
		self.validate_button.pack(side=TOP)
		if(self.user_data != None):
			self.loadPreferences()


	def loadPreferences(self):
		if(len(list(self.user_data["PRESET"].keys())) > 0 and self.current_preset in list(self.user_data["PRESET"].keys())):
			udo = self.user_data["PRESET"][str(self.current_preset)]["OPTIONS"]
			self.mt_entry.delete(0, 'end')
			self.mt_entry.insert(0, udo["MT"])
			self.purge_ck_var.set(udo["PURGE"])
			self.e_ck_var.set(udo["E"])
			self.r_entry.delete(0, 'end')
			self.r_entry.insert(0, udo["R"])
			self.w_entry.delete(0, 'end')
			self.w_entry.insert(0, udo["W"])
			self.o_ck_var.set(udo["XO"])


	def getOptionsPreferences(self):
		res = {"MT":int(self.mt_entry.get()),"PURGE":self.purge_ck_var.get(),"E":self.e_ck_var.get(),"R":int(self.r_entry.get()),"W":int(self.w_entry.get()),"XO":self.o_ck_var.get()}
		return res


	def loadOptions(self):
		if(self.user_data != None and self.user_data["PRESET"] != {} and self.current_preset in list(self.user_data["PRESET"].keys()) and self.user_data["PRESET"][self.current_preset]["OPTIONS"] != {}):
			self.current_options = self.user_data["PRESET"][self.current_preset]["OPTIONS"]


	def cleanSRCDST(self):
		self.src_listbox.delete(0, 'end')
		self.dst_listbox.delete(0, 'end')

	def loadSRC(self):
		if(self.user_data != None and self.user_data["PRESET"] != {} and self.current_preset in list(self.user_data["PRESET"].keys()) and self.user_data["PRESET"][self.current_preset]["SRC"] != []):
			src_list = self.user_data["PRESET"][self.current_preset]["SRC"]
			self.src_listbox.delete(0, 'end')
			for i in range(len(src_list)):
				self.src_listbox.insert(i, src_list[i])

	def loadDST(self):
		if(self.user_data != None and self.user_data["PRESET"] != {} and self.current_preset in list(self.user_data["PRESET"].keys()) and self.user_data["PRESET"][self.current_preset]["DST"] != {}):
			dst_list = self.user_data["PRESET"][self.current_preset]["DST"]
			diskIDlist = self.listDiskID()
			index = 0
			self.dst_listbox.delete(0, 'end')
			for dst in dst_list:
				diskID, path = dst_list[dst]
				if(path[0] in list(diskIDlist.keys()) and diskID == diskIDlist[path[0]]):
					self.dst_listbox.insert(index, path)
					index += 1
				else:
					self.showError("Erreur", "Le lecteur de destination est absent ou la lettre de lecteur et son numéro de série ne correspondent pas pour le chemin enregistré dans les préférences:\n"+path)

			return
			for i in range(len(dst_list)):
				self.dst_listbox.insert(i, src_list[i])


	def getDST(self):
		res = {}
		diskID = self.listDiskID()
		dst_list = self.getAllDST()
		for i in range(len(dst_list)):
			if(dst_list[i][0] in list(diskID.keys())):
				res[i] = [diskID[dst_list[i][0]], dst_list[i]]
		return res


	def saveAndExitPreferences(self, window):
		options = []
		# MULTITHREADING VALUE
		if(str.isdigit(self.mt_entry.get())):
			mt = int(self.mt_entry.get())
			if(mt > 128):
				mt = 128
				self.mt_entry.delete(0, 'end')
				self.mt_entry.insert(0, mt)
			if(mt < 1):
				mt = 1
				self.mt_entry.delete(0, 'end')
				self.mt_entry.insert(0, mt)
			options.append(("MT",mt)) 
		else:
			self.mt_entry.delete(0, 'end')
			self.showInfo("Attention", "Le champ 'Nombre de sous processus'\ndoit contenir une valeur numérique entre 1 et 128")
		# PURGE & EMPTY FOLDER VALUE
		options.append(("PURGE", self.purge_ck_var.get()))
		options.append(("E", self.e_ck_var.get()))
		# RETRIE VALUE
		if(str.isdigit(self.r_entry.get())):
			r = int(self.r_entry.get())
			if(r > 24):
				r = 24
				self.r_entry.delete(0, 'end')
				self.r_entry.insert(0, r)
			if(r < 0):
				r = 0
				self.r_entry.delete(0, 'end')
				self.r_entry.insert(0, r)
			options.append(("R",r)) 
		else:
			self.r_entry.delete(0, 'end')
			self.showInfo("Attention", "Le champ 'Nombre de tentative'\ndoit contenir une valeur numérique entre 0 et 24.")
		# WAIT VALUE
		if(str.isdigit(self.w_entry.get())):
			w = int(self.w_entry.get())
			if(w > 360):
				w = 360
				self.w_entry.delete(0, 'end')
				self.w_entry.insert(0, w)
			if(w < 1):
				w = 1
				self.w_entry.delete(0, 'end')
				self.w_entry.insert(0, w)
			options.append(("W",w)) 
		else:
			self.showInfo("Attention", "Le champ 'Temps d'attente entre chaque tentative'\ndoit contenir une valeur numérique entre 1 et 360.")
			self.w_entry.delete(0, 'end')
		# OLD FILE VALUE
		options.append(("PURGE", self.o_ck_var.get()))
		if(len(options) == 6):
			#self.saveOptionsPreferences(options)
			self.current_options = self.getOptionsPreferences()
			window.destroy()


	def saveOptionsPreferences(self, option_list):
		if(self.user_data != None):
			for option in option_list:
				self.user_data["PRESET"][str(self.current_preset)]["OPTIONS"][option[0]] = option[1]
		self.writeUserData()


	def loadData(self, json_file):
		try:
			file = open(json_file, "r")
			data = json.load(file)
			file.close()
			return 0, data
		except Exception as e:
			self.showError("Error", e)
			return -1, e


	def loadUserData(self):
		user_file = ""
		for file_name in os.listdir("User/"):
			if(file_name == "user-config.json"):
				user_file = file_name
				break
		if(user_file != ""):
			code, data = self.loadData("User/"+user_file)
			if(code == -1):
				self.showError("Error while reading user config file !", data)
			else:
				self.user_data = data
		else:
			self.showInfo("Important !", "No user config file found,\ncreating new one.")
			f = open("User/user-config.json", "w")
			new_user_data = {"LAST PRESET":"", "PRESET":{"1":{"OPTIONS":{"MT":0,"PURGE":False,"E":False,"R":0,"W":0,"XO":False},"SRC":{},"DST":{}}}}
			json.dump(new_user_data, f, indent=4)
			f.close()
			self.user_data = new_user_data

		if(self.user_data != None and self.user_data["LAST PRESET"] != ""):
			self.current_preset = self.user_data["LAST PRESET"]
			self.updateCurrentPresetLabel()


	def writeUserData(self):
		user_file = ""
		for file_name in os.listdir("User/"):
			if(file_name == "user-config.json"):
				user_file = file_name
				break
		f = open("User/user-config.json", "w")
		json.dump(self.user_data, f, indent=4)
		f.close()



	def listDiskID(self):
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
			res = self.systemCall("dir "+disk+":")
			res = res.split('\\r\\n')
			if(len(res) >= 2):
				res = res[1]
				if('-' in res):
					res = res.split(' ')[-1]
					diskID[disk] = res
			else:
				continue
		return diskID


	def INFO(self):
		#print(self.optionsToString())
		#print(self.getDST())
		#print(self.user_data)
		#print(self.src_listbox.get(0, 'end'))
		#self.getSelectedSRC()
		#self.getAllSRC()
		#print("Elements non selectionnés :",self.getNotSelectedSRC())
		print("INFO !")



	def getSelectedSRC(self):
		res = []
		selected = self.src_listbox.curselection()
		for src in selected:
			res.append(self.src_listbox.get(src))
		return res

	def getSelectedDST(self):
		res = []
		selected = self.dst_listbox.curselection()
		for dst in selected:
			res.append(self.dst_listbox.get(dst))
		return res


	def getNotSelectedSRC(self):
		selected = self.getSelectedSRC()
		elements = self.getAllSRC()
		res = []
		for e in elements:
			if(e not in selected):
				res.append(e)
		return res

	def getNotSelectedDST(self):
		selected = self.getSelectedDST()
		elements = self.getAllDST()
		res = []
		for e in elements:
			if(e not in selected):
				res.append(e)
		return res


	def getAllSRC(self):
		res = []
		res = list(self.src_listbox.get(0, 'end'))
		return res

	def getAllDST(self):
		res = []
		res = list(self.dst_listbox.get(0, 'end'))
		return res


	def deleteSelectedSRC(self):
		not_selected = self.getNotSelectedSRC()
		self.src_listbox.delete(0, 'end')
		for i in range(len(not_selected)):
			self.src_listbox.insert(i, not_selected[i])

	def deleteSelectedDST(self):
		not_selected = self.getNotSelectedDST()
		self.dst_listbox.delete(0, 'end')
		for i in range(len(not_selected)):
			self.dst_listbox.insert(i, not_selected[i])


	def deleteAllSRC(self):
		self.src_listbox.delete(0, 'end')

	def deleteAllDST(self):
		self.dst_listbox.delete(0, 'end')


	def addFolderSRC(self):
		path = self.openFolderDialog()
		if(path != ""):
			if(self.getAllSRC() != []):
				last_index = self.getAllSRC().index(self.src_listbox.get('end'))
				self.src_listbox.insert(last_index+1, path)
			else:
				self.src_listbox.insert(1, path)

	def addFileSRC(self):
		path = self.openFileDialog()
		if(path != ""):
			if(self.getAllSRC() != []):
				last_index = self.getAllSRC().index(self.src_listbox.get('end'))
				self.src_listbox.insert(last_index+1, path)
			else:
				self.src_listbox.insert(1, path)

	def addFolderDST(self):
		path = self.openFolderDialog()
		if(path != ""):
			if(self.getAllDST() != []):
				last_index = self.getAllDST().index(self.dst_listbox.get('end'))
				self.dst_listbox.insert(last_index+1, path)
			else:
				self.dst_listbox.insert(1, path)


	def systemCall(self, command):
		p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
		return str(p.stdout.read())[3:-1]

	
	# ALERT BOX
	def showError(self, title, msg):
		messagebox.showerror(title, msg)

	def showInfo(self, title, msg):
		messagebox.showinfo(title, msg)

	def showYesNo(self, title, msg):
		return messagebox.askyesno(title, msg)
    	

	def lockButtons(self):
		self.delete_current_preset_button['state'] = DISABLED
		self.save_current_preset_button['state'] = DISABLED
		self.delete_selected_SRC_button['state'] = DISABLED
		self.select_folder_SRC_button['state'] = DISABLED
		self.select_file_SRC_button['state'] = DISABLED
		self.delete_selected_DST_button['state'] = DISABLED
		self.select_folder_DST_button['state'] = DISABLED
		self.start_save['state'] = DISABLED
		self.file.entryconfig(0, state=DISABLED)
		self.file.entryconfig(2, state=DISABLED)
		for element in list(self.user_data["PRESET"].keys()):
			self.presetbar.entryconfig(self.presetbar.index(element), state=DISABLED)

	def unlockButtons(self):
		self.delete_current_preset_button['state'] = NORMAL
		self.save_current_preset_button['state'] = NORMAL
		self.delete_selected_SRC_button['state'] = NORMAL
		self.select_folder_SRC_button['state'] = NORMAL
		self.select_file_SRC_button['state'] = NORMAL
		self.delete_selected_DST_button['state'] = NORMAL
		self.select_folder_DST_button['state'] = NORMAL
		self.start_save['state'] = NORMAL
		self.file.entryconfig(0, state=NORMAL)
		self.file.entryconfig(2, state=NORMAL)
		for element in list(self.user_data["PRESET"].keys()):
			self.presetbar.entryconfig(self.presetbar.index(element), state=NORMAL)


if __name__ == '__main__':
	app = App()
	app.root.mainloop()