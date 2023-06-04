from tkinter import *
from tkinter import font as tkFont

# Written by FMA ;)
# this file contains 4 class of top level window.
# They are used in main program to replace default tkinter message box

class CustomError(Toplevel):
	def __init__(self, msg, root):
		Toplevel.__init__(self, root)
		self.title("Erreur")
		self.main_theme_light = "grey85"
		self.main_theme = "grey35"
		self.parent = root
		self.value = BooleanVar(value=False)
		self.minsizeX = 230
		self.minsizeY = 120
		self.minsize(self.minsizeX, self.minsizeY)
		self.resizable(False, False)
		self.attributes('-topmost', 'true')
		self.protocol("WM_DELETE_WINDOW", self.on_closing)
		self.error_label = Label(self, text=msg, wraplength=200, justify=LEFT)
		self.error_label.pack(side=TOP, expand=True, fill=X, padx=5, pady=5)
		self.button_frame = Frame(self, bg=self.main_theme_light, width=50)
		self.button_frame.pack(side=BOTTOM, expand=False, fill=X, padx=0, pady=0)
		self.error_button = Button(self.button_frame, command=self.on_button_ok_click, text="OK", width=8)
		self.error_button.pack(side=TOP, expand=False, padx=5, pady=5)

	def show(self):
		self.setPosition()
		self.grab_set()
		self.wm_deiconify()
		self.wait_window()
		self.grab_release()
		return self.value.get()

	def setPosition(self):
		self.geometry("+%d+%d" % (self.parent.winfo_x() + self.parent.winfo_width()/2 - self.minsizeX/2, self.parent.winfo_y() + self.parent.winfo_height()/2 - self.minsizeY/2))

	def on_button_ok_click(self):
		self.value.set(True)
		#print("Root X,Y, W,H :", self.parent.winfo_x(),self.parent.winfo_y(), self.parent.winfo_width(), self.parent.winfo_height())
		#print("Top  X,Y, W,H :", self.winfo_x(),self.winfo_y(), self.winfo_width(), self.winfo_height())
		self.destroy()

	def on_closing(self):
		self.destroy()




class CustomInfo(Toplevel):
	def __init__(self, msg, root):
		Toplevel.__init__(self, root)
		self.title("Information")
		self.main_theme_light = "grey85"
		self.main_theme = "grey35"
		self.parent = root
		self.value = BooleanVar(value=False)
		self.minsizeX = 230
		self.minsizeY = 120
		self.minsize(self.minsizeX, self.minsizeY)
		self.resizable(False, False)
		self.attributes('-topmost', 'true')
		self.protocol("WM_DELETE_WINDOW", self.on_closing)
		self.error_label = Label(self, text=msg, wraplength=200, justify=LEFT)
		self.error_label.pack(side=TOP, expand=True, fill=X, padx=5, pady=5)
		self.button_frame = Frame(self, bg=self.main_theme_light, width=50)
		self.button_frame.pack(side=BOTTOM, expand=False, fill=X, padx=0, pady=0)
		self.error_button = Button(self.button_frame, command=self.on_button_ok_click, text="OK", width=8)
		self.error_button.pack(side=TOP, expand=False, padx=5, pady=5)

	def show(self):
		self.setPosition()
		self.grab_set()
		self.wm_deiconify()
		self.wait_window()
		self.grab_release()
		return self.value.get()

	def setPosition(self):
		self.geometry("+%d+%d" % (self.parent.winfo_x() + self.parent.winfo_width()/2 - self.minsizeX/2, self.parent.winfo_y() + self.parent.winfo_height()/2 - self.minsizeY/2))

	def on_button_ok_click(self):
		self.value.set(True)
		self.destroy()

	def on_closing(self):
		self.destroy()




class CustomYesNo(Toplevel):
	def __init__(self, msg, root):
		Toplevel.__init__(self, root)
		self.title("Validation")
		self.main_theme_light = "grey85"
		self.main_theme = "grey35"
		self.parent = root
		self.value = BooleanVar(value=False)
		self.minsizeX = 230
		self.minsizeY = 120
		self.minsize(self.minsizeX, self.minsizeY)
		self.resizable(False, False)
		self.attributes('-topmost', 'true')
		self.protocol("WM_DELETE_WINDOW", self.on_closing)
		self.yesno_label = Label(self, text=msg, wraplength=250, justify=LEFT)
		self.yesno_label.pack(side=TOP, expand=True, fill=X, padx=5, pady=5)
		self.button_frame = Frame(self, bg=self.main_theme_light, width=50)
		self.button_frame.pack(side=BOTTOM, expand=False, fill=X, padx=0, pady=0)
		self.yesno_button_oui = Button(self.button_frame, command=self.on_button_oui_click, text="Oui", width=8)
		self.yesno_button_oui.pack(side=LEFT, expand=False, padx=(50, 5), pady=5)
		self.yesno_button_non = Button(self.button_frame, command=self.on_button_non_click, text="Non", width=8)
		self.yesno_button_non.focus()
		self.yesno_button_non.pack(side=RIGHT, expand=False, padx=(5, 50), pady=5)

	def show(self):
		self.setPosition()
		self.grab_set()
		self.wm_deiconify()
		self.wait_window()
		self.grab_release()
		return self.value.get()

	def setPosition(self):
		self.geometry("+%d+%d" % (self.parent.winfo_x() + self.parent.winfo_width()/2 - self.minsizeX/2, self.parent.winfo_y() + self.parent.winfo_height()/2 - self.minsizeY/2))

	def on_button_oui_click(self):
		self.value.set(True)
		self.destroy()

	def on_button_non_click(self):
		self.destroy()

	def on_closing(self):
		self.destroy()




class CustomInfoList(Toplevel):
	def __init__(self, msg, root, file_list):
		Toplevel.__init__(self, root)
		self.title("Information")
		self.main_theme_light = "grey85"
		self.main_theme = "grey35"
		self.parent = root
		self.startSizeX = 800
		self.startSizeY = 360
		self.minsize(500, 120)
		self.attributes('-topmost', 'true')
		self.protocol("WM_DELETE_WINDOW", self.on_closing)
		self.resizable(True, True)
		frame_font = tkFont.Font(size=13, weight="bold")
		self.main_sub_frame = LabelFrame(self, text=msg, font=frame_font, labelanchor="n", borderwidth=0, bg=self.main_theme, fg="white")
		self.main_sub_frame.pack(side=TOP, expand=True, fill=BOTH, padx=0, pady=0)
		self.sub_yscrollbar = Scrollbar(self.main_sub_frame, bg=self.main_theme, orient=VERTICAL)
		self.sub_yscrollbar.pack(side=RIGHT, padx=(0,5), pady=(5,5), fill=Y)
		self.sub_xscrollbar = Scrollbar(self.main_sub_frame, bg=self.main_theme, orient=HORIZONTAL)
		self.sub_xscrollbar.pack(side=BOTTOM, padx=(5,5), pady=(0,5), fill=X)
		self.sub_text = Text(self.main_sub_frame, fg="white", bg=self.main_theme, width=100, height=15, wrap="none", yscrollcommand=self.sub_yscrollbar.set, xscrollcommand=self.sub_xscrollbar.set)
		self.sub_text.pack(side=TOP, expand=True, fill=BOTH, padx=5, pady=5)
		self.sub_yscrollbar.config(command=self.sub_text.yview)
		self.sub_xscrollbar.config(command=self.sub_text.xview)
		self.sub_text.insert(0.0, '\n'.join(file_list))


	def show(self):
		self.grab_set()
		self.wm_deiconify()
		self.setPosition()
		self.wait_window()
		self.grab_release()

	def setPosition(self):
		self.geometry("+%d+%d" % (self.parent.winfo_x() + self.parent.winfo_width()/2 - self.startSizeX/2, self.parent.winfo_y() + self.parent.winfo_height()/2 - self.startSizeY/2))

	def on_closing(self):
		self.destroy()