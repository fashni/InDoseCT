import sqlite3 as sl
import pandas as pd

def create_connection(db_file):
  conn = None
  try:
    conn = sl.connect(db_file)
  except sl.Error as e:
    print(e)
  return conn

def create_patients_table(con):
  with con:
    try:
      con.execute("""
        CREATE TABLE PATIENTS (
          id INTEGER PRIMARY KEY,
          name TEXT,
          protocol_num INTEGER,
          protocol TEXT,
          date TEXT,
          age INTEGER,
          sex_id INTEGER,
          sex TEXT,
          CTDIVol REAL,
          DE_WED REAL,
          SSDE REAL,
          DLP REAL,
          DLPc REAL,
          Effective_Dose REAL
        );
      """)
    except sl.Error as e:
      print(e)

def insert_patient(con, patient_data):
  sql = """INSERT INTO PATIENTS (name, protocol_num, protocol, date, age, sex_id, sex, CTDIVol, DE_WED, SSDE, DLP, DLPc, Effective_Dose)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
  cur = con.cursor()
  cur.execute(sql, patient_data)
  con.commit()
  return cur.lastrowid

def remove_patient(con, id):
  sql = "DELETE FROM PATIENTS WHERE id=?"
  cur = con.cursor()
  cur.execute(sql, (id,))
  con.commit()

def remove_all_patients(con):
  sql = "DELETE FROM PATIENTS"
  cur = con.cursor()
  cur.execute(sql)
  # cur.execute("UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME=PATIENTS")
  con.commit()

def convert_to_excel(con, xls_file):
  sql = "SELECT * FROM PATIENTS"
  df = pd.read_sql_query(sql, con)
  print(df.head())
  df.to_excel(xls_file, index=False)

def main():
  db_file = 'db/patient_data.db'
  con = create_connection(db_file)
  create_patients_table(con)

  with con:
    patient1 = ('Heru', 11, 'HEAD', '20180209', 29, 1, 'Male', 10, 17.26, 9.66, 100, 96.8, 0.54)
    patient2 = ('Isabella', 11, 'HEAD', '20181031', 21, 2, 'Female', 10, 17.26, 9.66, 100, 96.8, 0.54)
    patient_id1 = insert_patient(con, patient1)
    patient_id2 = insert_patient(con, patient2)

  con.close()



if __name__ == '__main__':
  main()

  # db_file = 'db/patient_data.db'
  # con = create_connection(db_file)

  # with con:
  #   q = con.execute("SELECT * FROM PATIENTS")
  #   for row in q:
  #     print(row)
  # con.close()
