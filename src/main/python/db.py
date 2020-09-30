import sqlite3 as sl
import os
import json
import numpy as np
from scipy import interpolate

def get_db():
  with open('config.json', 'r') as f:
    js = json.load(f)
  return os.path.abspath(js['patients_db'])

def create_connection(db_file):
  conn = None
  try:
    conn = sl.connect(db_file)
  except sl.Error as e:
    print(e)
  return conn

def create_patients_table(path):
  # PATIENTS_DB_PATH = get_db()
  con = create_connection(path)
  with con:
    try:
      con.execute("""
        CREATE TABLE IF NOT EXISTS PATIENTS (
          ID INTEGER PRIMARY KEY,
          Name TEXT,
          Protocol_ID INTEGER,
          Protocol TEXT,
          Date TEXT,
          Age INTEGER,
          Sex_ID INTEGER,
          Sex TEXT,
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

def insert_patient(patient_data, path):
  # PATIENTS_DB_PATH = get_db()
  con = create_connection(path)
  sql = """INSERT INTO PATIENTS (Name, Protocol_ID, Protocol, Date, Age, Sex_ID, Sex, CTDIVol, DE_WED, SSDE, DLP, DLPc, Effective_Dose)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
  cur = con.cursor()
  cur.execute(sql, patient_data)
  con.commit()
  lastrowid = cur.lastrowid
  con.close()
  return lastrowid

def remove_patient(id, path):
  # PATIENTS_DB_PATH = get_db()
  con = create_connection(path)
  sql = "DELETE FROM PATIENTS WHERE id=?"
  cur = con.cursor()
  cur.execute(sql, (id,))
  con.commit()
  con.close()

def remove_all_patients(path):
  # PATIENTS_DB_PATH = get_db()
  con = create_connection(path)
  sql = "DELETE FROM PATIENTS"
  cur = con.cursor()
  cur.execute(sql)
  con.commit()
  con.close()

def get_records_num(path):
  # PATIENTS_DB_PATH = get_db()
  con = create_connection(path)
  cur = con.cursor()
  recs = cur.execute("SELECT * FROM PATIENTS")
  rows = len(recs.fetchall())
  con.close()
  return rows

def print_records(path, table):
  # PATIENTS_DB_PATH = get_db()
  con = create_connection(path)
  with con:
    for row in con.execute(f"SELECT * FROM {table}"):
      print(row)
  con.close()

def get_records(path, table):
  con = create_connection(path)
  data = []
  with con:
    for row in con.execute(f"SELECT * FROM {table}"):
      data.append(row[1:])
  con.close()
  return data

# path = r'D:\Undip\Project\InDoseCT\src\main\resources\base\db\aapm.db'
# data = np.array(get_records(path, 'Age'))
# # print(data)

# tck = interpolate.splrep(data[:,0], data[:,1])
# y = interpolate.splev(2.3, tck)
# print(y)

# def main():
#   create_patients_table()

#   patient1 = ('MACHRUP, TN', None, 'HEAD', '20150128', 72, 1, 'M', 7.0, 17.290882261324896, None, 70.0, None, None)
#   patient2 = ('XXXXXX-001', None, None, '20170209', None, None, None, 6.0, 15.613011979837614, None, 138.0, None, None)
#   patient_id1 = insert_patient(patient1)
#   patient_id2 = insert_patient(patient2)

# if __name__ == '__main__':
#   main()
#   print_records()
