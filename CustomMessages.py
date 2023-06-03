from tkinter import *


class CustomError(Toplevel):
	def __init__(self, msg):
		Toplevel.__init__(self)
		self.error_label = Label(self, text=msg)
		self.error_label.pack(side=TOP, expand=True, fill=X, padx=5, pady=5)
		self.error_button = Button(self, command=self.destroy, text="OK")
		self.error_button.pack(side=TOP, expand=False, padx=5, pady=5)
		self.attributes('-topmost', 'true')
		self.bind("<Configure>", self.getSize)


	def getSize(self):
		print(self.winfo_width(), self.winfo_height())



if __name__ == '__main__':
	w = Tk()
	CustomError("Ceci est un message d'erreur !")
	w.mainloop()