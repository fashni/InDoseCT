import sqlite3 as sl
import pandas as pd
import os
from constants import *

def create_connection(db_file):
  conn = None
  try:
    conn = sl.connect(db_file)
  except sl.Error as e:
    print(e)
  return conn

def create_patients_table():
  con = create_connection(PATIENTS_DB)
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
  con.close()

def insert_patient(patient_data):
  con = create_connection(PATIENTS_DB)
  sql = """INSERT INTO PATIENTS (name, protocol_num, protocol, date, age, sex_id, sex, CTDIVol, DE_WED, SSDE, DLP, DLPc, Effective_Dose)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
  cur = con.cursor()
  cur.execute(sql, patient_data)
  con.commit()
  lastrowid = cur.lastrowid
  con.close()
  return lastrowid

def remove_patient(id):
  con = create_connection(PATIENTS_DB)
  sql = "DELETE FROM PATIENTS WHERE id=?"
  cur = con.cursor()
  cur.execute(sql, (id,))
  con.commit()
  con.close()

def remove_all_patients():
  con = create_connection(PATIENTS_DB)
  sql = "DELETE FROM PATIENTS"
  cur = con.cursor()
  cur.execute(sql)
  con.commit()
  con.close()

def convert_to_excel(xls):
  con = create_connection(PATIENTS_DB)
  sql = "SELECT * FROM PATIENTS"
  df = pd.read_sql_query(sql, con)
  # print(df.head())
  df.to_excel(xls, index=False)
  con.close()

def open_excel_recs(xls):
  os.startfile(xls)

def get_records_num():
  con = create_connection(PATIENTS_DB)
  cur = con.cursor()
  recs = cur.execute("SELECT * FROM PATIENTS")
  rows = len(recs.fetchall())
  con.close()
  return rows

def print_records():
  con = create_connection(PATIENTS_DB)
  with con:
    for row in con.execute("SELECT * FROM PATIENTS"):
      print(row)
  con.close()


def main():
  create_patients_table()

  patient1 = ('Bagaskara', 11, 'HEAD', '20180209', 29, 1, 'Male', 10, 17.26, 9.66, 100, 96.8, 0.54)
  patient2 = ('Mayang', 11, 'HEAD', '20181031', 21, 2, 'Female', 10, 17.26, 9.66, 100, 96.8, 0.54)
  patient_id1 = insert_patient(patient1)
  patient_id2 = insert_patient(patient2)

if __name__ == '__main__':
  main()
  print_records()
