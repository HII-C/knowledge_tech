import os
import MySQLdb as sql
from getpass import getpass
from collections import defaultdict

class SemRepDerivedCreation:
    def __init__(self, limit=10000):
        self.semmed_conn = None
        self.semmed_cur = None
        self.semmed_table_name = None

        self.useful_conn = None
        self.useful_cur = None
        self.useful_table_name = None

        self.der_conn = None
        self.der_cur = None
        self.der_table_name = None
        self.new_der_table = False

        self.limit = limit
        self.list_of_rel_preds = list()
        self.dict_of_pred_occ = defaultdict(int)

    def connect_useful_db(self, database, table_name):
        self.useful_conn = sql.connect(**database)
        self.useful_cur = self.useful_conn.cursor()
        self.useful_table_name = table_name

    def connect_semmed(self, database, table_name):
        self.semmed_conn = sql.connect(**database)
        self.semmed_cur = self.semmed_conn.cursor()
        self.semmed_table_name = table_name

    def connect_der(self, database, table_name, drop=False):
        self.der_conn = sql.connect(**database)
        self.der_cur = self.der_conn.cursor()
        self.der_table_name = table_name
        if drop:
            print(f"Are you sure you want to drop the table \"{table_name}\"?")
            print("ALL DATA WILL BE LOST, THIS IS NOT REVERSABLE")
            user_resp = input("y/n?\n")
            if user_resp != "y":
                print("Exiting now")
                exit()
            else:
                print("Okay, data being dropped")
            self.der_cur.execute(f"DROP TABLE IF EXISTS {table_name}")
            self.der_cur.execute(f"""CREATE TABLE {table_name} 
                (PREDICATE VARCHAR(50),
                 SUBJECT_CUI CHAR(8), 
                 SUBJECT_NAME VARCHAR(200),
                 SUBJECT_SEMTYPE CHAR(4),
                 OBJECT_CUI CHAR(8),
                 OBJECT_NAME VARCHAR(200),
                 OBJECT_SEMTYPE CHAR(4),
                 OCC_COUNT INT)""")
            self.new_der_table = True

    def get_n_random_useful_articles(self, n=1000):
        exec_str = f"SELECT PMID from {self.useful_table_name} ORDER BY RAND() limit {n}"
        self.useful_cur.execute(exec_str)
        ret_list = list()
        return self.useful_cur.fetchall()

    def useful_preds_by_PMID(self, pmid_list, n=10000):
        sel_str = "PREDICATE, SUBJECT_CUI, SUBJECT_NAME, SUBJECT_SEMTYPE, OBJECT_CUI, OBJECT_NAME, OBJECT_SEMTYPE"
        new_pmid = [str(x[0]) for x in pmid_list if x[0] != ""]
        exec_str = f"SELECT {sel_str} FROM {self.semmed_table_name} WHERE PMID in {tuple(new_pmid)}"
        self.semmed_cur.execute(exec_str)
        self.list_of_rel_preds = self.semmed_cur.fetchall()

    def assign_occ_to_preds(self):
        s_ = "(PREDICATE, SUBJECT_CUI, SUBJECT_NAME, SUBJECT_SEMTYPE, OBJECT_CUI, OBJECT_NAME, OBJECT_SEMTYPE, OCC_COUNT)"
        for pred in self.list_of_rel_preds:
            pred = tuple(pred)
            self.dict_of_pred_occ[pred] += 1
        
        exec_str = f"INSERT INTO {self.der_table_name} {s_} VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
        val_list = list()
        c = 0
        for val in self.dict_of_pred_occ.keys():
            list_val = [*val]
            if (len(list_val[1]) == 8) and (len(list_val[4]) == 8):
                val_list.append(tuple([*list_val, self.dict_of_pred_occ[val]]))
            else:
                if "|" in list_val[4]:
                    new_val = list_val[4].split("|")[0]
                    if len(new_val) == 8 and (len(list_val[4]) == 8):
                        list_val[4] = new_val
                        val_list.append(tuple([*list_val, self.dict_of_pred_occ[val]]))
            if c < 5:
                print(val_list[-1])
                c += 1
        print(val_list[-1])
        self.der_cur.executemany(exec_str, val_list)
        self.der_conn.commit()

if __name__ == "__main__":
    example = SemRepDerivedCreation()
    # user = input("What is the name of the DB user? (Must have access to semmed and derived and pubmed)\n")
    user = 'hiic'
    pw = getpass(f"What is the password for {user}?\n")

    semmed_db = {'user': user, 'db': 'semmed', 'host': 'db01.healthcreek.org', 'password': pw}
    der_db = {'user': user, 'db': 'derived', 'host': 'db01.healthcreek.org', 'password': pw}
    useful_db = {'user': user, 'db': 'pubmed', 'host': 'db01.healthcreek.org', 'password': pw}

    # useful_table_name = input(f"What is the table to be used on {useful_db['db']}?\n")
    useful_table_name = "derived"
    example.connect_useful_db(useful_db, useful_table_name)
    print(f'Connected to database: {useful_db["db"]} on table: {useful_table_name}')

    # semmed_table_name = input(f"What is the table to be used on {semmed_db['db']}?\n")
    semmed_table_name = "PREDICATION"
    example.connect_semmed(semmed_db, semmed_table_name)
    print(f'Connected to database: {semmed_db["db"]} on table: {semmed_table_name}')

    # der_table_name = input(f"What is the table to be used on {der_db['db']}?\n")
    der_table_name = "austin_pred_occ_test"
    example.connect_der(der_db, der_table_name, drop=True)
    print(f'Connected to database: {der_db["db"]} on table: {der_table_name}')


    ret_pmid_list = example.get_n_random_useful_articles()
    example.useful_preds_by_PMID(ret_pmid_list)
    example.assign_occ_to_preds()
