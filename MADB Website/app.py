from flask import Flask, render_template
import csv
import json

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route('/')
def mainpg():
    return render_template("Main_Page.html")

@app.route('/Main_Page.html')
def mainpg2():
    return render_template("Main_Page.html")

@app.route('/Tool.html')
def tool():
    return render_template("Tool.html")

@app.route('/Overview.html')
def overview():
    return render_template("Overview.html")

@app.route('/How_It_Works.html')
def readme():
    return render_template("How_It_Works.html")

@app.route('/Bios.html')
def bios():
    return render_template("Bios.html")

#if __name__ == '__main__':
#    app.run(debug=True)
