import os.path

from flask import Flask, render_template, request, url_for, flash, session, redirect
import mysql.connector
import smtplib
from email.mime.text import MIMEText
import  random

app = Flask (__name__)
app.secret_key='tejaskumar12345'
app.config['Upload_image']='static/img'

conn=mysql.connector.connect(host="localhost",user="root",password="",database="shopping")
cursor=conn.cursor()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/contactus")
def contactus():
    return render_template("contactus.html")

@app.route("/aboutus")
def aboutus():
    return render_template("aboutus.html")

@app.route("/registrar",methods=['POST','GET'])
def registrar():
    msg = "registered successful"
    if (request.method == "POST"):
        print(request)
        name = request.form['name']
        email = request.form['email']
        telephone = request.form['telephone']
        password = request.form['password']
        address = request.form['address']
        sql = "Insert into register (Name,email,password,phonenumber,address) value('%s','%s', '%s', '%s', '%s')" % (name, email, password, telephone, address)
        cursor.execute(sql)
        conn.commit()
        msg = "Registered Successfully"
    return render_template("registrar.html", msg=msg)


@app.route("/login",methods=['POST','GET'])
def login():
    if request.method=="POST":
        print(request)
        email=request.form['email']
        print(email)
        password=request.form['password']
        print(password)
        if email=="tejas@gmail.com" and password=="tejas":
            return render_template("admin.html")
        else:
            sql="select * from register where email like'%s' and password like'%s'"%(email,password)
            cursor.execute(sql)
            data=cursor.fetchone()
            if data:
                session['id']=data[0]
                print(session['id'])

                return render_template("usermain.html",data=data)

    return render_template("login.html")



@app.route("/forget")
def forget():
    return  render_template("forgot.html")

def send_email(subject, body, sender, recipients, password):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
       smtp_server.login(sender, password)
       smtp_server.sendmail(sender, recipients, msg.as_string())
    print("Message sent!")

@app.route("/checkemail", methods=["POST","GET"])
def checkemail():
    try:
        email =request.form['email']
        sql="Select * from register  where email like '%s'" % (email)
        print("Sql : ", sql)

        cursor.execute(sql)
        row = cursor.fetchone()
        if(row):
            session['email']=email
            subject = "OTP to reset the password"
            otp = random.randint(1000,9999)
            session['otp']=otp
            body = "Thank you for changing the Password, your OTP is : " + str(otp)
            sender = "tejaskumar40085@gmail.com"
            recipients = [email]
            password = "qynvixuloizgbunp"
            send_email(subject, body, sender, recipients, password)
            return render_template("enterotppage.html", email = email)
        else:

            msg = 'Invalid EmailId'
            return render_template("forgot.html", msg=msg)
    except Exception as e:
        return render_template("login.html",msg=e)

@app.route("/checkotp", methods=["POST","GET"])
def checkotp():
    try:
        sentotp = request.form['otp']
        savedotp = session['otp']
        email = session['email']
        print("Saved Otp : ", savedotp, " Sent Otp : ", sentotp)
        if(int(sentotp)==int(savedotp)):
            return render_template("passwordchangepage.html", email = email)
        else:
            return render_template("enterotppage.html", email = email,msg='Incorrect OTP')
    except Exception as e:
        return render_template("login.html",msg=e)
@app.route("/changepwd", methods=["POST","GET"])
def changepwd():
    try:
        password = request.form['password']
        email=session['email']
        sql="Update register set password = '%s' where email = '%s'" % (password, email)
        print("Sql : ", sql)

        cursor.execute(sql)
        conn.commit()
        msg="Password Changes Success"
        return render_template("login.html", msg=msg)
    except Exception as e:
        return render_template("login.html",msg=e)

@app.route("/team")
def team():
    return render_template("team.html")

@app.route("/userdetail")
def userdetail():
    sql="select * from register"
    cursor.execute(sql)
    data=cursor.fetchall()
    return render_template("adinuserdetail.html",data=data)


@app.route("/product",methods=['POST','GET'])
def product():
    if request.method=='POST':
        ptype=request.form['ptype']
        pname = request.form['pname']
        pqty= request.form['pqty']
        pprice = request.form['pprice']
        pfile = request.files['pfile']
        rnum=random.randint(1000,9999)
        filename="IMG"+str(rnum)+".jpg"
        pfile.save(os.path.join(app.config['Upload_image'],filename))
        sql="insert into product(producttype,productname,productquantity,productprice,productfile)value('%s','%s','%s','%s','%s')"%(ptype,pname,pqty,pprice,filename)
        print(sql)
        cursor.execute(sql)
        conn.commit()
        productid=cursor.lastrowid
        session['productid']=productid
        msg="Product added"
        return render_template("product.html",msg=msg)

    return render_template("product.html")

@app.route("/adminProductdisplay")
def adminProductdisplay():
    sql="select * from product"
    cursor.execute(sql)
    data=cursor.fetchall()

    return render_template("adminProductdetail.html", data=data)

@app.route("/adminuserviewreport")
def adminuserviewreport():

    sql = "select * from paymenttable"
    cursor.execute(sql)
    data = cursor.fetchall()
    return render_template("adminuserviewreport.html", data=data)





@app.route("/paymentdetail")
def paymentdetail():
    return render_template("paymentdetail.html")

@app.route("/userproductdetail")
def userproductdetail():
    sql = "select * from product"
    cursor.execute(sql)
    data = cursor.fetchall()
    return render_template("userproductdetail.html", data=data)

@app.route("/deleteaddtocart")
def deleteaddtocart():
    rqty = request.args['rqty']
    pid = request.args['pid']
    id = request.args['id']
    sql = ("Update product set productquantity=productquantity+" + str(rqty) +
           " where productid = " + str(pid))
    cursor.execute(sql)
    conn.commit()

    sql = "delete from ordertable where orderid = "+str(id)
    cursor.execute(sql)
    conn.commit()
    return redirect(url_for("userorderdisplay"))


@app.route("/adminremoveproduct")
def adminremoveproduct():
    id = request.args['id']
    sql = ("Delete from product  where productid = " + str(id))
    cursor.execute(sql)
    conn.commit()
    return redirect(url_for("adminProductdisplay"))



@app.route("/order")
def order():
    id = request.args['id']
    sql = "select * from product where productid = " + str(id)
    cursor.execute(sql)
    data = cursor.fetchone()
    return render_template("order.html", data=data)

@app.route("/userorder",methods=['POST','GET'])
def userorder():
    if request.method=="POST":
        print(request)
        pid=request.form['pid']
        print(pid)
        userid=session['id']
        print(userid)
        ptype = request.form['ptype']
        pname = request.form['pname']
        pqty = request.form['pqty']
        pprice = request.form['pprice']
        filename= request.form['filename']
        reqty = request.form['reqty']
        total = request.form['total']
        sql=(("insert into ordertable(productid,userid,producttype,"
             "productname,productquantity,productprice,requireqty,total, productfile)"
             "value('%s','%s','%s','%s','%s','%s','%s','%s','%s')")%
             (pid,userid,ptype,pname,pqty,pprice,reqty,total,filename))
        print(sql)
        cursor.execute(sql)
        conn.commit()
        sql = ("Update product set productquantity=productquantity-"+str(reqty)+
               " where productid = "+str(pid))
        cursor.execute(sql)
        conn.commit()
    return redirect(url_for("userorderdisplay"))

@app.route("/userorderdisplay")
def userorderdisplay():
    id = session['id']
    sql="select * from ordertable where userid = "+str(id)
    cursor.execute(sql)
    data=cursor.fetchall()
    sql="SELECT SUM(total) FROM ordertable WHERE userid = "+str(id)
    cursor.execute(sql)
    data1 = cursor.fetchone()
    total=data1[0]
    return render_template(
        "userorderdisplay.html",
        data=data, total=total)

@app.route("/adminvieworderdisplay")
def adminvieworderdisplay():
    sql="select * from ordertable"
    cursor.execute(sql)
    data=cursor.fetchall()
    return render_template("adminvieworderdisplay.html",data=data)

@app.route("/usermainpage",methods=['POST','GET'])
def usermainpage():
    return render_template("usermain.html")

@app.route("/payment",methods=['POST','GET'])
def payment():
    total = request.args['total']
    return render_template("payment.html", total=total)


# Assuming 'conn' and 'cursor' are already set up correctly
# Make sure to import and configure the necessary libraries

@app.route("/makepayment", methods=['POST', 'GET'])
def makepayment():
    if request.method == "POST":
        userid = session.get('id')

        # Check if user is logged in
        if not userid:
            flash("User is not logged in.", "danger")
            return redirect(url_for("login"))

        # Retrieve common data
        amount = request.form.get('amt')
        payment_method = request.form.get('ptype')

        # Validate that amount exists
        if not amount:
            flash("Payment amount is required.", "danger")
            return redirect(url_for("payment_page"))

        # Prepare SQL and values for insertion
        sql, values = None, None

        if payment_method == 'CCard':
            cnum = request.form.get('cnum')
            ifsc = request.form.get('ifsc')
            cvv = request.form.get('cvv')
            exd = request.form.get('exd')

            # Example validation (you should expand this as needed)
            if not (cnum and cvv and exd):
                flash("Incomplete card details.", "danger")
                return redirect(url_for("payment_page"))

            sql = ("INSERT INTO paymenttable (userid, cardnumber, ifsc, cvv, expirydate, amount) "
                   "VALUES (%s, %s, %s, %s, %s, %s)")
            values = (userid, cnum, ifsc, cvv, exd, amount)

        elif payment_method == 'GooglePay':
            gpay_id = request.form.get('gpayId')
            gpay_phone = request.form.get('gpayPhone')

            if not (gpay_id and gpay_phone):
                flash("Google Pay details are incomplete.", "danger")
                return redirect(url_for("payment_page"))

            sql = ("INSERT INTO paymenttable (userid, gpay_id, gpay_phone, amount) "
                   "VALUES (%s, %s, %s, %s)")
            values = (userid, gpay_id, gpay_phone, amount)

        elif payment_method == 'PhonePay':
            phonepay_id = request.form.get('phonePayId')
            phonepay_phone = request.form.get('phonePayPhone')

            if not (phonepay_id and phonepay_phone):
                flash("PhonePe details are incomplete.", "danger")
                return redirect(url_for("payment_page"))

            sql = ("INSERT INTO paymenttable (userid, phonepay_id, phonepay_phone, amount) "
                   "VALUES (%s, %s, %s, %s)")
            values = (userid, phonepay_id, phonepay_phone, amount)

        else:
            flash("Invalid payment method selected.", "danger")
            return redirect(url_for("payment_page"))

        # Execute SQL statement
        try:
            cursor.execute(sql, values)
            conn.commit()
            flash("Payment successful!", "success")
        except Exception as e:
            conn.rollback()
            flash("An error occurred: " + str(e), "danger")

        return redirect(url_for("usermainpage"))

    return redirect(url_for("payment_page"))

@app.route("/userviewreport")
def userviewreport():
    id=session['id']
    sql = "select * from paymenttable where userid='%s'"%(id)
    cursor.execute(sql)
    data = cursor.fetchall()
    return render_template("userviewreport.html", data=data)


@app.route("/logout")
def logout():
    return render_template("index.html")

@app.route("/admin")
def admin():
    return render_template("admin.html")
@app.route("/message",methods=['POST','GET'])
def message():
    name=request.form['name']
    email=request.form['email']
    message=request.form['message']
    sql="insert into message(name,email,message)value('%s','%s','%s')"%(name,email,message)
    cursor.execute(sql)
    conn.commit()
    msg="Thank you for contacting us!"
    print(msg)
    return render_template("index.html",msg=msg)
if __name__=="__main__":
    app.run(debug=True)