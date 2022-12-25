from tkinter.ttk import Combobox
import tkinter.messagebox as MessageBox
from tkinter import *
from tkinter import ttk
import numpy as np
from connexion import *
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

db = Dbconnect()


# -----------------------Statistics des commande----------------------------------------------
class IntrfStatis(Frame):
    def __init__(self, window3, val, **kwargs):
        Frame.__init__(self, window3, width=2768, height=2576, **kwargs)
        self.plot2 = None
        self.canvas = None
        self.plot1 = None
        self.pack(fill=BOTH);
        self.nbEmp = val

        # all employees
        db.dbcursor.execute("SELECT Nom FROM `employés")
        employess = db.dbcursor.fetchall()

        # spesfic employee
        db.dbcursor.execute("select Nom From employés Where NEmployé = %s", self.nbEmp)
        employe = db.dbcursor.fetchall()

        self.Emp = Combobox(self, values=employess)
        self.Emp.set(employe)
        self.Emp.pack(side=TOP)

        self.maatCanvaLeft()
        self.Emp.bind("<<ComboboxSelected>>", lambda event: self.changHist())

    def changHist(self):
        # Retrieve the data for the new plot based on the combobox value
        db.dbcursor.execute(f"SELECT YEAR(c.DateCommande),SUM(dt.PrixUnitaire * dt.Quantité - 'dt.Remise (%)') as total_MT \
            from employés e LEFT JOIN commandes c on e.NEmployé = c.NEmployé \
            LEFT JOIN détailscommandes dt on c.NCommande=dt.NCommande \
            Where e.Nom = '{self.Emp.get()} ' GROUP BY e.Nom, YEAR(c.DateCommande)")
        res = db.dbcursor.fetchall()
        data = np.array(res)
        annee = data[:, 0]
        sells = data[:, 1]

        db.dbcursor.execute(f"SELECT YEAR(c.DateCommande), (c.DateEnvoi - c.ALivrerAvant  ) as retard FROM commandes as c \
                                    INNER JOIN employés as e ON (c.NEmployé = e.NEmployé)\
                                    Where e.Nom = '{self.Emp.get()} '  and (c.DateEnvoi - c.ALivrerAvant ) > 0  GROUP \
                                    BY e.Nom, YEAR(c.DateCommande)")

        res = db.dbcursor.fetchall()
        data2 = np.array(res)
        annee2 = data2[:, 0]
        sells2 = data2[:, 1]

        # Update the plot with the new data
        self.plot1.clear()  # Clear the old plot
        self.plot2.clear()  # Clear the old plot
        self.plot1.bar(annee, sells)  # Generate the new plot
        self.plot2.bar(annee2, sells2)  # Generate the new plot
        self.plot1.set_xlabel('annes')
        self.plot1.set_ylabel('montant totale')
        self.plot1.set_title('Total MT Commande par annee')

        self.plot2.set_title('Retard commande par anne')
        self.plot2.set_xlabel('annes')
        self.plot2.set_ylabel('days')

        self.canvas.draw()  # Redraw the canvas to show the updated plot

    def maatCanvaLeft(self):
        fig = Figure(figsize=(5, 5), dpi=100)
        # self.plot1 = fig.add_subplot(111)
        self.plot1 = fig.add_subplot(121)
        self.plot2 = fig.add_subplot(122)
        db.dbcursor.execute(f"SELECT YEAR(c.DateCommande),SUM(dt.PrixUnitaire * dt.Quantité - 'dt.Remise (%)') as total_MT \
            from employés e LEFT JOIN commandes c on e.NEmployé = c.NEmployé \
            LEFT JOIN détailscommandes dt on c.NCommande=dt.NCommande \
            Where e.Nom = '{self.Emp.get()} ' GROUP BY e.Nom, YEAR(c.DateCommande)")

        res = db.dbcursor.fetchall()
        data = np.array(res)
        annee = data[:, 0]
        sells = data[:, 1]

        db.dbcursor.execute(f"SELECT YEAR(c.DateCommande), (c.DateEnvoi - c.ALivrerAvant  ) as retard FROM commandes as c \
                                            INNER JOIN employés as e ON (c.NEmployé = e.NEmployé)\
                                            Where e.Nom = '{self.Emp.get()} '  and (c.DateEnvoi - c.ALivrerAvant ) > 0  GROUP \
                                            BY e.Nom, YEAR(c.DateCommande)")

        res = db.dbcursor.fetchall()
        data2 = np.array(res)
        annee2 = data2[:, 0]
        sells2 = data2[:, 1]

        self.plot1.bar(annee, sells)
        self.plot2.bar(annee2, sells2)

        plt.subplots_adjust(left=0.6, wspace=0.8, hspace=0.4)
        self.plot1.set_xlabel('annes')
        self.plot1.set_ylabel('montant totale')
        self.plot1.set_title('Total MT Commande par annee')

        self.plot2.set_title('Retard commande par anne')
        self.plot2.set_xlabel('annes')
        self.plot2.set_ylabel('days')

        self.canvas = FigureCanvasTkAgg(fig, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=LEFT, padx=(100, 10), pady=20)
        self.canvas.get_tk_widget().config(height=470, width=760)


# -----------------------Consultation des Commande----------------------------------------------
class IntrfCmd(Frame):
    def __init__(self, window, val, **kwargs):
        Frame.__init__(self, window, width=2768, height=2576, **kwargs)
        self.pack(fill=BOTH);
        self.nbEmp = val

        """ ---first frame ---"""
        InfoCammande = Frame(self, bd=1, relief=SOLID, pady=4, padx=4)
        l0 = Label(InfoCammande, text="Infos Commandes")
        l0.grid(row=1, column=2)

        l1 = Label(InfoCammande, text="NCommande")
        l1.grid(row=2, column=1)

        # le numéro de commande
        self.nbrCommande = self.cammands()[0, 0]

        self.NCommande = Combobox(InfoCammande, values=list(self.cammands()[:, 0]), width=37)
        self.NCommande.grid(row=2, column=2, padx=(10, 52), pady=(5, 0))
        self.NCommande.set(self.cammands()[0, 0])

        l2 = Label(InfoCammande, text="DateCommande")
        l2.grid(row=3, column=1)
        self.dateCmd = StringVar()
        DateCommande = Entry(InfoCammande, width=40, textvariable=self.dateCmd)
        self.dateCmd.set(self.cammands()[0, 3])
        DateCommande.grid(row=3, column=2, padx=(10, 52), pady=(5, 0))

        l3 = Label(InfoCammande, text="AlivrerAvant")
        l3.grid(row=4, column=1)
        self.dateAvant = StringVar()
        AlivrerAvant = Entry(InfoCammande, width=40, textvariable=self.dateAvant)
        self.dateAvant.set(self.cammands()[0, 4])
        AlivrerAvant.grid(row=4, column=2, padx=(10, 52), pady=(5, 0))

        l4 = Label(InfoCammande, text="DateEnvoi")
        l4.grid(row=5, column=1)
        self.date_Envoi = StringVar()
        DateEnvoi = Entry(InfoCammande, width=40, textvariable=self.date_Envoi)
        self.date_Envoi.set(self.cammands()[0, 5])
        DateEnvoi.grid(row=5, column=2, padx=(10, 52), pady=(5, 0))

        l5 = Label(InfoCammande, text="CodeClient")
        l5.grid(row=6, column=1)
        self.codeCl = StringVar()
        CodeClient = Entry(InfoCammande, width=40, textvariable=self.codeCl)
        self.codeCl.set(self.cammands()[0, 1])
        CodeClient.grid(row=6, column=2, padx=(10, 52), pady=(5, 0))

        l6 = Label(InfoCammande, text="Socité")
        l6.grid(row=7, column=1, pady=(0, 40))
        db.dbcursor.execute("select Société from clients where clients.CodeClient =  %s", self.codeCl.get())
        company = db.dbcursor.fetchall()
        self.var_company = StringVar()
        Socite = Entry(InfoCammande, width=40, textvariable=self.var_company)
        self.var_company.set(company[0][0])
        Socite.grid(row=7, column=2, padx=(10, 52), pady=(5, 40))

        InfoCammande.pack(pady=(20, 20), padx=12)

        """ ---second frame ---"""
        DetailCommand = Frame(self, bd=1, relief=SOLID, pady=1, padx=4)

        self.my_tree = ttk.Treeview(DetailCommand, height=4)
        self.my_tree['columns'] = ('nomProduit', 'QtCom')
        self.my_tree.column('#0', width=100, minwidth=25)
        self.my_tree.column('nomProduit', width=180, minwidth=25)
        self.my_tree.column('QtCom', width=100, minwidth=25)

        self.my_tree.heading('#0', text='Réf produit')
        self.my_tree.heading('nomProduit', text='Nom du produit')
        self.my_tree.heading('QtCom', text='Qt Com')
        self.my_tree.grid(row=3, columnspan=4, pady=23)

        sbar = ttk.Scrollbar(self, orient='vertical', command=self.my_tree.yview)
        sbar.pack(side=RIGHT, fill=Y)
        self.my_tree.configure(yscroll=sbar.set)

        db.dbcursor.execute("SELECT produits.RéfProduit , produits.NomProduit ,  détailscommandes.Quantité "
                            "FROM produits INNER JOIN détailscommandes ON produits.RéfProduit = "
                            "détailscommandes.RéfProduit Where détailscommandes.NCommande = %s", self.nbrCommande)

        i = 0
        for ele in db.dbcursor.fetchall():
            self.my_tree.insert(parent='', index='end', text=ele[0], iid=i, values=(ele[1], ele[2]))
            i += 1

        DetailCommand.pack(padx=(10, 0))

        self.NCommande.bind("<<ComboboxSelected>>", lambda event: self.changeStatus())

    def changeStatus(self):
        value = self.NCommande.get()
        db.dbcursor.execute("select cmd.NCommande ,cmd.DateCommande , cmd.ALivrerAvant , cmd.DateEnvoi , "
                            "cmd.CodeClient ,clt.Société from commandes as cmd INNER JOIN clients as clt ON "
                            "cmd.CodeClient = clt.CodeClient where cmd.NCommande = %s", value)
        res = db.dbcursor.fetchall()
        self.dateCmd.set(res[0][1])
        self.dateAvant.set(res[0][2])
        self.date_Envoi.set(res[0][3])
        self.codeCl.set(res[0][4])
        self.var_company.set(res[0][5])

        db.dbcursor.execute("SELECT produits.RéfProduit , produits.NomProduit ,  détailscommandes.Quantité "
                            "FROM produits INNER JOIN détailscommandes ON produits.RéfProduit = "
                            "détailscommandes.RéfProduit Where détailscommandes.NCommande = %s", value)

        res2 = db.dbcursor.fetchall()
        # clear data from treeview
        self.my_tree.delete(*self.my_tree.get_children())

        for i, ele in enumerate(res2):
            self.my_tree.insert(parent='', index='end', text=ele[0], iid=i, values=(ele[1], ele[2]))

    def cammands(self):
        db.dbcursor.execute("select * from commandes Where NEmployé = %s", self.nbEmp)
        results = db.dbcursor.fetchall()
        A = np.array(results)
        return A


# ----------------------------------------------------------------------------------------
class Interface(Frame):
    def __init__(self, fenetre, **kwargs):
        Frame.__init__(self, fenetre, width=2768, height=2576, **kwargs)
        self.pack(fill=BOTH);

        # create a notebook
        notebook = ttk.Notebook(self)
        notebook.pack(pady=10, expand=True)

        # create frames
        frame1 = ttk.Frame(notebook, width=360, height=160)
        frame2 = ttk.Frame(notebook, width=360, height=160)

        """ ---First frame ---"""
        # application des valeur
        self.nb = 0
        self.result = []
        self.result = self.employes()

        Nemploye = Label(frame1, text='N° employé')
        Nemploye.grid(row=2, column=1, pady=6, padx=6)
        self.entry_text1 = StringVar()
        inmput1 = Entry(frame1, width=40, textvariable=self.entry_text1)
        self.entry_text1.set(self.result[self.nb][0])
        inmput1.grid(row=2, column=2, pady=6, padx=6)

        Nom = Label(frame1, text='Nom')
        Nom.grid(row=3, column=1, pady=6, padx=6)
        self.entry_text2 = StringVar()
        inmput2 = Entry(frame1, width=40, textvariable=self.entry_text2)
        self.entry_text2.set(self.result[self.nb][1])
        inmput2.grid(row=3, column=2, pady=6, padx=6)

        Prenom = Label(frame1, text='Prenom')
        Prenom.grid(row=4, column=1, pady=6, padx=6)
        self.entry_text3 = StringVar()
        inmput3 = Entry(frame1, width=40, textvariable=self.entry_text3)
        self.entry_text3.set(self.result[self.nb][2])
        inmput3.grid(row=4, column=2, pady=6, padx=6)

        fonction = Label(frame1, text='Fonction')
        fonction.grid(row=5, column=1, pady=6, padx=6)
        self.entry_text4 = StringVar()
        inmput4 = Entry(frame1, width=40, textvariable=self.entry_text4)
        self.entry_text4.set(self.result[self.nb][3])
        inmput4.grid(row=5, column=2, pady=6, padx=6)

        frame1.pack(fill='both', expand=True)
        frame2.pack(fill='both', expand=True)

        notebook.add(frame1, text='Infos socitété')
        notebook.add(frame2, text='Infos personnelles')

        # Frame Button 1
        ButtonFrame = Frame(self)

        # Exit Button
        Quitter = Button(ButtonFrame, text='Quitter', width=10, bg='#33adff', fg='white', command=self.quit)
        Quitter.grid(row=0, column=4)

        # Pagination
        btn1 = Button(ButtonFrame, text="|<", bg='#ffcccc', command=self.first)
        btn1.grid(row=0, column=0, padx=(0, 10))

        btn2 = Button(ButtonFrame, text="<", bg='#ffcccc', command=self.previous)
        btn2.grid(row=0, column=1, padx=10)

        btn3 = Button(ButtonFrame, text=">", bg='#ffcccc', command=self.next)
        btn3.grid(row=0, column=2, padx=10)

        btn4 = Button(ButtonFrame, text=">|", bg='#ffcccc', command=self.last)
        btn4.grid(row=0, column=3, padx=(10, 40))

        ButtonFrame.pack()

        # Frame Button 2
        Button2Frame = Frame(self)

        # Consulter Commande
        consulter = Button(Button2Frame, text='consulter', width=10, command=self.consulterCmd)
        consulter.grid(row=0, column=3, pady=20, padx=30)

        # Statistique
        statistics = Button(Button2Frame, text='Statistique', width=10, command=self.statistics)
        statistics.grid(row=0, column=2, pady=20, padx=30)

        Button2Frame.pack()

    def consulterCmd(self):
        win = Toplevel(self)
        win.transient(self)
        win.title("Consulter  Commande")
        win.geometry("420x420")
        interf = IntrfCmd(win, self.entry_text1.get())

    def statistics(self):
        win3 = Toplevel(self)
        win3.transient(self)
        win3.title("Consulter  Commande")
        win3.geometry("980x500")
        interf3 = IntrfStatis(win3, self.entry_text1.get())

    def employes(self):
        db.dbcursor.execute("select NEmployé , Nom , Prénom , Fonction from employés")
        res = db.dbcursor.fetchall()
        listEmp = []
        for ele in res:
            listEmp.append(ele)
            # print(ele)
        return listEmp

    def previous(self):
        if self.nb > 0:
            self.nb = self.nb - 1
            self.entry_text1.set(self.result[self.nb][0])
            self.entry_text2.set(self.result[self.nb][1])
            self.entry_text3.set(self.result[self.nb][2])
            self.entry_text4.set(self.result[self.nb][3])
        else:
            self.nb = 0

    def next(self):
        if self.nb < len(self.result):
            self.nb = self.nb + 1
            self.entry_text1.set(self.result[self.nb][0])
            self.entry_text2.set(self.result[self.nb][1])
            self.entry_text3.set(self.result[self.nb][2])
            self.entry_text4.set(self.result[self.nb][3])
        else:
            self.nb = len(self.result) - 1

    def last(self):
        self.nb = len(self.result) - 1
        self.entry_text1.set(self.result[self.nb][0])
        self.entry_text2.set(self.result[self.nb][1])
        self.entry_text3.set(self.result[self.nb][2])
        self.entry_text4.set(self.result[self.nb][3])

    def first(self):
        self.nb = 0
        self.entry_text1.set(self.result[self.nb][0])
        self.entry_text2.set(self.result[self.nb][1])
        self.entry_text3.set(self.result[self.nb][2])
        self.entry_text4.set(self.result[self.nb][3])


# ----------------------------------------------------------------------------------------
fenetre = Tk()
fenetre.title("Ajout de nouveau personne")
fenetre.geometry("420x380")
interface = Interface(fenetre)
interface.mainloop()
# interface.destroy()
