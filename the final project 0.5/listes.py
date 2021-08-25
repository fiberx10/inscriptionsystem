import psycopg2
from psycopg2 import Error





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
            return "postgres Auth. Error  : please login first  ! "
        try:
            self.conn = psycopg2.connect(
                database=self._dbname, 
                user=self.authontification[0],
                sslmode='prefer', 
                host=self._host, 
                port=self._port, 
                password=self.authontification[1]
                )
            self.conn.set_session(autocommit=True)
            print(self.conn.get_dsn_parameters(), "\n")
        except(Exception, Error) as error:
            print("postgressql error : ",  error)





    
    def getpays(self) :
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT (libelle) FROM pays")
            data = cursor.fetchall()
        except (Exception, Error) as _config_error:
            print(_config_error)
        ndata = ["-----------"]
        for i in data : 
            ndata.append(i[0]) 
        return tuple(list(ndata))
    def getfiliere(self) :
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT (acronyme) FROM filiere")
            data = cursor.fetchall()
        except (Exception, Error) as _config_error:
            print(_config_error)
        ndata = ["-----------"]
        for i in data : 
            ndata.append(i[0]) 
        return tuple(list(ndata))
    def getdiplome(self) :
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT (acronyme) FROM diplome")
            data = cursor.fetchall()
        except (Exception, Error) as _config_error:
            print(_config_error)
        ndata = ["-----------"]
        for i in data : 
            ndata.append(i[0]) 
        return tuple(list(ndata))
    def getcsp(self) :
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT (titre) FROM categorie_csp")
            data = cursor.fetchall()
        except (Exception, Error) as _config_error:
            print(_config_error)
        ndata = ["-----------"]
        for i in data : 
            ndata.append(i[0]) 
        return tuple(list(ndata))
    def getprovince(self) :
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT (nom) FROM province")
            data = cursor.fetchall()
        except (Exception, Error) as _config_error:
            print(_config_error)
        ndata = ["-----------"]
        for i in data : 
            ndata.append(i[0]) 
        return tuple(list(ndata))
    def getacademy(self) :
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT (nom) FROM region")
            data = cursor.fetchall()
        except (Exception, Error) as _config_error:
            print(_config_error)
        ndata = ["-----------"]
        for i in data : 
            ndata.append(i[0]) 
        return tuple(list(ndata))

    def getserie(self) :
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT (libelle) FROM serie_baccalaureat")
            data = cursor.fetchall()
        except (Exception, Error) as _config_error:
            print(_config_error)
        ndata = ["-----------"]
        for i in data : 
            ndata.append(i[0]) 
        return tuple(list(ndata))





admI = Dbconnect("localhost", 5432, "inscription2")
admI._auth('fiberx01', '0000')
admI.connect()   





pays  = admI.getpays() 

# admision :

filere = admI.getfiliere()


phase = ("-----------","phase 1","phase 2","phase 3","phase 4","phase 5","phase 6","phase 7","phase 8")

diplom = admI.getdiplome()
# fiche 1
handi = ("-----------","aucun handicap", "vue", "audition", "mouvement",\
"mémoire", "mental", "prendre soi de soi", "communication")

csp  = admI.getcsp()

provin = admI.getprovince()
# fiche 2 

province_fiche2 = admI.getprovince()
#fiche 3
categorie_Socio_prof_mere = admI.getcsp()
categorie_Socio_prof_pere  = admI.getcsp()

ProvenceDe_Residence = admI.getprovince()
#fiche 4 
seriE = admI.getserie()
provence_fich4 = admI.getprovince()
AcaDemie = admI.getacademy()
mention = ("-----------",'très bien', 'bien', 'assez bien', 'passable', 'autre')