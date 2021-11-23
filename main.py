import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from configparser import ConfigParser
import sqlite3 as sq
from tkinter import messagebox
from tabulate import tabulate
from tkinter.simpledialog import askstring
from tkinter.messagebox import showinfo
import math
import time
import asyncio
import re

"""
TODO:

Velikost čudlíků
"""

# ------------------------------- GETING READY --------------------------------

# Set main Window
root = tk.Tk()
root.title('ATM! (Concept)')
root.geometry("630x160")
root.resizable(False, False)
root.config(background="black")

writeIdWindow = tk.Toplevel(root)
writeIdWindow.config(background="black")
writeIdWindow.withdraw()

writePinWindow = tk.Toplevel(root)
writePinWindow.config(background="black")
writePinWindow.withdraw()

registerWindow = tk.Toplevel(root)
registerWindow.config(background="black")
registerWindow.withdraw()

deleteUsersWindow = tk.Toplevel(root)
deleteUsersWindow.config(background="black")
deleteUsersWindow.withdraw()

dashboardWindow = tk.Toplevel(root)
dashboardWindow.config(background="black")
dashboardWindow.withdraw()

dashboardInsertWindow = tk.Toplevel(root)
dashboardInsertWindow.config(background="black")
dashboardInsertWindow.withdraw()

dashboardWithdrawWindow = tk.Toplevel(root)
dashboardWithdrawWindow.config(background="black")
dashboardWithdrawWindow.withdraw()

root.after(1, lambda: root.focus_force())

# Read config file
parser = ConfigParser()
parser.read("config.ini")

# Variables
orange = "#e8a915"
version_readFromConfig = parser.get('info', 'version')
version = tk.StringVar()
version.set(version_readFromConfig)
id = tk.StringVar()
pin = tk.StringVar()
registerName = tk.StringVar()
registerSurname = tk.StringVar()
registerId = tk.StringVar()
registerPin = tk.StringVar()
deleteId = tk.StringVar()
blockedPin = tk.BooleanVar()
blockedPin = False
blockedTries = 0
clientBalance = tk.IntVar()
clientId = tk.IntVar()
insertValue = tk.StringVar()
withdrawValue = tk.StringVar()

# Database
connection = sq.connect("main.db")
cursor = connection.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS clients (name TEXT, card_id TEXT, card_pin TEXT, balance INTEGER)")
currentClientsArray = cursor.execute("SELECT name, card_id, card_pin, balance FROM clients").fetchall()
print("Starting ATM - v" + version.get() + " By HelloItsMeAdm")
print("")


def printCurrentClients():
	global currentClientsArray
	cursor.execute("CREATE TABLE IF NOT EXISTS clients (name TEXT, card_id TEXT, card_pin TEXT, balance INTEGER)")
	currentClientsArray = cursor.execute("SELECT name, card_id, card_pin, balance FROM clients").fetchall()
	print("Fetching all clients from database...")
	print("Fetching complete!")
	print("")
	if not currentClientsArray:
		print("Current client list is EMPTY!")
		print("")
	else:
		print("Current client list:")
		print(tabulate(currentClientsArray, headers=["Name", "ID", "PIN", "Balance"]))
		print("")


printCurrentClients()


# ------------------------------- HANDLE CLOSING WINDOWS --------------------------------
def destroySession():
	print("Detected disconnect request! Saving database...")
	connection.commit()
	cursor.close()
	print("Database successfully saved. Goodbye!")
	root.destroy()


root.protocol("WM_DELETE_WINDOW", destroySession)


def destroywriteIdWindow():
	writeIdWindow.withdraw()

def destroywritePinWindow():
	writePinWindow.withdraw()

def destroyRegisterWindow():
	registerWindow.withdraw()

def destroyUsersWindow():
	deleteUsersWindow.withdraw()

def destroyDashboardMain():
	dashboardWindow.withdraw()
	logoutUser()

def destroyDashboardInsertWindow():
	dashboardInsertWindow.withdraw()

def destroyDashboardWithdrawWindow():
	dashboardWithdrawWindow.withdraw()

writeIdWindow.protocol("WM_DELETE_WINDOW", destroywriteIdWindow)
writePinWindow.protocol("WM_DELETE_WINDOW", destroywritePinWindow)
registerWindow.protocol("WM_DELETE_WINDOW", destroyRegisterWindow)
deleteUsersWindow.protocol("WM_DELETE_WINDOW", destroyUsersWindow)
dashboardWindow.protocol("WM_DELETE_WINDOW", destroyDashboardMain)
dashboardInsertWindow.protocol("WM_DELETE_WINDOW", destroyDashboardInsertWindow)
dashboardWithdrawWindow.protocol("WM_DELETE_WINDOW", destroyDashboardWithdrawWindow)

# ------------------------------- MAIN FUNCTIONS --------------------------------
def insertCard():
	global id
	global writeIdWindow
	writeIdWindowInput.delete(0, "end")
	writeIdWindow.update()
	writeIdWindow.deiconify()
	writeIdWindow.title("Zadej ID karty")
	writeIdWindow.geometry("300x140")
	writeIdWindow.resizable(False, False)
	writeIdWindowInput.focus()
	print("Registered user logging into account!")
	print("")


def insertCardConfirm():
	global writeIdWindow
	global id
	global writeIdWindowInput
	if id.get() != 0 and str.isdigit(id.get()) and len(id.get()) == 4:
		cursor.execute('SELECT card_id FROM clients WHERE card_id=?', (str(id.get()),))
		checkExists = cursor.fetchone()

		if checkExists:
			writeIdWindow.withdraw()
			print("Logging with ID: " + id.get())
			writePin()
		else:
			messagebox.showerror("Chyba!", "Zadané ID karty nebylo v databázi nalezeno!")
			writeIdWindowInput.delete(0, "end")
			writeIdWindow.after(1, lambda: writeIdWindow.focus_force())
	else:
		messagebox.showwarning("Chyba!", "ID karty musí mít 4 čísla!")


def writePin():
	global pin
	global writePinWindow
	writePinWindowInput.delete(0, "end")
	writePinWindow.update()
	writePinWindow.deiconify()
	writePinWindow.title("Zadej PIN")
	writePinWindow.geometry("240x180")
	writePinWindow.resizable(False, False)
	writePinWindowInput.focus()
	writePinWindowTriesLeft.config(text="Zbývající pokusy: " + str(3 - blockedTries))


def writePinConfirm():
	global writePinWindow
	global pin
	global id
	global blockedPin
	global blockedTries

	if blockedPin == False:
		if pin.get() != 0 and str.isdigit(pin.get()) and len(pin.get()) == 4:
			cursor.execute("SELECT * FROM clients WHERE card_id= ? and card_pin= ?", (id.get(), pin.get()))
			found = cursor.fetchone()
			if found:
				print("The PIN entry for ID " + id.get() + " was correct.")
				print("")
				writePinWindow.withdraw()
				runDashboard(id.get())
			else:
				if blockedTries < 2:
					blockedTries += 1
					blockedTriesText = str(3 - blockedTries)
					print("Attempt for login was incorrect. Number of tries left (" + blockedTriesText + ")")
					writePinWindowTriesLeft.config(text="Zbývající pokusy: " + blockedTriesText)
					return
				else:
					print("Card was blocked. It will be automatically unblocked after 60 seconds.")
					writePinWindowButton["state"] = "disabled"
					writePinWindowTriesLeft.config(text="Karta zablokována!\nDalší možný pokus za 60 sekund.", fg="red")
					writePinWindow.after(50, blockCardStart)
		else:
			messagebox.showwarning("Chyba!", "PIN karty musí mít 4 čísla!")
			writePinWindowInput.delete(0, "end")
			writePinWindow.after(1, lambda: writePinWindow.focus_force())


def blockCardStart():
	global blockedPin
	global blockedTries
	start = time.time()
	while time.time() - start < 60:
		blockedPin = True
	while not time.time() - start < 60:
		blockedPin = False
		blockedTries = 0
		print("Card was unblocked. Number of tries left (3)")
		writePinWindowButton["state"] = "normal"
		writePinWindow.withdraw()
		writePin()
		return


def registerUser():
	global registerId
	global registerWindow
	registerWindow.update()
	registerWindow.deiconify()
	registerWindow.title("Založení nového uživatelského účtu")
	registerWindow.geometry("630x270")
	registerWindow.resizable(False, False)
	registerWindowInputName.insert(0, "Jméno")
	registerWindowInputSurname.insert(0, "Příjmení")
	registerWindowInputId.insert(0, "ID")
	registerWindowInputPin.insert(0, "PIN")
	registerWindowInputName.configure(state=tk.DISABLED)
	registerWindowInputSurname.configure(state=tk.DISABLED)
	registerWindowInputId.configure(state=tk.DISABLED)
	registerWindowInputPin.configure(state=tk.DISABLED)
	registerWindowInputName.delete(0, 'end')
	registerWindowInputSurname.delete(0, 'end')
	registerWindowInputId.delete(0, 'end')
	registerWindowInputPin.delete(0, 'end')


def registerNameClick(event):
	registerWindowInputName.configure(state=tk.NORMAL)
	registerWindowInputName.delete(0, tk.END)
	registerWindowInputName.unbind('<Button-1>', registerNameClick_id)
	registerWindowInputNameTitle.grid(row=2, padx=8)


def registerSurnameClick(event):
	registerWindowInputSurname.configure(state=tk.NORMAL)
	registerWindowInputSurname.delete(0, tk.END)
	registerWindowInputSurname.unbind('<Button-1>', registerSurnameClick_id)
	registerWindowInputSurnameTitle.grid(row=4, padx=8)


def registerIdClick(event):
	registerWindowInputId.configure(state=tk.NORMAL)
	registerWindowInputId.delete(0, tk.END)
	registerWindowInputId.unbind('<Button-1>', registerIdClick_id)
	registerWindowInputIdTitle.grid(row=2, column=3, padx=8)


def registerPinClick(event):
	registerWindowInputPin.configure(state=tk.NORMAL)
	registerWindowInputPin.delete(0, tk.END)
	registerWindowInputPin.unbind('<Button-1>', registerPinClick_id)
	registerWindowInputPinTitle.grid(row=4, column=3, padx=8)


def registerUserConfirm():
	global registerWindow
	global registerName
	global registerSurname
	global registerId
	global registerPin

	cursor.execute('SELECT card_id FROM clients WHERE card_id=?', (str(registerId.get()),))
	result = cursor.fetchone()

	if registerId.get() != 0 and str.isdigit(registerId.get()) and len(
			registerId.get()) == 4 and registerPin.get() != 0 and str.isdigit(registerPin.get()) and len(
			registerPin.get()) == 4:
		if result:
			messagebox.showerror('Chyba!',
								 "Zadané ID (" + registerId.get() + ") je již zaregistrované v databázi! Vyber si prosím jiné.")
			registerWindow.after(1, lambda: registerWindow.focus_force())
		else:
			messagebox.showinfo('Hotovo!',
								"Byl jsi úspěšně zaregistrován! Nyní použij následující údaje k přihlášení:\n\nID: " + registerId.get() + "\nPIN: " + registerPin.get())
			registerWindow.withdraw()
			print("Detected new registration! Added this card to the database:")
			print("Owner: " + registerName.get() + " " + registerSurname.get())
			print("ID: " + registerId.get())
			print("PIN: " + registerPin.get())
			print("Balance: 0 Kč")
			print("")
			cursor.execute(
				"INSERT INTO clients VALUES ('" + registerName.get() + " " + registerSurname.get() + "', '" + registerId.get() + "', '" + registerPin.get() + "', 0)")
			connection.commit()
			printCurrentClients()
			refreshDeleteButton()
	else:
		if len(registerName.get()) == 0 or str.isdigit(registerName.get()):
			messagebox.showwarning('Chyba!', "Nesprávně zadané jméno!")
			registerWindow.after(1, lambda: registerWindow.focus_force())
		elif len(registerSurname.get()) == 0 or str.isdigit(registerSurname.get()):
			messagebox.showwarning('Chyba!', "Nesprávně zadané příjmení!")
			registerWindow.after(1, lambda: registerWindow.focus_force())
		elif len(registerId.get()) != 4 or not str.isdigit(registerId.get()):
			messagebox.showwarning('Chyba!', "ID karty musí mít 4 čísla.")
			registerWindow.after(1, lambda: registerWindow.focus_force())
		elif len(registerPin.get()) != 4 or not str.isdigit(registerPin.get()):
			messagebox.showwarning('Chyba!', "PIN karty musí mít 4 čísla.")
			registerWindow.after(1, lambda: registerWindow.focus_force())


def deleteUsers():
	deleteUsersInput.delete(0, 'end')
	deleteUsersWindow.update()
	deleteUsersWindow.deiconify()
	deleteUsersWindow.title("Smazání uživatelských účtů")
	deleteUsersWindow.geometry("250x240")
	deleteUsersWindow.resizable(False, False)


def deleteOneUser():
	global deleteId
	global currentClientsArray
	if deleteId.get() != 0 and str.isdigit(deleteId.get()) and len(deleteId.get()) == 4:
		cursor.execute('SELECT card_id FROM clients WHERE card_id=?', (str(deleteId.get()),))
		result = cursor.fetchone()
		if result:
			confirmDeleteOne = messagebox.askquestion("Potvrzení",
													  "Opravdu chceš smazat uživatele s ID " + deleteId.get() + "?")
			if confirmDeleteOne == "yes":
				cursor.execute('DELETE FROM clients WHERE card_id=?', (str(deleteId.get()),))
				connection.commit()
				print("User with ID " + deleteId.get() + " has been deleted from database!")
				print("Database successfully saved.")
				print("")
				printCurrentClients()
				refreshDeleteButton()
				if not currentClientsArray:
					messagebox.askquestion("Smazáno!", "Úspěšně jsi smazal uživatele s ID " + deleteId.get() + ".")
					deleteUsersWindow.withdraw()
					refreshDeleteButton()
				else:
					confirmDeleteOneAfter = messagebox.askquestion("Smazáno!",
																   "Úspěšně jsi smazal uživatele s ID " + deleteId.get() + ". Chceš smazat dalšího uživatele?")
					if confirmDeleteOneAfter == "yes":
						deleteUsersWindow.after(1, lambda: deleteUsersWindow.focus_force())
						deleteUsersInput.delete(0, 'end')
						refreshDeleteButton()
					else:
						deleteUsersWindow.withdraw()
						refreshDeleteButton()
			else:
				deleteUsersWindow.after(1, lambda: deleteUsersWindow.focus_force())
		else:
			messagebox.showerror('Chyba!', "Uživatel s ID " + deleteId.get() + " nebyl nalezen!")
			deleteUsersWindow.after(1, lambda: deleteUsersWindow.focus_force())
			deleteUsersInput.delete(0, 'end')
	else:
		messagebox.showwarning('Chyba!', "ID karty musí mít 4 čísla.")
		deleteUsersWindow.after(1, lambda: deleteUsersWindow.focus_force())
		deleteUsersInput.delete(0, 'end')


def deleteAllUsers():
	deleteAllUsersConfirm = askstring('Opravdu?',
									  'Pokud chceš smazat VŠECHNY uživatele napiš do rámečku pod tento text slovo ANO')
	if deleteAllUsersConfirm == "ANO":
		cursor.execute('DELETE FROM clients')
		connection.commit()
		print("ALL users have been deleted!")
		print("Database successfully saved.")
		print("")
		deleteUsersWindow.withdraw()
		messagebox.showinfo("Smazáno!", "Všichni uživatelé byli úspěšně smazáni!")
		refreshDeleteButton()
	else:
		messagebox.showwarning("Chyba!", "Pokud chceš smazat VŠECHNY uživatele musíš napsat ANO.")
		deleteUsersWindow.after(1, lambda: deleteUsersWindow.focus_force())


def runDashboard(id):
	global dashboardWindow
	global clientBalance
	global clientId

	dashboardWindow.update()
	dashboardWindow.deiconify()
	dashboardWindow.geometry("475x255")
	dashboardWindow.resizable(False, False)

	cursor.execute("SELECT balance FROM clients WHERE card_id=?", (id,))
	balanceFirst = str(cursor.fetchone())
	characters_to_remove = "(),"
	pattern = "[" + characters_to_remove + "]"
	balance = re.sub(pattern, "", balanceFirst)

	clientBalance = int(re.sub(pattern, "", balanceFirst))
	clientId = int(id)

	dashboardTitle.config(text="Vítej uživateli " + id + "!\nStav účtu: " + str(balance) + " Kč")
	dashboardWindow.title("Dashboard (" + id + ")")


def insertMoney():
	global dashboardInsertWindow
	global insertValue

	dashboardInsertWindow.update()
	dashboardInsertWindow.deiconify()
	dashboardInsertWindow.title("Vložení peněz")
	dashboardInsertWindow.geometry("250x170")
	dashboardInsertWindow.resizable(False, False)
	dashboardInsertWindowInput.delete(0, "end")


def insertMoneyConfirm():
	global insertValue
	global id

	if insertValue.get() != 0 and str.isdigit(insertValue.get()):
		if messagebox.askquestion("Vložit tuto částku?", "Opravdu chceš vložit " + str(insertValue.get()) + " Kč na účet " + str(id.get()) + "?") == "yes":

			cursor.execute("UPDATE clients SET balance=? WHERE card_id=?", (str(insertValue.get()),str(id.get())))
			print("Successfully changed balance of ID " + id.get())
			print("")
			printCurrentClients()

			dashboardInsertWindow.withdraw()
			dashboardWindow.withdraw()
			runDashboard(id.get())
			dashboardWindow.after(1, lambda: dashboardWindow.focus_force())

			messagebox.showinfo("Hotovo!", "Bylo vloženo " + str(insertValue.get()) + " Kč na účet " + str(id.get()) + "!")
			dashboardWindow.after(1, lambda: dashboardWindow.focus_force())
		else:
			dashboardInsertWindow.after(1, lambda: dashboardInsertWindow.focus_force())

	else:
		messagebox.showwarning('Chyba!', "Musíš zadat číslo!")

def withdrawMoney():
	global dashboardWithdrawWindow
	global withdrawValue

	dashboardWithdrawWindow.update()
	dashboardWithdrawWindow.deiconify()
	dashboardWithdrawWindow.title("Výběr peněz")
	dashboardWithdrawWindow.geometry("250x170")
	dashboardWithdrawWindow.resizable(False, False)
	dashboardWithdrawWindowInput.delete(0, "end")

def withdrawMoneyConfirm():
	global withdrawValue
	global id
	global clientBalance

	if withdrawValue.get() != 0 and str.isdigit(withdrawValue.get()):
		if int(withdrawValue.get()) < clientBalance:
			if messagebox.askquestion("Vybrat tuto částku?", "Opravdu chceš vybrat " + str(withdrawValue.get()) + " Kč z účtu " + str(id.get()) + "?") == "yes":
				newClientBalance = clientBalance - int(withdrawValue.get())

				cursor.execute("UPDATE clients SET balance=? WHERE card_id=?", (str(newClientBalance),str(id.get())))
				print("Successfully changed balance of ID " + id.get())
				print("")
				printCurrentClients()
	
				dashboardWithdrawWindow.withdraw()
				dashboardWindow.withdraw()
				runDashboard(id.get())
				dashboardWindow.after(1, lambda: dashboardWindow.focus_force())
	
				messagebox.showinfo("Hotovo!", "Bylo vybráno " + str(withdrawValue.get()) + " Kč z účtu " + str(id.get()) + "!")
				dashboardWindow.after(1, lambda: dashboardWindow.focus_force())
			else:
				dashboardWithdrawWindow.after(1, lambda: dashboardWithdrawWindow.focus_force())
		else:
			messagebox.showwarning('Chyba!', "Na účtu " + str(id.get()) + " není k dispozici tolik peněz!")
			dashboardWithdrawWindow.after(1, lambda: dashboardWithdrawWindow.focus_force())
			dashboardWithdrawWindowInput.delete(0, "end")
	else:
		messagebox.showwarning('Chyba!', "Musíš zadat číslo!")
		dashboardWithdrawWindow.after(1, lambda: dashboardWithdrawWindow.focus_force())
		dashboardWithdrawWindowInput.delete(0, "end")

def logoutUser():
	global id

	print("User " + id.get() + " logged out! Cleared cache.")
	dashboardInsertWindow.withdraw()
	dashboardWithdrawWindow.withdraw()
	dashboardWindow.withdraw()
	return

# ------------------------------- WIDGETS --------------------------------

title = ttk.Label(root, text="ATM - v" + version.get(), font=("Poppins Bold", 25), background="black",
				  foreground="white")
title.pack()

secondMain = tk.Frame(root, background="black")
secondMain.pack()

insertCardButton = tk.Button(secondMain, text="Vložit Kartu", font=("Poppins Bold", 15), command=insertCard, bg="green",
							 fg="black")
insertCardButton.pack(padx=10, side=tk.LEFT)

registerButton = tk.Button(secondMain, text="Registrovat Uživatele", font=("Poppins Bold", 15), command=registerUser,
						   bg="aqua", fg="black")
registerButton.pack(padx=10, side=tk.LEFT)

deleteUserButton = tk.Button(secondMain, text="Smazat Uživatele", font=("Poppins Bold", 15), command=deleteUsers,
							 bg="red", fg="black")
deleteUserButton.pack(padx=10, side=tk.LEFT)

title2 = ttk.Label(root, text="Concept by HelloItsMeAdm", font=("Poppins Bold", 10), background="black",
				   foreground="gray")
title2.pack(pady=5)


def refreshDeleteButton():
	global currentClientsArray
	global deleteUserButton
	cursor.execute("CREATE TABLE IF NOT EXISTS clients (name TEXT, card_id TEXT, card_pin TEXT, balance INTEGER)")
	currentClientsArray = cursor.execute("SELECT name, card_id, card_pin, balance FROM clients").fetchall()
	if not currentClientsArray:
		deleteUserButton["state"] = "disabled"
		insertCardButton["state"] = "disabled"
		return
	else:
		deleteUserButton["state"] = "normal"
		insertCardButton["state"] = "normal"
		return


refreshDeleteButton()

writeIdWindowTitle = tk.Label(writeIdWindow, fg="white", bg="black", text="Zadej prosím své ID karty.",
							  font=("Poppins bold", 15))
writeIdWindowTitle.pack()

writeIdWindowInput = tk.Entry(writeIdWindow, fg="white", bg="black", textvariable=id, insertbackground="white",
							  justify=tk.CENTER, font=("Poppins bold", 12))
writeIdWindowInput.pack()

writeIdWindowButton = tk.Button(writeIdWindow, text="Potvrdit!", background="green", font=("Poppins Bold", 14),
								command=insertCardConfirm)
writeIdWindowButton.pack(pady=10)


writePinWindowTitle = tk.Label(writePinWindow, fg="white", bg="black", text="Zadej svůj PIN.",
							   font=("Poppins bold", 15))
writePinWindowTitle.pack()

writePinWindowInput = tk.Entry(writePinWindow, fg="white", bg="black", textvariable=pin, insertbackground="white",
							   justify=tk.CENTER, font=("Poppins bold", 12))
writePinWindowInput.pack()

writePinWindowTriesLeft = tk.Label(writePinWindow, fg="white", bg="black", text="", font=("Poppins bold", 10))
writePinWindowTriesLeft.pack()

writePinWindowButton = tk.Button(writePinWindow, text="Potvrdit!", background="green", font=("Poppins Bold", 14),
								 command=writePinConfirm)
writePinWindowButton.pack(pady=10)


registerWindowTitle = tk.Label(registerWindow, fg="white", bg="black", text="Založení účtu", font=("Poppins bold", 20))
registerWindowTitle.grid(row=1, column=2)

registerWindowInputNameTitle = tk.Label(registerWindow, fg="white", bg="black", text="Jméno", font=("Poppins bold", 12))

registerWindowInputName = tk.Entry(registerWindow, fg="white", bg="black", textvariable=registerName,
								   insertbackground="white", justify=tk.CENTER, font=("Poppins bold", 12),
								   disabledbackground="black", disabledforeground="gray")
registerWindowInputName.grid(row=3, padx=8)

registerWindowInputSurnameTitle = tk.Label(registerWindow, fg="white", bg="black", text="Příjmení",
										   font=("Poppins bold", 12))

registerWindowInputSurname = tk.Entry(registerWindow, fg="white", bg="black", textvariable=registerSurname,
									  insertbackground="white", justify=tk.CENTER, font=("Poppins bold", 12),
									  disabledbackground="black", disabledforeground="gray")
registerWindowInputSurname.grid(row=5, padx=8)

registerWindowInputIdTitle = tk.Label(registerWindow, fg="white", bg="black", text="ID", font=("Poppins bold", 12))

registerWindowInputId = tk.Entry(registerWindow, fg="white", bg="black", textvariable=registerId,
								 insertbackground="white", justify=tk.CENTER, font=("Poppins bold", 12),
								 disabledbackground="black", disabledforeground="gray")
registerWindowInputId.grid(row=3, column=3, padx=8)

registerWindowInputPinTitle = tk.Label(registerWindow, fg="white", bg="black", text="PIN", font=("Poppins bold", 12))

registerWindowInputPin = tk.Entry(registerWindow, fg="white", bg="black", textvariable=registerPin,
								  insertbackground="white", justify=tk.CENTER, font=("Poppins bold", 12),
								  disabledbackground="black", disabledforeground="gray")
registerWindowInputPin.grid(row=5, column=3, padx=8)

registerNameClick_id = registerWindowInputName.bind('<Button-1>', registerNameClick)
registerSurnameClick_id = registerWindowInputSurname.bind('<Button-1>', registerSurnameClick)
registerIdClick_id = registerWindowInputId.bind('<Button-1>', registerIdClick)
registerPinClick_id = registerWindowInputPin.bind('<Button-1>', registerPinClick)

registerWindowButton = tk.Button(registerWindow, text="Registrovat!", background="green", font=("Poppins Bold", 14),
								 command=registerUserConfirm)
registerWindowButton.grid(row=6, pady=10, column=2)


deleteUsersTitle = tk.Label(deleteUsersWindow, fg="white", bg="black", text="Zadej ID uživatele.",
							font=("Poppins bold", 15))
deleteUsersTitle.pack()

deleteUsersInput = tk.Entry(deleteUsersWindow, fg="white", bg="black", textvariable=deleteId, insertbackground="white",
							justify=tk.CENTER, font=("Poppins bold", 12))
deleteUsersInput.pack()

deleteUsersButton = tk.Button(deleteUsersWindow, text="Smazat uživatele", background="green", font=("Poppins Bold", 10),
							  command=deleteOneUser)
deleteUsersButton.pack(pady=10)

deleteUsersTitle = tk.Label(deleteUsersWindow, fg="white", bg="black", text="nebo", font=("Poppins bold", 15))
deleteUsersTitle.pack()

deleteUsersButton = tk.Button(deleteUsersWindow, text="Smazat VŠECHNY uživatele", background="green",
							  font=("Poppins Bold", 10), command=deleteAllUsers)
deleteUsersButton.pack(pady=10)


dashboardTitle = tk.Label(dashboardWindow, fg="white", bg="black", text=".", font=("Poppins bold", 20))
dashboardTitle.pack()

secondDashboard = tk.Frame(dashboardWindow, background="black")
secondDashboard.pack()


dashboardButtonInsertMoney = tk.Button(secondDashboard, text="Vložit peníze", background="green",
									   font=("Poppins Bold", 15), command=insertMoney)
dashboardButtonInsertMoney.pack(pady=10, side=tk.LEFT)

dashboardButtonWithdrawMoney = tk.Button(secondDashboard, text="Vybrat peníze", background="green",
										 font=("Poppins Bold", 15), command=withdrawMoney)
dashboardButtonWithdrawMoney.pack(pady=10, side=tk.LEFT, padx=20)

dashboardButtonLogout = tk.Button(dashboardWindow, text="Odhlásit", background="orange",
										 font=("Poppins Bold", 12), command=logoutUser)
dashboardButtonLogout.pack(pady=10)


dashboardInsertWindowTitle = tk.Label(dashboardInsertWindow, fg="white", bg="black", text="Zadej částku.",
									  font=("Poppins bold", 15))
dashboardInsertWindowTitle.pack()

dashboardInsertWindowInput = tk.Entry(dashboardInsertWindow, fg="white", bg="black", textvariable=insertValue,
									  insertbackground="white", justify=tk.CENTER, font=("Poppins bold", 12))
dashboardInsertWindowInput.pack()

dashboardInsertWindowButton = tk.Button(dashboardInsertWindow, text="Potvrdit!", background="green",
										font=("Poppins Bold", 14), command=insertMoneyConfirm)
dashboardInsertWindowButton.pack(pady=10)


dashboardWithdrawWindowTitle = tk.Label(dashboardWithdrawWindow, fg="white", bg="black", text="Zadej částku.",
									  font=("Poppins bold", 15))
dashboardWithdrawWindowTitle.pack()

dashboardWithdrawWindowInput = tk.Entry(dashboardWithdrawWindow, fg="white", bg="black", textvariable=withdrawValue,
									  insertbackground="white", justify=tk.CENTER, font=("Poppins bold", 12))
dashboardWithdrawWindowInput.pack()

dashboardWithdrawWindowButton = tk.Button(dashboardWithdrawWindow, text="Potvrdit!", background="green",
										font=("Poppins Bold", 14), command=withdrawMoneyConfirm)
dashboardWithdrawWindowButton.pack(pady=10)

# ------------------------------- END THINGS --------------------------------

# Run tkinter
root.mainloop()

# Close database
connection.commit()
cursor.close()
