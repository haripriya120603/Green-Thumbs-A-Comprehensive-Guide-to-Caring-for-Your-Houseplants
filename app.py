from flask import Flask, render_template, url_for, request, session, redirect, flash,send_from_directory
import ibm_db
import re
import os
import requests
import json
import ibm_boto3              #pip install ibm-cos-sdk in terminal
from ibm_botocore.client import Config, ClientError


app = Flask(__name__)

app.secret_key = 'a'
conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=98538591-7217-4024-b027-8baa776ffad1.c3n41cmd0nqnrk39u98g.databases.appdomain.cloud;PORT=30875;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=fnc49721;PWD=oI8YaxBwwrliegJ9", '', '')
print("connected")

# Constants for IBM COS values
COS_ENDPOINT = "https://s3.au-syd.cloud-object-storage.appdomain.cloud"
COS_API_KEY_ID = "7w01NqxV1GwsmQd49-X3eGUeePnL1JgZNhzYplxAo29q"
COS_INSTANCE_CRN = "crn:v1:bluemix:public:cloud-object-storage:global:a/267baef1483e4e7ea6114e4b9b941b65:bfdc12fb-3d5f-47a1-bc72-4f2cb1b959c3::"
# Create resource
cos = ibm_boto3.client("s3",
    ibm_api_key_id=COS_API_KEY_ID,
    ibm_service_instance_id=COS_INSTANCE_CRN,
    config=Config(signature_version="oauth"),
    endpoint_url=COS_ENDPOINT
)


@app.route('/')
@app.route('/login', methods=["POST", "GET"])
def login():
    msg = ''

    if request.method == 'POST':
        USERNAME = request.form['username']
        PASSWORD = request.form['password']

        sql = "SELECT * FROM REGISTER WHERE USERNAME = ? AND PASSWORD = ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, USERNAME)
        ibm_db.bind_param(stmt, 2, PASSWORD)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        if account['ROLE']==0:
            session['Loggedin'] = True
            session['USERNAME'] = account['USERNAME']
            session['USERID'] = account['USERID']
            session['EMAIL'] = account['EMAIL']
            return render_template("home.html")

        elif account['ROLE']==1:
            session['Loggedin'] = True
            session['USERID'] = account['USERID']
            return render_template("admin_home.html")
        else:
            msg="Incorrect username / Password !"
    return render_template('login.html', msg=msg)


@app.route('/register', methods=['GET', 'POST'])
def Register():
    msg = ' '

    if request.method == 'POST':
        USERNAME = request.form['username']
        EMAIL = request.form["email"]
        PASSWORD = request.form["password"]
        ROLE=0
        sql = "SELECT * FROM REGISTER WHERE USERNAME=? AND PASSWORD=? "
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, USERNAME)
        ibm_db.bind_param(stmt, 2, PASSWORD)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)

        if account:
            msg = 'Account already exists! '
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', EMAIL):
            msg = ' Invalid email address! '
        elif not re.match(r'[A-Za-z0-9]+', USERNAME):
            msg = ' username must contain only characters and numbers! '
        else:
            sql2 = "SELECT count(*) FROM REGISTER"
            stmt2 = ibm_db.prepare(conn, sql2)
            ibm_db.execute(stmt2)
            length = ibm_db.fetch_assoc(stmt2)
            print(length)
            insert_sql = "INSERT INTO REGISTER VALUES(?,?,?,?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, length['1']+1)
            ibm_db.bind_param(prep_stmt, 2, USERNAME)
            ibm_db.bind_param(prep_stmt, 3, EMAIL)
            ibm_db.bind_param(prep_stmt, 4, PASSWORD)
            ibm_db.bind_param(prep_stmt, 5, ROLE)
            ibm_db.execute(prep_stmt)
            msg = 'You have successfully registered !'
            return render_template("login.html", msg=msg)
    return render_template("register.html", msg=msg)

@app.route('/admin_register', methods=['GET', 'POST'])
def admin_register():
    msg = ' '
    if request.method == 'POST':
        USERNAME = request.form['username']
        EMAIL = request.form["email"]
        PASSWORD = request.form["password"]
        ROLE=1
        sql = "SELECT * FROM REGISTER WHERE USERNAME=? AND PASSWORD=? "
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, USERNAME)
        ibm_db.bind_param(stmt, 2, PASSWORD)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)

        if account:
            msg = 'Account already exists! '
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', EMAIL):
            msg = ' Invalid email address! '
        elif not re.match(r'[A-Za-z0-9]+', USERNAME):
            msg = ' username must contain only characters and numbers! '
        else:
            sql2 = "SELECT count(*) FROM REGISTER"
            stmt2 = ibm_db.prepare(conn, sql2)
            ibm_db.execute(stmt2)
            length = ibm_db.fetch_assoc(stmt2)
            print(length)
            insert_sql = " INSERT INTO REGISTER VALUES(?,?,?,?,?) "
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, length['1']+1)
            ibm_db.bind_param(prep_stmt, 2, USERNAME)
            ibm_db.bind_param(prep_stmt, 3, EMAIL)
            ibm_db.bind_param(prep_stmt, 4, PASSWORD)
            ibm_db.bind_param(prep_stmt, 5, ROLE)
            ibm_db.execute(prep_stmt)
            msg = 'You have successfully registered !'
            return render_template("login.html", msg=msg)
    return render_template("admin_register.html", msg=msg)



@app.route('/homepage', methods=['GET', 'POST'])
def Home():
    return render_template("home.html")

@app.route('/plant', methods=['GET', 'POST'])
def Plants():
    return render_template("plants.html")

@app.route('/guide', methods=['GET', 'POST'])
def Guides():
    return render_template("guides.html")

@app.route('/addplants', methods=['GET', 'POST'])
def addplants():

    sql="SELECT * FROM REGISTER WHERE ROLE=1"
    stmt=ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt)
    data=ibm_db.fetch_tuple(stmt)
    print(data)

    if request.method == 'POST':
        f = request.files['image']
        productname = request.form['name']
        proid = request.form["plantid"]
        cost = request.form["cost"]
        insert_sql ="INSERT INTO PRODUCT VALUES (?,?,?,?,?)"
        stmt1 = ibm_db.prepare(conn, insert_sql)
        ibm_db.bind_param(stmt1, 1, data[0])
        ibm_db.bind_param(stmt1, 2, data[1])
        ibm_db.bind_param(stmt1, 3, productname)
        ibm_db.bind_param(stmt1, 4, proid)
        ibm_db.bind_param(stmt1, 5, cost)
        ibm_db.execute(stmt1)

        sql = 'SELECT * FROM PRODUCT' 
        stmt2 = ibm_db.prepare(conn, sql)
        ibm_db.execute(stmt2)
        data = ibm_db.fetch_assoc(stmt2)
        print(data)
        
        basepath=os.path.dirname(__file__) #getting the current path i.e where app.py is present
        #print("current path",basepath)
        filepath=os.path.join(basepath,'uploads','.jpg') #from anywhere in the system we can give image but we want that image later  to process so we are saving it to uploads folder for reusing
        #print("upload folder is",filepath)
        f.save(filepath)
        
        cos.upload_file(Filename= filepath, Bucket='myplants', Key= productname +'.jpg')
        # image.save(os.path.join("static/images", filename))
        print('data sent tô db2')
        return render_template("admin_home.html") 
    return render_template("adplants.html")   

@app.route('/viewplants', methods=['GET', 'POST'])
def viewplants():

    sql = 'SELECT * FROM PRODUCT'
    stmt2 = ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt2)
    rows = []
    while True:
        data = ibm_db.fetch_assoc(stmt2)
        print("data:", )
        if not data:
            break
        else:
            data['PROID'] = str(data['PROID'])
            rows.append(data)
    print('rows: ', rows)

    # COS_ENDPOINT = "https://s3.au-syd.cloud-object-storage.appdomain.cloud"
    # COS_API_KEY_ID = "7w01NqxV1GwsmQd49-X3eGUeePnL1JgZNhzYplxAo29q"
    # COS_INSTANCE_CRN = "crn:v1:bluemix:public:cloud-object-storage:global:a/267baef1483e4e7ea6114e4b9b941b65:bfdc12fb-3d5f-47a1-bc72-4f2cb1b959c3::"
    # # Create resource
    # cos = ibm_boto3.client("s3",  
    #     ibm_api_key_id=COS_API_KEY_ID,
    #     ibm_service_instance_id=COS_INSTANCE_CRN,
    #     config=Config(signature_version="oauth"),
    #     endpoint_url=COS_ENDPOINT
    # )
    # myimage=cos.list_objects(Bucket = 'myplants')
    # print(len(myimage['Contents']))
    # print(myimage)
    # list1=[]
    # for i in range(0,len(myimage['Contents'])):
    #     j = myimage['Contents'][i]['Key']
    #     list1.append(j)
    # list1
    # print(list1)
    return render_template("displayplants.html", rows=rows)

@app.route('/userviewplants', methods=['GET', 'POST'])
def userviewplants():
    sql = 'SELECT * FROM PRODUCT'
    stmt2 = ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt2)
    rows = []
    while True:
        data = ibm_db.fetch_assoc(stmt2)
        print("data:", )
        if not data:
            break
        else:
            data['PROID'] = str(data['PROID'])
            rows.append(data)
    print('rows: ', rows)
    return render_template("displayuser.html", rows=rows)

@app.route('/delete_plant/<string:PROID>', methods = ['POST'])
def delete_plant(PROID):
    sql= "DELETE FROM PRODUCT WHERE PROID=?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, PROID)
    ibm_db.execute(stmt)
    print('item deleted')
    return redirect(url_for('viewplants'))

@app.route('/add_plant/<string:PROID>', methods = ['GET', 'POST'])
def add_plant(PROID):
    
    sql="SELECT * FROM REGISTER WHERE USERID=" +str(session['USERID'])
    stmt=ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt)
    data1=ibm_db.fetch_tuple(stmt)
    print(data1)
    print("addproductsss")
    
    # sql="SELECT * FROM REGISTER 
    # stmt=ibm_db.prepare(conn, sql)
    # ibm_db.execute(stmt)
    # data1=ibm_db.fetch_tuple(stmt)
    # print(data1)
    
    

    sql="SELECT * FROM PRODUCT WHERE PROID ="+PROID
    stmt=ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt)
    data=ibm_db.fetch_tuple(stmt)
    print(data)

    insert_sql ="INSERT INTO TRANS VALUES (?,?,?,?,?)"
    stmt = ibm_db.prepare(conn, insert_sql)
    ibm_db.bind_param(stmt, 1, data1[0])
    ibm_db.bind_param(stmt, 2, data1[1])
    ibm_db.bind_param(stmt, 3, data[3])
    ibm_db.bind_param(stmt, 4, data[2])
    ibm_db.bind_param(stmt, 5, data[4])
    ibm_db.execute(stmt)
    return redirect(url_for('userviewplants'))

@app.route('/transection')
def transection():
    
    select_sql = "SELECT * FROM TRANS"
    stmt = ibm_db.prepare(conn, select_sql)
    ibm_db.execute(stmt)
    data=ibm_db.fetch_tuple(stmt)
    print(data)
    rows = []
    while data!= False:
        rows.append(data)
        data=ibm_db.fetch_tuple(stmt)
    print(rows)
    
    sql='SELECT SUM(COST) AS TOT FROM TRANS WHERE USERID =' +str(session['USERID']) 
    stmt = ibm_db.prepare(conn,sql)
    # ibm_db.bind_param(stmt, 1, USERID)
    ibm_db.execute(stmt)
    account=ibm_db.fetch_tuple(stmt)
    print(account)
    total = int(account[0])
    print(total)
    print("ggggggg")
    
    
    return render_template('user_trans.html', rows=rows,total=total)

@app.route('/trans')
def admintrans():
    select_sql = "SELECT * FROM TRANS"
    stmt = ibm_db.prepare(conn, select_sql)
    ibm_db.execute(stmt)
    data=ibm_db.fetch_tuple(stmt)
    print(data)
    rows = []
    while data!= False:
        rows.append(data)
        data=ibm_db.fetch_tuple(stmt)
    print(rows)
    
    sql='SELECT SUM(COST) AS TOT FROM TRANS ' 
    stmt = ibm_db.prepare(conn,sql)
    ibm_db.execute(stmt)
    account=ibm_db.fetch_tuple(stmt)
    print(account)
    total = int(account[0])
    
    sql='SELECT COUNT(COST) AS TOT FROM TRANS'
    stmt = ibm_db.prepare(conn,sql)
    # ibm_db.bind_param(stmt, 1, USERID)
    ibm_db.execute(stmt)
    account1=ibm_db.fetch_tuple(stmt)
    print(account1)
    COUNT = int(account1[0])
    print(COUNT)   
    
    
    return render_template('trans_admin.html', rows=rows,total=total, COUNT=COUNT)

@app.route('/remove_plant/<string:PROID>', methods = ['POST'])
def remove_plant(PROID):
    sql= "DELETE FROM TRANS WHERE PROID=?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, PROID)
    ibm_db.execute(stmt)
    print('plant removed')
    return redirect(url_for('transection'))    

@app.route('/poppage',methods=['POST'])
def Pop():
    return render_template("Popup.html")
    return redirect(url_for('/homepage'))
    

@app.route("/output", methods=['GET','POST'])
def output():
    name = request.form['plants']
    #plant name
    print(name) 
    url = "https://house-plants.p.rapidapi.com/common/" + name    
    
    
    headers = {
        "X-RapidAPI-Key": "ad8dd9e205msh1b46ee7d2f5246fp145c0bjsn4f9d4d717193",
        "X-RapidAPI-Host": "house-plants.p.rapidapi.com"
}

    response = requests.request("GET", url, headers=headers)
    
    print(response.text)
    
    output=response.json()
    
    name = ["corralberry", "lipstick"]
    for x in name:
        print(x) 
        
        latinname = output[0]['latin']
        familyname = output[0]['family']
        commonname = output[0]['common']
        categoryname = output[0]['category']
        temp1 = output[0]['tempmax']
        temp2 = output[0]['tempmin']
        light = output[0]['ideallight']
        water = output[0]['watering']
        uses = output[0]['use']
    return render_template("plantsapi.html", latinname= latinname, familyname=familyname, categoryname=categoryname,temp1=temp1,
                           temp2=temp2, light=light, name=commonname, water = water, uses=uses)


@app.route('/plantinfo', methods=['GET', 'POST'])
def plantInfo():
    return render_template('plantsapi.html')

@app.route('/logout')
def logout():
    session.pop('loggedin',None)
    session.pop('username',None)
    return render_template("login.html")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
