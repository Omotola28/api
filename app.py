from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename


import os
import PyPDF2
import textract
import re

UPLOAD_FOLDER = "C:/Users/omotola.shogunle/PycharmProjects/api/resources/"
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'html'}


app = Flask(__name__, template_folder='template')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
basedir = os.path.abspath(os.path.dirname(__file__))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in \
         ALLOWED_EXTENSIONS


def extract_text(filename):
    print(filename)
    pdfFileObj = open(filename, 'rb')

    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

    num_pages = pdfReader.numPages

    count = 0
    text = ""

    while count < num_pages:
        pageObj = pdfReader.getPage(count)
        count += 1
        text += pageObj.extractText()

    if text != "":
        text = text
        return text
    else:
        text = textract.process(filename, method="tesseract", encoding="ascii")
        # re.sub("\s\s+", " ", text, re.MULTILINE)
        return text


def extract_thejuice(textfile):
    pattern = r"(?<=[^\n][^a-z][^A-Z][\s{1}0-9]$\n)^[\s]*(.*?)[\s]*$"
    pattern1 = r'-\s(Page|Location)\s[0-9]+'
    chapterMatch = r"^(CHAPTER)\s[A-Za-z]+:\s.*$"
    deleteMatch = '^.*(API).*$'
    # pattern2='\n?[^\r\n]+((\r|\n|\r\n)[^\r\n]+)*'
    highlightMatch = r"-\s(Page|Location)\s[0-9]+\n{1,2}[^\r\n]+((\r|\n|\r\n)[^\r\n]+)*"

    with open("demofile.txt") as fp:
        read = fp.read()

    gotback = {}
    regex = re.compile(highlightMatch, re.MULTILINE)
    matches = regex.finditer(read)

    for matchNum, match in enumerate(matches, start=1):
        gotback[matchNum] = match.group().replace("\n", " ")

    return jsonify(gotback)


@app.route('/handle_form', methods=['POST'])
def add_product():
    print("Posted file: {}".format(request.files['file']))

    if 'file' not in request.files:
        return "Invalid file format"

    file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        return "No file selected"
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        print(filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        text = extract_text("C:/Users/omotola.shogunle/PycharmProjects/api/resources/" + filename)
        f = open("demofile.txt", "wb")
        f.write(text)
        f.close()
    return extract_thejuice("/demofile.txt")


@app.route("/", methods=['GET'])
def index():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(debug=True)
