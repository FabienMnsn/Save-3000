from tkinter import *


class CustomError(Toplevel):
	def __init__(self, msg, root):
		Toplevel.__init__(self)
		self.title("Erreur")
		self.main_theme_light = "grey85"
		self.main_theme = "grey35"
		self.parent = root

		self.minsize(230, 120)
		
		self.resizable(False, False)
		self.attributes('-topmost', 'true')
		#self.protocol("WM_DELETE_WINDOW", self.on_closing)
		self.error_label = Label(self, text=msg, wraplength=200, justify=LEFT)
		self.error_label.pack(side=TOP, expand=True, fill=X, padx=5, pady=5)

		self.button_frame = Frame(self, bg=self.main_theme_light, width=50)
		self.button_frame.pack(side=BOTTOM, expand=False, fill=X, padx=0, pady=0)

		self.error_button = Button(self.button_frame, command=self.on_button_ok_click, text="OK", width=8)
		self.error_button.pack(side=TOP, expand=False, padx=5, pady=5)

		#self.setPosition()


	def setPosition(self):
		self.geometry("+%d+%d" % (self.parent.winfo_x() + self.parent.winfo_width()/2 - self.winfo_width()/2, self.parent.winfo_y() + self.parent.winfo_height()/2 - self.winfo_height()/2))


	def on_button_ok_click(self):
		self.destroy()


if __name__ == '__main__':
	w = Tk()
	w.geometry("700x400")
	CustomError("Ceci est un message d'erreur vraiment très très long hein il n'est pas pret de se terminer !", w)
	print(res)
	w.mainloop()

