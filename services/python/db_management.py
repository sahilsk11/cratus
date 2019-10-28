import psycopg2
import random

connection = psycopg2.connect(user="postgres", password="postgres",
                              host="localhost", port="5432", database="cratus-data")

def add():
  postgres_insert_query = """INSERT INTO mini_employee (name, employee_id, age) VALUES (%s,%s,%s)"""
  cursor = connection.cursor()
  for i in range(0, 9000):
  	record_to_insert = ("User"+str(random.randint(100, 200)), "purdue"+str(random.randint(0, 10)), "0")
  	cursor.execute(postgres_insert_query, record_to_insert)
  	connection.commit()

def get():
  postgres_get_query = """SELECT * FROM mini_employee"""
  cursor = connection.cursor()
  cursor.execute(postgres_get_query)
  print(cursor.fetchall())
  
  
add()
