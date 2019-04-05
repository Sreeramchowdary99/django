from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
import sqlite3 as sql
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
import datetime
from functools import wraps
app=Flask(__name__)
from logged_in import *
from classes import *
import random
import smtplib

count=0

def dead(email,title,isbn):

    se=smtplib.SMTP('smtp.gmail.com',587)
    se.starttls()
    se.login('kollu.sriramchowdary@gmail.com',"Ram@737047")
    message="Kindly return the book:" +title+" ISBN= "+isbn
    se.sendmail('kollu.sriramchowdary@gmail.com',mail,message)
    se.quit()

def deadline(issuedate,title,isbn,email):
    global count
    today = datetime.date.today()
    issue_date=issuedate.split('-')
    issuedate=datetime.date(int(issue_date[0]),int(issue_date[1]),int(issue_date[2]))
    days_past=today-issuedate
    penalty=0
    days_past=days_past.days
    days_left=7-days_past
    if(days_past>7):
        dead(email,title,isbn)
        count=1
    return

def fun(mail,otp):
    se=smtplib.SMTP('smtp.gmail.com',587)
    se.starttls()
    se.login('kollu.sriramchowdary@gmail.com',"Ram@737047")
    message=str(otp)+" "+"is your portal verification code"
    se.sendmail('kollu.sriramchowdary@gmail.com',mail,message)
    se.quit()

def issue_mail(mail,isbn,title):
        se=smtplib.SMTP('smtp.gmail.com',587)
        se.starttls()
        se.login('kollu.sriramchowdary@gmail.com',"Ram@737047")
        message="You can collect the book "+str(title[0].encode(encoding='UTF-8'))+" with ISBN "+str(isbn)
        se.sendmail('kollu.sriramchowdary@gmail.com',mail,message)
        se.quit()

#Function to send mail after deadline

#Function to calculate penalty

keka=0


def calc_fee(issuedate):
    today = datetime.date.today()
    issue_date=issuedate.split('-')
    issuedate=datetime.date(int(issue_date[0]),int(issue_date[1]),int(issue_date[2]))
    days_past=today-issuedate
    penalty=0
    days_past=days_past.days
    days_left=7-days_past
    if days_past<=7:
        return days_left,"NA"
    else:
        penalty=(days_past-7)*5 #penalty
        return "NA",penalty
#Home


@app.route('/')
@app.route('/home')
def home():
    print ("Okay")
    return render_template('home.html')

#Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard.html')

#Register
@app.route('/register', methods=['GET', 'POST'])
@is_not_logged_in
def register():
    form=RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        with sql.connect('database.db') as con:
            username=form.name.data
            email=form.email.data
            password=sha256_crypt.encrypt(str(form.password.data))
            role='students'
            cur=con.cursor()
        #Create cursor
            sql_query = "select * from students where email ='" + email + "';"
            res=cur.execute(sql_query)
            res=cur.fetchone()
            if res :
                flash('A student account with this E-mail already exists','danger')
                cur.close()
            else:
                session['field1']=username
                session['field2']=email
                session['field3']=password
                OTP=random.randint(1000,9999)
                session['otp']=OTP
                fun(email,OTP)
                global keka
                keka=1
                return redirect(url_for('verification'))
    return render_template('register.html',form=form)

@app.route('/verification',methods=['GET','POST'])
@is_not_logged_in
def verification():
    if keka==0:
        flash('Did not fill registration form','danger')
        return redirect(url_for('register'))
    elif keka==1:
        role='students'
        form=VerifyOTP(request.form)
        if request.method == 'POST' and form.validate():
            otp=form.otp.data
            if str(session['otp'])==otp:
                with sql.connect('database.db') as con:
                    cur=con.cursor()
                    cur.execute("INSERT INTO students(username,email,password,role) VALUES (?, ?, ?, ?)",(session['field1'],session['field2'],session['field3'],role))
                    con.commit()
                    cur.close()
                    flash('Successfully registered as a student. Now you can login','success')
                    session.pop('otp')
                    session.pop('field1')
                    session.pop('field2')
                    session.pop('field3')
                    return redirect(url_for('login'))
            else:
                error="Wrong OTP. Re-enter the OTP"
                return render_template('verification.html',error=error,form=form)
        else:
            return render_template('verification.html',form=form)


#Login
@app.route('/login', methods=['GET', 'POST'])
@is_not_logged_in
def login():
    if request.method == 'POST':
        # Get Form Fields
        email = request.form['email']
        password_field = request.form['password']
        # Create cursor
        with sql.connect('database.db') as con:
        # Get user by username
            cur=con.cursor()

            role= str(request.form['role'])
            if(role=='admin'):
                sql_query = "select * from admins where email ='" + email + "';"
                result=cur.execute(sql_query)
                result=cur.execute(sql_query)
                data = cur.fetchone()
            elif(role=='faculty'):
                sql_query = "select * from faculty where email ='" + email + "';"
                result=cur.execute(sql_query)
            else:
                sql_query = "select * from students where email ='" + email + "';"
                result=cur.execute(sql_query)
                data = cur.fetchone()
                print (data)
            if data != None:
                password=data[2]
    # Compare Passwords
                if sha256_crypt.verify(password_field, password):
                    # Passed
                    session['logged_in'] = True
                    session['email'] = email

                    if(role=='admin'):
                        sql_q="select * from admins where email ='"+email+"';"
                        cur.execute(sql_q)
                        res=cur.fetchone()
                        session['id']=res[0]
#                        session['email']=res[4]
                        session['usertype']='admins'
                        session['email']=res[4]
                        session['username']=res[1]
                        session['logged_in']=True
                        session['notif']=0
                        flash('You are now logged in as Admin ', 'success')
                    elif role=='faculty':
                        session['usertype']='faculty'
                        session['logged_in']=True
                        flash('You are now logged in as Faculty ', 'success')
                    else :
                        sql_q="select * from students where email ='"+email+"';"
                        cur.execute(sql_q)
                        res=cur.fetchone()
                        session['id']=res[0]
                        session['email']=res[4]
                        session['username']=res[1]
                        session['usertype']='students'
                        session['logged_in']=True
                        cur.execute('select * from issue where studentid=? and notif=1',[session['id']])
                        res=cur.fetchall()
                        cur.execute('update issue set notif=0 where studentid=? and notif=1', [session['id']])
                        if len(res)==0:
                            session['notif']=0
                        else:
                            session['notif']=1
                        flash('You are now logged in as Student ', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    error = 'Invalid login'
                    return render_template('login.html', error=error)
            # Close connection
                cur.close()
            else:
                error = 'E-mail not found'
                return render_template('login.html', error=error)

    return render_template('login.html')

#Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('home'))

#To access books
@app.route('/books/<isbn>',methods=['GET','POST'])
@is_logged_in
def book_data(isbn=None):
    if(isbn==None):
        return redirect(url_for(showall))
    else:

        form=CommentForm(request.form)
        with sql.connect('database.db') as con:
            cur=con.cursor()
            if request.method=='POST' and form.validate():
                review_given=form.comment.data
                cur.execute("insert into reviews(review,isbn,username) values(?,?,?)",[review_given,isbn,session['username']])
                con.commit()
            sql_query = "select * from books where isbn ='" +isbn + "';"
            cur.execute(sql_query)
            res=cur.fetchone()
            if(res==None):
                flash('Invalid ISBN')
                return redirect(url_for(showall))
            else:
                cur.execute("select * from reviews where isbn=?",[isbn])
                tot=cur.fetchall()
                if(len(tot)==0):
                    comm=0
                else:
                    comm=tot
                    print ("Not okay")


            return render_template('book_data.html',res=res,comm=comm)

#Requesting Books
@app.route('/books/<isbn>/req')
@is_logged_in
def req(isbn=None):
    if session['usertype']=='students':
        if isbn==None:
            flash('Invalid isbn number')
            return redirect(url_for('showall'))
        else:
            with sql.connect('database.db') as con:
                cur=con.cursor()
                #print (int(str(session['id'])))
                cur.execute("select * from books where isbn ='" + isbn + "';")
                no=cur.fetchone()
                if(no==None):
                    flash("No book exists with this isbn",'danger')
                    return redirect(url_for('showall'))
                else:
                    if(int(no[3])<1):
                        flash('Sorry! This book is currently unavailable','danger')
                        return redirect(url_for('showall'))
                    else:
                        cur.execute("insert into requests(isbn,studentid) values(?,?)",(isbn,session['id']))
                        con.commit()
                        cur.close()
                        flash('Request made successfully','success')
                        return redirect(url_for('showall'))

    else:
        flash('Admin can not make a book request','danger')
        return redirect(url_for('dashboard'))
lol=0

#Show All
@app.route('/showall')
@is_logged_in
def showall():
    with sql.connect('database.db') as con:
        cur=con.cursor()
        cur.execute('SELECT * from books;')
        rows=cur.fetchall()
        Books = [dict(author=row[0],
                        title=row[1],
                        ratings=row[2],
                        copya=row[3],
                        isbn=row[4])
                     for row in rows]
    cur.close()
    return render_template('show_all.html', Books=Books)
#Return Book
@app.route('/returnbook/<isbn>/<studid>')
@is_logged_in
def returnbook(isbn,id):
    if session['usertype']=='students':
        with sql.connect('database.db') as con:
            cur=con.cursor()
            cur.execute('delete from issue where studentid=? and isbn=?',[studid,isbn])
            cur.execute('select copy from books where isbn=?',[isbn])
            copy_no=cur.fetchone()
            copy_no=int(copy_no)+1
            cur.execute("update books set copy=? where isbn = ? ",[str(copy_no),isbn])
            con.commit()
            cur.close()
    return redirect(url_for('dashboard'))

#UserProfile
@app.route('/user/<studid>')
@is_logged_in
def user(studid):
    if session['usertype']=='admins' or str(session['id'])==studid:
        Issue=[]
        Issue_history=[]
        studentid=int(studid)

        with sql.connect('database.db') as con:
            cur=con.cursor()
            print (studentid)
            print (int(studentid))
            cur.execute("select isbn,issuedate from issue where studentid=? ",[studentid])
            book_isbns=cur.fetchall()
            if(len(book_isbns)==0):
                issue_check=0
            else:
                issue_check=1
                for isbn in book_isbns:
                    print ("mama")
                    val=isbn[0]
                    issuedate=isbn[1]
                    val=str(val)
                    cur.execute("select * from books where isbn = ?",[val])
                    data=cur.fetchone()
                    if data!=None:
                        days,penalty=calc_fee(issuedate)
                        Issue.append(dict(title=data[1],author=data[0],isbn=data[4],days=days,penal=penalty))

            cur.execute("select isbn from issue_history where studentid=?",[studentid])
            book_isbns_history=cur.fetchall()
            if(len(book_isbns_history)==0):
                issue_history_check=0
            else:
                issue_history_check=1

                for isbn in book_isbns_history:
                    cur.execute("select * from books where isbn=?",isbn)
                    data=cur.fetchone()
                    if data!=None:
                        Issue_history.append(dict(title=data[1],author=data[0],isbn=data[4]))
        return render_template('user_info.html',Issue=Issue,Issue_history=Issue_history,studid=studid,issue_check=issue_check,issue_history_check=issue_history_check)
    else:
        flash('Unauthorized','danger')
        return redirect(url_for('dashboard'))
#Admin Rights
@app.route('/add_book',methods=['GET','POST'])
@is_logged_in
def add_book():
    if session['usertype']=='admins':
        form=BookAdd(request.form)
        if request.method == 'POST' and form.validate():
            with sql.connect('database.db') as con:
                title=form.title.data
                author=form.author.data
                ratings=form.ratings.data
                isbn=form.ISBN.data
                cur=con.cursor()
                res=0
                if res :
                    flash('A student account with this E-mail already exists','danger')
                else:
                    cur.execute("INSERT INTO books(title,author,ratings,isbn,copy) VALUES (?, ?, ?,?,?)",(title,author,ratings,isbn,1))
                    #Commit to DB
                    con.commit()
                    #Close DB
                    cur.close()
                    flash('You have added a book successfully','success')
                    return redirect(url_for('dashboard'))
        else:
            return render_template('add_book.html',form=form)
    else:
        flash('Not an Admin','danger')
        return redirect (url_for('dashboard'))

@app.route('/add_user',methods=['GET','POST'])
@is_logged_in
def add_user():
    if session['usertype']=='admins':
        form=RegisterForm(request.form)
        if request.method == 'POST' and form.validate():
            with sql.connect('database.db') as con:
                username=form.name.data
                email=form.email.data
                password=sha256_crypt.encrypt(str(form.password.data))
                role='students'
                cur=con.cursor()
        #Create cursor
                sql_query = "select * from students where email ='" + email + "';"
                res=cur.execute(sql_query)
                res=cur.fetchone()
                if res :
                    flash('A student account with this E-mail already exists','danger')
                else:
                    cur.execute("INSERT INTO students(username,email,password,role) VALUES (?, ?, ?, ?)",(username,email,password,role))
                #Commit to DB
                #Close DB
                    cur.close()
                    con.commit()
                    flash('You have added a user successfully.','success')
                    return redirect(url_for('dashboard'))
        else:
            return render_template('add_user.html',form=form)
    else:
        flash('Not an Admin','danger')
        return redirect(url_for('dashboard'))
@app.route('/remove_book/<isbn>')
@is_logged_in
def remove_book(isbn):
    if session['usertype']=='admins':
        with sql.connect('database.db') as con:
            cur=con.cursor()
            cur.execute("delete from books where isbn=?",[isbn])
            con.commit()
            cur.close()
            flash('Removed Book Successfully','success')
        return redirect(url_for('showall'))
    else:
        flash('Not an Admin','danger')
        return redirect(url_for('dashboard'))

@app.route('/remove_user/<studid>')
@is_logged_in
def remove_user(studid):
    if session['usertype']=='admins':
        with sql.connect('database.db') as con:
            cur=con.cursor()
            cur.execute("delete from students where id=?",[studid])

            con.commit()
            cur.close()
            flash('Removed User Successfully','success')
            return redirect(url_for('dashboard'))
    else:
        flash('Not an Admin','danger')
        return redirect(url_for('dashboard'))

@app.route('/user_search',methods=['GET','POST'])
@is_logged_in
def user_search():
    if session['usertype']=='admins':
        print ("Okay")
        form = UserSearch(request.form)
        if request.method == 'POST' and form.validate():
            with sql.connect('database.db') as con:
                email=form.email.data
                cur=con.cursor()
                sql_query = "select * from students where email ='" + email + "';"
                res=cur.execute(sql_query)
                res=cur.fetchone()

                if res:
                    message="User is found"
                    return render_template('user_search.html',msg=message,form=form,res=res,check=1)
                else :
                    error='No user exists with the provided e-mail'
                    return render_template('user_search.html',error=error,form=form,check=0)
        else:
            return render_template('user_search.html',form=form)
    else:
        flash('Not admin','danger')
        return redirect(url_for(dashboard))

@app.route('/delete_comment/<isbn>/<id>')
@is_logged_in
def delete_comment(id,isbn):
    if session['usertype']=='admins':
        with sql.connect('database.db') as con:
            cur=con.cursor()
            cur.execute("delete from reviews where id=?",[int(id)])
            con.commit()
            cur.close()
            return redirect(url_for('showall'))
    else:
        flash('Not an Admin','danger')
        return redirect(url_for('dashboard'))


@app.route('/showallusers')
@is_logged_in
def showallusers():
    with sql.connect('database.db') as con:
        cur=con.cursor()
        cur.execute('SELECT * from students')
        rows=cur.fetchall()
        Students = [dict(username=row[1],
                        id=row[0],
                        email=row[4])
                     for row in rows]
    cur.close()
    return render_template('show_all_users.html', Students=Students)

@app.route('/book_req')
@is_logged_in
def book_req():
    if session['usertype']=='admins':
        with sql.connect('database.db') as con:
            cur=con.cursor()
            cur.execute("select * from requests")
            Requests = [dict(studentid=row[2],
                            isbn=row[1]
                            )
                            for row in cur.fetchall()]
            if (len(Requests)!=0):
                session['req']=1
            else:
                req=0
                session['req']=0
            return render_template('book_req.html',Requests=Requests)
    else:
        flash('Not an Admin','danger')
        return redirect(url_for('showall'))
@app.route('/approve/<studid>/<bookisbn>')
@is_logged_in
def approve(studid,bookisbn):
    if session['usertype']=='admins':
        with sql.connect('database.db') as con:
            cur=con.cursor()
            print(session['id'])
            studid = int(studid)
            c_id = int(session['id'])
            cur.execute("INSERT INTO issue (isbn,studentid,adminid,notif) VALUES(?,?,?,?)",(bookisbn,studid,c_id,1))
            cur.execute("INSERT INTO issue_history (isbn,studentid,adminid) VALUES(?,?,?)",(bookisbn,studid,c_id))
            cur.execute("delete from requests where isbn  = ? and studentid = ?",[bookisbn,studid])
            cur.execute("update issue set issuedate=(select date('now')) where isbn = ? and studentid = ?",[bookisbn,studid])
            cur.execute("update issue_history set issuedate=(select date('now')) where isbn = ? and studentid = ?",[bookisbn,studid])
            cur.execute("select email from students where id=?",[studid])
            email=cur.fetchone()
            cur.execute("select title from books where isbn=?",[bookisbn])
            title=cur.fetchone()
            issue_mail(email,bookisbn,title)
            cur.execute("select copy from books where isbn = ? ",[bookisbn])
            copy_no=int(cur.fetchone()[0])
            copy_no=copy_no-1
            cur.execute("update books set copy=? where isbn = ? ",[str(copy_no),bookisbn])
            con.commit()
            cur.close()
            flash("Request is approved",'success')
            return redirect('book_req')
    else:
        flash("Not an Admin")
        return redirect(url_for('dashboard'))

@app.route('/decline/<studid>/<bookisbn>')
@is_logged_in
def decline(studid,bookisbn):
    if session['usertype']=='admins':
        with sql.connect('database.db') as con:
            cur=con.cursor()
            sql_query="delete from requests where isbn ='" + bookisbn + "';"
            cur.execute(sql_query)
            con.commit()
            cur.close()
            flash('Request is declined','danger')
            return redirect(url_for('book_req'))
    else:
        flash("Not an Admin",'danger')
        return redirect(url_for('dashboard'))

@app.route('/sendmail_')
@is_logged_in
def sendmailall():
    if session['usertype']=='admins':
        with sql.connect('database.db') as con:
            cur=con.cursor()
            cur.execute("select * from issue")
            total=cur.fetchall()
            for issue in total:
                cur.execute("select email from students where id=?",[issue[2]])
                email=cur.fetchone()
                cur.execute("select title from books where isbn=?",[issue[1]])
                title=cur.fetchone()
                deadline(issue[4],title,issue[1],email)
            flash('Sent Mail to Book Recipents','success')
            return redirect(url_for('dashboard'))
    else:
        flash('Not an Admin','danger')
        return redirect(url_for('dashboard'))

#Search
@app.route('/search',methods=['GET', 'POST'])
@is_logged_in
def search():
    if request.method == 'POST':
        field=str(request.form['field'])
        search_field=request.form['search_field']
        print (search_field)
        with sql.connect('database.db') as con:
            cur=con.cursor()
            if(field=='title'):
                cur.execute('select * from books where title=?',[search_field])
                res=cur.fetchall()
            elif(field=='author'):
                cur.execute('select * from books where author=?',[search_field])
                res=cur.fetchall()
            elif(field=='isbn'):
                cur.execute('select * from books where isbn=?',[search_field])
                res=cur.fetchall()

            SearchResults=[dict(title=row[1],author=row[0],isbn=row[4],ratings=row[2],copyal=row[3]) for row in res]
            print (SearchResults)
            if (len(res)==0):
                res=0
            else:
                res=1
            lol=1
            cur.close()
        return render_template('search.html',res=res,SearchResults=SearchResults,lol=lol)
    return render_template('search.html')

@app.route('/about')
def about():
    return render_template('about.html')
#@app.route('/contact')
@app.route('/open')
def open():
    return render_template('open.html')
if __name__ == '__main__':
    app.secret_key="ban123"
    app.run(debug=True)
