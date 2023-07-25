from flask import Flask
from threading import Thread

app = Flask('')


@app.route('/')
def home():
    html_code = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Bot en línea</title>
    </head>
    <body>
        <h1>Bot en línea</h1>
        <p>Bienvenido a mi bot en línea.</p>
        <p>
        <p>Por: YoandyC.</p>
    </body>
    </html>
    """
    return html_code

def run():
  app.run(host='0.0.0.0',port=8080)

def live():  
    t = Thread(target=run)
    t.start()