import time
from flask import Flask, render_template, request, redirect, session, url_for
from flask_mysqldb import MySQL
import MySQLdb
from datetime import datetime, timedelta
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import matplotlib
from matplotlib.pyplot import title
import pytz
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import calendar
from pytz import timezone
from datetime import datetime
import requests
from datetime import date
import socket
import math
from werkzeug.utils import secure_filename
import ftplib
from flask_cors import CORS, cross_origin

app = Flask(__name__,
            static_url_path='',
            static_folder='Soham/static')
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

app.secret_key = "374375376"
app.permanent_session_lifetime = timedelta(days=1)
app.static_folder = 'static'

app.config["MYSQL_HOST"] = "43.225.54.56"
app.config["MYSQL_USER"] = "sohamgu4_ngma"
app.config["MYSQL_PASSWORD"] = "ngmaMysql*123"
app.config["MYSQL_DB"] = "sohamgu4_ngma_db"

db = MySQL(app)

app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_TLS=False,
    MAIL_USE_SSL=True,
    MAIL_USERNAME='soham.ngma.noreply@gmail.com',
    MAIL_PASSWORD='Soham123!'
)

send_email = Mail(app)

serial = URLSafeTimedSerializer('374375376')
serial2 = URLSafeTimedSerializer('377378379')


@app.route('/login', methods=['POST', 'GET'])
def index():
    if "user" in session:
        return redirect(url_for('homepage'))
    if request.method == 'POST':
        print(1, request.form)
        if 'username' in request.form and 'password' in request.form:

            username = request.form.get('username')
            password = request.form.get('password')
            print(username, password)
            cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM ngma2_users WHERE user_email=%s or user_login=%s ",
                           (username, username))
            info = cursor.fetchone()

            if info is not None:
                if check_password_hash(info['user_pass'], password) and info['user_confirmed'] == 0 and (
                        info['user_email'] == username or info['user_login'] == username):
                    return "Please confirm your email."

                elif check_password_hash(info['user_pass'], password) and (
                        info['user_email'] == username or info['user_login'] == username):
                    session['user'] = info['user_login']
                    session['display_name'] = info['display_name']
                    session['user_id'] = info['ID']
                    cursor.execute(
                        "SELECT guid FROM ngma2_posts WHERE(post_author=%s AND post_status=%s AND post_parent=%s)",
                        (info['ID'], 'inherit', '0'))
                    profile_pic = cursor.fetchone()
                    if profile_pic is None:
                        session['guid'] = '../img/user.png'
                    else:
                        session['guid'] = profile_pic['guid']
                    print(session['guid'])

                    return redirect(url_for('homepage'))

                else:
                    return "Invalid credentials"

            return "User not found"
    print("nothere")
    return render_template("SohamLogIn.html")


@app.route('/', methods=['POST', 'GET'])
def reg():
    data = request.form
    # print(data)
    if "username" in request.form and "email" in request.form and "password" in request.form and "displayname" in request.form:
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        display_name = request.form['displayname']
        time_code = datetime.now()
        password_hashed = generate_password_hash(
            password, "pbkdf2:sha256", salt_length=8)

        if username is not None and email is not None and password is not None and display_name is not None:

            check_email_login = db.connection.cursor(
                MySQLdb.cursors.DictCursor)
            check_email_login.execute("SELECT * FROM ngma2_users WHERE user_email=%s or user_login=%s",
                                      (email, username))
            info = check_email_login.fetchone()

            if info is not None:
                return "Username or email address is already in use."

            token = serial.dumps(email, salt='email_confirm')

            msg = Message('Confirm your So-ham Account',
                          sender='soham.ngma.noreply@gmail.com', recipients=[email])
            confirm_link = url_for(
                'confirm_email', token=token, _external=True)
            msg.body = 'Hi {},\r\n\nClick this link to confirm your email: {} .\r\n\nIf this action was not performed ' \
                       'by ' \
                       'you, please ignore this email.'.format(
                           display_name, confirm_link)
            send_email.send(msg)

            register_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
            register_cursor.execute(
                "INSERT INTO sohamgu4_ngma_db.ngma2_users(user_login, user_pass, user_email, display_name, "
                "user_registered,user_confirmed) VALUES(%s,%s,%s,%s,%s,%s)",
                (username, password_hashed, email, display_name, time_code, 0))

            db.connection.commit()

        return 'A confirmation email has been sent to your email. Make sure to check your spam folder as well.'

    return render_template("index.html")


@app.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = serial.loads(token, salt='email_confirm', max_age=3600)

        confirm_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        # Cursor executes the SQL statement and returns a tuple
        confirm_cursor.execute(
            "UPDATE ngma2_users SET user_confirmed=%s WHERE user_email=%s", (1, email))
        db.connection.commit()

    except SignatureExpired:
        return 'Token expired.'

    return 'Your email has been confirmed! You can log in now.'


@app.route('/forgot_password', methods=['POST', 'GET'])
def forgot():
    if "email" in request.form:
        email = request.form["email"]
        token = serial2.dumps(email, salt='forgot_password')

        msg = Message('Change your So-ham password',
                      sender='soham.ngma.noreply@gmail.com', recipients=[email])
        change_pw_link = url_for(
            'enter_password', token=token, email=email, password=request.form["password"], _external=True)
        msg.body = 'Change your password using the following link {} .\r\n\nIf this action was not performed by you, ' \
                   'please ignore this email.'.format(change_pw_link)
        send_email.send(msg)

        return "A mail has been sent to your email. Please click on it and follow the instructions given. Make sure " \
               "to check your spam folder as well. "

    return render_template("forgot_password.html")


# @ app.route('/change_password')
# def changePassword():
#     return render_template("changePassword.html")


@app.route('/enter_password/<token>/<password>/<email>', methods=['POST', 'GET'])
def enter_password(token, password, email):
    try:
        email = serial2.loads(token, salt='forgot_password', max_age=3600)
        password_hashed = generate_password_hash(
            password, "pbkdf2:sha256", salt_length=8)
        cursor4 = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor4.execute(
            "UPDATE ngma2_users SET user_pass=%s WHERE user_email=%s", (password_hashed, email))
        db.connection.commit()
        return 'Your password has been changed.'

    except SignatureExpired:
        return 'Token expired.'


@app.route('/submit_post', methods=['POST', 'GET'])
def submit_post():
    if "user" in session:
        category = request.args.get('category', default="")
    return render_template("submitForm.html", user=session['user'], type=category)


@app.route('/like/<author_id>/<post_id>', methods=['POST', 'GET'])
def like(author_id, post_id):
    if 'user' in session:

        like_check_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        db_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        like_check_cursor.execute("SELECT * FROM ngma2_exc_votes WHERE (post_id=%s AND user_id=%s)",
                                  (post_id, session['user_id']))
        liked = like_check_cursor.fetchone()

        if liked is None:
            like_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
            like_cursor.execute(
                "INSERT INTO sohamgu4_ngma_db.ngma2_exc_votes(author_id, post_id, user_id, status) VALUES(%s,%s,%s,%s)",
                (author_id, post_id, session['user_id'], '1'))
            db.connection.commit()

        elif liked['status'] == 1:
            unlike_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
            unlike_cursor.execute("UPDATE ngma2_exc_votes SET status=%s WHERE user_id=%s AND post_id=%s",
                                  (0, session['user_id'], post_id))
            db.connection.commit()

        else:
            relike_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
            relike_cursor.execute(
                "UPDATE ngma2_exc_votes SET status=%s WHERE (user_id=%s AND post_id=%s)",
                (1, session['user_id'], post_id))
            db.connection.commit()
        db_cursor.execute("SELECT COUNT(vote_id) AS total FROM ngma2_exc_votes WHERE (post_id=%s AND status=%s)", (post_id, '1'))
        current_likes = db_cursor.fetchone()
        print(current_likes)
        return { "post_likes": str(current_likes['total']) }
        # return redirect(url_for('homepage'))
    else:
        return redirect(url_for('index'))


# @app.route('/update_profile', methods=['POST', 'GET'])
def update_profile(user_id, file):
    print("Reached here1111111111111111111111111111111111111111")
    d = date.today()
    year, month = d.year, d.month
    year, month = '2069', '6'

    ftpsession = ftplib.FTP(
        'ftp.so-ham.in', 'demo@so-ham.in', 'demo123')  # Created session

    print(file)
    cur_now = datetime.now()
    mime_type = file.mimetype
    cur_now_time = cur_now.strftime("%m%d%Y%H%M%S")
    filename = str(session['user_id'])+cur_now_time+secure_filename(
        file.filename)
    filelist = []
    ftpsession.retrlines('LIST', filelist.append)
    found = False
    for f in filelist:
        if f.split()[-1] == year:
            found = True
    if found == False:
        ftpsession.mkd(year)
    ftpsession.cwd(year)
    filelist = []
    ftpsession.retrlines('LIST', filelist.append)
    found = False
    for f in filelist:
        if f.split()[-1] == month:
            found = True
    if not found:
        ftpsession.mkd(month)
    ftpsession.cwd(month)
    ftpsession.storbinary('STOR %s' % (filename), file)
    ftpsession.quit()
    guid = "https://so-ham.in/wp-content/uploads/%s/%s/%s" % (
        year, month, filename)
    post_db = db.connection.cursor(MySQLdb.cursors.DictCursor)

    post_db.execute(
        "SELECT guid FROM ngma2_posts WHERE(post_author=%s AND post_status=%s AND post_parent=%s)",
        (user_id, 'inherit', '0'))
    profile_pic = post_db.fetchone()
    print(profile_pic)
    if profile_pic is None:
        post_date = datetime.now()
        post_date_gmt = datetime.now(timezone('UTC')).astimezone(
            timezone('Asia/Kolkata'))
        title = str(user_id)+"profile_pic"
        post_db.execute("INSERT INTO sohamgu4_ngma_db.ngma2_posts(post_author, post_date, post_date_gmt,post_modified, post_modified_gmt, post_title,post_status,comment_status,ping_status,post_parent,guid,post_type,post_mime_type) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", [
                        user_id, post_date, post_date_gmt, post_date, post_date_gmt, title, "inherit", "closed", "closed", 0, guid, "attachment", mime_type])
        db.connection.commit()
    else:
        post_db.execute("UPDATE ngma2_posts set guid = %s WHERE post_author = %s AND post_status = %s AND post_parent = %s;", [
                        guid, user_id, "inherit", 0])
        db.connection.commit()
    return


def update_cover(user_id, file):
    d = date.today()
    year, month = d.year, d.month
    year, month = '2069', '6'

    ftpsession = ftplib.FTP(
        'ftp.so-ham.in', 'demo@so-ham.in', 'demo123')  # Created session

    print(file)
    cur_now = datetime.now()
    mime_type = file.mimetype
    cur_now_time = cur_now.strftime("%m%d%Y%H%M%S")
    filename = str(session['user_id'])+cur_now_time+secure_filename(
        file.filename)
    print("Filename = ", filename)
    filelist = []
    ftpsession.retrlines('LIST', filelist.append)
    found = False
    for f in filelist:
        if f.split()[-1] == year:
            found = True
    if found == False:
        ftpsession.mkd(year)
    ftpsession.cwd(year)
    filelist = []
    ftpsession.retrlines('LIST', filelist.append)
    found = False
    for f in filelist:
        if f.split()[-1] == month:
            found = True
    if not found:
        ftpsession.mkd(month)
    ftpsession.cwd(month)
    ftpsession.storbinary('STOR %s' % (filename), file)
    ftpsession.quit()
    guid = "https://so-ham.in/wp-content/uploads/%s/%s/%s" % (
        year, month, filename)
    print("guid = ", guid)
    post_db = db.connection.cursor(MySQLdb.cursors.DictCursor)

    post_db.execute(
        "SELECT guid FROM ngma2_posts WHERE(post_author=%s AND post_status=%s AND post_parent=%s)",
        (user_id, 'cover', '0'))
    profile_pic = post_db.fetchone()
    print(profile_pic)
    if profile_pic is None:
        post_date = datetime.now()
        post_date_gmt = datetime.now(timezone('UTC')).astimezone(
            timezone('Asia/Kolkata'))
        title = str(user_id)+"cover_pic"
        post_db.execute("INSERT INTO sohamgu4_ngma_db.ngma2_posts(post_author, post_date, post_date_gmt,post_modified, post_modified_gmt, post_title,post_status,comment_status,ping_status,post_parent,guid,post_type,post_mime_type) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", [
                        user_id, post_date, post_date_gmt, post_date, post_date_gmt, title, "cover", "closed", "closed", 0, guid, "attachment", mime_type])
        db.connection.commit()
    else:
        post_db.execute("UPDATE ngma2_posts set guid = %s WHERE post_author = %s AND post_status = %s AND post_parent = %s;", [
                        guid, user_id, "cover", 0])
        db.connection.commit()
    return


@app.route('/upload', methods=['POST', 'GET'])
def uploader():
    d = date.today()
    year, month = d.year, d.month
    year, month = '2069', '6'
    if request.method == 'POST':
        file = request.files['file']
        if file:
            ftpsession = ftplib.FTP(
                'ftp.so-ham.in', 'demo@so-ham.in', 'demo123')  # Created session
            cur_now = datetime.now()
            cur_now_time = cur_now.strftime("%m%d%Y%H%M%S")
            filename = str(session['user_id'])+cur_now_time+'-'+secure_filename(
                file.filename)
            filelist = []
            print(file)
            ftpsession.retrlines('LIST', filelist.append)
            found = False
            for f in filelist:
                if f.split()[-1] == year:
                    found = True
            if found == False:
                ftpsession.mkd(year)
            ftpsession.cwd(year)
            filelist = []
            ftpsession.retrlines('LIST', filelist.append)
            found = False
            for f in filelist:
                if f.split()[-1] == month:
                    found = True
            if not found:
                ftpsession.mkd(month)
            ftpsession.cwd(month)
            ftpsession.storbinary('STOR %s' % (filename), file)
            ftpsession.quit()

            post_author = session['user_id']
            post_date = datetime.now()
            post_date_gmt = datetime.now(timezone('UTC')).astimezone(
                timezone('Asia/Kolkata'))
            print(post_date, post_date_gmt)
            post_content = request.form['description']
            post_title = request.form['title']

            guid = "https://so-ham.in/wp-content/uploads/%s/%s/%s" % (
                year, month, filename)

            post_db = db.connection.cursor(MySQLdb.cursors.DictCursor)
            post_db.execute(
                "INSERT INTO sohamgu4_ngma_db.ngma2_posts(post_author, post_date, post_date_gmt, post_content, post_title,guid,post_type ) VALUES(%s,%s,%s,%s,%s,%s,%s)",
                (post_author, post_date, post_date_gmt, post_content, post_title, guid, 'attachment'))
            post_db.execute(
                "SELECT MAX(ID) AS ID FROM sohamgu4_ngma_db.ngma2_posts")
            ID = post_db.fetchone()
            post_db.execute(
                "INSERT INTO sohamgu4_ngma_db.ngma2_posts(post_author, post_date, post_date_gmt, post_content, post_title,guid,post_type,post_parent ) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",
                (post_author, post_date, post_date_gmt, post_content, post_title, guid, 'attachment', ID['ID']))
            # post_db.execute(
            #     "UPDATE sohamgu4_ngma_db.ngma2_posts SET post_parent =%s WHERE ID = %s", [ID["ID"], ID["ID"]])
            print(ID)
            db.connection.commit()
    return render_template("submitForm.html", user=session['user'])


@ app.route('/homepage')
def homepage():
    # print(session)
    # start = time.time()
    home_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    home_cursor.execute(
        "SELECT ID,post_author,post_title,guid FROM ngma2_posts WHERE (post_status=%s AND post_parent=%s AND guid IS NOT NULL) ORDER BY post_date DESC LIMIT 30",
        ('publish', '0'))
    posts = home_cursor.fetchall()

    for one_post in posts:
        author_current = one_post['post_author']
        home_cursor.execute(
            "SELECT display_name FROM ngma2_users WHERE ID=%s", [author_current])
        author_str = home_cursor.fetchone()
        one_post['post_author_name'] = author_str['display_name']

        home_cursor.execute(
            "SELECT guid FROM ngma2_posts WHERE(post_author=%s AND post_status=%s AND post_parent=%s)",
            (author_current, 'inherit', '0'))
        profile_pic = home_cursor.fetchone()
        if profile_pic is not None:
            one_post['pp_link'] = profile_pic['guid']
        else:
            one_post['pp_link'] = "https://plusvalleyadventure.com/wp-content/uploads/2020/11/default-user-icon-8.jpg"

        post_id = one_post['ID']
        home_cursor.execute("SELECT COUNT(vote_id) AS total FROM ngma2_exc_votes WHERE (post_id=%s AND status=%s)",
                            ([post_id], '1'))
        post_likes = home_cursor.fetchone()
        one_post['likes'] = post_likes['total']

        post_id = one_post['ID']
        home_cursor.execute(
            "SELECT * FROM ngma2_posts WHERE (post_parent=%s AND post_type=%s AND guid is NOT NULL)",
            (post_id, 'attachment'))

        display_photo = home_cursor.fetchone()
        # print("SELECT * FROM ngma2_posts WHERE (post_parent=%s AND post_type=%s AND guid is NOT NULL)",
        #       (post_id, 'attachment'))
        # print(post_id, display_photo)
        home_cursor.execute("SELECT meta_value FROM ngma2_postmeta WHERE(post_id=%s AND meta_key=%s)",
                            (post_id, '_exc_views_count'))
        view_count = home_cursor.fetchone()

        if view_count is not None:
            one_post['views'] = view_count['meta_value']

        if display_photo is not None:
            # print(post_id, display_photo['ID'])
            one_post['guid'] = display_photo['guid']
        else:
            one_post['guid'] = "http://www.tgsin.in/images/joomlart/demo/default.jpg"
    # end = time.time()
    if posts is not None:
        # print(end-start)
        return render_template("homePage.html", posts=posts)
    else:
        return "No posts to display."


@ app.route('/post/<post_id>', methods=['POST', 'GET'])
def post(post_id):
    print(post_id)
    if request.method == "POST":
        data = request.form
        insert_comment_post(data['comment'], session['user_id'], post_id)

    post_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    post_cursor.execute("SELECT * FROM ngma2_posts WHERE ID= %s", [post_id])
    post_page = post_cursor.fetchone()
    post_cursor.execute(
        "SELECT * FROM ngma2_posts WHERE (post_parent=%s AND post_type=%s AND guid is NOT NULL)",
        (post_id, 'attachment'))
    dp = post_cursor.fetchone()

    if dp is not None:
        display_photo = dp['guid']
    else:
        display_photo = "http://www.tgsin.in/images/joomlart/demo/default.jpg"

    author_current = post_page['post_author']
    post_cursor.execute(
        "SELECT display_name FROM ngma2_users WHERE ID=%s", [author_current])
    author_name = post_cursor.fetchone()
    post_page['display_name'] = author_name['display_name']

    post_cursor.execute(
        "SELECT * FROM ngma2_posts WHERE post_status = %s AND post_author = %s AND post_parent = %s ORDER BY post_date DESC LIMIT 8", ['publish', author_current, 0])
    author_work = post_cursor.fetchall()
    print(author_work)
    post_cursor.execute("SELECT * FROM ngma2_posts WHERE(post_author=%s AND post_status=%s AND post_parent=%s)",
                        ([author_current], 'inherit', '0'))
    author_pp = post_cursor.fetchone()
    if author_pp is not None:
        post_page['author_pp'] = author_pp['guid']
    else:
        post_page['author_pp'] = "https://plusvalleyadventure.com/wp-content/uploads/2020/11/default-user-icon-8.jpg"

    post_cursor.execute(
        "SELECT COUNT(follower_id) AS total FROM ngma2_exc_followers WHERE (follower_author_id=%s AND follower_status=%s)",
        ([author_current], '1'))
    post_profile_followers = post_cursor.fetchone()
    post_page['follows'] = post_profile_followers['total']

    post_cursor.execute(
        "SELECT * FROM ngma2_posts WHERE post_parent = %s", [post_id])
    child_posts = post_cursor.fetchone()
    # print(child_posts)

    post_cursor.execute(
        "SELECT * FROM ngma2_comments WHERE comment_post_ID=%s", [post_id])
    post_comments = post_cursor.fetchall()
    for work in author_work:
        post_cursor.execute(
            "SELECT * FROM ngma2_posts WHERE (post_parent=%s AND post_type=%s AND guid is NOT NULL)",
            (work['ID'], 'attachment'))
        guid = post_cursor.fetchone()
        if guid is not None:
            work['guid'] = guid['guid']
        else:
            work['guid'] = "http://www.tgsin.in/images/joomlart/demo/default.jpg"

    for comment in post_comments:
        author_email_current = comment['comment_author_email']
        post_cursor.execute("SELECT ID FROM ngma2_users WHERE user_email=%s", [
                            author_email_current])
        author = post_cursor.fetchone()

        post_cursor.execute(
            "SELECT * FROM ngma2_posts WHERE(post_author=%s AND post_status=%s AND post_parent=%s)",
            (author['ID'], 'inherit', '0'))
        profile_pic = post_cursor.fetchone()
        if profile_pic is not None:
            comment['pp_link'] = profile_pic['guid']
        else:
            comment[
                'pp_link'] = "https://plusvalleyadventure.com/wp-content/uploads/2020/11/default-user-icon-8.jpg"
        # post_cursor.close()

    post_cursor.execute("SELECT * FROM ngma2_posts WHERE(post_author=%s AND post_status=%s AND post_parent=%s)",
                        (session['user_id'], 'inherit', '0'))
    self_pp = post_cursor.fetchone()

    if self_pp is not None:
        post_page['self_pp_link'] = self_pp['guid']
    else:
        post_page['self_pp_link'] = "https://plusvalleyadventure.com/wp-content/uploads/2020/11/default-user-icon-8.jpg"

    return render_template("artDescription.html", display_photo=display_photo, post_comments=post_comments, post_page=post_page,
                           post_children=child_posts, count=len(post_comments), total_work=author_work, user_id=session['user_id'], postid=post_id)


@ app.route('/about')
def about():
    return render_template('about.html')


@ app.route('/contact', methods=['POST', 'GET'])
def contact():
    if "email" in request.form:
        email = request.form['email']
        name = request.form['name']
        subject = request.form['subject']
        message = request.form['message']
        receiver = "soham.ngma@gmail.com"

        if email is not None and name is not None and subject is not None and message is not None:

            msg = Message(subject, sender='soham.ngma.noreply@gmail.com',
                          recipients=[receiver])
            msg.body = 'Sender email: {}\r\nName: {}\r\nMessage:{}'.format(
                email, name, message)
            # send_email.send(msg)
            print(request.form)
            return "Email has been sent."

        else:
            return "Please fill all details correctly."

    return render_template("contact.html")

@ app.route('/adminLogin', methods=['POST', 'GET'])
def adminLogin():
    if request.method == 'POST':
        print(1, request.form)
        if 'username' in request.form and 'password' in request.form:

            admin_username = request.form.get('username')
            admin_password = request.form.get('password')
            username = "ngma.soham2021@gmail.com"
            password = admin_password
            print(username, password)
            cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM ngma2_users WHERE user_email=%s or user_login=%s ",
                           (username, username))
            admin = cursor.fetchone()
            
            cursor.execute("SELECT * FROM ngma2_users WHERE user_email=%s or user_login=%s ",
                           (username, username))
            info = cursor.fetchone()
            admin_pass = info['user_pass']

            if info is not None and admin_username==username:
                if check_password_hash(admin_pass, password) and info['user_confirmed'] == 0 and (
                        info['user_email'] == username or info['user_login'] == username):
                    return "Please confirm your email."

                elif check_password_hash(admin_pass, password) and (
                        info['user_email'] == username or info['user_login'] == username):
                    session['user'] = info['user_login']
                    session['display_name'] = info['display_name']
                    session['user_id'] = info['ID']

                    return redirect(url_for('museumAccountCreation'))

                else:
                    return "Invalid credentials"

            return "Invalid credentials"
    return render_template("adminLogin.html")

@ app.route('/museum/createAccount', methods=['POST', 'GET'])
def museumAccountCreation():
    if "username" in request.form and "email" in request.form and "password" in request.form and "website" in  request.form and "location" in request.form and "contact" in request.form:
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        website_url = request.form['website']
        location = request.form['location']
        contact = request.form['contact']
        time_code = datetime.now()
        password_hashed = generate_password_hash(
            password, "pbkdf2:sha256", salt_length=8)
        if username is not None and email is not None and password is not None and website_url is not None and location is not None and contact is not None:
    
            check_email_login = db.connection.cursor(
                MySQLdb.cursors.DictCursor)
            check_email_login.execute("SELECT * FROM ngma2_museums WHERE email=%s or name=%s",
                                      (email, username))
            info = check_email_login.fetchone()

            if info is not None:
                return "Username or email address is already in use."
            
            register_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
            
            register_cursor.execute(
                "INSERT INTO sohamgu4_ngma_db.ngma2_users(user_login, user_pass, user_email, display_name, "
                "user_registered,user_confirmed) VALUES(%s,%s,%s,%s,%s,%s)",
                (username, password_hashed, email, username, time_code, 0))
            db.connection.commit()
            
            register_cursor.execute(
                "INSERT INTO sohamgu4_ngma_db.ngma2_museums(name, location, email, website_url, "
                "contact_no ,password) VALUES(%s,%s,%s,%s,%s,%s)",
                (username, location, email, website_url, contact, password_hashed))
            db.connection.commit()

        return 'Congratulations! Your Museum has been registered.'
    return render_template("museumAccount.html")

@ app.route('/blog', methods=['POST', 'GET'])
def blog():
    page = request.args.get('page', 1, type=int)
    LIMIT = 10
    offset = (page-1)*LIMIT
    print('offset', offset)

    blog_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    blog_cursor.execute("SELECT * FROM ngma2_blog")
    total_row = blog_cursor.rowcount
    total_page = math.ceil(total_row/LIMIT)

    next = page + 1
    prev = page - 1
    print('next', next)
    blog_cursor.execute(
        "SELECT * FROM ngma2_blog ORDER BY post_date desc LIMIT %s OFFSET %s", (LIMIT, offset))

    print(total_page)
    blog_posts = blog_cursor.fetchall()
    return render_template("blog.html", blog_posts=blog_posts, pages=total_page, next=next, prev=prev, current_page=page)


@ app.route('/museum')
def museum():
    museum_name = "NGMADELHI"
    museum_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    museum_cursor.execute(
        "SELECT * FROM ngma2_users WHERE user_login= %s", [museum_name])
    museum_details = museum_cursor.fetchone()
    # print(museum_details)
    museum_id = museum_details["ID"]
    # print(museum_id)
    museum_cursor.execute(
        "SELECT * FROM ngma2_posts WHERE(post_author=%s AND post_status=%s AND post_parent=%s)",
        (museum_id, 'inherit', '0'))
    profile_pic_link = museum_cursor.fetchone()
    if profile_pic_link is not None:
        museum_details['pp_link'] = profile_pic_link['guid']
    else:
        museum_details['pp_link'] = "https://plusvalleyadventure.com/wp-content/uploads/2020/11/default-user-icon-8.jpg"
    print(museum_details)

    return render_template("museumCorner.html", museum_details=museum_details)


def insert_comment(comment, user_id, comment_post_ID):
    user_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    user_cursor.execute(
        "SELECT * FROM ngma2_users WHERE ID =%s" % user_id)
    user = user_cursor.fetchone()
    now_utc = datetime.now()
    now_asia = datetime.now(timezone('UTC')).astimezone(
        timezone('Asia/Kolkata'))
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}
    response = requests.get("http://localhost:5000/", headers=headers)
    Ip = socket.gethostbyname(socket.gethostname())
    comment_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    comment_cursor.execute("INSERT INTO ngma2_theme_comments(comment_post_ID,comment_author,comment_author_email,comment_author_IP,comment_date,comment_date_gmt,comment_content, comment_approved,comment_agent,comment_parent,user_id) values(%s, %s,%s,%s, %s,%s, %s,%s, %s,%s, %s)",
                           (comment_post_ID, user['display_name'], user["user_email"], Ip, now_asia, now_utc, comment, '1', "comment_agent", 0, user_id))
    db.connection.commit()
    return


@ app.route('/delete_comment/<theme_id>/<comment_id>', methods=['POST', 'GET'])
def delete_comment(theme_id, comment_id):
    comment_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    comment_cursor.execute(
        "delete FROM ngma2_theme_comments WHERE comment_ID =%s" % comment_id)
    db.connection.commit()
    return redirect(url_for('theme_ID', theme_id=theme_id))


def insert_comment_post(comment, user_id, comment_post_ID):
    user_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    user_cursor.execute(
        "SELECT * FROM ngma2_users WHERE ID =%s" % user_id)
    user = user_cursor.fetchone()
    now_utc = datetime.now()
    now_asia = datetime.now(timezone('UTC')).astimezone(
        timezone('Asia/Kolkata'))
    Ip = socket.gethostbyname(socket.gethostname())
    comment_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    comment_cursor.execute("INSERT INTO ngma2_comments(comment_post_ID,comment_author,comment_author_email,comment_author_IP,comment_date,comment_date_gmt,comment_content, comment_approved,comment_agent,comment_parent,user_id) values(%s, %s,%s,%s, %s,%s, %s,%s, %s,%s,%s)",
                           (comment_post_ID, user['display_name'], user["user_email"], Ip, now_asia, now_utc, comment, 1, "-", 0, user_id))
    db.connection.commit()
    return


@ app.route('/delete_comment_post/<post_id>/<comment_id>', methods=['POST', 'GET'])
def delete_comment_post(post_id, comment_id):
    comment_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    comment_cursor.execute(
        "delete FROM ngma2_comments WHERE comment_ID =%s" % comment_id)
    db.connection.commit()
    return redirect(url_for('post', post_id=post_id))


@ app.route('/theme/<theme_id>', methods=['POST', 'GET'])
def theme_ID(theme_id):
    data = request.form
    print(data)
    if request.method == "POST":
        insert_comment(data['comment'], session['user_id'], theme_id)
    theme_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    theme_cursor.execute("SELECT * FROM ngma2_themeof_month WHERE ID=%s", [theme_id])
    theme_post = theme_cursor.fetchone()

    Months = dict()
    year = '2020'
    for month in range(1, 13):
        month_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        month_cursor.execute(
            "SELECT * FROM ngma2_themes WHERE month(post_date)=%s and year(post_date) = %s", [month, year])
        theme_post1 = month_cursor.fetchone()
        if theme_post1 is not None:
            Months[month] = theme_post1['ID']
        else:
            Months[month] = None
    print(Months)

    list(theme_post['content'])
    theme_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    theme_cursor.execute(
        "SELECT * FROM ngma2_theme_comments WHERE comment_post_ID=%s", [theme_id])
    theme_comments = theme_cursor.fetchall()
    for comment in theme_comments:
        em = comment['comment_author_email']
        theme_cursor.execute(
            "SELECT * FROM ngma2_users WHERE user_email=%s", [em])
        author_details = theme_cursor.fetchone()
        author_current = author_details['ID']

        theme_cursor.execute(
            "SELECT * FROM ngma2_posts WHERE(post_author=%s AND post_status=%s AND post_parent=%s)",
            (author_current, 'inherit', '0'))
        profile_pic = theme_cursor.fetchone()
        if profile_pic is not None:
            comment['pp_link'] = profile_pic['guid']
        else:
            comment['pp_link'] = "https://plusvalleyadventure.com/wp-content/uploads/2020/11/default-user-icon-8.jpg"
    # print("theme_post", theme_post)
    try:
        theme_month = theme_post['datetime'].month
    except:
        theme_month = datetime.today().month
    print(theme_month)
    return render_template("theme.html", theme_post=theme_post, theme_comments=theme_comments, Months=Months, count=len(theme_comments), theme_month=theme_month)# , user_id=session['user_id'])
  


@ app.route('/theme-of-the-month/', methods=['POST', 'GET'])
def theme():
    theme_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    theme_cursor.execute(
            "SELECT * FROM sohamgu4_ngma_db.ngma2_themeof_month ORDER BY ID DESC LIMIT 1")
    theme_post = theme_cursor.fetchone()
    print(theme_post)
    # if theme_post is None:
    #     theme_cursor.execute(
    #         "SELECT * FROM ngma2_themes WHERE month(post_date)=%s and year(post_date) = %s", [month-1, year])
    #     theme_post = theme_cursor.fetchone()
    return redirect(url_for('theme_ID', theme_id=theme_post['ID']))


@ app.route('/events')
def events():
    event_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    event_cursor.execute(
        "SELECT thumbnail,title,type, time_format(time_from,'%h:%i %p') as timestringfrom,time_format(time_to,'%h:%i %p') as timestringto,description,date_format(date_from,'%a, %M %d, %Y') as datestringfrom,date_format(date_to,'%a, %M %d, %Y') as datestringto FROM ngma2_events")
    ev = event_cursor.fetchall()
    return render_template("events.html",ev=ev)



@ app.route('/exhibitions')
def exhibitions():
    ex_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    past = []
    future = []
    current = []
    ex_cursor.execute("SELECT * FROM ngma2_exhibitions")
    all_ex = ex_cursor.fetchall()
    for ex in all_ex:
        if ex['Status'] == -1:
            past.append(ex)
        elif ex['Status'] == 0:
            current.append(ex)
        else:
            future.append(ex)
    # print(past)
    # print(current)
    # print(future)
    return render_template("exhibitions.html", past=past, upcoming=future, current=current)


@ app.route('/livestream')
def livestream():
    ls_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    past = []
    future = []
    current = []
    ls_cursor.execute("SELECT * FROM ngma2_live_stream")
    all_streams = ls_cursor.fetchall()
    for stream in all_streams:
        if stream['Status'] == -1:
            past.append(stream)
        elif stream['Status'] == 0:
            current.append(stream)
        else:
            future.append(stream)
    return render_template("livestream.html", past=past, upcoming=future, current=current)


@ app.route('/hall-of-fame')
def hall_of_fame():
    # d = date.today()
    # year, month = d.year,d.month
    Months = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
              7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}
    year, month = "2022", "01"
    post_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    user_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    hall_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    hall_cursor.execute(
        "SELECT * FROM ngma2_hall_of_fame WHERE month=%s and year = %s", [month, year])
    hall_post = hall_cursor.fetchone()
    dp = None

    if hall_post is None:
        hall_cursor.execute(
            "SELECT * FROM ngma2_hall_of_fame WHERE month=%s and year = %s", [month-1, year])
        hall_post = hall_cursor.fetchone()

    user_cursor.execute(
        "SELECT * FROM ngma2_users WHERE ID=%s", [hall_post['user_id']])
    author_details = user_cursor.fetchone()
    author_current = author_details['ID']
    user_cursor.execute(
        "SELECT * FROM ngma2_posts WHERE(post_author=%s AND post_status=%s AND post_parent=%s)",
        (author_current, 'inherit', '0'))
    profile_pic = user_cursor.fetchone()
    if profile_pic is not None:
        dp = profile_pic['guid']
    else:
        dp = "https://plusvalleyadventure.com/wp-content/uploads/2020/11/default-user-icon-8.jpg"

    # print(hall_post)
    post_cursor.execute(
        "SELECT * FROM ngma2_posts WHERE ID = %s", [hall_post['post_id']])

    user_cursor.execute(
        "SELECT * FROM ngma2_users WHERE ID = %s", [hall_post['user_id']])
    post = post_cursor.fetchone()
    post_cursor.execute(
        "SELECT * FROM ngma2_posts WHERE (post_parent=%s AND post_type=%s AND guid is NOT NULL)",
        (post['ID'], 'attachment'))
    # print("post", post)
    display_photo = post_cursor.fetchone()

    if display_photo is not None:
        post['guid'] = display_photo['guid']
    else:
        post['guid'] = "http://www.tgsin.in/images/joomlart/demo/default.jpg"
    month = Months[int(month)]
    photo = post['guid']
    # print(post)
    print(photo)
    return render_template("HallOfFame.html", hall_post=hall_post, post=post, month=month, dp=dp, photo=photo)


@ app.route('/profile/<user_id>')
def profile(user_id):
    profile_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    profile_cursor.execute("SELECT * FROM ngma2_users WHERE ID= %s", [user_id])
    profile_details = profile_cursor.fetchone()

    profile_cursor.execute(
        "SELECT * FROM ngma2_posts WHERE(post_author=%s AND post_status=%s AND post_parent=%s)",
        (user_id, 'inherit', '0'))
    profile_pic_link = profile_cursor.fetchone()
    profile_cursor.execute(
        "SELECT guid FROM ngma2_posts WHERE(post_author=%s AND post_status=%s AND post_parent=%s)",
        (user_id, 'cover', '0'))
    cover_pic = profile_cursor.fetchone()
    profile_cursor.execute(
        "SELECT * FROM ngma2_exc_followers WHERE (follower_author_id=%s AND follower_user_id=%s)",
        (user_id, session['user_id']))
    followed = profile_cursor.fetchone()
    is_followed = True
    if followed is None:
        is_followed = False
    elif followed['follower_status'] == 1:
        is_followed = True
    else:
        is_followed = False

    if profile_pic_link is not None:
        profile_details['pp_link'] = profile_pic_link['guid']
        print(profile_pic_link['guid'])
    else:
        profile_details['pp_link'] = "https://plusvalleyadventure.com/wp-content/uploads/2020/11/default-user-icon-8.jpg"
    if cover_pic is not None:
        profile_details['cover_pic'] = cover_pic['guid']
    else:
        profile_details['cover_pic'] = "https://so-ham.in/wp-content/uploads/2022/02/Default_cover_pic.jpeg"

    profile_cursor.execute("SELECT COUNT(vote_id) AS total FROM ngma2_exc_votes WHERE (author_id=%s AND status=%s)",
                           ([user_id], '1'))
    profile_likes = profile_cursor.fetchone()
    profile_details['likes'] = profile_likes['total']

    profile_cursor.execute(
        "SELECT COUNT(follower_id) AS total FROM ngma2_exc_followers WHERE (follower_author_id=%s AND follower_status=%s)",
        ([user_id], '1'))
    profile_followers = profile_cursor.fetchone()
    profile_details['follows'] = profile_followers['total']

    profile_cursor.execute(
        "SELECT COUNT(follower_id) AS total FROM ngma2_exc_followers WHERE (follower_user_id=%s AND follower_status=%s)",
        ([user_id], '1'))
    profile_following = profile_cursor.fetchone()
    profile_details['following'] = profile_following['total']

    profile_cursor.execute(
        "SELECT * FROM ngma2_posts WHERE (post_author=%s AND post_status=%s AND post_parent=%s) ORDER BY post_date DESC LIMIT 20",
        (user_id, 'publish', '0'))
    profile_posts = profile_cursor.fetchall()

    for one_profile_post in profile_posts:
        profile_post_id = one_profile_post['ID']
        profile_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        profile_cursor.execute(
            "SELECT COUNT(vote_id) AS total FROM ngma2_exc_votes WHERE (post_id=%s AND status=%s)",
            ([profile_post_id], '1'))
        profile_post_likes = profile_cursor.fetchone()
        one_profile_post['likes'] = profile_post_likes['total']

        profile_cursor.execute("SELECT * FROM ngma2_posts WHERE (post_parent=%s AND post_type=%s)",
                               (profile_post_id, 'attachment'))
        display_photo = profile_cursor.fetchone()

        profile_cursor.execute("SELECT * FROM ngma2_postmeta WHERE(post_id=%s AND meta_key=%s)",
                               (profile_post_id, '_exc_views_count'))
        profile_view_count = profile_cursor.fetchone()
        if profile_view_count is not None:
            one_profile_post['views'] = profile_view_count['meta_value']

        if display_photo is not None:
            one_profile_post['guid'] = display_photo['guid']
        else:
            one_profile_post['guid'] = "http://www.tgsin.in/images/joomlart/demo/default.jpg"

    return render_template("userProfile.html", profile_details=profile_details,
                           posts=profile_posts, is_followed=is_followed)  # , liked_posts = liked_posts)


@ app.route('/profile/follow/<follower_author_id>', methods=['POST', 'GET'])
def follow(follower_author_id):
    if 'user' in session:
        follow_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        follow_cursor.execute(
            "SELECT * FROM ngma2_exc_followers WHERE (follower_author_id=%s AND follower_user_id=%s)",
            (follower_author_id, session['user_id']))
        followed = follow_cursor.fetchone()

        if followed is None:

            if session['user_id'] == follower_author_id:
                return "You can't follow yourself!"

            follow_cursor.execute(
                "INSERT INTO sohamgu4_ngma_db.ngma2_exc_followers(follower_author_id, follower_user_id, follower_status) VALUES(%s,%s,%s)",
                (follower_author_id, session['user_id'], '1'))
            db.connection.commit()

        elif followed['follower_status'] == 1:

            if session['user_id'] == follower_author_id:
                return "You can't follow yourself!"

            follow_cursor.execute(
                "UPDATE ngma2_exc_followers SET follower_status=%s WHERE (follower_user_id=%s AND follower_author_id=%s)",
                (0, session['user_id'], follower_author_id))
            db.connection.commit()

        else:

            if session['user_id'] == follower_author_id:
                return "You can't follow yourself!"

            follow_cursor.execute("UPDATE ngma2_exc_followers SET follower_status=%s WHERE (follower_user_id=%s AND "
                                  "follower_author_id=%s)",
                                  (1, session['user_id'], follower_author_id))
            db.connection.commit()

        return redirect(url_for('profile', user_id=follower_author_id))
    else:
        return "Please log in!"


@ app.route('/profile/profile_like/<author_id>/<post_id>', methods=['POST', 'GET'])
def profile_like(author_id, post_id):
    if 'user' in session:
        profile_like_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        profile_like_cursor.execute("SELECT * FROM ngma2_exc_votes WHERE (post_id=%s AND user_id=%s)",
                                    (post_id, session['user_id']))
        liked = profile_like_cursor.fetchone()

        if liked is None:
            profile_like_cursor.execute(
                "INSERT INTO sohamgu4_ngma_db.ngma2_exc_votes(author_id, post_id, user_id, status) VALUES(%s,%s,%s,%s)",
                (author_id, post_id, session['user_id'], '1'))
            db.connection.commit()

        elif liked['status'] == 1:
            profile_like_cursor.execute("UPDATE ngma2_exc_votes SET status=%s WHERE user_id=%s AND post_id=%s",
                                        (0, session['user_id'], post_id))
            db.connection.commit()

        else:
            profile_like_cursor.execute(
                "UPDATE ngma2_exc_votes SET status=%s WHERE (user_id=%s AND post_id=%s)",
                (1, session['user_id'], post_id))
            db.connection.commit()

        return redirect(url_for('profile', user_id=author_id))
    else:
        return "Please log in!"


@ app.route('/editprofile/<int:user_id>', methods=['POST', 'GET'])
def edit(user_id):
    ec = None
    edit_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    edit_cursor.execute("SELECT * FROM ngma2_profile WHERE ID=%s", [user_id])
    profile_detail = edit_cursor.fetchone()

    edit_cursor.execute(
        "SELECT guid FROM ngma2_posts WHERE(post_author=%s AND post_status=%s AND post_parent=%s)",
        (user_id, 'inherit', '0'))

    profile_pic = edit_cursor.fetchone()
    pp_link = "https://plusvalleyadventure.com/wp-content/uploads/2020/11/default-user-icon-8.jpg"
    if profile_pic is not None:
        pp_link = profile_pic['guid']

    if profile_detail is None:
        edit_cursor.execute("SELECT * FROM ngma2_users WHERE ID=%s", [user_id])
        ec = edit_cursor.fetchone()
        print('user not register in profile', ec)
    else:
        edit_cursor.execute(
            "SELECT * FROM ngma2_profile JOIN ngma2_users ON ngma2_profile.ID=ngma2_users.ID WHERE ngma2_profile.id = %s", [user_id])
        ec = edit_cursor.fetchone()

    # edit_cursor.execute(
    #     "SELECT * FROM ngma2_profile JOIN ngma2_users ON ngma2_profile.ID=ngma2_users.ID JOIN ngma2_posts ON ngma2_profile.ID=ngma2_posts.ID WHERE ngma2_profile.id = %s", [user_id])
    # #edit_cursor.execute("SELECT * FROM ngma2_profile,ngma2_users,ngma2_posts WHERE ngma2_profile.ID = %s AND ngma2_profile.ID = ngma2_users.ID AND ngma2_posts.ID = ngma2_profile.ID", [user_id])
    # ec = edit_cursor.fetchone()
    # #profile_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    # edit_cursor.execute("SELECT * FROM ngma2_users WHERE ID= %s", [user_id])
    # profile_details = edit_cursor.fetchone()

    # edit_cursor.execute(
    #     "SELECT * FROM ngma2_posts WHERE(post_author=%s AND post_status=%s AND post_parent=%s)",
    #     (user_id, 'inherit', '0'))
    # profile_pic_link = edit_cursor.fetchone()

    # if profile_pic_link is not None:
    #     profile_details['pp_link'] = profile_pic_link['guid']
    # else:
    #     profile_details['pp_link'] = "https://plusvalleyadventure.com/wp-content/uploads/2020/11/default-user-icon-8.jpg"
    # # print(profile_details)
    return render_template('editProfile.html', ec=ec, profile_details='', user_id=user_id, pp_link=pp_link)

    # return render_template("editProfile.html")


@app.route('/editprofile/update/<int:user_id>', methods=['POST', 'GET'])
def update(user_id):
    if request.method == "POST":
        # print(user_id)
        _id = user_id
        _fname = request.form['first_name']
        _lname = request.form['last_name']
        _dob = request.form['dob']
        _gender = request.form['gender']
        _message = request.form['message']
        _phone = request.form['phone']
        _address = request.form['address']
        _city = request.form['city']
        _state = request.form['state']
        _pin = request.form['pincode']
        _country = request.form['country']
        _skype = request.form['skype']
        _facebook = request.form['facebook']
        _youtube = request.form['youtube']
        _twitter = request.form['twitter']
        _google = request.form['google']
        _instagram = request.form['instagram']
        _oldpassword = request.form['oldPassword']
        _newpassword = request.form['newPassword']
        _confirmpassword = request.form['confirmPassword']
        #_password = request.form['password']
        #_c_password = request.form['c_password']

        # password_hashed = generate_password_hash(
        #    _password, "pbkdf2:sha256", salt_length=8)
        print("here", request.form)
        print('--', request.files)
        if 'file' in request.files and request.files['file']:
            print("update profile called")
            update_profile(user_id, request.files['file'])

        if 'cover' in request.files and request.files['cover']:
            print("update cover profile called")
            update_cover(user_id, request.files['cover'])

        if _oldpassword and _newpassword and _confirmpassword:
            changepassword(_id, _oldpassword, _newpassword, _confirmpassword)
        edit_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        edit_cursor.execute(
            "SELECT * FROM ngma2_profile WHERE ID=%s", [user_id])
        profile_detail = edit_cursor.fetchone()
        if profile_detail is None:
            edit_cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
            edit_cursor.execute("INSERT INTO ngma2_profile(ID, first_name, last_name, Dob, gender, connects_to_art, contact_no, address, city, state, pin_code, country, skype_id, facebook, youtube, twitter, google, instagram) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (
                _id, _fname, _lname, _dob, _gender, _message, _phone, _address, _city, _state, _pin, _country, _skype, _facebook, _youtube, _twitter, _google, _instagram))
            db.connection.commit()
        else:
            edit_cursor.execute("UPDATE ngma2_profile SET first_name=%s,last_name=%s,Dob=%s,gender=%s,connects_to_art=%s,contact_no=%s,address=%s,city=%s,state=%s, pin_code=%s,country=%s,skype_id=%s,facebook=%s,youtube=%s,twitter=%s,google=%s,instagram=%s WHERE ID=%s", ([
                                _fname], [_lname], [_dob], [_gender], [_message], [_phone], [_address], [_city], [_state], [_pin], [_country], [_skype], [_facebook], [_youtube], [_twitter], [_google], [_instagram], [_id]))
            db.connection.commit()
    # edit_cursor.execute(
    #     "SELECT * FROM ngma2_profile JOIN ngma2_users ON ngma2_profile.ID=ngma2_users.ID JOIN ngma2_posts ON ngma2_profile.ID=ngma2_posts.ID WHERE ngma2_profile.id = %s", [user_id])
    # profile_details = edit_cursor.fetchone()
    # if profile_details is None:
    #     edit_cursor.execute(
    #         "SELECT * FROM ngma2_users WHERE ID= %s", [user_id])
    #     profile_details = edit_cursor.fetchone()

    # new_entry = []
    # user_entered = request.form
    # print(user_entered)
    # print(profile_details)

    # for detail in user_entered:
    #     if detail == 'Dob':
    #         year, month, day = user_entered[detail].split('-')
    #         print(date(2020, 5, 17))
    #         new_entry.append(date(2020, 5, 17))
    #     elif user_entered[detail] == "":
    #         new_entry.append(profile_details[detail])
    #     else:
    #         new_entry.append(user_entered[detail])

    # print(user_entered, "\n", profile_details, "\n", new_entry)
    # edit_cursor.execute("INSERT INTO ngma2_profile(first_name,last_name,Dob,gender,connects_to_art,user_email,skype_id,facebook,youtube,twitter,google,instagram) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", new_entry)
    # edit_cursor.commit()
    return redirect('/editprofile/%s' % user_id)
    '''
    profile_details = fetch {'contact_no': 123}
    user_entered = request.form
    {'contact_no': 12345}
    new_entry = {}
    for detail in user_entered:
        if user_entered['detail'] =="":
            new_entry['detail'] = profile_details['detail']
        else:
            new_entry['detail'] = user_entered['detail']

    update_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)



    '''


@ app.route('/changepassword', methods=['POST', 'GET'])
def changepassword(user_id, _oldpassword, _newpassword, _confirmpassword):
    if request.method == "POST":
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM ngma2_users WHERE ID = %s ",
                       [user_id])
        info = cursor.fetchone()
        password_hashed = generate_password_hash(
            _newpassword, "pbkdf2:sha256", salt_length=8)

        if check_password_hash(info['user_pass'], _oldpassword):
            if _newpassword == _confirmpassword:
                cursor.execute(
                    "UPDATE ngma2_users SET user_pass=%s WHERE ID=%s", ([password_hashed], [user_id]))
                db.connection.commit()
                return redirect('/')

            else:
                return "New password and confirm password do not match"
        else:
            return "Invalid credentials"


# @app.route('/update', methods=['POST', 'GET'])
# def update():
#     up_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
#     _fname = request.form['first_name']
#     _lname = request.form['last_name']
#     _dob = request.form['dob']
#     _gender = request.form['gender']
#     _message = request.form['message']
#     #_email = request.form['email']
#     #_nemail = request.form['notification_email']
#     _phone = request.form['phone']
#     _address = request.form['address']
#     _city = request.form['city']
#     _state = request.form['state']
#     _pin = request.form['pincode']
#     _country = request.form['country']
#     _skype = request.form['skype']
#     _facebook = request.form['facebook']
#     _youtube = request.form['youtube']
#     _twitter = request.form['twitter']
#     _google = request.form['google']
#     _instagram = request.form['instagram']
#     _idd = request.form['userid']
#     _password = request.form['password']
#     password_hashed = generate_password_hash(
#             _password, "pbkdf2:sha256", salt_length=8)
#     #if _fname and _lname and _idd and _dob and _gender and _message and _phone and _address and _city and _state and _pin and _country and _skype and _google and _instagram and _twitter and _youtube and _facebook and request.method == 'POST':
#     #up_cursor.execute("UPDATE ngma2_profile SET first_name=%s,last_name=%s,Dob=%s,gender=%s,connects_to_art=%s,contact_no=%s,address=%s,city=%s,state=%s,pin_code=%s,country=%s,skype_id=%s,facebook=%s,youtube=%s,twitter=%s,google=%s,instagram=%s WHERE ID=%s",([_fname],[_lname],[_dob],[_gender],[_message],[_phone],[_address],[_city],[_state],[_pin],[_country],[_skype],[_facebook],[_youtube],[_twitter],[_google],[_instagram],[_idd]))
#     print(_gender)
#     print("hello")
#     if _fname and _lname and _dob and _gender and _message and _phone and _address and _city and _state and _pin and _country and _skype and _facebook and _youtube  and _twitter and _google and _instagram and _idd and request.method == "POST":
#         up_cursor.execute("UPDATE ngma2_profile SET first_name=%s,last_name=%s,Dob=%s,gender=%s,connects_to_art=%s,contact_no=%s,address=%s,city=%s,state=%s, pin_code=%s,country=%s,skype_id=%s,facebook=%s,youtube=%s,twitter=%s,google=%s,instagram=%s WHERE ID=%s",([_fname],[_lname],[_dob],[_gender],[_message],[_phone],[_address],[_city],[_state],[_pin],[_country],[_skype],[_facebook],[_youtube],[_twitter],[_google],[_instagram],[_idd]))
#         up_cursor.execute("UPDATE ngma2_users SET user_pass=%s WHERE ID=%s",([password_hashed],[_idd]))
#         flash('User updated successfully!')
#         db.connection.commit()
#     return redirect('/')


@app.route('/logout')
def logout():
    if "user" in session:
        session.pop("user", None)
    return redirect(url_for("index"))


@app.route('/virtual_exhibiton')
def virtualExhibitions():

    ex_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    past = []
    future = []
    current = []
    c_id = []
    p_id = []
    f_id = []
    #ex_cursor.execute("SELECT * FROM ngma2_virtual_exhibitions WHERE DISTINCT exhibition_name")
    #ex_cursor.execute("SELECT DISTINCT(exhibition_name), portrait_guid, Status FROM ngma2_virtual_exhibitions GROUP BY id HAVING COUNT(*) = 1;")
    ex_cursor.execute(
        "SELECT MIN(Status) AS Status, exhibition_name, portrait_guid, ID, post_title, post_excerpt, post_id date FROM ngma2_virtual_exhibitions GROUP BY exhibition_name")
    all_ex = ex_cursor.fetchall()
    # print(all_ex)
    for ex in all_ex:
        if ex['Status'] == -1:
            past.append(ex)
            p_id.append(ex['ID'])
        elif ex['Status'] == 0:
            current.append(ex)
            c_id.append(ex['ID'])
        else:
            future.append(ex)
    # print(past)
    # print(future)
    return render_template("virtualExhibition.html", past=past, upcoming=future, current=current, c_id=c_id)


@app.route('/virtual_exhibiton/<id>')
def singleVirtualExhibition(id):
    ve_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    ve_cursor.execute(
        "SELECT * FROM ngma2_virtual_exhibitions WHERE post_id= %s", [id])
    ve_details = ve_cursor.fetchall()
    post_guid = []
    for ve in ve_details:
        post_guid.append(ve['post_guid'])

    # print(post_guid)
    ve_cursor.execute(
        "SELECT * FROM ngma2_virtual_exhibitions WHERE post_id= %s", [id])
    ve_single_post = ve_cursor.fetchone()
    title = ve_single_post['post_title']
    # print(title)
    content = ve_single_post['post_content']
    # print(content)
    excerpt = ve_single_post['post_excerpt']
    # print(excerpt)
    name = ve_single_post['exhibition_name']
    portrait = ve_single_post['portrait_guid']

    return render_template("singleVirtualExhibition.html", post_guid=post_guid, title=title, content=content, excerpt=excerpt, name=name, portrait=portrait)

# Admin Dashboard


@ app.route('/dashboard', methods=['POST', 'GET'])
def dashboard():
    if request.method == 'POST':
        imgIdArray = request.form.getlist('imgId[]')
    return render_template("dashboard/bestArtwork.html")


@ app.route('/dashboard/bestArtwork', methods=['POST', 'GET'])
def bestArtwork():
    cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    date = datetime.today()
    month = date.month
    year = date.year
    if month == 1:
        month = 12
    else:
        month -= 1
    print(date)
    if request.method == 'POST':
        data = request.get_json()
        images = data['imgArray']
        print(images)

        for post in images:
            cursor.execute(
                "SELECT ID from ngma2_nominations WHERE (post_ID = %s AND year=%s AND month = %s)", [post['id'], year, month])
            present = cursor.fetchone()
            if not present:
                cursor.execute(
                    "INSERT INTO ngma2_nominations(post_ID,year,month,guid) values(%s,%s,%s,%s)", [post['id'], year, month, post['src']])
                db.connection.commit()
        return render_template("dashboard/nomination.html")

    print(month)

    cursor.execute(
        "SELECT ID,post_author,post_title,guid FROM ngma2_posts WHERE (post_status=%s AND post_parent=%s AND guid IS NOT NULL AND MONTH(post_date)=%s AND YEAR(post_date)=%s)",
        ('publish', '0', month, year))

    posts = cursor.fetchall()
    all_posts = []
    for post in posts:
        cursor.execute(
            "SELECT ID from ngma2_nominations WHERE (post_ID = %s AND year=%s AND month = %s)", [post['ID'], year, month])
        present = cursor.fetchone()
        if not present:
            cursor.execute(
                "SELECT guid FROM ngma2_posts WHERE (post_parent=%s AND post_type=%s AND guid is NOT NULL)",
                (post['ID'], 'attachment'))
            picture = cursor.fetchone()
            if picture is not None:
                post["display_photo"] = picture['guid']
                all_posts.append(post)

    return render_template("dashboard/bestArtwork.html", posts=all_posts)


@app.route('/dashboard/nomination', methods=['POST', 'GET'])
def nomination():
    cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    date = datetime.today()
    month = date.month
    year = date.year
    if month == 1:
        month = 12
    else:
        month -= 1
    print(date)
    cursor.execute(
        "SELECT * from ngma2_nominations WHERE year=%s AND month = %s", [year, month])
    all_posts = cursor.fetchall()
    return render_template("dashboard/nomination.html", posts=all_posts)


@ app.route('/dashboard/hallOffame', methods=['GET', 'POST'])
def hallOffame():
    id = request.args.get('id')
    print(id)
    image = request.args.get('image')
    print(image)
    cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    date = datetime.today()
    month = date.month
    year = date.year
    if month == 1:
        month = 12
    else:
        month -= 1
    if request.method == 'POST':
        print("hellp")
        id = request.form['imgId']
        print(id)
        cursor.execute(
            "SELECT * FROM ngma2_posts WHERE ID = %s", [id])
        post = cursor.fetchone()
        cursor.execute(
            "SELECT * FROM ngma2_users WHERE ID = %s", [post['post_author']])
        author_details = cursor.fetchone()
        cursor.execute(
            "SELECT * from ngma2_hall_of_fame WHERE month = %s AND year = %s", [month, year])
        is_available = cursor.fetchone()
        print(post)

        print()

        print(author_details)
        print("IS_ available ", is_available)

        if is_available != None:
            print("aana chaiye idhar")
            return "<h1>Hall of Fame already Selected<h1>"
            # cursor.execute("UPDATE ngma2_hall_of_fame set post_id = %s,user_name = %s,user_id = %s,user_email = %s", [
            #                post['ID'], author_details['display_name'], post['post_author'], author_details['user_email']])
            # db.connection.commit()
        else:
            cursor.execute("INSERT INTO ngma2_hall_of_fame(post_id,user_name,user_id,user_email,month,year) values(%s,%s,%s,%s,%s,%s)", [
                           post['ID'], author_details['display_name'], post['post_author'], author_details['user_email'], month, year])
            db.connection.commit()

    return render_template("dashboard/hallOffame.html", post=id, guid=image)



@ app.route('/dashboard/bestArtworkYear', methods=['POST', 'GET'])
@cross_origin()
def bestArtWorkYear():
    cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    date = datetime.today()
    month = date.month
    year = date.year
    check = False
    if month == 1:
        check = True

    if request.method == 'POST':
        data = request.get_json()
        images = data['imgArray']

        for post in images:
            cursor.execute(
                "SELECT ID from ngma2_nominations_year WHERE (post_ID = %s AND year=%s)", [post['id'], year])
            present = cursor.fetchone()
            if not present:
                cursor.execute(
                    "INSERT INTO ngma2_nominations_year(post_ID,year,guid) values(%s,%s,%s)", [post['id'], year, post['src']])
                db.connection.commit()
        # return render_template("dashboard/nominationYear.html")
        return url_for('nomination_year')

    cursor.execute(
        "SELECT * FROM ngma2_hall_of_fame ")

    posts = cursor.fetchall()
    all_posts = []
    for post in posts:
        cursor.execute(
            "SELECT ID from ngma2_nominations_year WHERE (post_ID = %s AND year=%s)", [post['ID'], year])
        present = cursor.fetchone()
        if not present:
            cursor.execute(
                "SELECT guid FROM ngma2_posts WHERE (post_parent=%s AND post_type=%s AND guid is NOT NULL)",
                (post['post_id'], 'attachment'))
            picture = cursor.fetchone()
            if picture is not None:
                post["display_photo"] = picture['guid']
                all_posts.append(post)
    print(all_posts)
    return render_template("dashboard/bestArtworkYear.html", posts=all_posts)


@app.route('/dashboard/nominationYear', methods=['POST', 'GET'])
@cross_origin()
def nomination_year():
    cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    date = datetime.today()
    year = date.year
    cursor.execute(
        "SELECT * from ngma2_nominations_year WHERE year=%s", [year])
    all_posts = cursor.fetchall()
    return render_template("dashboard/nominationYear.html", posts=all_posts)


@ app.route('/dashboard/hallOffameYear', methods=['POST', 'GET'])
@cross_origin()
def ArtworkYear():
     id = request.args.get('id')
     # print(id)
     image = request.args.get('image')
     # print(image)
     cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
     date = datetime.today()
     year = date.year

     if request.method == 'POST':
         # print("hellp ME ME MEEEEEEE")
         id = request.form['imgId']
         # print(id)
         cursor.execute(
             "SELECT * FROM ngma2_posts WHERE ID = %s", [id])
         post = cursor.fetchone()
         cursor.execute(
             "SELECT * FROM ngma2_users WHERE ID = %s", [post['post_author']])
         author_details = cursor.fetchone()
         cursor.execute(
             "SELECT * from ngma2_artwork_of_year WHERE year = %s", [year])
         is_available = cursor.fetchone()
         # print(post)

         # print()

         # print(author_details)
         print("IS_ available ", is_available)

         if is_available != None:
             # print("aana chaiye idhar")
             return "<h1>Hall of Fame already Selected<h1>"
             # cursor.execute("UPDATE ngma2_hall_of_fame set post_id = %s,user_name = %s,user_id = %s,user_email = %s", [
             #                post['ID'], author_details['display_name'], post['post_author'], author_details['user_email']])
             # db.connection.commit()
         else:
             cursor.execute("INSERT INTO ngma2_artwork_of_year(post_id,user_name,user_id,user_email,year) values(%s,%s,%s,%s,%s)", [
                            post['ID'], author_details['display_name'], post['post_author'], author_details['user_email'], year])
             db.connection.commit()

     return render_template("dashboard/hallOffameYear.html", post=id, guid=image)




@ app.route('/Artwork-of-the-year', methods=["GET", "POST"])
def artwork_of_year():
    d = date.today()
    year = d.year
    # year = "2022"
    cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        "SELECT * FROM ngma2_artwork_of_year WHERE year = %s", [year])
    art_post = cursor.fetchone()
    dp = None
    if art_post is None:
        cursor.execute(
            "SELECT * FROM ngma2_artwork_of_year WHERE month=%s and year = %s", [year-1])
        art_post = cursor.fetchone()

    cursor.execute(
        "SELECT * FROM ngma2_users WHERE ID=%s", [art_post['user_id']])
    author_details = cursor.fetchone()
    author_current = author_details['ID']
    cursor.execute(
        "SELECT * FROM ngma2_posts WHERE(post_author=%s AND post_status=%s AND post_parent=%s)",
        (author_current, 'inherit', '0'))
    profile_pic = cursor.fetchone()
    if profile_pic is not None:
        dp = profile_pic['guid']
    else:
        dp = "https://plusvalleyadventure.com/wp-content/uploads/2020/11/default-user-icon-8.jpg"

    cursor.execute(
        "SELECT * FROM ngma2_posts WHERE ID = %s", [art_post['post_id']])
    post = cursor.fetchone()
    print(post)
    cursor.execute(
        "SELECT * FROM ngma2_posts WHERE (post_parent=%s AND post_type=%s AND guid is NOT NULL)",
        (post['ID'], 'attachment'))
    # print("post", post)
    display_photo = cursor.fetchone()

    if display_photo is not None:
        post['guid'] = display_photo['guid']
    else:
        post['guid'] = "http://www.tgsin.in/images/joomlart/demo/default.jpg"
    photo = post['guid']
    # print(post)
    print(photo)
    return render_template("ArtworkofYear.html", art_post=art_post, post=post, dp=dp, photo=photo, year=year)


@ app.route('/dashboard/blog', methods=['POST', 'GET'])
def addBlog():
    if request.method == "POST":
        post_date = datetime.now()
        post_date_gmt = datetime.now(timezone('UTC')).astimezone(timezone('Asia/Kolkata'))
        blog_title = request.form.get("title")
        blog_description = request.form.get("description")
        blog_name = request.form.get("name")
        blog_status = request.form.get("blog_status")
        blog_comment_status = request.form.get("comment_status")
        blog_ping_status = request.form.get("ping_status")
        blog_type = request.form.get("blog_type")
        d = date.today()
        year, month = d.year, d.month
        blog_banner = request.files['banner']
        if blog_banner:
            ftpsession = ftplib.FTP(
                'ftp.so-ham.in', 'demo@so-ham.in', 'demo123')  # Created session
            cur_now = datetime.now()
            cur_now_time = cur_now.strftime("%m%d%Y%H%M%S")
            filename = secure_filename(str(blog_title))+cur_now_time+'-'+secure_filename(
                blog_banner.filename)
            filelist = []
            ftpsession.retrlines('LIST', filelist.append)
            found = False
            for f in filelist:
                if f.split()[-1] == year:
                    found = True
            # if found == False:                                    #uncomment it to use it in a new directory after month and year changes

            #     ftpsession.mkd(str(year))
            ftpsession.cwd(str(year))
            filelist = []
            ftpsession.retrlines('LIST', filelist.append)
            found = False
            for f in filelist:
                if f.split()[-1] == month:
                    found = True
            # if not found:                            #uncomment it to use it in a new directory after month and year changes
            #     ftpsession.mkd(str(month))
            ftpsession.cwd(str(month))
            ftpsession.storbinary('STOR %s' % (filename), blog_banner)
            ftpsession.quit()
            guid = "https://so-ham.in/wp-content/uploads/%s/%s/%s" % (
                year, month, filename)
            blog_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
            blog_cursor.execute(
                    "INSERT INTO sohamgu4_ngma_db.ngma2_blog(ID,post_author,post_date,post_date_gmt,post_content,post_title, post_status,comment_status,ping_status,post_name,guid,post_type)"
                    "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (5,111,post_date,post_date_gmt,blog_description,blog_title,blog_status,blog_comment_status,blog_ping_status,blog_name,guid,blog_type))
            db.connection.commit()        
            return render_template("dashboard/blog.html",message=True)
    else:
        return render_template("dashboard/blog.html")

@ app.route('/dashboard/events',methods=['POST','GET'])
def addEvents():
    if request.method == "POST":
        event_title = request.form.get("title")
        type = request.form.get("type")
        description = request.form.get("description")
        date_from = request.form.get("date_from")
        date_to = request.form.get("date_to")
        time_from = request.form.get("time_from")
        time_to = request.form.get("time_to")
        thumbnail = "https://plusvalleyadventure.com/wp-content/uploads/2020/11/default-user-icon-8.jpg"
        d = date.today()
        year, month = d.year, d.month
        event_banner = request.files['banner']
        if event_banner:
            ftpsession = ftplib.FTP(
                'ftp.so-ham.in', 'demo@so-ham.in', 'demo123')  # Created session
            cur_now = datetime.now()
            cur_now_time = cur_now.strftime("%m%d%Y%H%M%S")
            filename = secure_filename(str(event_title))+cur_now_time+'-'+secure_filename(
                event_banner.filename)
            filelist = []
            ftpsession.retrlines('LIST', filelist.append)
            found = False
            for f in filelist:
                if f.split()[-1] == year:
                    found = True
            # if found == False:                                    #uncomment it to use it in a new directory after month and year changes

            #     ftpsession.mkd(str(year))
            ftpsession.cwd(str(year))
            filelist = []
            ftpsession.retrlines('LIST', filelist.append)
            found = False
            for f in filelist:
                if f.split()[-1] == month:
                    found = True
            # if not found:                            #uncomment it to use it in a new directory after month and year changes
            #     ftpsession.mkd(str(month))
            ftpsession.cwd(str(month))
            ftpsession.storbinary('STOR %s' % (filename), event_banner)
            ftpsession.quit()
            guid = "https://so-ham.in/wp-content/uploads/%s/%s/%s" % (
                year, month, filename)
        
        event_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        event_cursor.execute(
            "INSERT INTO sohamgu4_ngma_db.ngma2_events(thumbnail, title, type, time_from, time_to, description, date_from, date_to,guid)"
            "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (thumbnail, event_title, type, time_from, time_to, description,date_from,date_to,guid))
        db.connection.commit()
        return render_template('dashboard/events.html',message=True)       
    else:
        return render_template('dashboard/events.html')

@app.route("/dashboard/exhibition",methods=['POST','GET'])
def exhibitionAdmin():
    if request.method =="POST":
        post_date = datetime.now()
        post_date_gmt = datetime.now(timezone('UTC')).astimezone(timezone('Asia/Kolkata'))
        link = request.form.get("link")
        thumbanail = request.form.get("url")
        title = request.form.get("title")
        description = request.form.get("description")
        status = request.form.get("status")

        exhibition_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        exhibition_cursor.execute(
                "INSERT INTO sohamgu4_ngma_db.ngma2_exhibitions(link,thumbnail,link_desc,ex_title,status,datetime_gmt,datetime_ist,museum_id,link_visible)"
                "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (link,thumbanail,description,title,status,post_date_gmt,post_date,1,1))
        db.connection.commit() 
        
        return render_template('dashboard/exhibition.html',message=True)
    else:
        return render_template('dashboard/exhibition.html')

@ app.route('/dashboard/theme_month')
def theme_of_month():
     return render_template("dashboard/themeofmonth.html")

@app.route('/dashboard/save_theme_of_month', methods=["POST"]) 
def save_theme_of_month(): 
    d = date.today()
    year, month = d.year, d.month
    theme_title = request.form.get('theme_title')
    theme_content = request.form.get('theme_content')
    theme_file = request.files['theme_image']
    print(theme_file)
    if theme_file:
        ftpsession = ftplib.FTP(
            'ftp.so-ham.in', 'demo@so-ham.in', 'demo123')  # Created session
        cur_now = datetime.now()
        cur_now_time = cur_now.strftime("%m%d%Y%H%M%S")
        filename = secure_filename(str(theme_title))+cur_now_time+'-'+secure_filename(
            theme_file.filename)
        filelist = []
        print(theme_file)
        ftpsession.retrlines('LIST', filelist.append)
        found = False
        for f in filelist:
            if f.split()[-1] == year:
                found = True
        # if found == False:                                    #uncomment it to use it in a new directory after month and year changes

        #     ftpsession.mkd(str(year))
        ftpsession.cwd(str(year))
        filelist = []
        ftpsession.retrlines('LIST', filelist.append)
        found = False
        for f in filelist:
            if f.split()[-1] == month:
                found = True
        # if not found:                            #uncomment it to use it in a new directory after month and year changes
        #     ftpsession.mkd(str(month))
        ftpsession.cwd(str(month))
        ftpsession.storbinary('STOR %s' % (filename), theme_file)
        ftpsession.quit()
        guid = "https://so-ham.in/wp-content/uploads/%s/%s/%s" % (
            year, month, filename)
        save_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        save_cursor.execute(
                "INSERT INTO sohamgu4_ngma_db.ngma2_themeof_month ( title, content, guid ) VALUES (%s, %s, %s)", [theme_title, theme_content, guid]
                )
        db.connection.commit()
        save_cursor.close()
    else:
        return redirect(url_for('theme_of_month'))
    return redirect(url_for('theme'))

# Runs app
if __name__ == '__main__':
    app.debug = True
    app.run()
