from flask import Flask, flash, redirect, render_template
from flask import request, session, abort, url_for
from flask_mail import Mail
from flask_login import LoginManager, current_user, login_required
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.sql import select
from unidecode import unidecode
from details_table import Details
from user_table import User
from projects_table import Projects
from traffic_table import Traffic
from mail import send_bug_report
from copy import copy
import datetime
import sqlite3
import glob
import time
import os
import re
import inspect
import logging
import json

engine = create_engine('sqlite:///tutorial.db', echo=True)

UserName = ''

app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'iamjustice443@gmail.com'
app.config['MAIL_PASSWORD'] = 'iamsanketh1'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
login_manager = LoginManager(app)
error_list = []


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/index')
def index():
    try:
        if not session.get('logged_in'):
            return render_template('login.html')
        else:
            return render_template('index.html', data={})
    except Exception as error:
        if inspect.stack()[0][3] not in error_list:
            send_bug_report(app, mail, inspect.stack()[0][3], str(error))
            error_list.append(inspect.stack()[0][3])

@app.route("/tutorial")
def tutorial():
    return render_template('tutorial.html')


@app.route("/traffic")
def traffic():
    labels = []
    values = []
    conn = sqlite3.connect('traffic.db')
    cursor = conn.cursor()
    query = 'SELECT * FROM traffic'
    lists = cursor.execute(query)
    for item in lists:
        labels.append(item[1])
        values.append(item[2])
    cursor.close()
    return render_template('traffic.html', values=values, labels=labels)


@app.route('/login', methods=['POST'])
def do_admin_login():
    try:
        POST_USERNAME = str(request.form['username'])
        POST_PASSWORD = str(request.form['password'])
        Session = sessionmaker(bind=engine)
        s = Session()
        query = s.query(User).filter(User.username.in_(
            [POST_USERNAME]), User.password.in_([POST_PASSWORD]))
        session['username'] = POST_USERNAME
        result = query.first()
        if result:
            session['logged_in'] = True
            conn = sqlite3.connect('traffic.db')
            cursor = conn.cursor()
            query = 'SELECT * FROM traffic'
            result = cursor.execute(query)
            result_list = result.fetchall()
            flag = 0
            count = 0
            cursor.close()
            for results in result_list:
                if str(datetime.date.today()) in results:
                    flag = 1
                    count = results[-1]+1
            engine2 = create_engine('sqlite:///traffic.db', echo=True)
            Session2 = sessionmaker(bind=engine2)
            session2 = Session2()
            if flag:
                query = 'DELETE FROM traffic WHERE date = \''+str(datetime.date.today())+'\''
                session2.execute(query)
            traffic = Traffic(str(datetime.date.today()), count)
            session2.add(traffic)
            session2.commit()
            session2.close()
        else:
            flash('Wrong password!')
        return redirect(url_for('home'))
    except Exception as error:
        if inspect.stack()[0][3] not in error_list:
            send_bug_report(app, mail, inspect.stack()[0][3], str(error))
            error_list.append(inspect.stack()[0][3])


@app.route("/logout")
def logout():
    try:
        session.pop('username', None)
        session['logged_in'] = False
        return redirect(url_for('home'))
    except Exception as error:
        if inspect.stack()[0][3] not in error_list:
            send_bug_report(app, mail, inspect.stack()[0][3], str(error))
            error_list.append(inspect.stack()[0][3])


@app.route("/admin")
def admin():
    try:
        return render_template('adminlogin.html')
    except Exception as error:
        if inspect.stack()[0][3] not in error_list:
            send_bug_report(app, mail, inspect.stack()[0][3], str(error))
            error_list.append(inspect.stack()[0][3])


@app.route("/db", methods=['POST'])
def db():
    user = str(request.form['username'])
    password = str(request.form['password'])
    if(user == "admin" and password == "bsrc123"):
        return render_template('admin.html')
    else:
        return render_template('login.html')


@app.route("/query")
def query():
    try:
        conn = sqlite3.connect('details.db')
        cursor = conn.cursor()
        query = 'SELECT * FROM users'
        result = cursor.execute(query)
        result_list = result.fetchall()
        cursor.close()
        return render_template('query.html', students=result_list)
    except Exception as error:
        if inspect.stack()[0][3] not in error_list:
            send_bug_report(app, mail, inspect.stack()[0][3], str(error))
            error_list.append(inspect.stack()[0][3])


@app.route("/search")
def search():
    try:
        return render_template('search.html')
    except Exception as error:
        if inspect.stack()[0][3] not in error_list:
            send_bug_report(app, mail, inspect.stack()[0][3], str(error))
            error_list.append(inspect.stack()[0][3])


@app.route("/searchres", methods=['POST'])
def searchres():
    user = str(request.form['username'])
    conn = sqlite3.connect('details.db')
    cursor = conn.cursor()
    query = 'SELECT * FROM users WHERE username = \''+str(user)+'\''
    result = cursor.execute(query)
    result_list = result.fetchall()
    cursor.close()
    return render_template('query.html', students=result_list)


@app.route("/delete")
def delete():
    try:
        return render_template('delete.html')
    except Exception as error:
        if inspect.stack()[0][3] not in error_list:
            send_bug_report(app, mail, inspect.stack()[0][3], str(error))
            error_list.append(inspect.stack()[0][3])


@app.route("/deletefunc", methods=['POST'])
def deletefunc():
    user = str(request.form['username'])
    conn = sqlite3.connect('details.db')
    cursor = conn.cursor()
    query = 'DELETE FROM users WHERE username = \''+str(user)+'\''
    cursor.execute(query)
    cursor.close()
    return redirect(url_for('query'))


@app.route("/signup")
def signuppage():
    try:
        return render_template('signup.html')
    except Exception as error:
        if inspect.stack()[0][3] not in error_list:
            send_bug_report(app, mail, inspect.stack()[0][3], str(error))
            error_list.append(inspect.stack()[0][3])


@app.route("/signup", methods=['POST'])
def addtodb():
    name = str(request.form['name'])
    email = str(request.form['email'])
    number = str(request.form['number'])
    username = str(request.form['username'])
    password = str(request.form['password'])
    engine = create_engine('sqlite:///details.db', echo=True)
    Session1 = sessionmaker(bind=engine)
    session1 = Session1()
    user1 = Details(username, number, name, email, password)
    session1.add(user1)
    session1.commit()
    session1.close()
    engine2 = create_engine('sqlite:///tutorial.db', echo=True)
    Session2 = sessionmaker(bind=engine2)
    session2 = Session2()
    user2 = User(username, password)
    session2.add(user2)
    session2.commit()
    session2.close()
    return render_template('login.html')


@app.route("/projects")
def display_projects():
    try:
        if(session['logged_in'] is False):
            return render_template('login.html')
        else:
            username = session['username']
            conn = sqlite3.connect('projects.db')
            cursor = conn.cursor()
            query = 'SELECT id,username,projectname FROM projects WHERE username = \'' + str(username)+ '\''
            result = cursor.execute(query)
            projects_list = result.fetchall()
            cursor.close()
            return render_template('projects.html', projects=projects_list)
    except Exception as error:
        if inspect.stack()[0][3] not in error_list:
            send_bug_report(app, mail, inspect.stack()[0][3], str(error))
            error_list.append(inspect.stack()[0][3])


@app.route("/projects/<idno>")
def retreive_projects(idno):
    try:
        if(session['logged_in'] is False):
            return render_template('login.html')
        else:
            conn = sqlite3.connect('projects.db')
            cursor = conn.cursor()
            query = 'SELECT username,projectname,data FROM projects WHERE id = \''+str(idno)+ '\''
            result = cursor.execute(query)
            projects_list = result.fetchall()
            cursor.close()
            return render_template('index.html', data=json.loads(projects_list[0][2]))
    except Exception as error:
        if inspect.stack()[0][3] not in error_list:
            send_bug_report(app, mail, inspect.stack()[0][3], str(error))
            error_list.append(inspect.stack()[0][3])


@app.route("/delete_projects/<idno>")
def delete_projects(idno):
    try:
        if(session['logged_in'] is False):
            return render_template('login.html')
        else:
            conn = sqlite3.connect('projects.db')
            cursor = conn.cursor()
            query = 'DELETE from projects where id = \'' + str(idno) + '\''
            cursor.execute(query)
            cursor.close()
            return redirect(url_for('display_projects'))
    except Exception as error:
        if inspect.stack()[0][3] not in error_list:
            send_bug_report(app, mail, inspect.stack()[0][3], str(error))
            error_list.append(inspect.stack()[0][3])


@app.route('/success/<name>')
def success(name):
    try:
        Username = session['username']
        if(session['logged_in'] is False):
            return render_template('login.html')
        Dict = {}
        tempo = name
        tempo1 = name
        tempo2 = name
        ash = name

        executable = "runenergyplus"
        execute_on = "./static/Data/"
        epw_location = "/usr/local/EnergyPlus-8-6-0/WeatherData/1.epw"

        os.system(executable + " " + execute_on + UserName + tempo + "input/" +
                  tempo + ".idf " + epw_location)
        htmlfiles = glob.glob("./static/Data/" + UserName + tempo +
                              "input/Output/*.html")
        pattern1 = '<td align="right">Total Site Energy</td>'
        pattern2 = "\d+.\d+"
        for htmlfile in htmlfiles:
            tuple1 = ()
            tuple2 = ()
            f = open(htmlfile, "r")
            for line in f:
                tuple1 = re.findall(pattern1, line, re.M)
                if len(tuple1) > 0:
                    break
            for line in f:
                tuple2 = re.findall(pattern2, line)
                break
        Dict[tempo+'input'] = tuple2[0]
        x = float(ash)*20
        rem = float(x % 4)
        if(rem == 3):
            os.system(executable + " " + execute_on + UserName +
                      str((float(x)-float(rem)+1)/20) + "/" +
                      str((float(x)-float(rem)+1)/20) +
                      ".idf " + epw_location + " &!" +
                      " " + executable + " " + execute_on + UserName +
                      str((float(x)-float(rem)+2)/20) + "/" +
                      str((float(x)-float(rem)+2)/20) +
                      ".idf " + epw_location + " &!" +
                      " " + execute + " " + execute_on + UserName +
                      str((float(x)-float(rem)+3)/20) + "/" +
                      str((float(x)-float(rem)+3)/20) +
                      ".idf " + epw_location)
        elif(rem == 2):
            os.system(executable + " " + execute_on + UserName +
                      str((float(x)-float(rem)+2)/20) + "/" +
                      str((float(x)-float(rem) + 2)/20) +
                      ".idf " + epw_location + " &!" +
                      " " + execute + " " + execute_on + UserName +
                      str((float(x)-float(rem) + 1)/20) + "/" +
                      str((float(x)-float(rem) + 1)/20) +
                      ".idf " + epw_location)
        elif(rem == 1):
            os.system(executable + " " + execute_on + UserName +
                      str((float(x)-float(rem) + 1)/20) + "/" +
                      str((float(x)-float(rem)+1)/20) +
                      ".idf " + epw_location)
        x = x - float(rem)
        while(float(x) > 0):
            os.system(executable + " " + execute_on + UserName +
                      str((float(x))/20) + "/" + str((float(x))/20) +
                      ".idf " + epw_location + " &!" +
                      str((float(x)-float(rem) + 1)/20) + "/" +
                      str((float(x)-float(rem)+1)/20) +
                      ".idf " + epw_location)
        x = x - float(rem)
        while(float(x) > 0):
            os.system(execute + " " + execute_on + UserName +
                      str((float(x))/20) + "/" + str((float(x))/20) +
                      ".idf " + epw_location + " &!" +
                      " " + execute + " " + execute_on + UserName +
                      str((float(x)-1)/20) + "/" + str((float(x)-1)/20) +
                      ".idf " + epw_location + " &!" +
                      " " + execute + " " + execute_on + UserName +
                      str((float(x)-2)/20) + "/" + str((float(x)-2)/20) +
                      ".idf " + epw_location + " &!" +
                      " " + execute + " " + execute_on + UserName +
                      str((float(x)-3)/20) + "/" + str((float(x)-3)/20) +
                      ".idf " + epw_location)
            x = x-4
        while (float(tempo) >= 0.05):
            time.sleep(1)
            rfilename = './static/Data/'+UserName + tempo+'/Output/*Table.html'
            htmlfiles = glob.glob(rfilename)
            pattern1 = '<td align="right">Total Site Energy</td>'
            pattern2 = "\d+.\d+"
            for htmlfile in htmlfiles:
                tuple1 = ()
                tuple2 = ()
                f = open(htmlfile, "r")
                for line in f:
                    tuple1 = re.findall(pattern1, line, re.M)
                    if len(tuple1) > 0:
                        break
                for line in f:
                    tuple2 = re.findall(pattern2, line)
                    break
            Dict[tempo] = tuple2[0]
            tempo = float(tempo) - 0.05
            tempo = str(tempo)
        while(float(tempo1) >= 0.05):
            if((Dict[tempo1] >= Dict[tempo2+'input']) and
               (Dict[str(float(tempo1)-0.05)] <= Dict[tempo2+'input'])):
                a = tempo1
                break
            else:
                tempo1 = float(tempo1) - 0.05
                tempo1 = str(tempo1)
        slope = (float(Dict[a])-float(Dict[str(float(a)-0.05)])) / (0.05)
        const = float(Dict[a]) - slope*(float(a))
        final_shgc = (float(Dict[str(tempo2) + 'input']) -
                      float(const))/float(slope)
        final_shgc = round(final_shgc, 2)

        return render_template('output.html', text=final_shgc)
    except Exception as error:
        if inspect.stack()[0][3] not in error_list:
            send_bug_report(app, mail, inspect.stack()[0][3], str(error))
            error_list.append(inspect.stack()[0][3])


@app.route('/ecbc', methods=['POST', 'GET'])
def ecbc():
    try:
        UserName = session['username']
        project_name = request.form['projectname']
        ecbc_Orientation = request.form['orien']
        ecbc_SHGC = request.form['shgc']
        ecbc_Win_H = request.form['wheight']
        ecbc_Win_L = request.form['wlength']
        ecbc_Building_L = float(ecbc_Win_L) + 2
        ecbc_Building_L = str(ecbc_Building_L)
        ohang = request.form['overhang']
        ecbc_Overhang_D = request.form['odepth']
        ecbc_Overhang_H = request.form['oheight']
        ecbc_Overhang_A = request.form['otilt']
        ecbc_Overhang_LE = request.form['le']
        ecbc_Overhang_RE = request.form['re']
        ecbc_Fin_L_E = request.form['fle']
        ecbc_Fin_L_AT = request.form['flda']
        ecbc_Fin_L_BB = request.form['fldb']
        ecbc_Fin_L_A = request.form['flt']
        ecbc_Fin_L_D = request.form['fld']
        ecbc_Fin_R_E = request.form['fre']
        ecbc_Fin_R_AT = request.form['frda']
        ecbc_Fin_R_BB = request.form['frdb']
        ecbc_Fin_R_A = request.form['frt']
        ecbc_Fin_R_D = request.form['frd']
        if request.form['finish'] == 'Save':
            engine = create_engine('sqlite:///projects.db', echo=True)
            Session = sessionmaker(bind=engine)
            s = Session()
            data = json.dumps(request.form)
            conn = sqlite3.connect('projects.db')
            cursor = conn.cursor()
            query = 'SELECT id from projects where username = \'' + session["username"] + '\' and projectname = \'' + project_name + '\''
            result = cursor.execute(query)
            result = result.fetchall()
            if result:
                idno = result[0][0]
                query = 'DELETE from projects where id = \'' + str(idno) + '\''
                s.execute(query)
            project = Projects(session['username'], project_name, data)
            s.add(project)
            s.commit()
            cursor.close()
            s.close()
            return render_template('index.html', data={})
        else:
            temp = ecbc_SHGC
            print('----------------------------------------------------------------' +
                  '-------------------')
            print(os.getcwd())
            os.system("mkdir" + ' ./static/Data/' + UserName + ecbc_SHGC+'input')
            with open('./static/template.idf', 'rt') as file1:
                 with open('./static/Data/' + UserName + ecbc_SHGC + 'input/' + ecbc_SHGC + '.idf', 'wt') as file2:
                    for line in file1:
                        line = line.decode('utf-8')
                        line = line.replace('ecbc_Overhang_D', ecbc_Overhang_D)
                        line = line.replace('ecbc_Overhang_H', ecbc_Overhang_H)
                        line = line.replace('ecbc_Overhang_A', ecbc_Overhang_A)
                        line = line.replace('ecbc_Overhang_LE', ecbc_Overhang_LE)
                        line = line.replace('ecbc_Overhang_RE', ecbc_Overhang_RE)
                        line = line.replace('ecbc_Fin_L_E', ecbc_Fin_L_E)
                        line = line.replace('ecbc_Fin_L_D', ecbc_Fin_L_D)
                        line = line.replace('ecbc_Fin_L_AT', ecbc_Fin_L_AT)
                        line = line.replace('ecbc_Fin_L_BB', ecbc_Fin_L_BB)
                        line = line.replace('ecbc_Fin_L_A', ecbc_Fin_L_A)
                        line = line.replace('ecbc_Fin_L_D', ecbc_Fin_L_D)
                        line = line.replace('ecbc_Fin_R_E', ecbc_Fin_R_E)
                        line = line.replace('ecbc_Fin_R_D', ecbc_Fin_R_D)
                        line = line.replace('ecbc_Fin_R_AT', ecbc_Fin_R_AT)
                        line = line.replace('ecbc_Fin_R_BB', ecbc_Fin_R_BB)
                        line = line.replace('ecbc_Fin_R_A', ecbc_Fin_R_A)
                        line = line.replace('ecbc_Fin_R_D', ecbc_Fin_R_D)
                        line = line.encode('utf-8')
                        file2.write(line)
            file1.close()
            file2.close()
            while (float(ecbc_SHGC) >= 0.05):
                os.system("mkdir" + ' ./static/Data/' + UserName + ecbc_SHGC)
                with open('./static/template_2.idf', 'rt') as file1:
                    with open('./static/Data/' + UserName + ecbc_SHGC + '/' +
                              ecbc_SHGC + '.idf', 'wt') as file2:
                        for line in file1:
                            line = line.decode('utf-8')
                            line = line.replace('ecbc_SHGC', ecbc_SHGC)
                            line = line.replace('ecbc_Win_H', ecbc_Win_H)
                            line = line.replace('ecbc_Win_L', ecbc_Win_L)
                            line = line.replace('ecbc_Orientation', ecbc_Orientation)
                            line = line.replace('ecbc_Building_L', ecbc_Building_L)
                            line = line.replace('ecbc_Overhang_D', ecbc_Overhang_D)
                            line = line.replace('ecbc_Overhang_H', ecbc_Overhang_H)
                            line = line.replace('ecbc_Overhang_A', ecbc_Overhang_A)
                            line = line.replace('ecbc_Overhang_LE', ecbc_Overhang_LE)
                            line = line.replace('ecbc_Overhang_RE', ecbc_Overhang_RE)
                            line = line.replace('ecbc_Fin_L_E', ecbc_Fin_L_E)
                            line = line.replace('ecbc_Fin_L_D', ecbc_Fin_L_D)
                            line = line.replace('ecbc_Fin_L_AT', ecbc_Fin_L_AT)
                            line = line.replace('ecbc_Fin_L_BB', ecbc_Fin_L_BB)
                            line = line.replace('ecbc_Fin_L_A', ecbc_Fin_L_A)
                            line = line.replace('ecbc_Fin_L_D', ecbc_Fin_L_D)
                            line = line.replace('ecbc_Fin_R_E', ecbc_Fin_R_E)
                            line = line.replace('ecbc_Fin_R_D', ecbc_Fin_R_D)
                            line = line.replace('ecbc_Fin_R_AT', ecbc_Fin_R_AT)
                            line = line.replace('ecbc_Fin_R_BB', ecbc_Fin_R_BB)
                            line = line.replace('ecbc_Fin_R_A', ecbc_Fin_R_A)
                            line = line.replace('ecbc_Fin_R_D', ecbc_Fin_R_D)
                            line = line.encode('utf-8')
                            file2.write(line)
                ecbc_SHGC = float(ecbc_SHGC) - 0.05
                ecbc_SHGC = str(ecbc_SHGC)
                file1.close()
                file2.close()
            return redirect(url_for('success', name=temp))
    except Exception as error:
        if inspect.stack()[0][3] not in error_list:
            send_bug_report(app, mail, inspect.stack()[0][3], str(error))
            error_list.append(inspect.stack()[0][3])


if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True, host='127.0.0.1', port=5000)
