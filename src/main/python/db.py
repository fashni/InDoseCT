import sqlite3 as sl
import os
import json
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtSql import QSqlDatabase

class Database(object):
  def __init__(self, **kwargs):
    self.keys = []
    for key, value in kwargs.items():
      setattr(self, key, value)
      self.keys.append(key)
    print(self.keys)
    self.set_connection()
    print('db estabilished')

  def set_connection(self):
    for key in self.keys:
      setattr(self, key+'_db', QSqlDatabase.addDatabase("QSQLITE", key+"_connection"))
      db = getattr(self, key+'_db')
      db.setDatabaseName(getattr(self, key))
      if not db.open():
        QMessageBox.warning(None, "Database Error:", f"{db.lastError().text()}")

  def update_connection(self, key, new_db):
    if not hasattr(self, key+'_db'):
      QMessageBox.warning(None, "Database Error", f"No db connection with the name {key}")
      return
    db = getattr(self, key+'_db')
    path = getattr(self, key)
    db.close()
    db.removeDatabase(path)
    db.setDatabaseName(new_db)
    setattr(self, key, new_db)
    if not db.open():
      QMessageBox.warning(None, "Database Error:", f"{db.lastError().text()}")


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
  con = create_connection(path)
  with con:
    try:
      con.execute("""
        CREATE TABLE IF NOT EXISTS PATIENTS (
          id INTEGER PRIMARY KEY,
          name TEXT,
          protocol TEXT,
          exam_date TEXT,
          age INTEGER,
          sex TEXT,
          CTDIvol REAL,
          diameter REAL,
          diameter_type TEXT,
          SSDE REAL,
          DLP REAL,
          DLPc REAL,
          effective_dose REAL
        );
      """)
    except sl.Error as e:
      print(e)
  con.close()

def insert_patient(patient_data, path):
  con = create_connection(path)
  sql = """INSERT INTO PATIENTS (name, protocol, exam_date, age, sex, CTDIvol, diameter, diameter_type, SSDE, DLP, DLPc, effective_dose)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
  cur = con.cursor()
  cur.execute(sql, patient_data)
  con.commit()
  lastrowid = cur.lastrowid
  con.close()
  return lastrowid

def remove_record(path, table, id):
  con = create_connection(path)
  sql = f"DELETE FROM {table} WHERE id={id}"
  cur = con.cursor()
  cur.execute(sql)
  con.commit()
  con.close()

def remove_all_records(path, table):
  con = create_connection(path)
  sql = f"DELETE FROM {table}"
  cur = con.cursor()
  cur.execute(sql)
  con.commit()
  con.close()

def get_records_num(path, table):
  con = create_connection(path)
  cur = con.cursor()
  recs = cur.execute(f"SELECT * FROM {table}")
  rows = len(recs.fetchall())
  con.close()
  return rows

def print_records(path, table):
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
