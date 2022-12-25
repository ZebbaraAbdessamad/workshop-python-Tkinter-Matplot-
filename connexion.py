import pymysql


class Dbconnect(object):
    def __init__(self):
        self.dbconection = pymysql.connect(host='localhost', port=3306, user='root', passwd='', db='dbcomptoire')
        self.dbcursor = self.dbconection.cursor()

    def commit_db(self):
        self.dbconection.commit()

    def close_db(self):
        self.dbcursor.close();
        self.dbconection.close()


# db = Dbconnect()
req = 'SELECT Nom , Prénom , (DateEnvoi - ALivrerAvant) as retard FROM' \
      ' commandes  INNER JOIN employés ON (commandes.NEmployé = employés.NEmployé)' \
      ' where (DateEnvoi - ALivrerAvant) > 3'

req2 = "select commandes.NCommande, DateCommande, SUM(PrixUnitaire * Quantité *(1- `Remise (%)`)) as MT " \
       "FROM détailscommandes INNER JOIN commandes ON (détailscommandes.NCommande = commandes.NCommande) " \
       " GROUP BY commandes.NCommande, DateCommande"
"""
db.dbcursor.execute(req2)
for rec in db.dbcursor.fetchall():
    print(rec)
"""
