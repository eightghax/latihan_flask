from flask import Flask, render_template, request, jsonify
import re
import string
import pandas as pd
import numpy as np
import nltk
from nltk.corpus import stopwords
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
import sqlite3
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from

app = Flask(__name__)




def fungsi_tokenize(text):
    return nltk.tokenize.word_tokenize(text)

def fungsi_cleantext(text):
    text = text.lower()
    text = re.sub('\[.*\]','', text).strip()
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = re.sub('\S*\d\S*\s*','', text).strip()
    return text.strip()

def fungsi_cleanalay(text):
    alay_dict = pd.read_csv('kamusalay.csv', encoding='latin-1')
    alay_dict = dict(zip(alay_dict['slang'], alay_dict['formal']))
    cleaned_text = []
    for word in text.split():
        if word in alay_dict:
            cleaned_text.append(alay_dict[word])
        else:
            cleaned_text.append(word)
    return " ".join(cleaned_text)

def fungsi_stem(text):
    factory = StemmerFactory()
    stemmer = factory.create_stemmer()
    cleaned_alay = fungsi_cleanalay(text)
    return stemmer.stem(cleaned_alay)

def fungsi_removestopwords(text):
    stop_factory = StopWordRemoverFactory()
    stopwords = stop_factory.create_stop_word_remover()
    cleaned_alay = fungsi_cleanalay(text)
    return stopwords.remove(cleaned_alay)

import dbconf

def fungsi_simpanlog(metode,strout):
    conn = sqlite3.connect(dbconf.DBNAME)
    c = conn.cursor()
    c.execute(f'CREATE TABLE IF NOT EXISTS {dbconf.TABLE} (metode text, strout text)')
    c.execute(f'DELETE FROM {dbconf.TABLE}')
    c.execute(f'INSERT INTO {dbconf.TABLE} VALUES (?,?)', (metode,strout))
    conn.commit()
    conn.close()
    return "Hasil terakhir berhasil disimpan."

def fungsi_tampillog():
    txt = ""
    conn = sqlite3.connect(dbconf.DBNAME)
    c = conn.cursor()
    c.execute(f'SELECT * FROM {dbconf.TABLE}')
    rows = c.fetchall()
    for row in rows:
        txt = row[1]
    conn.close()
    return txt
    
def bungkus_json(txtoutput,metode):
    import json
    obj = {'hasil':txtoutput,'metode':metode}
    return json.dumps(obj)

app.json_encoder = LazyJSONEncoder
swagger_template = dict(
    info = {
        'title': LazyString(lambda: 'API Documentation for Data Preprocessing and Modeling'),
        'version': LazyString(lambda: '1.0.0'),
        'description': LazyString(lambda: 'Dokumentasi API untuk Data Processing dan Modeling')
 
    },
    host = LazyString(lambda: request.host)
    )

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'docs',
            "route": '/docs.json',
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs"
}

swagger = Swagger(app, template=swagger_template, config=swagger_config)
@swag_from("docs/user.yml", methods=['GET','POST'])
@app.route('/api', methods=['GET'])
def hello_world():
    json_response = {
        'status_code': 200,
        'description': "Menyapa Hello World",
        'data': "Hello World",
    }

    response_data = jsonify(json_response)
    return response_data


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/proses',methods = ['POST'])
def proses():
    metode = request.form['metode']
    strinput = request.form['input']
    stroutput = ""

    if metode == "tokenize":
        stroutput = fungsi_tokenize(strinput)
    elif metode == "clean":
        stroutput = fungsi_cleantext(strinput)
    elif metode == "clean alay":
        stroutput = fungsi_cleanalay(strinput)
    elif metode == "stem":
        stroutput = fungsi_stem(strinput)
    elif metode == "remove stopwords":
        stroutput = fungsi_removestopwords(strinput)
    elif metode == "simpan":
        stroutput = fungsi_simpanlog(metode,strinput)
    elif metode == "load":
        stroutput = fungsi_tampillog()
    return bungkus_json(stroutput,metode)

if __name__ == '__main__':
    app.run()