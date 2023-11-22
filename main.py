import facebook_scraper
import json
import unittest
import json
import pandas as pd
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi import Request
from sqlalchemy.orm import sessionmaker, Session, declarative_base
import MySQLdb
import csv
import  sqlite3
from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
        
          

data_path = r"C:\Users\fares\OneDrive\Bureau"
fb = facebook_scraper.Facebook_scraper("spacextechnologies",20,"firefox")
#fb.scrap_to_csv("spacex",data_path)

data = fb.scrap_to_json()
data = fb.get_csv('f',json.loads(data))
# Database 
with open(data, 'r') as file:
    
    df = pd.read_csv(file)
connection = sqlite3.connect('mydb.db')
cursor = connection.cursor()
cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS scrap (
               id TEXT,
               name TEXT,
               shares INTEGER,
               likes INTEGER,
               loves INTEGER,
               wow INTEGER,
               cares INTEGER,
               sad INTEGER,
               angry INTEGER,
               haha INTEGER,
               reaction_count INTEGER,
               comments INTEGER,
               content TEXT,
               posted_on DATE,
               video TEXT,
               image TEXT,
               post_url TEXT

    )
''')

#print(df)
df.to_sql('scrap', connection, if_exists='replace', index=False)
connection.commit()
connection.close()


connection = sqlite3.connect('mydb.db')
cursor = connection.cursor()
select_query = "SELECT * FROM scrap"
cursor.execute(select_query)

# Fetch all the results
results = cursor.fetchall()

# Display the results
#for row in results:
#    print(row)

connection.close()
# FastAPI app
app = FastAPI()



def get_cursor():
    connection = sqlite3.connect('mydb.db')
    cursor = connection.cursor()
    try:
        yield cursor
    finally:
        cursor.close()
        connection.close()
templates = Jinja2Templates(directory="templates")
select_query = "SELECT * FROM scrap"

# Endpoint to display results in a web app
@app.get("/show_results")
def show_results(request: Request, cursor: sqlite3.Cursor = Depends(get_cursor)):
    cursor.execute(select_query)
    # Fetch all the results
    results = cursor.fetchall()
    for row in results:
        print(row)
    # Render the results using an HTML template
    return templates.TemplateResponse("results.html", {"request": request, "results": results})
