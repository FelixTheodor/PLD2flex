from flask import Flask, request, render_template, send_from_directory, make_response, current_app, session, redirect, url_for
from werkzeug.utils import secure_filename
import os
import Levenshtein20 as LS
from datetime import datetime
import files
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['txt'])

app = Flask(__name__)
app.secret_key = ";8};\xec\x7f\x88'9\x04\x08\t\xcd\xd5ze"

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def delete_folder(pth) :
    pth_new = os.listdir(pth)
    for sub in pth_new:
        if sub != "results" and sub != "protocols" and sub != ".DS_Store":
            os.remove(pth + sub)
        else:
            delete_folder(pth + "results/")
            delete_folder(pth + "protocols/")


@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    delete_folder(os.curdir + "/uploads/")
    return redirect(url_for('index'))

def protocol(string, version):
    """
    The function protocol(string, version) prints a string into the protocol file
    If the version is 1 it also prints the result into the result file
    :param string: Output
    :param version: version == 0: only prints into protocol file; version == 1: prints also into the result file
    """
    result = ""
    with (open(files.filePro, encoding = "utf-8", mode = "a")) as fileProtocol:
        fileProtocol.write("\n" + string + "\n")
    if version == 1:
        with (open(files.fileRes, encoding="utf-8", mode="a")) as fileResult:
            fileResult.write("\n" + string + "\n")
    with (open(files.filePro, encoding = "utf-8", mode = "r")) as fileProtocol:
        protocol = fileProtocol.read()
    if version == 1:
        with (open(files.fileRes, encoding="utf-8", mode="r")) as fileResult:
            result = fileResult.read()
    return protocol, result


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)
    # Das ist der Inhalt der Datei


@app.route('/', methods=['GET', 'POST'])
def index():
    user = str(datetime.now().isoformat(timespec='seconds'))
    if "login" in request.form and request.form['userid'] != "":
        if request.form['userid'] != "":
            user = request.form['userid']
        #else:
        #    delete_folder(os.curdir + "/uploads")
        session['username'] = user
        files.filePro = os.curdir + "/uploads/protocols/protocol-" + session['username'] + ".csv"
        files.fileRes = os.curdir + "/uploads/results/result-" + session['username'] + ".csv"
        if os.path.isdir(files.filePro) == False:
            with (open(files.filePro, encoding="utf-8", mode="a")) as fileProtocol:
                fileProtocol.write("")
        if os.path.isdir(files.fileRes) == False:
            with (open(files.fileRes, encoding="utf-8", mode="a")) as fileResult:
                fileResult.write("")
        return render_template("PLD20.html", user = session['username'], file1 = files.filePro[1:], file2 = files.fileRes[1:])

    if 'username' in session:
        name = session['username']
    else:
        name = user


    files.filePro = os.curdir + "/uploads/protocols/protocol-" + name + ".csv"
    files.fileRes = os.curdir + "/uploads/results/result-" + name + ".csv"

    if os.path.isdir(files.filePro) == False:
        with (open(files.filePro, encoding="utf-8", mode="a")) as fileProtocol:
            fileProtocol.write("")

    if os.path.isdir(files.fileRes) == False:
        with (open(files.fileRes, encoding="utf-8", mode="a")) as fileResult:
            fileResult.write("")

    if "logout" in request.form:
        return redirect(url_for('logout'))

    result = ""
    res = ""
    pro = ""
    if request.method == 'POST':
        # if button list is pushed and the user has given a list of words and a target word
        if "list" in request.form and (request.form['target'] != "Insert target here" and request.form['target'] != "")\
            and (request.form['words'] != "Insert list of words here" and request.form['words'] != ""):
            print (request.form['words'])
            target = request.form['target']
            words = request.form['words']
            if "\n" in words:
                words = words.split("\n")
            elif "," in words:
                words = words.split(",")
            elif " " in words:
                words = words.split(" ")
            else:
                words = [words]
            print (words)
            if words == []:
                # error 7
                protocol("No data: input", 0)
            else:
                print (words)
                if len(words) < 20:
                    pro, res = protocol("These are less than 20 words!", 0)
                elif len(words) > 20:
                    pro, res = protocol("These are more than 20 words!", 0)
                try:
                    result = LS.getInfos(liste=words, w1=target)
                except:
                    pro, res = protocol("Data not appropriate", 0)

            # vielleicht immer den Datei Inhalt ausgeben??? Klingt eigentlich einfach und könnte man hier machen
            # Dann müsste ich nur, wie in meiner urpsrünglichen Datei, alles mitschreiben
            # Das könnte ich dann auch mit dem Protokoll machen
            # sieht nur nicht so schön aus
            # sonst vielleicht die geschweiften Klammern als Text in den output???
            #  hab es in das Textfeld geschafft!!!!!
            # return jsonify(output= str(result[0]) + str(result[1]))

        # r
        elif "list" in request.form and (request.form['target'] != "Insert target here" and request.form['target'] != "") and (request.form[
            'words'] == "Insert list of words here" or request.form['words'] == "") and 'fileField' in request.files:

            file = request.files['fileField']
            if file and allowed_file(file.filename):
                if 'Options2' in request.form:
                    target = request.form['target']
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    result = LS.getInfos(file="uploads/" + filename, w1=target)

        # wenn keine checkbox????
        elif "list" in request.form and (request.form['target'] == "Insert target here" or request.form['target'] == "")and (request.form[
            'words'] == "Insert list of words here" or request.form['words'] == "")and 'fileField' in request.files:
            try:
                file = request.files['fileField']
                output = ""
                # wenn zwei columns
                if file and allowed_file(file.filename):
                    if 'Options1' in request.form and 'Options2' in request.form:
                        pro, res = protocol("Please only use one Checkbox!", 0)
                    elif 'Options1' not in request.form and 'Options2' not in request.form:
                        pro, res = protocol("Please only use a Checkbox!", 0)
                    elif 'Options1' in request.form:
                        filename = secure_filename(file.filename)
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        fileTwo = open("uploads/" + filename, mode="r", encoding="utf-8")
                        # inhalt der eingelesenen Datei
                        # calculating the levenshtein-distance for each line of the text file (two words)
                        liste = fileTwo.read().split("\n")
                        fileTwo.close()
                        error = True
                        for word in liste:
                            if "\t" in word:
                                error = False
                                word = word.split("\t")
                                word[0] = LS.translate(w1=word[0])
                                word[1] = LS.translate(w1=word[1])

                                lev = LS.levenshtein(word[0], word[1])
                                # function prints the results
                                # ui.output.insertPlainText(word[0] + "\t" + word[1] + "\tdistance: " + str(lev) + "\n")
                                output += word[0] + ";" + word[1] + ";" + str(lev) + "\n"
                                # error 7
                                if error == True:
                                    pro,res = protocol("Only one column found!", 0)
                                    break
                        result = output
                    elif 'Options2' in request.form:
                        filename = secure_filename(file.filename)
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        lev, cross = LS.getInfos(file="uploads/" + filename, w1="")
                        output = ""
                        # function prints the results
                        for tuple in cross:
                            output += tuple[0] + ";" + tuple[1] + ";" + str(tuple[2]) + "\n"
                        result = ""
                        pro, res = protocol("Tested file " + "uploads/" + filename + " with cross validation. mean = " + str(lev) + "\n" + output, 1)
            except:
                protocol("Cannot read file:" + "uploads/" + filename, 0)



        elif "subtlex" in request.form and (request.form['target'] != "Insert target here" and request.form['target'] != ""):
            target = request.form['target']
            result = LS.automatic(target, [os.curdir + "/corpora/Phon-SUBTLEX-DE.txt"])

        #wenn keine angegebenP???
        elif "database" in request.form and 'corpusField' in request.files and (request.form[
            'target'] != "Insert target here" or request.form['target'] != ""):
            target = request.form['target']
            file = request.files['corpusField']
            if file and allowed_file(file.filename):
                corpusname = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], corpusname))
                with open("uploads/" + corpusname, mode="r") as fileTest:
                    if ";" not in fileTest.readlines()[0]:
                        protocol("No corpus found", 0)
                    else:
                        # function calls automatic(target word, file) which calculates the distances and extracts the 20 nearest words
                        result = LS.automatic(target, ["uploads/" + corpusname])
                        protocol("Tested " + target + " with the given corpus.\nLevenshtein-distance: ;" + str(
                                result[0]) + "\n" + "\n".join(result[1]).replace("\t", ";"), 1)

                # function calls automatic(target word, file) which calculates the distances and extracts the 20 nearest words
                result = LS.automatic(target, ["uploads/" + corpusname])
            else:
                protocol("No corpus found", 0)


        elif "database" in request.form or "list" in request.form or "subtlex" in request.form:
            if (request.form['words'] == "Insert list of words here" or request.form['words'] == "") and "list" in request.form:
                pro, res = protocol("No data: list of words", 0)
            if 'fileField' not in request.files and "list" in request.form:
                pro, res = protocol("No data: input file", 0)
            if 'corpusField' not in request.files and "database" in request.form:
                pro, res = protocol("No data: corpus file", 0)
            if (request.form['target'] == "Insert target here" or request.form['target'] == ""):
                pro, res = protocol("No data: input", 0)
            else:
                pro,res = protocol("No data", 0)

            return render_template("PLD20.html", output=res, protocol_output=pro, user = name, file1 = files.filePro[1:], file2 = files.fileRes[1:])

        print (result)
        if result != "":
            #addOutput(result[0], result[1])
            pro, res = protocol("Tested " + request.form['target'] + ".\nLevenshtein-distance: ;" + str(result[0]) + "\n" + "\n".join(
                    result[1]).replace("\t", ";"), 1)

    return render_template("PLD20.html", output=res, protocol_output=pro, user = name, file1 = files.filePro[1:], file2 = files.fileRes[1:])

@app.route('/uploads/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    uploads = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])
    return send_from_directory(directory=uploads, filename=filename, as_attachment = True)

if __name__ == "__main__":
    app.debug = False
    app.run(host='0.0.0.0')


