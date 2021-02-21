from flask import Flask, render_template, request
app = Flask(__name__)

#functions
def fungsi_md5(strinput):
    import hashlib
    m = hashlib.md5()
    m.update(strinput)
    return m.hexdigest()

def fungsi_base64(strinput):
    import base64
    message_bytes = strinput.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')
    return base64_message

def fungsi_reverse(strinput):
    return strinput[::-1]
    
def bungkus_json(txtoutput,metode):
    import json
    obj = {'hasil':txtoutput,'metode':metode}
    return json.dumps(obj)
    

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/proses',methods = ['POST'])
def proses():
    metode = request.form['metode']
    strinput = request.form['input']
    stroutput = "error!"
    if metode == "base64":
        stroutput = fungsi_base64(strinput)
    elif metode == "md5":
        stroutput = fungsi_md5(strinput)
    elif metode == "reverse":
        stroutput = fungsi_reverse(strinput)
    return bungkus_json(stroutput,metode)

if __name__ == '__main__':
    app.run()