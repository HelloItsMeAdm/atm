import tkinter as tk
from tkinter import ttk
from configparser import ConfigParser
import sqlite3 as sq
from tkinter import messagebox
from tabulate import tabulate
from tkinter.simpledialog import askstring
import time
import re

from database import database

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

dashboardSendValueWindow = tk.Toplevel(root)
dashboardSendValueWindow.config(background="black")
dashboardSendValueWindow.withdraw()

dashboardSendIdWindow = tk.Toplevel(root)
dashboardSendIdWindow.config(background="black")
dashboardSendIdWindow.withdraw()

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
sendValue = tk.StringVar()
sendId = tk.StringVar()

# Database
connection = sq.connect("main.db")
cursor = connection.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS clients (name TEXT, card_id TEXT, card_pin TEXT, balance INTEGER)")
currentClientsArray = cursor.execute("SELECT name, card_id, card_pin, balance FROM clients").fetchall()
print("Starting ATM - v" + version.get() + " By HelloItsMeAdm")
print("")

database.printCurrentClients()

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

def destroyDashboardSendValueWindow():
    dashboardSendValueWindow.withdraw()

def destroyDashboardSendIdWindow():
    dashboardSendIdWindow.withdraw()

writeIdWindow.protocol("WM_DELETE_WINDOW", destroywriteIdWindow)
writePinWindow.protocol("WM_DELETE_WINDOW", destroywritePinWindow)
registerWindow.protocol("WM_DELETE_WINDOW", destroyRegisterWindow)
deleteUsersWindow.protocol("WM_DELETE_WINDOW", destroyUsersWindow)
dashboardWindow.protocol("WM_DELETE_WINDOW", destroyDashboardMain)
dashboardInsertWindow.protocol("WM_DELETE_WINDOW", destroyDashboardInsertWindow)
dashboardWithdrawWindow.protocol("WM_DELETE_WINDOW", destroyDashboardWithdrawWindow)
dashboardSendValueWindow.protocol("WM_DELETE_WINDOW", destroyDashboardSendValueWindow)
dashboardSendIdWindow.protocol("WM_DELETE_WINDOW", destroyDashboardSendIdWindow)

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

def insertCardConfirm():
    global writeIdWindow
    global id
    global writeIdWindowInput
    if id.get() != 0 and str.isdigit(id.get()) and len(id.get()) == 4:
        cursor.execute('SELECT card_id FROM clients WHERE card_id=?', (str(id.get()),))
        checkExists = cursor.fetchone()

        if checkExists:
            writeIdWindow.withdraw()
            writePin()
        else:
            messagebox.showerror("Chyba!", "Zadan?? ID karty nebylo v datab??zi nalezeno!")
            writeIdWindowInput.delete(0, "end")
            writeIdWindow.after(1, lambda: writeIdWindow.focus_force())
    else:
        messagebox.showwarning("Chyba!", "ID karty mus?? m??t 4 ????sla!")


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
    writePinWindowTriesLeft.config(text="Zb??vaj??c?? pokusy: " + str(3 - blockedTries))


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
                print("User " + id.get() + " logged in!")
                print("")
                writePinWindow.withdraw()
                runDashboard(id.get())
            else:
                if blockedTries < 2:
                    blockedTries += 1
                    blockedTriesText = str(3 - blockedTries)
                    print("Attempt for login was incorrect. Number of tries left (" + blockedTriesText + ")")
                    writePinWindowTriesLeft.config(text="Zb??vaj??c?? pokusy: " + blockedTriesText)
                    return
                else:
                    print("Card was blocked. It will be automatically unblocked after 60 seconds.")
                    writePinWindowButton["state"] = "disabled"
                    writePinWindowTriesLeft.config(text="Karta zablokov??na!\nDal???? mo??n?? pokus za 60 sekund.", fg="red")
                    writePinWindow.after(50, blockCardStart)
        else:
            messagebox.showwarning("Chyba!", "PIN karty mus?? m??t 4 ????sla!")
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
    registerWindow.title("Zalo??en?? nov??ho u??ivatelsk??ho ????tu")
    registerWindow.geometry("630x270")
    registerWindow.resizable(False, False)
    registerWindowInputName.delete(0, 'end')
    registerWindowInputSurname.delete(0, 'end')
    registerWindowInputId.delete(0, 'end')
    registerWindowInputPin.delete(0, 'end')


def registerUserConfirm():
    global registerWindow
    global registerName
    global registerSurname
    global registerId
    global registerPin

    cursor.execute('SELECT card_id FROM clients WHERE card_id=?', (str(registerId.get()),))
    result = cursor.fetchone()

    if len(registerName.get()) == 0 or str.isdigit(registerName.get()) or len(registerSurname.get()) == 0 or str.isdigit(registerSurname.get()):
        messagebox.showwarning('Chyba!', "Nespr??vn?? zadan?? jm??no nebo p????jmen??!")
        registerWindow.after(1, lambda: registerWindow.focus_force())
    else:
        if len(registerId.get()) != 4 or not str.isdigit(registerId.get()):
            messagebox.showwarning('Chyba!', "ID karty mus?? m??t 4 ????sla.")
            registerWindow.after(1, lambda: registerWindow.focus_force())
        else:
            if len(registerPin.get()) != 4 or not str.isdigit(registerPin.get()):
                messagebox.showwarning('Chyba!', "PIN karty mus?? m??t 4 ????sla.")
                registerWindow.after(1, lambda: registerWindow.focus_force())
            else:
                if result:
                    messagebox.showerror('Chyba!',
                                         "Zadan?? ID (" + registerId.get() + ") je ji?? zaregistrovan?? v datab??zi! Vyber si pros??m jin??.")
                    registerWindow.after(1, lambda: registerWindow.focus_force())
                else:
                    messagebox.showinfo('Hotovo!',
                                        "Byl jsi ??sp????n?? zaregistrov??n! Nyn?? pou??ij n??sleduj??c?? ??daje k p??ihl????en??:\n\nID: " + registerId.get() + "\nPIN: " + registerPin.get())
                    registerWindow.withdraw()
                    print("Detected new registration! Added this card to the database:")
                    print("Owner: " + registerName.get() + " " + registerSurname.get())
                    print("ID: " + registerId.get())
                    print("PIN: " + registerPin.get())
                    print("Balance: 0 K??")
                    print("")
                    cursor.execute(
                        "INSERT INTO clients VALUES ('" + registerName.get() + " " + registerSurname.get() + "', '" + registerId.get() + "', '" + registerPin.get() + "', 0)")
                    connection.commit()
                    database.printCurrentClients()
                    refreshDeleteButton()

def deleteUsers():
    deleteUsersInput.delete(0, 'end')
    deleteUsersWindow.update()
    deleteUsersWindow.deiconify()
    deleteUsersWindow.title("Smaz??n?? u??ivatelsk??ch ????t??")
    deleteUsersWindow.geometry("250x240")
    deleteUsersWindow.resizable(False, False)


def deleteOneUser():
    global deleteId
    global currentClientsArray
    if deleteId.get() != 0 and str.isdigit(deleteId.get()) and len(deleteId.get()) == 4:
        cursor.execute('SELECT card_id FROM clients WHERE card_id=?', (str(deleteId.get()),))
        result = cursor.fetchone()
        if result:
            confirmDeleteOne = messagebox.askquestion("Potvrzen??",
                                                      "Opravdu chce?? smazat u??ivatele s ID " + deleteId.get() + "?")
            if confirmDeleteOne == "yes":
                cursor.execute('DELETE FROM clients WHERE card_id=?', (str(deleteId.get()),))
                connection.commit()
                print("User with ID " + deleteId.get() + " has been deleted from database!")
                print("Database successfully saved.")
                print("")
                database.printCurrentClients()
                refreshDeleteButton()
                if not currentClientsArray:
                    messagebox.askquestion("Smaz??no!", "??sp????n?? jsi smazal u??ivatele s ID " + deleteId.get() + ".")
                    deleteUsersWindow.withdraw()
                    refreshDeleteButton()
                else:
                    confirmDeleteOneAfter = messagebox.askquestion("Smaz??no!",
                                                                   "??sp????n?? jsi smazal u??ivatele s ID " + deleteId.get() + ". Chce?? smazat dal????ho u??ivatele?")
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
            messagebox.showerror('Chyba!', "U??ivatel s ID " + deleteId.get() + " nebyl nalezen!")
            deleteUsersWindow.after(1, lambda: deleteUsersWindow.focus_force())
            deleteUsersInput.delete(0, 'end')
    else:
        messagebox.showwarning('Chyba!', "ID karty mus?? m??t 4 ????sla.")
        deleteUsersWindow.after(1, lambda: deleteUsersWindow.focus_force())
        deleteUsersInput.delete(0, 'end')


def deleteAllUsers():
    deleteAllUsersConfirm = askstring('Opravdu?',
                                      'Pokud chce?? smazat V??ECHNY u??ivatele napi?? do r??me??ku pod tento text slovo ANO')
    if deleteAllUsersConfirm == "ANO":
        cursor.execute('DELETE FROM clients')
        connection.commit()
        print("ALL users have been deleted!")
        print("Database successfully saved.")
        print("")
        deleteUsersWindow.withdraw()
        messagebox.showinfo("Smaz??no!", "V??ichni u??ivatel?? byli ??sp????n?? smaz??ni!")
        refreshDeleteButton()
    else:
        messagebox.showwarning("Chyba!", "Pokud chce?? smazat V??ECHNY u??ivatele mus???? napsat ANO.")
        deleteUsersWindow.after(1, lambda: deleteUsersWindow.focus_force())


def runDashboard(id):
    global dashboardWindow
    global clientBalance
    global clientId

    dashboardWindow.update()
    dashboardWindow.deiconify()
    dashboardWindow.geometry("550x255")
    dashboardWindow.resizable(False, False)

    cursor.execute("SELECT balance FROM clients WHERE card_id=?", (id,))
    balanceFirst = str(cursor.fetchone())
    characters_to_remove = "(),"
    pattern = "[" + characters_to_remove + "]"
    balance = re.sub(pattern, "", balanceFirst)

    clientBalance = int(re.sub(pattern, "", balanceFirst))
    clientId = int(id)

    dashboardTitle.config(text="V??tej u??ivateli " + id + "!\nStav ????tu: " + str(balance) + " K??")
    dashboardWindow.title("Dashboard (" + id + ")")


def insertMoney():
    global dashboardInsertWindow
    global insertValue

    dashboardInsertWindow.update()
    dashboardInsertWindow.deiconify()
    dashboardInsertWindow.title("Vlo??en?? pen??z")
    dashboardInsertWindow.geometry("250x170")
    dashboardInsertWindow.resizable(False, False)
    dashboardInsertWindowInput.delete(0, "end")


def insertMoneyConfirm():
    global insertValue
    global id

    if insertValue.get() != 0 and str.isdigit(insertValue.get()):
        if messagebox.askquestion("Vlo??it tuto ????stku?",
                                  "Opravdu chce?? vlo??it " + str(insertValue.get()) + " K?? na ????et " + str(
                                          id.get()) + "?") == "yes":

            cursor.execute("UPDATE clients SET balance=? WHERE card_id=?", (str(insertValue.get()), str(id.get())))
            print("Successfully changed balance of ID " + id.get())
            print("")
            database.printCurrentClients()

            dashboardInsertWindow.withdraw()
            dashboardWindow.withdraw()
            runDashboard(id.get())
            dashboardWindow.after(1, lambda: dashboardWindow.focus_force())

            messagebox.showinfo("Hotovo!",
                                "Bylo vlo??eno " + str(insertValue.get()) + " K?? na ????et " + str(id.get()) + "!")
            dashboardWindow.after(1, lambda: dashboardWindow.focus_force())
        else:
            dashboardInsertWindow.after(1, lambda: dashboardInsertWindow.focus_force())

    else:
        messagebox.showwarning('Chyba!', "Mus???? zadat ????slo!")


def withdrawMoney():
    global dashboardWithdrawWindow
    global withdrawValue

    dashboardWithdrawWindow.update()
    dashboardWithdrawWindow.deiconify()
    dashboardWithdrawWindow.title("V??b??r pen??z")
    dashboardWithdrawWindow.geometry("250x170")
    dashboardWithdrawWindow.resizable(False, False)
    dashboardWithdrawWindowInput.delete(0, "end")


def withdrawMoneyConfirm():
    global withdrawValue
    global id
    global clientBalance

    if withdrawValue.get() != 0 and str.isdigit(withdrawValue.get()):
        if int(withdrawValue.get()) < clientBalance:
            if messagebox.askquestion("Vybrat tuto ????stku?",
                                      "Opravdu chce?? vybrat " + str(withdrawValue.get()) + " K?? z ????tu " + str(
                                              id.get()) + "?") == "yes":
                newClientBalance = clientBalance - int(withdrawValue.get())

                cursor.execute("UPDATE clients SET balance=? WHERE card_id=?", (str(newClientBalance), str(id.get())))
                print("Successfully changed balance of ID " + id.get())
                print("")
                database.printCurrentClients()

                dashboardWithdrawWindow.withdraw()
                dashboardWindow.withdraw()
                runDashboard(id.get())
                dashboardWindow.after(1, lambda: dashboardWindow.focus_force())

                messagebox.showinfo("Hotovo!",
                                    "Bylo vybr??no " + str(withdrawValue.get()) + " K?? z ????tu " + str(id.get()) + "!")
                dashboardWindow.after(1, lambda: dashboardWindow.focus_force())
            else:
                dashboardWithdrawWindow.after(1, lambda: dashboardWithdrawWindow.focus_force())
        else:
            messagebox.showwarning('Chyba!', "Na ????tu " + str(id.get()) + " nen?? k dispozici tolik pen??z!")
            dashboardWithdrawWindow.after(1, lambda: dashboardWithdrawWindow.focus_force())
            dashboardWithdrawWindowInput.delete(0, "end")
    else:
        messagebox.showwarning('Chyba!', "Mus???? zadat ????slo!")
        dashboardWithdrawWindow.after(1, lambda: dashboardWithdrawWindow.focus_force())
        dashboardWithdrawWindowInput.delete(0, "end")

def logoutUser():
    global id
    print("User " + id.get() + " logged out! Cleared cache.")
    dashboardInsertWindow.withdraw()
    dashboardWithdrawWindow.withdraw()
    dashboardWindow.withdraw()
    return

def sendMoney():
    global dashboardSendWindow
    global sendValue

    dashboardSendValueWindow.update()
    dashboardSendValueWindow.deiconify()
    dashboardSendValueWindow.title("P??evod pen??z - ????stka")
    dashboardSendValueWindow.geometry("300x170")
    dashboardSendValueWindow.resizable(False, False)
    dashboardSendValueWindowInput.delete(0, "end")

def sendMoneyConfirm():
    global sendValue
    global id
    global clientBalance

    if sendValue.get() != 0 and str.isdigit(sendValue.get()):
        if int(sendValue.get()) < clientBalance:
        	dashboardSendValueWindow.withdraw()
        	sendMoneyId()
        else:
            messagebox.showwarning('Chyba!', "Na ????tu " + str(id.get()) + " nen?? k dispozici tolik pen??z!")
            dashboardSendValueWindow.after(1, lambda: dashboardSendValueWindow.focus_force())
            dashboardSendValueWindowInput.delete(0, "end")
    else:
        messagebox.showwarning('Chyba!', "Mus???? zadat ????slo!")
        dashboardSendValueWindow.after(1, lambda: dashboardSendValueWindow.focus_force())
        dashboardSendValueWindowInput.delete(0, "end")

def sendMoneyId():
    global sendValue
    global id
    global sendId

    dashboardSendIdWindow.update()
    dashboardSendIdWindow.deiconify()
    dashboardSendIdWindow.title("P??evod pen??z - ID")
    dashboardSendIdWindow.geometry("300x170")
    dashboardSendIdWindow.resizable(False, False)
    dashboardSendIdWindowInput.delete(0, "end")

def sendMoneyIdConfirm():
	if sendId.get() != 0 and str.isdigit(sendId.get()) and len(sendId.get()) == 4 and sendId.get() != id.get():
		cursor.execute('SELECT card_id FROM clients WHERE card_id=?', (str(sendId.get()),))
		result = cursor.fetchone()

		if result:
			if (messagebox.askquestion("Potvrzen??", "Opravdu chce?? poslat " + str(sendValue.get()) + " K?? na ????et " + str(sendId.get()) + "?") == "yes"):
					
				cursor.execute("SELECT balance FROM clients WHERE card_id=?", (sendId.get(),))
				balanceFirstSecond = str(cursor.fetchone())
				characters_to_remove = "(),"
				pattern = "[" + characters_to_remove + "]"
				balance = re.sub(pattern, "", balanceFirstSecond)

				clientBalanceSecond = int(re.sub(pattern, "", balanceFirstSecond))

				newClientBalanceFirst = clientBalance - int(sendValue.get())
				newClientBalanceSecond = clientBalanceSecond + int(sendValue.get())

				cursor.execute("UPDATE clients SET balance=? WHERE card_id=?", (str(newClientBalanceFirst), str(id.get())))
				cursor.execute("UPDATE clients SET balance=? WHERE card_id=?", (str(newClientBalanceSecond), str(sendId.get())))

				print("Successfully changed balance of ID " + str(id.get()) + " and ID " + str(sendId.get()))
				print("")
				database.printCurrentClients()

				dashboardSendIdWindow.withdraw()
				messagebox.showinfo("Hotovo!", "Poslal jsi " + sendValue.get() + " K?? na ????et " + sendId.get() + "!")
			else:
				dashboardSendIdWindow.after(1, lambda: dashboardSendIdWindow.focus_force())
		else:
			messagebox.showwarning('Chyba!', "ID ????tu nebylo v datab??zi nalezeno!")
			dashboardSendIdWindow.after(1, lambda: dashboardSendIdWindow.focus_force())
			dashboardSendIdWindowInput.delete(0, 'end')
	else:
		messagebox.showwarning('Chyba!', "Bylo zad??no neplatn?? ID!")
		dashboardSendIdWindow.after(1, lambda: dashboardSendIdWindow.focus_force())
		dashboardSendIdWindowInput.delete(0, 'end')

# ------------------------------- WIDGETS --------------------------------

title = ttk.Label(root, text="ATM - v" + version.get(), font=("Poppins Bold", 25), background="black",
                  foreground="white")
title.pack()

secondMain = tk.Frame(root, background="black")
secondMain.pack()

insertCardButton = tk.Button(secondMain, text="Vlo??it Kartu", font=("Poppins Bold", 15), command=insertCard, bg="green",
                             fg="black")
insertCardButton.pack(padx=10, side=tk.LEFT)

registerButton = tk.Button(secondMain, text="Registrovat U??ivatele", font=("Poppins Bold", 15), command=registerUser,
                           bg="aqua", fg="black")
registerButton.pack(padx=10, side=tk.LEFT)

deleteUserButton = tk.Button(secondMain, text="Smazat U??ivatele", font=("Poppins Bold", 15), command=deleteUsers,
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

writeIdWindowTitle = tk.Label(writeIdWindow, fg="white", bg="black", text="Zadej pros??m sv?? ID karty.",
                              font=("Poppins bold", 15))
writeIdWindowTitle.pack()

writeIdWindowInput = tk.Entry(writeIdWindow, fg="white", bg="black", textvariable=id, insertbackground="white",
                              justify=tk.CENTER, font=("Poppins bold", 12))
writeIdWindowInput.pack()

writeIdWindowButton = tk.Button(writeIdWindow, text="Potvrdit!", background="green", font=("Poppins Bold", 14),
                                command=insertCardConfirm)
writeIdWindowButton.pack(pady=10)

writePinWindowTitle = tk.Label(writePinWindow, fg="white", bg="black", text="Zadej sv??j PIN.",
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

registerWindowTitle = tk.Label(registerWindow, fg="white", bg="black", text="Zalo??en?? ????tu", font=("Poppins bold", 20))
registerWindowTitle.grid(row=1, column=2)

registerWindowInputNameTitle = tk.Label(registerWindow, fg="white", bg="black", text="Jm??no", font=("Poppins bold", 12))
registerWindowInputNameTitle.grid(row=2, padx=8)

registerWindowInputName = tk.Entry(registerWindow, fg="white", bg="black", textvariable=registerName,
                                   insertbackground="white", justify=tk.CENTER, font=("Poppins bold", 12),
                                   disabledbackground="black", disabledforeground="gray")
registerWindowInputName.grid(row=3, padx=8)

registerWindowInputSurnameTitle = tk.Label(registerWindow, fg="white", bg="black", text="P????jmen??",
                                           font=("Poppins bold", 12))
registerWindowInputSurnameTitle.grid(row=4, padx=8)

registerWindowInputSurname = tk.Entry(registerWindow, fg="white", bg="black", textvariable=registerSurname,
                                      insertbackground="white", justify=tk.CENTER, font=("Poppins bold", 12),
                                      disabledbackground="black", disabledforeground="gray")
registerWindowInputSurname.grid(row=5, padx=8)

registerWindowInputIdTitle = tk.Label(registerWindow, fg="white", bg="black", text="ID", font=("Poppins bold", 12))
registerWindowInputIdTitle.grid(row=2, column=3, padx=8)

registerWindowInputId = tk.Entry(registerWindow, fg="white", bg="black", textvariable=registerId,
                                 insertbackground="white", justify=tk.CENTER, font=("Poppins bold", 12),
                                 disabledbackground="black", disabledforeground="gray")
registerWindowInputId.grid(row=3, column=3, padx=8)

registerWindowInputPinTitle = tk.Label(registerWindow, fg="white", bg="black", text="PIN", font=("Poppins bold", 12))
registerWindowInputPinTitle.grid(row=4, column=3, padx=8)

registerWindowInputPin = tk.Entry(registerWindow, fg="white", bg="black", textvariable=registerPin,
                                  insertbackground="white", justify=tk.CENTER, font=("Poppins bold", 12),
                                  disabledbackground="black", disabledforeground="gray")
registerWindowInputPin.grid(row=5, column=3, padx=8)


registerWindowButton = tk.Button(registerWindow, text="Registrovat!", background="green", font=("Poppins Bold", 14),
                                 command=registerUserConfirm)
registerWindowButton.grid(row=6, pady=10, column=2)

deleteUsersTitle = tk.Label(deleteUsersWindow, fg="white", bg="black", text="Zadej ID u??ivatele.",
                            font=("Poppins bold", 15))
deleteUsersTitle.pack()

deleteUsersInput = tk.Entry(deleteUsersWindow, fg="white", bg="black", textvariable=deleteId, insertbackground="white",
                            justify=tk.CENTER, font=("Poppins bold", 12))
deleteUsersInput.pack()

deleteUsersButton = tk.Button(deleteUsersWindow, text="Smazat u??ivatele", background="green", font=("Poppins Bold", 10),
                              command=deleteOneUser)
deleteUsersButton.pack(pady=10)

deleteUsersTitle = tk.Label(deleteUsersWindow, fg="white", bg="black", text="nebo", font=("Poppins bold", 15))
deleteUsersTitle.pack()

deleteUsersButton = tk.Button(deleteUsersWindow, text="Smazat V??ECHNY u??ivatele", background="green",
                              font=("Poppins Bold", 10), command=deleteAllUsers)
deleteUsersButton.pack(pady=10)

dashboardTitle = tk.Label(dashboardWindow, fg="white", bg="black", text=".", font=("Poppins bold", 20))
dashboardTitle.pack()

secondDashboard = tk.Frame(dashboardWindow, background="black")
secondDashboard.pack()

dashboardButtonInsertMoney = tk.Button(secondDashboard, text="Vlo??it pen??ze", background="green",
                                       font=("Poppins Bold", 15), command=insertMoney)
dashboardButtonInsertMoney.pack(pady=10, side=tk.LEFT)

dashboardButtonWithdrawMoney = tk.Button(secondDashboard, text="Vybrat pen??ze", background="green",
                                         font=("Poppins Bold", 15), command=withdrawMoney)
dashboardButtonWithdrawMoney.pack(pady=10, side=tk.LEFT, padx=20)

dashboardButtonSendMoney = tk.Button(secondDashboard, text="Poslat pen??ze", background="green",
                                         font=("Poppins Bold", 15), command=sendMoney)
dashboardButtonSendMoney.pack(pady=10, side=tk.LEFT)

dashboardButtonLogout = tk.Button(dashboardWindow, text="Odhl??sit", background="orange",
                                  font=("Poppins Bold", 12), command=logoutUser)
dashboardButtonLogout.pack(pady=10)

dashboardInsertWindowTitle = tk.Label(dashboardInsertWindow, fg="white", bg="black", text="Zadej ????stku.",
                                      font=("Poppins bold", 15))
dashboardInsertWindowTitle.pack()

dashboardInsertWindowInput = tk.Entry(dashboardInsertWindow, fg="white", bg="black", textvariable=insertValue,
                                      insertbackground="white", justify=tk.CENTER, font=("Poppins bold", 12))
dashboardInsertWindowInput.pack()

dashboardInsertWindowButton = tk.Button(dashboardInsertWindow, text="Potvrdit!", background="green",
                                        font=("Poppins Bold", 14), command=insertMoneyConfirm)
dashboardInsertWindowButton.pack(pady=10)

dashboardWithdrawWindowTitle = tk.Label(dashboardWithdrawWindow, fg="white", bg="black", text="Zadej ????stku.",
                                        font=("Poppins bold", 15))
dashboardWithdrawWindowTitle.pack()

dashboardWithdrawWindowInput = tk.Entry(dashboardWithdrawWindow, fg="white", bg="black", textvariable=withdrawValue,
                                        insertbackground="white", justify=tk.CENTER, font=("Poppins bold", 12))
dashboardWithdrawWindowInput.pack()

dashboardWithdrawWindowButton = tk.Button(dashboardWithdrawWindow, text="Potvrdit!", background="green",
                                          font=("Poppins Bold", 14), command=withdrawMoneyConfirm)
dashboardWithdrawWindowButton.pack(pady=10)


dashboardSendValueWindowTitle = tk.Label(dashboardSendValueWindow, fg="white", bg="black", text="Zadej ????stku.",
                                        font=("Poppins bold", 15))
dashboardSendValueWindowTitle.pack()

dashboardSendValueWindowInput = tk.Entry(dashboardSendValueWindow, fg="white", bg="black", textvariable=sendValue,
                                        insertbackground="white", justify=tk.CENTER, font=("Poppins bold", 12))
dashboardSendValueWindowInput.pack()

dashboardSendValueWindowButton = tk.Button(dashboardSendValueWindow, text="Potvrdit!", background="green",
                                          font=("Poppins Bold", 14), command=sendMoneyConfirm)
dashboardSendValueWindowButton.pack(pady=10)


dashboardSendIdWindowTitle = tk.Label(dashboardSendIdWindow, fg="white", bg="black", text="Zadej ID, kam \nchce?? pen??ze poslat.",
                                        font=("Poppins bold", 15))
dashboardSendIdWindowTitle.pack()

dashboardSendIdWindowInput = tk.Entry(dashboardSendIdWindow, fg="white", bg="black", textvariable=sendId,
                                        insertbackground="white", justify=tk.CENTER, font=("Poppins bold", 12))
dashboardSendIdWindowInput.pack()

dashboardSendIdWindowButton = tk.Button(dashboardSendIdWindow, text="Potvrdit!", background="green",
                                          font=("Poppins Bold", 14), command=sendMoneyIdConfirm)
dashboardSendIdWindowButton.pack(pady=10)

# ------------------------------- END THINGS --------------------------------

# Run tkinter
root.mainloop()

# Close database
connection.commit()
cursor.close()