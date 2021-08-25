# import Important modules       #####################
from PyQt5.QtWidgets import *                        #
from PyQt5.QtCore import *                           #
from PyQt5.QtGui import *
from PyQt5.uic import loadUiType
import listes                                        #
from os import path                                  #
import sys                                           #
import qdarkstyle                                    #
import decimal
from PyPDF2 import PdfFileWriter, PdfFileReader      #
import io                                            #
from reportlab.pdfgen import canvas                  #
from reportlab.lib.pagesizes import letter           #
import os                                            #                                       #
######################################################
import webbrowser as wb
from datetime import date
import datetime
#_mohamed work1#################################################################
import psycopg2
from psycopg2 import Error, connect
# import nmap , socket

class Dbconnect():
    def __init__(self, host, port, dbname):
        self._host = host
        self._port = port
        self._dbname = dbname
        self.authontification = []
        self.conn = None

    def _auth(self, username: str, password: str) -> bool:
        self.authontification.append(username)
        self.authontification.append(password)
        return True

    def connect(self):
        if len(self.authontification) == 0:
            return "postgres Auth. Error  : plaise login first  ! "
        try:
            self.conn = psycopg2.connect(
                database=self._dbname, user=self.authontification[0], sslmode='prefer', host=self._host, port=self._port, password=self.authontification[1])
            self.conn.set_session(autocommit=True)
            print(self.conn.get_dsn_parameters(), "\n")
        except(Exception, Error) as error:
            print("postgressql error : ",  error)

class getAllMatch(Dbconnect):
    def __init__(self, host, port, dbname):
        super().__init__(host, port, dbname)
        self.personneID = 0
        self.admissionID = 0

    def get_admission_search(self, data: list):
        print(data)
        cursor = self.conn.cursor()
        # prepare sql query
        select_query = "SELECT admission.cne , admission.nom , admission.note_voeux , admission.prenom , offre_formation.phase , filiere.acronyme FROM "
        join_query = " (diplome INNER JOIN filiere ON diplome.id=diplome INNER JOIN offre_formation ON filiere.id=filiere INNER JOIN admission ON offre_formation.id=offre_formation) INNER JOIN annee_universitaire ON (offre_formation.annee_universitaire = annee_universitaire.id ) "
        condition_query = " WHERE etat='pre_inscrit'"
        ndata_1 = []
        for i in range(len(data)):
            if data[i] != []:
                ndata_1.append(data[i])
                condition_query = condition_query + \
                    " AND " + data[i][0] + "='{}' ".format(data[i][1])
        query = select_query + join_query + condition_query + " ;"
        print(ndata_1, query)
        ndata_2 = []
        for i in range(len(ndata_1)):
            ndata_2.append(ndata_1[i][1])
        print(ndata_2)
        try:
            gdata = []
            cursor.execute(query, tuple(ndata_2))
            gdata = cursor.fetchall()
            print("the data  : ", gdata[0][0])
            return gdata
        except (Exception, Error) as _config_error:
            print(_config_error)
            return []

    def get_student_info(self, cne):
        print("get_student_info")
        cne = cne.upper()

        cursor = self.conn.cursor()
        first_query = """SELECT admission.cne  , admission.cin , admission.nom , admission.prenom , admission.nom_ar , admission.prenom_ar , admission.naissance_date , admission.naissance_lieu   , province.nom , admission.sexe ,  pays.libelle , \"e-mail\" , admission.telephone FROM province INNER JOIN admission ON province.id=naissance_province INNER JOIN pays ON pays.id=naissance_pays  where cne='{}'""".format(
            cne)
        try:
            cursor.execute(first_query)
            data = cursor.fetchall()
        except (Exception, Error) as _config_error:
            print(_config_error)
            return []

        first_query = "SELECT pays.libelle FROM pays INNER JOIN admission ON pays.id = nationalite where cne='{}' ; ".format(
            cne)
        try:
            cursor.execute(first_query)
            data_2 = cursor.fetchall()
        except (Exception, Error) as _config_error:
            print(_config_error)
            return []
        data = data[0]
        data_schema1 = {
            "cne": data[0],
            "cin": data[1],
            "nom": data[2],
            "prenom": data[3],
            "nom_ar": data[4],
            "prenom_ar": data[5],
            "naissance_date": data[6].strftime("%m/%d/%Y"),
            "naissance_lieu": data[7],
            "naissance_province": data[8],
            "sexe": data[9].upper(),
            "naissance_pays": data[10],
            "e-mail": data[11],
            "telephone": data[12],
            "nationalite": data_2[0][0],
        }
        cursor = self.conn.cursor()
        first_query = "SELECT admission.bac_annee , admission.bac_mention , province.nom   , serie_baccalaureat.acronyme, admission.bac_type FROM province INNER JOIN admission ON province.id=bac_province INNER JOIN serie_baccalaureat ON serie_baccalaureat.id=bac_serie WHERE cne= '{}' ; ".format(
            cne)
        try:
            cursor.execute(first_query)
            data = cursor.fetchall()
        except (Exception, Error) as _config_error:
            print(_config_error)
            return []
        data = data[0]
        data_schema2 = {
            "bac_annee": data[0],
            "bac_mention": data[1],
            "bac_province": data[2],
            "bac_serie": data[3],
            "bac_type": data[4],
        }
        print(data[4])
        for key in data_schema2:
            data_schema1[key] = data_schema2[key]
        print("bac data  : ", data_schema1)
        return data_schema1

    def get_student_info_bac(self, cne):
        cursor = self.conn.cursor()
        first_query = "SELECT admission.bac_annee , admission.bac_mention , province.nom   , serie_baccalaureat.acronyme, admission.bac_type FROM province INNER JOIN admission ON province.id=bac_province INNER JOIN serie_baccalaureat ON serie_baccalaureat.id=bac_serie WHERE cne= '{}' ; ".format(
            cne)
        try:
            cursor.execute(first_query)
            data = cursor.fetchall()
        except (Exception, Error) as _config_error:
            print(_config_error)
            return
        data = data[0]
        data_schema = {
            "bac_annee": data[0],
            "bac_mention": data[1],
            "bac_province": data[2],
            "bac_serie": data[3],
            "bac_type": data[4],
        }

    def translatenamesforper(self, data):

        ndata = {}
        ndata["cne"] = data["cne"]
        ndata["cin"] = data["cin"]
        ndata["nom"] = data["nom"]
        ndata["prenom"] = data["prenom"]
        ndata["nom_ar"] = data["nom_arab"]
        ndata["prenom_ar"] = data["prenom_arab"]
        ndata["naissance_date"] = data["date_naissance"]
        ndata["naissance_lieu"] = data["lieu_naissance"]
        ndata["naissance_lieu_ar"] = data["lieu_naissance_arab"]
        ndata["naissance_province"] = data["Province_de_naissance"]
        ndata["naissance_pays"] = data["Pays_de_naissance"]
        ndata["handicap"] = data["handicap"]
        ndata["nationalite"] = data["Nationalite"]
        ndata["csp"] = data["Categorie_socioprofessionnelle_etudiant"]
        ndata["sexe"] = data["Sexe"]
        ndata["situation_familiale"] = data["Situation_familiale"]
        ndata["photo"] = data["photo_path"]

        ndata["adresse"] = data["Adresse_de_residence_etudiant"]
        ndata["e-mail"] = data["mail_etudiant"]
        ndata["adresse_province"] = data["Province_de_residence_etudiant"]
        ndata["telephone"] = data["telephone_etudiant"]

        ndata["nom_prenom_mère"] = data["Nom_complet_mere"]
        ndata["nom_prenom_père"] = data["Nom_complet_pere"]
        ndata["csp_mère"] = data["Categorie_sociopro_mere"]
        ndata["csp_père"] = data["Categorie_sociopro_pere"]
        ndata["adresse_province_parents"] = data["Province_residence_parent"]
        ndata["adresse_pays_parents"] = data["Pays_residence_parent"]
        ndata["adresse_parents"] = data["Adresse_de_residence_parent"]
        ndata["telephone_parents"] = data["telephone_parent"]
        ndata["email_parents"] = data["mail_parent"]

        ndata["bac_type"] = data["Type_baccalaureat"]
        ndata["bac_serie"] = data["Serie_Baccalaureat"]
        ndata["bac_province"] = data["Province_Baccalaureat"]
        ndata["bac_region"] = data["Academie_Baccalaureat"]
        ndata["bac_annee"] = data["Annee_Baccalaureat"]
        ndata["bac_moyenne"] = data["Moyenne_Baccalaureat"]
        ndata["bac_mention"] = data["Mention_Baccalaureat"]
        ndata["filiere"] = data["filier_demander"]
        ndata["annee_universitaire"] = str(datetime.datetime.today().year -1) + "-" + str(datetime.datetime.today().year)
        today = date.today()
        ndata["date_inscription"] = today.strftime("%m/%d/%Y")
        ndata["numero_inscription"] = ndata["cne"] + "_" + str(ndata["annee_universitaire"] ),
        print("from trabnslate funcs  .............."  , ndata["numero_inscription"])
        a = ndata["numero_inscription"]
        ndata["numero_inscription"] = a[0]
        ndata["etat"] = "inscris"
        ndata["naissance_a_letranger"] = self.ismarocain(
            data["Pays_de_naissance"])
        ndata["email_usmba"] = data["mail_etudiant"]
        ndata["code_apogee"] = ndata["cne"] + "_" + str(ndata["annee_universitaire"] )
        for key in ndata:
            if ndata[key] == None:
                ndata[key] = ""
        return ndata

    def ismarocain(self, c):
        return c == "MAROC"

    def adddatatoetudanttb(self, data):
        print("add to etudents")
        print("add to etudiant" , data)
        cursor = self.conn.cursor()
        first_query = """SELECT id FROM admission WHERE cne='{}'""".format(data["cne"])
        try:
            cursor.execute(first_query)
            a = cursor.fetchone()
            data["admission"] = a[0]
        except (Exception, Error) as _config_error:
            print(_config_error)
            return False

        cursor = self.conn.cursor()
        first_query = """SELECT id from personne WHERE cin='{}'""".format(data["cin"])
        try:
            cursor.execute(first_query)
            a = cursor.fetchone()
            data["personne"] = a[0]
        except (Exception, Error) as _config_error:
            print(_config_error)
            return False

        columns = [
            "personne",
            "bac_serie",
            "bac_province",
            "bac_region",
            "csp_mère",
            "csp_père",
            "adresse_province_parents",
            "adresse_pays_parents",
            "admission",
            "nom_prenom_mère",
            "nom_prenom_père",
            "cne",
            "code_apogee",
            "bac_type",
            "bac_annee",
            "email_parents",
            "telephone_parents",
            "adresse_parents",
            "bac_mention",
        ]
        cursor = self.conn.cursor()
        first_query = """INSERT INTO etudiant({}) VALUES {}""".format(
            ",".join(columns), tuple([data.get(key) for key in columns]))
        try:
            cursor.execute(first_query)
        except (Exception, Error) as _config_error:
            print(_config_error)
            return False
        return True

    def adddatatopersontb(self, data):
        print("add to personne")
        print("add to personne" , data)
        cursor = self.conn.cursor()
        columns = [
            "nationalite",
            "naissance_date",
            "naissance_a_letranger",
            "naissance_province",
            "naissance_pays",
            "csp",
            "adresse_province",
            "email_usmba",
            "naissance_lieu",
            "naissance_lieu_ar",
            "adresse",
            "photo",
            "sexe",
            "telephone",
            '"e-mail"',
            "cin",
            "nom",
            "prenom",
            "nom_ar",
            "prenom_ar",
            "handicap",
            "situation_familiale",
        ]
        columns2 = [
            "nationalite",
            "naissance_date",
            "naissance_a_letranger",
            "naissance_province",
            "naissance_pays",
            "csp",
            "adresse_province",
            "email_usmba",
            "naissance_lieu",
            "naissance_lieu_ar",
            "adresse",
            "photo",
            "sexe",
            "telephone",
            "e-mail",
            "cin",
            "nom",
            "prenom",
            "nom_ar",
            "prenom_ar",
            "handicap",
            "situation_familiale",
        ]
        first_query = """INSERT INTO personne({}) VALUES {}""".format(
            ",".join(columns), tuple([data.get(key) for key in columns2]))
        try:
            cursor.execute(first_query)
        except (Exception, Error) as _config_error:
            print(_config_error)
            return False

       
        return True
    def adddatatoinscriptiontb(self , data) : 
        print("add to inscription" , data)


        
        cursor = self.conn.cursor()
        first_query = """SELECT id FROM etudiant WHERE cne='{}'""".format(data["cne"])
        try:
            cursor.execute(first_query)
            a = cursor.fetchone()
            data["etudiant"] = a[0]
        except (Exception, Error) as _config_error:
            print(_config_error)
            return False



        print("add to inscription step 1")
        cursor = self.conn.cursor()
        columns = [
            "etudiant" ,
            "admission" ,
            "filiere" ,  
            "annee_universitaire" ,
            "numero_inscription" ,
            "date_inscription" ,
            "etat"
        ]
        print([data.get(key) for key in columns])
        first_query = """INSERT INTO inscription_diplome ({}) VALUES {}""".format(
            ",".join(columns), tuple([data.get(key) for key in columns]))
        try:
            cursor.execute(first_query)
        except (Exception, Error) as _config_error:
            print(_config_error)
            return False
        print("add to inscription step 1")
        return True

    def addtodbinfo(self, data):
        data = self.translatenamesforper(data)
        print("addtodb  ..................." , data)
        # for persone table

        # get csp
        cursor = self.conn.cursor()
        first_query = "SELECT id FROM categorie_csp WHERE titre='{}'".format(
            data["csp"])
        try:
            cursor.execute(first_query)
            a = cursor.fetchone()
            data["csp"] = a[0]
        except (Exception, Error) as _config_error:
            print(_config_error)
            return False
        # get csp mere
        cursor = self.conn.cursor()
        first_query = "SELECT id FROM categorie_csp WHERE titre='{}'".format(
            data["csp_mère"])
        try:
            cursor.execute(first_query)
            a = cursor.fetchone()
            data["csp_mère"] = a[0]
        except (Exception, Error) as _config_error:
            print(_config_error)
            return False

            # get csp pere
        cursor = self.conn.cursor()
        first_query = "SELECT id FROM categorie_csp WHERE titre='{}'".format(
            data["csp_père"])
        try:
            cursor.execute(first_query)
            a = cursor.fetchone()
            data["csp_père"] = a[0]
        except (Exception, Error) as _config_error:
            print(_config_error)
            return False

        # get parents address_pys
        cursor = self.conn.cursor()
        first_query = "SELECT id FROM pays WHERE libelle='{}'".format(
            data["adresse_pays_parents"])
        try:
            cursor.execute(first_query)
            a = cursor.fetchone()
            data["adresse_pays_parents"] = a[0]
        except (Exception, Error) as _config_error:
            print(_config_error)
            return False

    # get parents naissance province
        cursor = self.conn.cursor()
        first_query = "SELECT id FROM province WHERE nom='{}'".format(
            data["naissance_province"])
        try:
            cursor.execute(first_query)
            a = cursor.fetchone()
            data["naissance_province"] = a[0]

        except (Exception, Error) as _config_error:
            print(_config_error)
            return False

# get parents add_parent pro
        cursor = self.conn.cursor()
        first_query = "SELECT id FROM province WHERE nom='{}'".format(
            data["adresse_province_parents"])
        try:
            cursor.execute(first_query)
            a = cursor.fetchone()
            data["adresse_province_parents"] = a[0]

        except (Exception, Error) as _config_error:
            print(_config_error)
            return False

# get address province
        cursor = self.conn.cursor()
        first_query = "SELECT id FROM province  WHERE nom='{}'".format(
            data["adresse_province"])
        try:
            cursor.execute(first_query)
            a = cursor.fetchone()
            data["adresse_province"] = a[0]
        except (Exception, Error) as _config_error:
            print(_config_error)
            return False

# get bac province
        cursor = self.conn.cursor()
        first_query = "SELECT id FROM province  WHERE nom='{}'".format(
            data["bac_province"])
        try:
            cursor.execute(first_query)
            a = cursor.fetchone()
            data["bac_province"] = a[0]
        except (Exception, Error) as _config_error:
            print(_config_error)
            return False

# get bac province
        cursor = self.conn.cursor()
        first_query = "SELECT id FROM region  WHERE nom='{}'".format(
            data["bac_region"])
        try:
            cursor.execute(first_query)
            a = cursor.fetchone()
            data["bac_region"] = a[0]
        except (Exception, Error) as _config_error:
            print(_config_error)
            return False

########################################################################################### problem is here
# get bac serie
        cursor = self.conn.cursor()
        first_query = "SELECT id FROM serie_baccalaureat  WHERE libelle='{}'".format(
            data["bac_serie"])
        try:
            cursor.execute(first_query)
            a = cursor.fetchone()
            data["bac_serie"] = a[0]
        except (Exception, Error) as _config_error:
            print(_config_error)
            return False

# get nationalite
        cursor = self.conn.cursor()
        first_query = "SELECT id FROM pays  WHERE libelle='{}'".format(
            data["nationalite"])
        try:
            cursor.execute(first_query)
            a = cursor.fetchone()
            data["nationalite"] = a[0]
        except (Exception, Error) as _config_error:
            print(_config_error)
            return False
# get filiere
        cursor = self.conn.cursor()
        first_query = "SELECT id FROM filiere  WHERE acronyme='{}'".format(
            data["filiere"])
        try:
            cursor.execute(first_query)
            a = cursor.fetchone()
            data["filiere"] = a[0]
        except (Exception, Error) as _config_error:
            print(_config_error)
            return False
# get naissance pays 
        cursor = self.conn.cursor()
        first_query = "SELECT id FROM pays  WHERE libelle='{}'".format(
            data["naissance_pays"])
        try:
            cursor.execute(first_query)
            a = cursor.fetchone()
            data["naissance_pays"] = a[0]
        except (Exception, Error) as _config_error:
            print(_config_error)
            return False
# get annee_universitaire
        cursor = self.conn.cursor()
        first_query = "SELECT id FROM annee_universitaire  WHERE annee='{}'".format(
            data["annee_universitaire"])
        try:
            cursor.execute(first_query)
            a = cursor.fetchone()
            data["annee_universitaire"] = a[0]
        except (Exception, Error) as _config_error:
            print(_config_error)
            return False
        self.adddatatopersontb(data)
        self.adddatatoetudanttb(data)
        self.adddatatoinscriptiontb(data)
        return 

#_zakaria_work1_#################################################################
def create_pdf(full_name, cne, cin, filiere, numero_inscrit, annee):
    # file name
    outfile_name = full_name.split(' ')
    outfile_name = outfile_name[0] + '_' + outfile_name[1]

    # draw new pdf
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFillColorRGB(0, 0, 0)
    can.setFont("Times-Roman", 12)
    can.drawString(240, 592, full_name)
    can.drawString(250, 578, cne)
    can.drawString(220, 564, cin)
    can.drawString(305, 550, filiere)
    can.drawString(160, 537, numero_inscrit)
    can.drawString(419, 537, annee)
    can.save()

    packet.seek(0)
    new_pdf = PdfFileReader(packet)
    THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
    my_file = os.path.join(THIS_FOLDER, "pdf_in.pdf")
    existing_pdf = PdfFileReader(open(my_file, "rb"))
    output = PdfFileWriter()
    # merge pdf
    page = existing_pdf.getPage(0)
    page.mergePage(new_pdf.getPage(0))
    output.addPage(page)
    cwd = os.getcwd()
    dir = os.path.join(THIS_FOLDER, "InscriptionFiles")
    if not os.path.exists(dir):
        os.mkdir(dir)
        print("Create Directory successfully")
    else:
        print("Directory already exists")
    # output pdf to the inscrption folder
    path = THIS_FOLDER + "/InscriptionFiles/" + outfile_name + ".pdf"
    outputStream = open(path, "wb")
    output.write(outputStream)
    outputStream.close()
#_theEnd_ziko_work1_#############################################################


#_Welcom_page_########################################################################
FORM_CLASS, _ = loadUiType(path.join(path.dirname(__file__), 'z_welcome.ui'))
class WelcomScreen(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(WelcomScreen, self).__init__(parent)
        QDialog.__init__(self)
        self.setupUi(self)
        self.setup()
        self.check()

    def setup(self):
        self.settings = QSettings('ESTF APPS', 'AnneeInsci')
        self.aNee = self.settings.value('annee')

    def check(self):
        self.pushButton.clicked.connect(self.gotoadmis)
        self.fiche_etud.clicked.connect(self.gotofiche1)
        self.about.clicked.connect(self.potmessage)
        self.Inscription.clicked.connect(self.InscriptioN)
        self.Exports.clicked.connect(self.ExportS)
        self.para.clicked.connect(self.gotopara)

    def gotopara(self):
        widget.setCurrentIndex(10)

    def ExportS(self):
        QMessageBox.information(self, "information",
                                "Cette option nécessite une version plus récente")

    def InscriptioN(self):
        QMessageBox.information(self, "information",
                                "Cette option nécessite une version plus récente")

    def potmessage(self):
        QMessageBox.information(self, "About",
                                "EST fes Apps Inscription version 0.5")

    def gotofiche1(self):
        widget.setCurrentIndex(11)

    def gotoadmis(self):
        widget.setCurrentIndex(1)


#_fiche_choose_########################################################################
FORM_CLASS,_ = loadUiType(path.join(path.dirname(__file__),'z_fichetudechoose.ui'))
class fich_choose(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(fich_choose,self).__init__(parent)
        QDialog.__init__(self)
        self.setupUi(self)
        self.chek()
    
    def chek(self):
        self.Retour.clicked.connect(self.gotoWelcom)
        self.nvl.clicked.connect(self.gotofiche1)
        self.consult.clicked.connect(self.InscriptioN)
        self.modif.clicked.connect(self.InscriptioN)
    
    def gotofiche1(self):
        widget.setCurrentIndex(2)

    def gotoWelcom(self):
        widget.setCurrentIndex(0)

    def InscriptioN(self):
        QMessageBox.information(self, "information",
                                "Cette option nécessite une version plus récente")

#_admi_page_##########################################################################
FORM_CLASS, _ = loadUiType(path.join(path.dirname(__file__), 'z_admis.ui'))
class admis_Screen(QDialog, FORM_CLASS, getAllMatch):
    def __init__(self, host, port, dbname, parent=None):
        super(admis_Screen, self).__init__(parent)
        QMainWindow.__init__(self)
        getAllMatch.__init__(self, host, port, dbname)
        self.setupUi(self)
        self.getanne()
        self.check()
        self.rempli()




    def getanne(self):
        pass

    
     





    def check(self):
        self.chercher.clicked.connect(self.getinfo)
        self.Retour.clicked.connect(self.okaychek)
        self.AjouterIncrit.clicked.connect(self.gotoCHek)

    def okaychek(self):
        self.labelEror.setText("")
        qm = QMessageBox
        pip = qm.question(self,'confirmation', "voulez-vous annuler !?", qm.Yes | qm.No)
        if pip == qm.Yes:
            self.gotoWelcom()

    def gotoCHek(self):
        try:
            indexRow = self.tableWidget.selectedIndexes()[0].row()
            self.DAta_Etude = self.tableInfo[indexRow][0].upper()
            # chouichou work
            self.dataEtudeGlobal = self.get_student_info(str(self.DAta_Etude))
            self.send_inforamtion_to_ficheEtudiant()
        except:
            self.labelEror.setText(
                "Erreur s'il vous plaît selectionner un élément !")

    def send_inforamtion_to_ficheEtudiant(self):
        #_sendInfo_######################################
        fich_5.cnE.setText(self.dataEtudeGlobal["cne"])
        fich_5.Nmr_Cin.setText(self.dataEtudeGlobal["cin"])
        fich_5.name.setText(self.dataEtudeGlobal["nom"])
        fich_5.Preno.setText(self.dataEtudeGlobal["prenom"])
        fich_5.nom_arabe.setText(self.dataEtudeGlobal["nom_ar"])
        fich_5.preno_arab.setText(self.dataEtudeGlobal["prenom_ar"])
        fich_5.dateNaiss.setDateTime(self.potDate())
        fich_5.lieuDeNais.setText(self.dataEtudeGlobal["naissance_lieu"])
        fich_5.Provence.addItem(self.dataEtudeGlobal["naissance_province"])
        self.molp()
        self.cheket()  # self.dataEtudeGlobal["sexe"]
        fich_5.Pays_1.addItem(self.dataEtudeGlobal["naissance_pays"])
        self.molp1()
        fich_5.Pays_2.addItem(self.dataEtudeGlobal["nationalite"])
        self.molp2()
        fich_6.Email.setText(self.dataEtudeGlobal["e-mail"])
        fich_6.telephone.setText(self.dataEtudeGlobal["telephone"])
        fich_8.annee.setText(self.dataEtudeGlobal["bac_annee"])
        fich_8.Mention.addItem(self.dataEtudeGlobal["bac_mention"])
        self.molp3()
        fich_8.provenceFich4.addItem(self.dataEtudeGlobal["bac_province"])
        self.molp4()
        fich_8.Serie.addItem(self.dataEtudeGlobal["bac_serie"])
        self.molp5()
        indexRow = self.tableWidget.selectedIndexes()[0].row()
        fich_8.filiere.addItem(self.tableInfo[indexRow][-1])
        fich_8.filiere.setCurrentText(self.tableInfo[indexRow][-1])
        self.cheketType()  # self.dataEtudeGlobal["bac_type"]
        ################################################
        self.labelEror.setText("")
        self.pip()

    def cheket(self):
        if self.dataEtudeGlobal["sexe"].upper() == "H":
            fich_5.no.setChecked(True)
        elif self.dataEtudeGlobal["sexe"].upper() == "F":
            fich_5.yes.setChecked(True)

    def cheketType(self):
        if self.dataEtudeGlobal["bac_type"].upper() == "MAROCAIN":
            fich_8.maroc.setChecked(True)
        elif self.dataEtudeGlobal["bac_type"].upper() == "MISSION":
            fich_8.miss.setChecked(True)
        elif self.dataEtudeGlobal["bac_type"].upper() == "ETRANGER":
            fich_8.etrg.setChecked(True)

    def molp5(self):
        fich_8.Serie.setCurrentText(self.dataEtudeGlobal["bac_serie"])

    def molp4(self):
        fich_8.provenceFich4.setCurrentText(
            self.dataEtudeGlobal["bac_province"])

    def molp3(self):
        fich_8.Mention.setCurrentText(self.dataEtudeGlobal["bac_mention"])

    def molp2(self):
        fich_5.Pays_2.setCurrentText(self.dataEtudeGlobal["nationalite"])

    def molp(self):
        fich_5.Provence.setCurrentText(
            self.dataEtudeGlobal["naissance_province"])

    def molp1(self):
        fich_5.Pays_1.setCurrentText(self.dataEtudeGlobal["naissance_pays"])

    def potDate(self):
        time = QDateTime(int(self.dataEtudeGlobal["naissance_date"][6:10]),
                         int(self.dataEtudeGlobal["naissance_date"][3:5]),
                         int(self.dataEtudeGlobal["naissance_date"][0:2]), 1, 1)
        return time

    def pip(self):
        qm = QMessageBox
        pip = qm.question(self, 'confirmation',
                          "voulez-vous faire une inscription ?", qm.Yes | qm.No)
        if pip == qm.Yes:
            self.gotofiche1()

    def gotofiche1(self):
        widget.setCurrentIndex(6)

    def getinfo(self):
        Annee = self.annee.text()
        if Annee == '-':
            Annee = ""
        Phase = self.phase.currentText()
        Cne = self.CNe.text()
        Diplome = self.diplome.currentText()
        Filier = self.filier.currentText()
        self.bdit = []
        if Annee != '':
            self.bdit.append(['annee', Annee])
        else:
            self.bdit.append([])
        if Phase != "-----------":
            self.bdit.append(['phase', Phase])
        else:
            self.bdit.append([])
        if Cne != '':
            self.bdit.append(['cne', Cne])
        else:
            self.bdit.append([])
        if Diplome != '-----------':
            self.bdit.append(['diplome.acronyme', Diplome])
        else:
            self.bdit.append([])
        if Filier != '-----------':
            self.bdit.append(['filiere.acronyme', Filier])
        else:
            self.bdit.append([])
        self.getinfoTable()

    def getinfoTable(self):
        self.tableInfo = []
        # get data search
        self.tableInfo = self.get_admission_search(self.bdit)
        # self.tableInfo = [('R139221224', 'rhiba', decimal.Decimal('15.500'), 'yahya', "phase 1", 'SE')]
        self.tableWidget.setRowCount(len(self.tableInfo))
        row = 0
        for etude in self.tableInfo:
            self.tableWidget.setItem(row, 0, QTableWidgetItem(etude[0]))
            self.tableWidget.setItem(row, 1, QTableWidgetItem(etude[3]))
            self.tableWidget.setItem(row, 2, QTableWidgetItem(etude[1]))
            self.tableWidget.setItem(row, 3, QTableWidgetItem(etude[5]))
            self.tableWidget.setItem(row, 4, QTableWidgetItem(str(etude[2])))
            self.tableWidget.setItem(row, 5, QTableWidgetItem(etude[4]))
            row = row+1
        if len(self.tableInfo) == 0:
            self.labelEror.setText("Not found !")
        else:
            self.labelEror.setText("")

    def rempli(self):
        self.tableWidget.setColumnWidth(5, 127)
        self.phase.addItems(listes.phase)
        self.diplome.addItems(listes.diplom)
        self.filier.addItems(listes.filere)

    def gotoWelcom(self):
        self.inite()
        self.labelEror.setText("")
        widget.setCurrentIndex(0)
        # initializé la page admission c'est t'adire supprimé tout
    
    def inite(self):
        admI.phase.setCurrentText("-----------")
        admI.diplome.setCurrentText("-----------")
        admI.filier.setCurrentText("-----------")
        admI.CNe.setText("")
        self.clearTable()
    
    def clearTable(self):
        self.tableWidget.setRowCount(0)

#_fiche_etudiant_par_admission_####################################################
#_fiche1_##################################################################################
FORM_CLASS, _ = loadUiType(path.join(path.dirname(__file__), 'z_ficheEtude1.ui'))
class fich6(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(fich6, self).__init__(parent)
        QDialog.__init__(self)
        self.setupUi(self)
        self.rempli()
        self.check()

    def rempli(self):
        self.nom_arabe.setCursorPosition(1)
        self.Pays_1.addItems(listes.pays)
        self.Handicap.addItems(listes.handi)
        self.Pays_2.addItems(listes.pays)
        self.csp.addItems(listes.csp)
        self.Provence.addItems(listes.provin)

    def check(self):
        self.yes.stateChanged.connect(self.yesChangedAction)
        self.no.stateChanged.connect(self.noChangedAction)
        self.celebat.stateChanged.connect(self.celebaTChangedAction)
        self.mari.stateChanged.connect(self.mariChangedAction)
        self.file_name = ''
        self.Import.clicked.connect(self.getImage)
        self.suivant.clicked.connect(self.sendInfo)
        self.Annuler.clicked.connect(self.annuler)

#_sendInfo_############################################################################################
    #
    def sendInfo(self):
        #
        fich_6.cNe.setText(fich_5.cnE.text())
        #
        fich_6.fname.setText(fich_5.name.text())
        #
        fich_6.lname.setText(fich_5.Preno.text())
        #
        fich_6.NmrCin.setText(fich_5.Nmr_Cin.text())
        fich_6.nomArabic.setText(fich_5.nom_arabe.text(
        ))                                             #
        fich_6.prenoArab.setText(fich_5.preno_arab.text(
        ))                                            #
        #######_transfer_picture_si_il_existe_###################################################     #
        if self.file_name != '':
            fich_6.picture.setPixmap(QPixmap(self.file_name))
            fich_6.picture.repaint()
            QApplication.processEvents()
        #########################################################################################     #
        #
        fich_7.cNe.setText(fich_5.cnE.text())
        #
        fich_7.fname.setText(fich_5.name.text())
        #
        fich_7.lname.setText(fich_5.Preno.text())
        #
        fich_7.NmrCin.setText(fich_5.Nmr_Cin.text())
        fich_7.nomArabic.setText(fich_5.nom_arabe.text(
        ))                                             #
        fich_7.prenoArab.setText(fich_5.preno_arab.text(
        ))                                            #
        #######_transfer_picture_si_il_existe_###################################################     #
        if self.file_name != '':
            fich_7.picture.setPixmap(QPixmap(self.file_name))
            fich_7.picture.repaint()
            QApplication.processEvents()
        #########################################################################################     #
        #
        fich_8.cNe.setText(fich_5.cnE.text())
        #
        fich_8.fname.setText(fich_5.name.text())
        #
        fich_8.lname.setText(fich_5.Preno.text())
        #
        fich_8.NmrCin.setText(fich_5.Nmr_Cin.text())
        fich_8.nomArabic.setText(fich_5.nom_arabe.text(
        ))                                             #
        fich_8.prenoArab.setText(fich_5.preno_arab.text(
        ))                                            #
        #######_transfer_picture_si_il_existe_###################################################     #
        if self.file_name != '':
            fich_8.picture.setPixmap(QPixmap(self.file_name))
            fich_8.picture.repaint()
            QApplication.processEvents()
        self.gotchiki()

    def gotchiki(self):
        t1 = fich_5.cnE.text()
        t2 = fich_5.name.text()
        t3 = fich_5.Preno.text()
        t4 = fich_5.Provence.currentText()
        if t4 == "-----------":
            t4 = ''
        if t1=='' or t2=='' or t3=="" or t4=='':
            self.labelEror1.setText("s'il vous plaît entrer tout les champs impotant")
        else:
            self.labelEror1.setText("")
            self.gotofich2()
#######################################################################################################
  
    def annuler(self):
        self.labelEror1.setText("")
        qm = QMessageBox
        pip = qm.question(self, 'confirmation',
                          "voulez-vous annuler  l'inscription ?", qm.Yes | qm.No)
        if pip == qm.Yes:
            self.gotowelcom()
            self.clearAllWindowInfo()

    def clearAllWindowInfo(self):
        admI.phase.setCurrentText("-----------")
        admI.diplome.setCurrentText("-----------")
        admI.filier.setCurrentText("-----------")
        admI.CNe.setText("")
        admI.tableWidget.setRowCount(0)
        ####################################
        fich_5.cnE.setText("")
        fich_5.Nmr_Cin.setText("")
        fich_5.name.setText("")
        fich_5.Preno.setText("")
        fich_5.nom_arabe.setText("")
        fich_5.preno_arab.setText("")
        fich_5.dateNaiss.setDateTime(QDateTime(2000,1,1,1,1))
        fich_5.lieuDeNais.setText('')
        fich_5.Provence.setCurrentText("-----------")
        fich_5.lieuDeNais_arab.setText("")
        fich_5.Handicap.setCurrentText("-----------")
        fich_5.csp.setCurrentText("-----------")
        fich_5.Pays_1.setCurrentText("-----------")
        fich_5.Pays_2.setCurrentText("-----------")
        fich_5.no.setChecked(False)
        fich_5.yes.setChecked(False)
        fich_5.celebat.setChecked(False)
        fich_5.mari.setChecked(False)
        if fich_5.file_name != "": ##################################################
            fich_5.picture.setPixmap(QPixmap("inconu.jpg"))
        fich_5.picture.repaint()
        QApplication.processEvents() ###############################################
        fich_6.adresss.setText("")
        fich_6.Email.setText("")
        fich_6.telephone.setText("")
        fich_6.Provence.setCurrentText("-----------")
        #######
        fich_7.nomMere.setText("")
        fich_7.nomPere.setText("")
        fich_7.adreS.setText("")
        fich_7.telephone.setText("")
        fich_7.mail.setText("")
        fich_7.categorie_socio_prof_mere.setCurrentText("-----------")
        fich_7.categorie_socio_prof_pere.setCurrentText("-----------")
        fich_7.PaYs.setCurrentText("-----------")
        fich_7.ProvenceDeResidence.setCurrentText("-----------")
        ######
        fich_8.filiere.setCurrentText("-----------")
        fich_8.Serie.setCurrentText("-----------")
        fich_8.provenceFich4.setCurrentText("-----------")
        fich_8.Academie.setCurrentText("-----------")
        fich_8.Mention.setCurrentText("-----------")
        fich_8.annee.setText("")
        fich_8.moyenne.setText("")
        fich_8.maroc.setChecked(False)
        fich_8.miss.setChecked(False)
        fich_8.etrg.setChecked(False)

    def gotowelcom(self):
        widget.setCurrentIndex(0)

    def gotoAdmission(self):
        widget.setCurrentIndex(1)

    def gotofich2(self):
        widget.setCurrentIndex(7)

    def getImage(self):
        self.file_name, _ = QFileDialog.getOpenFileName(self, 'Open Image File',
                                                        r"<Default dir>", "Image files (*.jpg *.jpeg *.png)")
        if self.file_name != "":
            self.picture.setPixmap(QPixmap(self.file_name))
        self.picture.repaint()
        QApplication.processEvents()

    def mariChangedAction(self, state):
        if (Qt.Checked == state):
            if self.celebat.isChecked():  # ""
                self.celebat.setChecked(False)

    def celebaTChangedAction(self, state):  # ""
        if (Qt.Checked == state):
            if self.mari.isChecked():
                self.mari.setChecked(False)

    def yesChangedAction(self, state):  # ""
        if (Qt.Checked == state):
            if self.no.isChecked():
                self.no.setChecked(False)

    def noChangedAction(self, state):
        if (Qt.Checked == state):  # ""
            if self.yes.isChecked():  # ""
                self.yes.setChecked(False)

#_the_end_fiche1_##########################################################################


#_fiche2_##################################################################################
FORM_CLASS, _ = loadUiType(
    path.join(path.dirname(__file__), 'z_ficheEtude2.ui'))
class fich7(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(fich7, self).__init__(parent)
        QDialog.__init__(self)
        self.setupUi(self)
        self.rempli()
        self.chek()

    def rempli(self):
        self.Provence.addItems(listes.province_fiche2)

    def chek(self):
        self.Retour.clicked.connect(self.gotofich1)
        self.suivant.clicked.connect(self.gotofich3)
        self.Annuler.clicked.connect(self.annuler)

    def annuler(self):
        qm = QMessageBox
        pip = qm.question(self, 'confirmation',
                          "voulez-vous annuler  l'inscription ?", qm.Yes | qm.No)
        if pip == qm.Yes:
            self.gotowelcom()
            self.clearAllWindowInfo()

    def clearAllWindowInfo(self):
        admI.phase.setCurrentText("-----------")
        admI.diplome.setCurrentText("-----------")
        admI.filier.setCurrentText("-----------")
        admI.CNe.setText("")
        admI.tableWidget.setRowCount(0)
        ####################################
        fich_5.cnE.setText("")
        fich_5.Nmr_Cin.setText("")
        fich_5.name.setText("")
        fich_5.Preno.setText("")
        fich_5.nom_arabe.setText("")
        fich_5.preno_arab.setText("")
        fich_5.dateNaiss.setDateTime(QDateTime(2000,1,1,1,1))
        fich_5.lieuDeNais.setText('')
        fich_5.Provence.setCurrentText("-----------")
        fich_5.lieuDeNais_arab.setText("")
        fich_5.Handicap.setCurrentText("-----------")
        fich_5.csp.setCurrentText("-----------")
        fich_5.Pays_1.setCurrentText("-----------")
        fich_5.Pays_2.setCurrentText("-----------")
        fich_5.no.setChecked(False)
        fich_5.yes.setChecked(False)
        fich_5.celebat.setChecked(False)
        fich_5.mari.setChecked(False)
        if fich_5.file_name != "": ##################################################
            fich_5.picture.setPixmap(QPixmap("inconu.jpg"))
        fich_5.picture.repaint()
        QApplication.processEvents() ###############################################
        fich_6.adresss.setText("")
        fich_6.Email.setText("")
        fich_6.telephone.setText("")
        fich_6.Provence.setCurrentText("-----------")
        #######
        fich_7.nomMere.setText("")
        fich_7.nomPere.setText("")
        fich_7.adreS.setText("")
        fich_7.telephone.setText("")
        fich_7.mail.setText("")
        fich_7.categorie_socio_prof_mere.setCurrentText("-----------")
        fich_7.categorie_socio_prof_pere.setCurrentText("-----------")
        fich_7.PaYs.setCurrentText("-----------")
        fich_7.ProvenceDeResidence.setCurrentText("-----------")
        ######
        fich_8.filiere.setCurrentText("-----------")
        fich_8.Serie.setCurrentText("-----------")
        fich_8.provenceFich4.setCurrentText("-----------")
        fich_8.Academie.setCurrentText("-----------")
        fich_8.Mention.setCurrentText("-----------")
        fich_8.annee.setText("")
        fich_8.moyenne.setText("")
        fich_8.maroc.setChecked(False)
        fich_8.miss.setChecked(False)
        fich_8.etrg.setChecked(False)

    def gotowelcom(self):
        widget.setCurrentIndex(0)

    def gotofich3(self):
        widget.setCurrentIndex(8)

    def gotofich1(self):
        widget.setCurrentIndex(6)
#_the_end_fiche2_##########################################################################


#_fiche3_##################################################################################
FORM_CLASS, _ = loadUiType(path.join(path.dirname(__file__), 'z_ficheEtude3.ui'))
class fich8(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(fich8, self).__init__(parent)
        QDialog.__init__(self)
        self.setupUi(self)
        self.rempli()
        self.chek()

    def rempli(self):
        self.categorie_socio_prof_mere.addItems(
            listes.categorie_Socio_prof_mere)
        self.categorie_socio_prof_pere.addItems(
            listes.categorie_Socio_prof_pere)
        self.ProvenceDeResidence.addItems(listes.ProvenceDe_Residence)
        self.PaYs.addItems(listes.pays)

    def chek(self):
        self.Retour.clicked.connect(self.gotofich2)
        self.Suivant.clicked.connect(self.gotofich4)
        self.Annuler.clicked.connect(self.annuler)

    def annuler(self):
        qm = QMessageBox
        pip = qm.question(self, 'confirmation',
                          "voulez-vous annuler  l'inscription ?", qm.Yes | qm.No)
        if pip == qm.Yes:
            self.gotowelcom()
            self.clearAllWindowInfo()

    def clearAllWindowInfo(self):
        admI.phase.setCurrentText("-----------")
        admI.diplome.setCurrentText("-----------")
        admI.filier.setCurrentText("-----------")
        admI.CNe.setText("")
        admI.tableWidget.setRowCount(0)
        ####################################
        fich_5.cnE.setText("")
        fich_5.Nmr_Cin.setText("")
        fich_5.name.setText("")
        fich_5.Preno.setText("")
        fich_5.nom_arabe.setText("")
        fich_5.preno_arab.setText("")
        fich_5.dateNaiss.setDateTime(QDateTime(2000,1,1,1,1))
        fich_5.lieuDeNais.setText('')
        fich_5.Provence.setCurrentText("-----------")
        fich_5.lieuDeNais_arab.setText("")
        fich_5.Handicap.setCurrentText("-----------")
        fich_5.csp.setCurrentText("-----------")
        fich_5.Pays_1.setCurrentText("-----------")
        fich_5.Pays_2.setCurrentText("-----------")
        fich_5.no.setChecked(False)
        fich_5.yes.setChecked(False)
        fich_5.celebat.setChecked(False)
        fich_5.mari.setChecked(False)
        if fich_5.file_name != "": ##################################################
            fich_5.picture.setPixmap(QPixmap("inconu.jpg"))
        fich_5.picture.repaint()
        QApplication.processEvents() ###############################################
        fich_6.adresss.setText("")
        fich_6.Email.setText("")
        fich_6.telephone.setText("")
        fich_6.Provence.setCurrentText("-----------")
        #######
        fich_7.nomMere.setText("")
        fich_7.nomPere.setText("")
        fich_7.adreS.setText("")
        fich_7.telephone.setText("")
        fich_7.mail.setText("")
        fich_7.categorie_socio_prof_mere.setCurrentText("-----------")
        fich_7.categorie_socio_prof_pere.setCurrentText("-----------")
        fich_7.PaYs.setCurrentText("-----------")
        fich_7.ProvenceDeResidence.setCurrentText("-----------")
        ######
        fich_8.filiere.setCurrentText("-----------")
        fich_8.Serie.setCurrentText("-----------")
        fich_8.provenceFich4.setCurrentText("-----------")
        fich_8.Academie.setCurrentText("-----------")
        fich_8.Mention.setCurrentText("-----------")
        fich_8.annee.setText("")
        fich_8.moyenne.setText("")
        fich_8.maroc.setChecked(False)
        fich_8.miss.setChecked(False)
        fich_8.etrg.setChecked(False)

    def gotowelcom(self):
        widget.setCurrentIndex(0)

    def gotofich2(self):
        widget.setCurrentIndex(7)

    def gotofich4(self):
        widget.setCurrentIndex(9)
#_the_end_fiche3_##########################################################################


#_fiche4_##################################################################################
FORM_CLASS, _ = loadUiType(path.join(path.dirname(__file__), 'z_ficheEtude4.ui'))
class fich9(QDialog, FORM_CLASS, getAllMatch):
    def __init__(self, host, port, dbname, parent=None):
        super(fich9, self).__init__(parent)
        QDialog.__init__(self)
        getAllMatch.__init__(self, host, port, dbname)
        self.setupUi(self)
        self.rempli()
        self.chek()

    def rempli(self):
        self.Serie.addItems(listes.seriE)
        self.provenceFich4.addItems(listes.provence_fich4)
        self.Academie.addItems(listes.AcaDemie)
        self.Mention.addItems(listes.mention)
        self.filiere.addItems(listes.filere)

    def chek(self):
        self.maroc.stateChanged.connect(self.marocChangedAction)
        self.miss.stateChanged.connect(self.missChangedAction)
        self.etrg.stateChanged.connect(self.etrgChangedAction)
        self.Retour.clicked.connect(self.gotofich3)
        self.Valider.clicked.connect(self.validation)
        self.Annuler.clicked.connect(self.annuler)
        self.Imprimer.clicked.connect(self.validation2)

    def validation2(self):
        t1 = self.moyenne.text()
        t2 = self.filiere.currentText()
        if t1 == '.':
            t1 = ''
        if t2 == "-----------":
            t2 = ''
        if t1 == "" or t2 == "":
            self.labelEror1.setText("s'il vous plaît entrer tout les champs impotant")
        else:
            self.labelEror1.setText("")
            self.chekOkya()

    def validation(self):
        t1 = self.moyenne.text()
        if t1 == '.':
            t1 = ''
        t2 = self.filiere.currentText()
        if t2 == "-----------":
            t2 = ''
        if t1 == "" or t2 == "":
            self.labelEror1.setText("s'il vous plaît entrer tout les champs impotant")
        else:
            self.labelEror1.setText("")
            self.gotovalide()

    def clearAllWindowInfo(self):
        admI.phase.setCurrentText("-----------")
        admI.diplome.setCurrentText("-----------")
        admI.filier.setCurrentText("-----------")
        admI.CNe.setText("")
        admI.tableWidget.setRowCount(0)
        ####################################
        fich_5.cnE.setText("")
        fich_5.Nmr_Cin.setText("")
        fich_5.name.setText("")
        fich_5.Preno.setText("")
        fich_5.nom_arabe.setText("")
        fich_5.preno_arab.setText("")
        fich_5.dateNaiss.setDateTime(QDateTime(2000,1,1,1,1))
        fich_5.lieuDeNais.setText('')
        fich_5.Provence.setCurrentText("-----------")
        fich_5.lieuDeNais_arab.setText("")
        fich_5.Handicap.setCurrentText("-----------")
        fich_5.csp.setCurrentText("-----------")
        fich_5.Pays_1.setCurrentText("-----------")
        fich_5.Pays_2.setCurrentText("-----------")
        fich_5.no.setChecked(False)
        fich_5.yes.setChecked(False)
        fich_5.celebat.setChecked(False)
        fich_5.mari.setChecked(False)
        if fich_5.file_name != "": ##################################################
            fich_5.picture.setPixmap(QPixmap("inconu.jpg"))
        fich_5.picture.repaint()
        QApplication.processEvents() ###############################################
        fich_6.adresss.setText("")
        fich_6.Email.setText("")
        fich_6.telephone.setText("")
        fich_6.Provence.setCurrentText("-----------")
        #######
        fich_7.nomMere.setText("")
        fich_7.nomPere.setText("")
        fich_7.adreS.setText("")
        fich_7.telephone.setText("")
        fich_7.mail.setText("")
        fich_7.categorie_socio_prof_mere.setCurrentText("-----------")
        fich_7.categorie_socio_prof_pere.setCurrentText("-----------")
        fich_7.PaYs.setCurrentText("-----------")
        fich_7.ProvenceDeResidence.setCurrentText("-----------")
        ######
        fich_8.filiere.setCurrentText("-----------")
        fich_8.Serie.setCurrentText("-----------")
        fich_8.provenceFich4.setCurrentText("-----------")
        fich_8.Academie.setCurrentText("-----------")
        fich_8.Mention.setCurrentText("-----------")
        fich_8.annee.setText("")
        fich_8.moyenne.setText("")
        fich_8.maroc.setChecked(False)
        fich_8.miss.setChecked(False)
        fich_8.etrg.setChecked(False)

    def chekOkya(self):
        dip = QMessageBox
        pip = dip.question(
            self, 'confirmation', "voulez-vous imprimer attestation ?", dip.Yes | dip.No)
        if pip == dip.Yes:
            self.gotoYesInfo()

    def gotoYesInfo(self):
        self.CNNe = fich_5.cnE.text()
        self.fullName = fich_5.name.text() + " " + fich_5.Preno.text()
        self.cIN = fich_5.Nmr_Cin.text()
        self.filieR = fich_8.filiere.currentText()
        self.annEE = welcome.aNee
        self.numure = self.getNumber()
        create_pdf(self.fullName, self.CNNe, self.cIN,
                   self.filieR, self.numure, self.annEE)
        self.openpdf(self.fullName)

    def openpdf(self, full_name):
        outfile_name = full_name.split(' ')
        outfile_name = outfile_name[0] + '_' + outfile_name[1]
        THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(
            THIS_FOLDER, f"InscriptionFiles\{outfile_name}.pdf")
        try:
            wb.open_new(rf"{path}")
        except Exception as er:
            print("file not open because of : ")
            print(er)

    def getNumber(self):
        a = welcome.aNee
        nurm = fich_8.cNe.text() + a[0:4]
        return nurm

    
    def annuler(self):
        self.labelEror1.setText("")
        qm = QMessageBox
        pip = qm.question(self, 'confirmation',
                          "voulez-vous annuler  l'inscription ?", qm.Yes | qm.No)
        if pip == qm.Yes:
            self.gotowelcom()
            self.clearAllWindowInfo()

    def clearAllWindowInfo(self):
        admI.phase.setCurrentText("-----------")
        admI.diplome.setCurrentText("-----------")
        admI.filier.setCurrentText("-----------")
        admI.CNe.setText("")
        admI.tableWidget.setRowCount(0)
        ####################################
        fich_5.cnE.setText("")
        fich_5.Nmr_Cin.setText("")
        fich_5.name.setText("")
        fich_5.Preno.setText("")
        fich_5.nom_arabe.setText("")
        fich_5.preno_arab.setText("")
        fich_5.dateNaiss.setDateTime(QDateTime(2000,1,1,1,1))
        fich_5.lieuDeNais.setText('')
        fich_5.Provence.setCurrentText("-----------")
        fich_5.lieuDeNais_arab.setText("")
        fich_5.Handicap.setCurrentText("-----------")
        fich_5.csp.setCurrentText("-----------")
        fich_5.Pays_1.setCurrentText("-----------")
        fich_5.Pays_2.setCurrentText("-----------")
        fich_5.no.setChecked(False)
        fich_5.yes.setChecked(False)
        fich_5.celebat.setChecked(False)
        fich_5.mari.setChecked(False)
        if fich_5.file_name != "": ##################################################
            fich_5.picture.setPixmap(QPixmap("inconu.jpg"))
        fich_5.picture.repaint()
        QApplication.processEvents() ###############################################
        fich_6.adresss.setText("")
        fich_6.Email.setText("")
        fich_6.telephone.setText("")
        fich_6.Provence.setCurrentText("-----------")
        #######
        fich_7.nomMere.setText("")
        fich_7.nomPere.setText("")
        fich_7.adreS.setText("")
        fich_7.telephone.setText("")
        fich_7.mail.setText("")
        fich_7.categorie_socio_prof_mere.setCurrentText("-----------")
        fich_7.categorie_socio_prof_pere.setCurrentText("-----------")
        fich_7.PaYs.setCurrentText("-----------")
        fich_7.ProvenceDeResidence.setCurrentText("-----------")
        ######
        fich_8.filiere.setCurrentText("-----------")
        fich_8.Serie.setCurrentText("-----------")
        fich_8.provenceFich4.setCurrentText("-----------")
        fich_8.Academie.setCurrentText("-----------")
        fich_8.Mention.setCurrentText("-----------")
        fich_8.annee.setText("")
        fich_8.moyenne.setText("")
        fich_8.maroc.setChecked(False)
        fich_8.miss.setChecked(False)
        fich_8.etrg.setChecked(False)

    def gotowelcom(self):
        widget.setCurrentIndex(0)

    def gotovalide(self):
        qm = QMessageBox
        pip = qm.question(self, 'confirmation',
                          "voulez-vous faire une inscription ?", qm.Yes | qm.No)
        if pip == qm.Yes:
            self.GetInfo()

    def GetInfo(self):
        self.DataEtudiant = {}
        #_dataFiche1_####################################################
        self.DataEtudiant["cne"] = fich_5.cnE.text()
        self.DataEtudiant["cin"] = fich_5.Nmr_Cin.text()
        self.DataEtudiant["nom"] = fich_5.name.text()
        self.DataEtudiant["prenom"] = fich_5.Preno.text()
        self.DataEtudiant["nom_arab"] = fich_5.nom_arabe.text()
        self.DataEtudiant["prenom_arab"] = fich_5.preno_arab.text()
        self.DataEtudiant["date_naissance"] = fich_5.dateNaiss.text()
        self.DataEtudiant["lieu_naissance"] = fich_5.lieuDeNais.text()
        self.DataEtudiant["lieu_naissance_arab"] = fich_5.lieuDeNais_arab.text()
        self.DataEtudiant["Province_de_naissance"] = fich_5.Provence.currentText()
        self.DataEtudiant["Pays_de_naissance"] = fich_5.Pays_1.currentText()
        self.DataEtudiant["handicap"] = fich_5.Handicap.currentText()
        self.DataEtudiant["Nationalite"] = fich_5.Pays_2.currentText()
        self.DataEtudiant["Categorie_socioprofessionnelle_etudiant"] = fich_5.csp.currentText(
        )
        self.DataEtudiant["Sexe"] = self.sexe()
        self.DataEtudiant["Situation_familiale"] = self.stiuall()
        self.DataEtudiant["photo_path"] = fich_5.file_name
        #_theEnd_Fiche1_data_##############################################
        #_start_data_fich2_################################################
        self.DataEtudiant["Adresse_de_residence_etudiant"] = fich_6.adresss.toPlainText(
        ).replace('\n', ' ')
        self.DataEtudiant["mail_etudiant"] = fich_6.Email.text()
        self.DataEtudiant["Province_de_residence_etudiant"] = fich_6.Provence.currentText(
        )
        self.DataEtudiant["telephone_etudiant"] = fich_6.telephone.text()
        #_theEnd_Fiche2_data_##############################################
        #_start_data_fich3_################################################
        self.DataEtudiant["Nom_complet_mere"] = fich_7.nomMere.text()
        self.DataEtudiant["Nom_complet_pere"] = fich_7.nomPere.text()
        self.DataEtudiant["Categorie_sociopro_mere"] = fich_7.categorie_socio_prof_mere.currentText()
        self.DataEtudiant["Categorie_sociopro_pere"] = fich_7.categorie_socio_prof_pere.currentText()
        self.DataEtudiant["Province_residence_parent"] = fich_7.ProvenceDeResidence.currentText(
        )
        self.DataEtudiant["Pays_residence_parent"] = fich_7.PaYs.currentText()
        self.DataEtudiant["Adresse_de_residence_parent"] = fich_7.adreS.toPlainText(
        ).replace('\n', ' ')
        self.DataEtudiant["telephone_parent"] = fich_7.telephone.text()
        self.DataEtudiant["mail_parent"] = fich_7.mail.text()
        #_theEnd_Fiche3_data_##############################################
        #_start_data_fich4_################################################
        self.DataEtudiant["Type_baccalaureat"] = self.giveMetype()
        self.DataEtudiant["Serie_Baccalaureat"] = fich_8.Serie.currentText()
        self.DataEtudiant["Province_Baccalaureat"] = fich_8.provenceFich4.currentText(
        )
        self.DataEtudiant["Academie_Baccalaureat"] = fich_8.Academie.currentText()
        self.DataEtudiant["Annee_Baccalaureat"] = fich_8.annee.text()
        self.DataEtudiant["Moyenne_Baccalaureat"] = fich_8.moyenne.text()
        self.DataEtudiant["Mention_Baccalaureat"] = fich_8.Mention.currentText()
        self.DataEtudiant["filier_demander"] = fich_8.filiere.currentText()
        #_theEnd_Fiche4_data_##############################################
        ###################################################################
        self.chekable()
        self.AddToDataBase()

    def chekable(self):
        if self.DataEtudiant["Province_de_naissance"] == "-----------":
            self.DataEtudiant["Province_de_naissance"] = ""
        if self.DataEtudiant["Pays_de_naissance"] == "-----------":
            self.DataEtudiant["Pays_de_naissance"] = ""
        if self.DataEtudiant["handicap"] == "-----------":
            self.DataEtudiant["handicap"] = ""
        if self.DataEtudiant["Nationalite"] == "-----------":
            self.DataEtudiant["Nationalite"] = ""
        if self.DataEtudiant["Categorie_socioprofessionnelle_etudiant"] == "-----------":
            self.DataEtudiant["Categorie_socioprofessionnelle_etudiant"] = ""
        if self.DataEtudiant["Province_de_residence_etudiant"] == "-----------":
            self.DataEtudiant["Province_de_residence_etudiant"] = ""
        if self.DataEtudiant["Categorie_sociopro_mere"] == "-----------":
            self.DataEtudiant["Categorie_sociopro_mere"] = ""
        if self.DataEtudiant["Categorie_sociopro_pere"] == "-----------":
            self.DataEtudiant["Categorie_sociopro_pere"] = ""
        if self.DataEtudiant["Province_residence_parent"] == "-----------":
            self.DataEtudiant["Province_residence_parent"] = ""
        if self.DataEtudiant["Pays_residence_parent"] == "-----------":
            self.DataEtudiant["Pays_residence_parent"] = ""
        if self.DataEtudiant["Serie_Baccalaureat"] == "-----------":
            self.DataEtudiant["Serie_Baccalaureat"] = ""
        if self.DataEtudiant["Province_Baccalaureat"] == "-----------":
            self.DataEtudiant["Province_Baccalaureat"] = ""
        if self.DataEtudiant["Academie_Baccalaureat"] == "-----------":
            self.DataEtudiant["Academie_Baccalaureat"] = ""
        if self.DataEtudiant["Mention_Baccalaureat"] == "-----------":
            self.DataEtudiant["Mention_Baccalaureat"] = ""
        if self.DataEtudiant["filier_demander"] == "-----------":
            self.DataEtudiant["filier_demander"] = ""

    def giveMetype(self):
        if fich_8.maroc.isChecked():
            return 'Marocain'
        elif fich_8.miss.isChecked():
            return 'Mission'
        elif fich_8.etrg.isChecked():
            return 'Etranger'
        else:
            return ''

    def stiuall(self):
        if fich_5.celebat.isChecked():
            return 'Célibataire'
        elif fich_5.mari.isChecked():
            return 'Marié(e)'
        else:
            return ''

    def sexe(self):
        if fich_5.no.isChecked():
            return 'H'
        elif fich_5.yes.isChecked():
            return 'F'
        else:
            return ''

    def AddToDataBase(self):
        # chouichou work
        # self.DataEtudiant = dict()
        # ...................
        # ....................
        self.addtodbinfo(self.DataEtudiant)
        self.gotowelcom()
        self.talkToUser()
        self.clearAllWindowInfo()

    def talkToUser(self):
        QMessageBox.information(self, "succes",
                                "Inscription ajouté avec succes")

    def gotofich3(self):
        self.labelEror1.setText("")
        widget.setCurrentIndex(8)

#_interdit_modifé_#################################################################################
    def marocChangedAction(self, state):
        if (Qt.Checked == state):
            if self.miss.isChecked():
                self.miss.setChecked(False)
            elif self.etrg.isChecked():
                self.etrg.setChecked(False)

    def missChangedAction(self, state):
        if (Qt.Checked == state):
            if self.maroc.isChecked():
                self.maroc.setChecked(False)
            elif self.etrg.isChecked():
                self.etrg.setChecked(False)

    def etrgChangedAction(self, state):
        if (Qt.Checked == state):
            if self.miss.isChecked():
                self.miss.setChecked(False)
            elif self.maroc.isChecked():
                self.maroc.setChecked(False)
#_the_end_fiche4_##########################################################################
#_the_end_fiche_admission_#########################################################



#_Start_Fiche_Etude_###############################################################
#_fiche_etude_page_1_#################################################################
FORM_CLASS, _ = loadUiType(path.join(path.dirname(__file__), 'z_ficheEtude1.ui'))
class fich1(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(fich1, self).__init__(parent)
        QDialog.__init__(self)
        self.setupUi(self)
        self.rempli()
        self.check()

    def check(self):
        self.yes.stateChanged.connect(self.yesChangedAction)
        self.no.stateChanged.connect(self.noChangedAction)
        self.celebat.stateChanged.connect(self.celebaTChangedAction)
        self.mari.stateChanged.connect(self.mariChangedAction)
        self.file_name = ''
        self.Import.clicked.connect(self.getImage)
        self.suivant.clicked.connect(self.get_info)
        self.Annuler.clicked.connect(self.annuler)

    def annuler(self):
        self.labelEror1.setText("")
        qm = QMessageBox
        pip = qm.question(self, 'confirmation',
                          "voulez-vous annuler  l'inscription ?", qm.Yes | qm.No)
        if pip == qm.Yes:
            self.gotowelcom()
            self.clearAllWindowInfo()

    def clearAllWindowInfo(self):
        fich_1.cnE.setText("")
        fich_1.Nmr_Cin.setText("")
        fich_1.name.setText("")
        fich_1.Preno.setText("")
        fich_1.nom_arabe.setText("")
        fich_1.preno_arab.setText("")
        fich_1.dateNaiss.setDateTime(QDateTime(2000,1,1,1,1))
        fich_1.lieuDeNais.setText('')
        fich_1.Provence.setCurrentText("-----------")
        fich_1.lieuDeNais_arab.setText("")
        fich_1.Handicap.setCurrentText("-----------")
        fich_1.csp.setCurrentText("-----------")
        fich_1.Pays_1.setCurrentText("-----------")
        fich_1.Pays_2.setCurrentText("-----------")
        fich_1.no.setChecked(False)
        fich_1.yes.setChecked(False)
        fich_1.celebat.setChecked(False)
        fich_1.mari.setChecked(False)
        if fich_1.file_name != "": ##################################################
            fich_1.picture.setPixmap(QPixmap("inconu.jpg"))
        fich_1.picture.repaint()
        QApplication.processEvents() ###############################################
        fich_2.adresss.setText("")
        fich_2.Email.setText("")
        fich_2.telephone.setText("")
        fich_2.Provence.setCurrentText("-----------")
        #######
        fich_3.nomMere.setText("")
        fich_3.nomPere.setText("")
        fich_3.adreS.setText("")
        fich_3.telephone.setText("")
        fich_3.mail.setText("")
        fich_3.categorie_socio_prof_mere.setCurrentText("-----------")
        fich_3.categorie_socio_prof_pere.setCurrentText("-----------")
        fich_3.PaYs.setCurrentText("-----------")
        fich_3.ProvenceDeResidence.setCurrentText("-----------")
        ######
        fich_4.filiere.setCurrentText("-----------")
        fich_4.Serie.setCurrentText("-----------")
        fich_4.provenceFich4.setCurrentText("-----------")
        fich_4.Academie.setCurrentText("-----------")
        fich_4.Mention.setCurrentText("-----------")
        fich_4.annee.setText("")
        fich_4.moyenne.setText("")
        fich_4.maroc.setChecked(False)
        fich_4.miss.setChecked(False)
        fich_4.etrg.setChecked(False)

    def gotowelcom(self):
        widget.setCurrentIndex(0)

    def get_info(self):
        self.remplifich234()
        self.gotopik()

    def gotopik(self):
        t1 = fich_1.cnE.text()
        t2 = fich_1.name.text()
        t3 = fich_1.Preno.text()
        t4 = fich_1.Provence.currentText()
        if t4 == "-----------":
            t4 = ''
        if t1=='' or t2=='' or t3=="" or t4=='':
            self.labelEror1.setText("s'il vous plaît entrer tout les champs impotant")
        else:
            self.labelEror1.setText("")
            self.gotofiche2()

#######################################################################################################
    #
    def remplifich234(self):
        #
        fich_2.cNe.setText(fich_1.cnE.text())
        #
        fich_2.fname.setText(fich_1.name.text())
        #
        fich_2.lname.setText(fich_1.Preno.text())
        #
        fich_2.NmrCin.setText(fich_1.Nmr_Cin.text())
        fich_2.nomArabic.setText(fich_1.nom_arabe.text(
        ))                                             #
        fich_2.prenoArab.setText(fich_1.preno_arab.text(
        ))                                            #
        #######_transfer_picture_si_il_existe_###################################################     #
        if self.file_name != '':
            fich_2.picture.setPixmap(QPixmap(self.file_name))
            fich_2.picture.repaint()
            QApplication.processEvents()
        #########################################################################################     #
        #
        fich_3.cNe.setText(fich_1.cnE.text())
        #
        fich_3.fname.setText(fich_1.name.text())
        #
        fich_3.lname.setText(fich_1.Preno.text())
        #
        fich_3.NmrCin.setText(fich_1.Nmr_Cin.text())
        fich_3.nomArabic.setText(fich_1.nom_arabe.text(
        ))                                             #
        fich_3.prenoArab.setText(fich_1.preno_arab.text(
        ))                                            #
        #######_transfer_picture_si_il_existe_###################################################     #
        if self.file_name != '':
            fich_3.picture.setPixmap(QPixmap(self.file_name))
            fich_3.picture.repaint()
            QApplication.processEvents()
        #########################################################################################     #
        #
        fich_4.cNe.setText(fich_1.cnE.text())
        #
        fich_4.fname.setText(fich_1.name.text())
        #
        fich_4.lname.setText(fich_1.Preno.text())
        #
        fich_4.NmrCin.setText(fich_1.Nmr_Cin.text())
        fich_4.nomArabic.setText(fich_1.nom_arabe.text(
        ))                                             #
        fich_4.prenoArab.setText(fich_1.preno_arab.text(
        ))                                            #
        #######_transfer_picture_si_il_existe_###################################################     #
        if self.file_name != '':
            fich_4.picture.setPixmap(QPixmap(self.file_name))
            fich_4.picture.repaint()
            QApplication.processEvents()
        ###############################################################################################
#######################################################################################################

#_fuction_pour_changer_la_page_####################################################################
    def gotofiche2(self):
        widget.setCurrentIndex(3)

    def gotoWelcom(self):
        widget.setCurrentIndex(0)

#_interdit_modifié_#############################################################################
    def rempli(self):
        self.Pays_1.addItems(listes.pays)
        self.Handicap.addItems(listes.handi)
        self.Pays_2.addItems(listes.pays)
        self.csp.addItems(listes.csp)
        self.Provence.addItems(listes.provin)

    def stiuall(self):
        if self.celebat.isChecked():
            return 'Célibataire'
        elif self.mari.isChecked():
            return 'Marié(e)'
        else:
            return ''

    def Sexe(self):
        if self.no.isChecked():
            return 'H'
        elif self.yes.isChecked():
            return 'F'
        else:
            return ''

    def getImage(self):
        self.file_name, _ = QFileDialog.getOpenFileName(self, 'Open Image File',
                                                        r"<Default dir>", "Image files (*.jpg *.jpeg *.png)")
        if self.file_name != "":
            self.picture.setPixmap(QPixmap(self.file_name))
        self.picture.repaint()
        QApplication.processEvents()

    def mariChangedAction(self, state):
        if (Qt.Checked == state):
            if self.celebat.isChecked():  # ""
                self.celebat.setChecked(False)

    def celebaTChangedAction(self, state):  # ""
        if (Qt.Checked == state):
            if self.mari.isChecked():
                self.mari.setChecked(False)

    def yesChangedAction(self, state):  # ""
        if (Qt.Checked == state):
            if self.no.isChecked():
                self.no.setChecked(False)

    def noChangedAction(self, state):
        if (Qt.Checked == state):  # ""
            if self.yes.isChecked():  # ""
                self.yes.setChecked(False)


#__fiche_page_2_##################################################################################
FORM_CLASS, _ = loadUiType(
    path.join(path.dirname(__file__), 'z_ficheEtude2.ui'))
class fich2(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(fich2, self).__init__(parent)
        QDialog.__init__(self)
        self.setupUi(self)
        self.rempli()
        self.chek()

    def rempli(self):
        self.Provence.addItems(listes.province_fiche2)

    def chek(self):
        self.Retour.clicked.connect(self.gotofich1)
        self.suivant.clicked.connect(self.gotofich3)
        self.Annuler.clicked.connect(self.annuler)

    def annuler(self):
        qm = QMessageBox
        pip = qm.question(self, 'confirmation',
                          "voulez-vous annuler  l'inscription ?", qm.Yes | qm.No)
        if pip == qm.Yes:
            self.gotowelcom()
            self.clearAllWindowInfo()

    def clearAllWindowInfo(self):
        fich_1.cnE.setText("")
        fich_1.Nmr_Cin.setText("")
        fich_1.name.setText("")
        fich_1.Preno.setText("")
        fich_1.nom_arabe.setText("")
        fich_1.preno_arab.setText("")
        fich_1.dateNaiss.setDateTime(QDateTime(2000,1,1,1,1))
        fich_1.lieuDeNais.setText('')
        fich_1.Provence.setCurrentText("-----------")
        fich_1.lieuDeNais_arab.setText("")
        fich_1.Handicap.setCurrentText("-----------")
        fich_1.csp.setCurrentText("-----------")
        fich_1.Pays_1.setCurrentText("-----------")
        fich_1.Pays_2.setCurrentText("-----------")
        fich_1.no.setChecked(False)
        fich_1.yes.setChecked(False)
        fich_1.celebat.setChecked(False)
        fich_1.mari.setChecked(False)
        if fich_1.file_name != "": ##################################################
            fich_1.picture.setPixmap(QPixmap("inconu.jpg"))
        fich_1.picture.repaint()
        QApplication.processEvents() ###############################################
        fich_2.adresss.setText("")
        fich_2.Email.setText("")
        fich_2.telephone.setText("")
        fich_2.Provence.setCurrentText("-----------")
        #######
        fich_3.nomMere.setText("")
        fich_3.nomPere.setText("")
        fich_3.adreS.setText("")
        fich_3.telephone.setText("")
        fich_3.mail.setText("")
        fich_3.categorie_socio_prof_mere.setCurrentText("-----------")
        fich_3.categorie_socio_prof_pere.setCurrentText("-----------")
        fich_3.PaYs.setCurrentText("-----------")
        fich_3.ProvenceDeResidence.setCurrentText("-----------")
        ######
        fich_4.filiere.setCurrentText("-----------")
        fich_4.Serie.setCurrentText("-----------")
        fich_4.provenceFich4.setCurrentText("-----------")
        fich_4.Academie.setCurrentText("-----------")
        fich_4.Mention.setCurrentText("-----------")
        fich_4.annee.setText("")
        fich_4.moyenne.setText("")
        fich_4.maroc.setChecked(False)
        fich_4.miss.setChecked(False)
        fich_4.etrg.setChecked(False)

    def gotowelcom(self):
        widget.setCurrentIndex(0)

    def gotofich3(self):
        widget.setCurrentIndex(4)

    def gotofich1(self):
        widget.setCurrentIndex(2)

#__fiche_page_3_##########################################################################
FORM_CLASS, _ = loadUiType(
    path.join(path.dirname(__file__), 'z_ficheEtude3.ui'))
class fich3(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(fich3, self).__init__(parent)
        QDialog.__init__(self)
        self.setupUi(self)
        self.rempli()
        self.chek()

    def rempli(self):
        self.categorie_socio_prof_mere.addItems(
            listes.categorie_Socio_prof_mere)
        self.categorie_socio_prof_pere.addItems(
            listes.categorie_Socio_prof_pere)
        self.ProvenceDeResidence.addItems(listes.ProvenceDe_Residence)
        self.PaYs.addItems(listes.pays)

    def chek(self):
        self.Retour.clicked.connect(self.gotofich2)
        self.Suivant.clicked.connect(self.gotofich4)
        self.Annuler.clicked.connect(self.annuler)

    def annuler(self):
        qm = QMessageBox
        pip = qm.question(self, 'confirmation',
                          "voulez-vous annuler  l'inscription ?", qm.Yes | qm.No)
        if pip == qm.Yes:
            self.gotowelcom()
            self.clearAllWindowInfo()

    def clearAllWindowInfo(self):
        fich_1.cnE.setText("")
        fich_1.Nmr_Cin.setText("")
        fich_1.name.setText("")
        fich_1.Preno.setText("")
        fich_1.nom_arabe.setText("")
        fich_1.preno_arab.setText("")
        fich_1.dateNaiss.setDateTime(QDateTime(2000,1,1,1,1))
        fich_1.lieuDeNais.setText('')
        fich_1.Provence.setCurrentText("-----------")
        fich_1.lieuDeNais_arab.setText("")
        fich_1.Handicap.setCurrentText("-----------")
        fich_1.csp.setCurrentText("-----------")
        fich_1.Pays_1.setCurrentText("-----------")
        fich_1.Pays_2.setCurrentText("-----------")
        fich_1.no.setChecked(False)
        fich_1.yes.setChecked(False)
        fich_1.celebat.setChecked(False)
        fich_1.mari.setChecked(False)
        if fich_1.file_name != "": ##################################################
            fich_1.picture.setPixmap(QPixmap("inconu.jpg"))
        fich_1.picture.repaint()
        QApplication.processEvents() ###############################################
        fich_2.adresss.setText("")
        fich_2.Email.setText("")
        fich_2.telephone.setText("")
        fich_2.Provence.setCurrentText("-----------")
        #######
        fich_3.nomMere.setText("")
        fich_3.nomPere.setText("")
        fich_3.adreS.setText("")
        fich_3.telephone.setText("")
        fich_3.mail.setText("")
        fich_3.categorie_socio_prof_mere.setCurrentText("-----------")
        fich_3.categorie_socio_prof_pere.setCurrentText("-----------")
        fich_3.PaYs.setCurrentText("-----------")
        fich_3.ProvenceDeResidence.setCurrentText("-----------")
        ######
        fich_4.filiere.setCurrentText("-----------")
        fich_4.Serie.setCurrentText("-----------")
        fich_4.provenceFich4.setCurrentText("-----------")
        fich_4.Academie.setCurrentText("-----------")
        fich_4.Mention.setCurrentText("-----------")
        fich_4.annee.setText("")
        fich_4.moyenne.setText("")
        fich_4.maroc.setChecked(False)
        fich_4.miss.setChecked(False)
        fich_4.etrg.setChecked(False)

    def gotowelcom(self):
        widget.setCurrentIndex(0)

    def gotofich2(self):
        widget.setCurrentIndex(3)

    def gotofich4(self):
        widget.setCurrentIndex(5)


#__fiche_page_4_##########################################################################
FORM_CLASS, _ = loadUiType(
    path.join(path.dirname(__file__), 'z_ficheEtude4.ui'))
class fich4(QDialog, FORM_CLASS  , getAllMatch):
    def __init__(self,host, port, dbname,  parent=None):
        super(fich4, self).__init__(parent)
        QDialog.__init__(self)
        getAllMatch.__init__(self , host, port, dbname,  ) 
        self.setupUi(self)
        self.rempli()
        self.chek()

    def rempli(self):
        self.Serie.addItems(listes.seriE)
        self.provenceFich4.addItems(listes.provence_fich4)
        self.Academie.addItems(listes.AcaDemie)
        self.Mention.addItems(listes.mention)
        self.filiere.addItems(listes.filere)

    def chek(self):
        self.maroc.stateChanged.connect(self.marocChangedAction)
        self.miss.stateChanged.connect(self.missChangedAction)
        self.etrg.stateChanged.connect(self.etrgChangedAction)
        self.Retour.clicked.connect(self.gotofich3)
        self.Valider.clicked.connect(self.validFirst)
        self.Annuler.clicked.connect(self.annuler)
        self.Imprimer.clicked.connect(self.vali2)
    
    def vali2(self):
        t1 = self.moyenne.text()
        if t1 == '.':
            t1 = ''
        t2 = self.filiere.currentText()
        if t2 == "-----------":
            t2 = ''
        if t1 == "" or t2 == "":
            self.labelEror1.setText("s'il vous plaît entrer tout les champs impotant")
        else:
            self.labelEror1.setText("")
            self.chekOkya()

    def validFirst(self):
        t1 = self.moyenne.text()
        if t1 == '.':
            t1 = ''
        t2 = self.filiere.currentText()
        if t2 == "-----------":
            t2 = ''
        if t1 == "" or t2 == "":
            self.labelEror1.setText("s'il vous plaît entrer tout les champs impotant")
        else:
            self.labelEror1.setText("")
            self.gotovalide()

    def chekOkya(self):
        dip = QMessageBox
        pip = dip.question(
            self, 'confirmation', "voulez-vous imprimer attestation ?", dip.Yes | dip.No)
        if pip == dip.Yes:
            self.gotoYesInfo()

    def gotoYesInfo(self):
        self.CNNe = fich_1.cnE.text()
        self.fullName = fich_1.name.text() + " " + fich_1.Preno.text()
        self.cIN = fich_1.Nmr_Cin.text()
        self.filieR = fich_4.filiere.currentText()
        self.annEE = welcome.aNee
        self.numure = self.getNumber()
        create_pdf(self.fullName, self.CNNe, self.cIN,
                   self.filieR, self.numure, self.annEE)
        self.openpdf(self.fullName)

    def openpdf(self, full_name):
        outfile_name = full_name.split(' ')
        outfile_name = outfile_name[0] + '_' + outfile_name[1]
        THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(
            THIS_FOLDER, f"InscriptionFiles\{outfile_name}.pdf")
        try:
            wb.open_new(rf"{path}")
        except Exception as er:
            print("file not open because of : ")
            print(er)

    def getNumber(self):
        a = welcome.aNee
        nurm = fich_4.cNe.text() + a[0:4]
        return nurm


    def annuler(self):
        self.labelEror1.setText("")
        qm = QMessageBox
        pip = qm.question(self, 'confirmation',
                          "voulez-vous annuler  l'inscription ?", qm.Yes | qm.No)
        if pip == qm.Yes:
            self.gotowelcom()
            self.clearAllWindowInfo()

    def clearAllWindowInfo(self):
        fich_1.cnE.setText("")
        fich_1.Nmr_Cin.setText("")
        fich_1.name.setText("")
        fich_1.Preno.setText("")
        fich_1.nom_arabe.setText("")
        fich_1.preno_arab.setText("")
        fich_1.dateNaiss.setDateTime(QDateTime(2000,1,1,1,1))
        fich_1.lieuDeNais.setText('')
        fich_1.Provence.setCurrentText("-----------")
        fich_1.lieuDeNais_arab.setText("")
        fich_1.Handicap.setCurrentText("-----------")
        fich_1.csp.setCurrentText("-----------")
        fich_1.Pays_1.setCurrentText("-----------")
        fich_1.Pays_2.setCurrentText("-----------")
        fich_1.no.setChecked(False)
        fich_1.yes.setChecked(False)
        fich_1.celebat.setChecked(False)
        fich_1.mari.setChecked(False)
        if fich_1.file_name != "": ##################################################
            fich_1.picture.setPixmap(QPixmap("inconu.jpg"))
        fich_1.picture.repaint()
        QApplication.processEvents() ###############################################
        fich_2.adresss.setText("")
        fich_2.Email.setText("")
        fich_2.telephone.setText("")
        fich_2.Provence.setCurrentText("-----------")
        #######
        fich_3.nomMere.setText("")
        fich_3.nomPere.setText("")
        fich_3.adreS.setText("")
        fich_3.telephone.setText("")
        fich_3.mail.setText("")
        fich_3.categorie_socio_prof_mere.setCurrentText("-----------")
        fich_3.categorie_socio_prof_pere.setCurrentText("-----------")
        fich_3.PaYs.setCurrentText("-----------")
        fich_3.ProvenceDeResidence.setCurrentText("-----------")
        ######
        fich_4.filiere.setCurrentText("-----------")
        fich_4.Serie.setCurrentText("-----------")
        fich_4.provenceFich4.setCurrentText("-----------")
        fich_4.Academie.setCurrentText("-----------")
        fich_4.Mention.setCurrentText("-----------")
        fich_4.annee.setText("")
        fich_4.moyenne.setText("")
        fich_4.maroc.setChecked(False)
        fich_4.miss.setChecked(False)
        fich_4.etrg.setChecked(False)

        

    def gotowelcom(self):
        widget.setCurrentIndex(0)

    def gotovalide(self):
        qm = QMessageBox
        pip = qm.question(self, 'confirmation',
                          "voulez-vous faire une inscription ?", qm.Yes | qm.No)
        if pip == qm.Yes:
            self.GetInfo()

    def GetInfo(self):
        self.DataEtudiant = {}
        #_dataFiche1_####################################################
        self.DataEtudiant["cne"] = fich_1.cnE.text()
        self.DataEtudiant["cin"] = fich_1.Nmr_Cin.text()
        self.DataEtudiant["nom"] = fich_1.name.text()
        self.DataEtudiant["prenom"] = fich_1.Preno.text()
        self.DataEtudiant["nom_arab"] = fich_1.nom_arabe.text()
        self.DataEtudiant["prenom_arab"] = fich_1.preno_arab.text()
        self.DataEtudiant["date_naissance"] = fich_1.dateNaiss.text()
        self.DataEtudiant["lieu_naissance"] = fich_1.lieuDeNais.text()
        self.DataEtudiant["lieu_naissance_arab"] = fich_1.lieuDeNais_arab.text()
        self.DataEtudiant["Province_de_naissance"] = fich_1.Provence.currentText()
        self.DataEtudiant["Pays_de_naissance"] = fich_1.Pays_1.currentText()
        self.DataEtudiant["handicap"] = fich_1.Handicap.currentText()
        self.DataEtudiant["Nationalite"] = fich_1.Pays_2.currentText()
        self.DataEtudiant["Categorie_socioprofessionnelle_etudiant"] = fich_1.csp.currentText(
        )
        self.DataEtudiant["Sexe"] = self.sexe()
        self.DataEtudiant["Situation_familiale"] = self.stiuall()
        self.DataEtudiant["photo_path"] = fich_1.file_name
        #_theEnd_Fiche1_data_##############################################
        #_start_data_fich2_################################################
        self.DataEtudiant["Adresse_de_residence_etudiant"] = fich_2.adresss.toPlainText(
        ).replace('\n', ' ')
        self.DataEtudiant["mail_etudiant"] = fich_2.Email.text()
        self.DataEtudiant["Province_de_residence_etudiant"] = fich_2.Provence.currentText(
        )
        self.DataEtudiant["telephone_etudiant"] = fich_2.telephone.text()
        #_theEnd_Fiche2_data_##############################################
        #_start_data_fich3_################################################
        self.DataEtudiant["Nom_complet_mere"] = fich_3.nomMere.text()
        self.DataEtudiant["Nom_complet_pere"] = fich_3.nomPere.text()
        self.DataEtudiant["Categorie_sociopro_mere"] = fich_3.categorie_socio_prof_mere.currentText()
        self.DataEtudiant["Categorie_sociopro_pere"] = fich_3.categorie_socio_prof_pere.currentText()
        self.DataEtudiant["Province_residence_parent"] = fich_3.ProvenceDeResidence.currentText(
        )
        self.DataEtudiant["Pays_residence_parent"] = fich_3.PaYs.currentText()
        self.DataEtudiant["Adresse_de_residence_parent"] = fich_3.adreS.toPlainText(
        ).replace('\n', ' ')
        self.DataEtudiant["telephone_parent"] = fich_3.telephone.text()
        self.DataEtudiant["mail_parent"] = fich_3.mail.text()
        #_theEnd_Fiche3_data_##############################################
        #_start_data_fich4_################################################
        self.DataEtudiant["Type_baccalaureat"] = self.giveMetype()
        self.DataEtudiant["Serie_Baccalaureat"] = fich_4.Serie.currentText()
        self.DataEtudiant["Province_Baccalaureat"] = fich_4.provenceFich4.currentText(
        )
        self.DataEtudiant["Academie_Baccalaureat"] = fich_4.Academie.currentText()
        self.DataEtudiant["Annee_Baccalaureat"] = fich_4.annee.text()
        self.DataEtudiant["Moyenne_Baccalaureat"] = fich_4.moyenne.text()
        self.DataEtudiant["Mention_Baccalaureat"] = fich_4.Mention.currentText()
        self.DataEtudiant["filier_demander"] = fich_4.filiere.currentText()
        #_theEnd_Fiche4_data_##############################################
        print(self.DataEtudiant)
        ###################################################################
        self.chekable()
        self.AddToDataBase()
        ###################################################################

    def chekable(self):
        if self.DataEtudiant["Province_de_naissance"] == "-----------":
            self.DataEtudiant["Province_de_naissance"] = ""
        if self.DataEtudiant["Pays_de_naissance"] == "-----------":
            self.DataEtudiant["Pays_de_naissance"] = ""
        if self.DataEtudiant["handicap"] == "-----------":
            self.DataEtudiant["handicap"] = ""
        if self.DataEtudiant["Nationalite"] == "-----------":
            self.DataEtudiant["Nationalite"] = ""
        if self.DataEtudiant["Categorie_socioprofessionnelle_etudiant"] == "-----------":
            self.DataEtudiant["Categorie_socioprofessionnelle_etudiant"] = ""
        if self.DataEtudiant["Province_de_residence_etudiant"] == "-----------":
            self.DataEtudiant["Province_de_residence_etudiant"] = ""
        if self.DataEtudiant["Categorie_sociopro_mere"] == "-----------":
            self.DataEtudiant["Categorie_sociopro_mere"] = ""
        if self.DataEtudiant["Categorie_sociopro_pere"] == "-----------":
            self.DataEtudiant["Categorie_sociopro_pere"] = ""
        if self.DataEtudiant["Province_residence_parent"] == "-----------":
            self.DataEtudiant["Province_residence_parent"] = ""
        if self.DataEtudiant["Pays_residence_parent"] == "-----------":
            self.DataEtudiant["Pays_residence_parent"] = ""
        if self.DataEtudiant["Serie_Baccalaureat"] == "-----------":
            self.DataEtudiant["Serie_Baccalaureat"] = ""
        if self.DataEtudiant["Province_Baccalaureat"] == "-----------":
            self.DataEtudiant["Province_Baccalaureat"] = ""
        if self.DataEtudiant["Academie_Baccalaureat"] == "-----------":
            self.DataEtudiant["Academie_Baccalaureat"] = ""
        if self.DataEtudiant["Mention_Baccalaureat"] == "-----------":
            self.DataEtudiant["Mention_Baccalaureat"] = ""
        if self.DataEtudiant["filier_demander"] == "-----------":
            self.DataEtudiant["filier_demander"] = ""

    def giveMetype(self):
        if fich_4.maroc.isChecked():
            return 'Marocain'
        elif fich_4.miss.isChecked():
            return 'Mission'
        elif fich_4.etrg.isChecked():
            return 'Etranger'
        else:
            return ''

    def stiuall(self):
        if fich_1.celebat.isChecked():
            return 'Célibataire'
        elif fich_1.mari.isChecked():
            return 'Marié(e)'
        else:
            return ''

    def sexe(self):
        if fich_1.no.isChecked():
            return 'H'
        elif fich_1.yes.isChecked():
            return 'F'
        else:
            return ''

    def AddToDataBase(self):
        # chouichou work
        # self.DataEtudiant = dict()
        # ...................
        # ....................
        self.addtodbinfo(self.DataEtudiant)
        self.gotowelcom()
        self.talkToUser()
        self.clearAllWindowInfo()

    def talkToUser(self):
        QMessageBox.information(self, "succes",
                                "Inscription ajouté avec succes")

    def gotofich3(self):
        self.labelEror1.setText("")
        widget.setCurrentIndex(4)

#_interdit_modifé_#################################################################################
    def marocChangedAction(self, state):
        if (Qt.Checked == state):
            if self.miss.isChecked():
                self.miss.setChecked(False)
            elif self.etrg.isChecked():
                self.etrg.setChecked(False)

    def missChangedAction(self, state):
        if (Qt.Checked == state):
            if self.maroc.isChecked():
                self.maroc.setChecked(False)
            elif self.etrg.isChecked():
                self.etrg.setChecked(False)

    def etrgChangedAction(self, state):
        if (Qt.Checked == state):
            if self.miss.isChecked():
                self.miss.setChecked(False)
            elif self.maroc.isChecked():
                self.maroc.setChecked(False)
#_the_end_fiche_etude_###############################################################################


#__Settings_page_##########################################################################
FORM_CLASS, _ = loadUiType(path.join(path.dirname(__file__), 'z_settings.ui'))
class fichSettings(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(fichSettings, self).__init__(parent)
        QDialog.__init__(self)
        self.setupUi(self)
        self.rempli()
        self.chek()

    def rempli(self):
        self.ANNEe.addItem(welcome.aNee)
        self.ANNEe.setCurrentText(welcome.aNee)

    def chek(self):
        self.Retour.clicked.connect(self.gotoWelcom)
        self.Valide.clicked.connect(self.gotosauveOkay)

    def gotosauveOkay(self):
        qm = QMessageBox
        pip = qm.question(self, 'confirmation',
                          "voulez-vous changer les Paramètres ?", qm.Yes | qm.No)
        if pip == qm.Yes:
            self.gotosauve()

    def gotosauve(self):
        self.anneE = self.ANNEe.currentText()
        welcome.settings.setValue('annee', self.anneE)
        self.gotoWelcom()
        self.infoOkay()

    def infoOkay(self):
        QMessageBox.information(self, "information",
                                "Veuillez redemarrer l'application pour appliquer les nouveaux Paramètres")

    def gotoWelcom(self):
        widget.setCurrentIndex(0)


#_main_############################################################################
if __name__ == "__main__":                                                        #
    #
    app = QApplication(sys.argv)
    widget = QStackedWidget()                                                     #
    ###############################################################################
    welcome = WelcomScreen()  # index 0                                            #
    #
    widget.addWidget(welcome)
    admI = admis_Screen("localhost", 5432, "inscription2")
    admI._auth('fiberx01', '0000')
    admI.connect()                                        #
    #
    widget.addWidget(admI)
    fich_1 = fich1()    # index 2                                                 #
    #
    widget.addWidget(fich_1)
    fich_2 = fich2()     # index 3                                                #
    #
    widget.addWidget(fich_2)
    fich_3 = fich3()    # index 4                                                 #
    #
    widget.addWidget(fich_3)
    fich_4 = fich4("localhost", 5432, "inscription2")
    fich_4._auth('fiberx01', '0000')
    fich_4.connect()                                              #
    #
    widget.addWidget(fich_4)
    fich_5 = fich6()    # index 6                                                 #
    #
    widget.addWidget(fich_5)
    fich_6 = fich7()     # index 7                                                #
    #
    widget.addWidget(fich_6)
    fich_7 = fich8()    # index 8                                                 #
    #
    widget.addWidget(fich_7)
    fich_8 = fich9("localhost", 5432, "inscription2")
    fich_8._auth('fiberx01', '0000')
    fich_8.connect()                                          #
    #
    widget.addWidget(fich_8)
    fichSetting = fichSettings()  # index 10                                        #
    widget.addWidget(fichSetting)
    fichChose = fich_choose()
    widget.addWidget(fichChose) # index 11
    ###############################################################################
    #
    widget.setFixedHeight(540)
    #
    widget.setFixedWidth(900)
    #
    widget.setWindowIcon(QIcon('icon.png'))
    widget.setWindowTitle(
        '  EsT Fes Inscription ')                               #
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5()
                      )                         #
    widget.show()                                                                 #
    try:                                                                          #
        #
        sys.exit(app.exec_())
    except:                                                                       #
        pass
#####_FIN_DE_CODE_#################################################################
