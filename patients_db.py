import sqlite3 as sl

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
          id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
          name TEXT,
          protocol_num INTEGER,
          protocol TEXT,
          date TEXT,
          age INTEGER,
          sex_id INTEGER,
          sex TEXT,
          CTDIVol REAL,
          Diameter REAL,
          SSDE REAL,
          DLP REAL,
          DLPc REAL,
          eff_dose REAL
        );
      """)
    except sl.Error as e:
      print(e)

def insert_patient(con, patient_data):
  sql = """INSERT INTO PATIENTS (name, protocol_num, protocol, date, age, sex_id, sex, CTDIVol, Diameter, SSDE, DLP, DLPc, eff_dose)
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
  con.commit()

def main():
  db_file = 'db/patient_data.db'
  con = create_connection(db_file)
  create_patients_table(con)

  with con:
    patient1 = ('Heru', 11, 'HEAD', '20180209', 29, 1, 'Male', 10, 17.26, 9.66, 100, 96.8, 0.54)
    patient_id = insert_patient(con, patient1)
  
if __name__ == '__main__':
  main()

  # db_file = 'db/patient_data.db'
  # con = create_connection(db_file)
  # with con:
  #   q = con.execute("SELECT * FROM PATIENTS")
  #   for row in q:
  #     print(row)
