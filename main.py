import werkzeug
from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from werkzeug.utils import secure_filename
from sqlalchemy import text
from flask_mail import Mail
import json
import os
import math
from datetime import datetime, timedelta
import matplotlib.pyplot as plt




with open('config.json','r') as c:
    params = json.load(c)['params']




local_server = True
app = Flask(__name__)
app.secret_key = "key"
# app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=5) # session time out
app.config['UPLOAD_FOLDER'] = params['upload_location'] # file location
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail-user'],
    MAIL_PASSWORD=  params['gmail-password']
)
mail = Mail(app)
if local_server:
    app.config["SQLALCHEMY_DATABASE_URI"] = params['local_uri']
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = params['prod_uri']
db = SQLAlchemy(app)


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    names = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    message = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(11), nullable=True)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    slug = db.Column(db.String(120), nullable=False)
    content = db.Column(db.String(), nullable=False)
    image = db.Column(db.String(12), nullable=False)
    date = db.Column(db.String(11), nullable=True)


class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(11), nullable=True)

#
# @app.route('/',  methods=['GET','POST'])
# def login():
#     if 'users' in session and session['users'] == params['aduser']:
#         return render_template('index.html', params=params)
#
#     if request.method == "POST":
#         username = request.form.get('uname')
#         adpass = request.form.get('pass')
#
#         if username == params['aduser'] and adpass == params['adpass']:
#             session['users'] = username
#             return render_template('index.html', params = params)
#     return render_template('login.html',params = params)
@app.route('/')
@app.route('/index')
def home():
    posts = Post.query.filter_by().all()
    last = math.ceil(len(posts) / int(params['no_of_posts'])) # no of posts
    # posts = posts[]
    page = request.args.get('page')
    if(not str(page).isnumeric()):
       page = 1
    page = int(page)

    posts = posts[(page-1)*int(params['no_of_posts']):(page-1)*int(params['no_of_posts']) + int(params['no_of_posts'])]
    if(page==1):
        prev = "#"
        next = "/?page="+str(page+1)

    elif(page == last):
        prev = "/?page=" + str(page - 1)
        next = "#"

    else:
        prev = "/?page=" + str(page - 1)
        next = "/?page=" + str(page + 1)



    for lasts in range(last):
        print(lasts)
    # pagination logic
    #fist
    # #mid
    # #last

    # posts = Post.query.filter_by().all()[0:params['no_of_posts']] #no of posts
    return render_template('index.html', params=params, posts=posts, prev=prev, next=next,  last=last)

# @app.route('/')
# @app.route('/index', methods = ['GET','POST'])
# def login():
#
#     if request.method == "POST":
#         username = request.form.get('uname')
#         adpass = request.form.get('pass')
#
#         if username == params['aduser'] and adpass == params['adpass']:
#             session['users'] = username
#             posts = Post.query.filter_by().all()[0:params['no_of_posts']]
#             return render_template('index.html', params=params, posts=posts)
#     return render_template('login.html', params=params)



@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post = Post.query.filter_by(slug=post_slug).first()
    return render_template('post.html', params=params, post=post)


@app.route('/about')
def about():
    return render_template('about.html', params=params)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        '''Add entry to the database'''
        username = request.form.get('username')
        password = request.form.get('password')
        register = Registration(username=username, password=password,  date=datetime.now())
        db.session.add(register)
        db.session.commit()
    return render_template('login.html', params=params)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        '''Add entry to the database'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = Contact(names=name, email=email, phone=phone, message=message, date=datetime.now())
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message from ' + name,
                          sender=email,
                          recipients=[params['gmail-user']],
                          body=message + "\n" + phone
                          )
    return render_template('contact.html', params=params)




@app.route('/mail')
def mails():
    #mails = Contact.query.filter_by().all()[0:params['no_of_posts']]
    # mails = Contact.query.filter_by(names =  'rupesh', email = 'rupesh@gmail').all()[0:params['no_of_posts']]
    #mails = Contact.query.filter_by(names = ('rupesh', 'sumitra') ).all()
    #another_mails = Contact.query.filter_by().all()[0:params['no_of_posts']]


    #sql = text('select * from contact where names =
    sql = text('select names, count(names) as count from contact group by names')
    result = list(db.engine.execute(sql))
    # mail pagination
    another_mails = Contact.query.filter_by().all()
    mails = Contact.query.filter_by().all()
    mail_pages = math.ceil(len(another_mails) / int(params['no_of_posts']))
    # page = request.args.get('page', 1, type=int)

    # another_mails = another_mails.query.paginate(page=page, per_page=int(2))

    # another_mails = another_mails[(page - 1) * int(params['no_of_posts']):(page - 1) * int(params['no_of_posts']) + int(params['no_of_posts'])]







    return render_template('mail.html', params=params, mails=mails, amails=another_mails, email=result,   mail_pages = mail_pages)








#
# @app.route('/email')
# def email():
#     sql = text('select * from contact')
#     result = db.engine.execute(sql)
#     return render_template('mail.html', params = params, email = result)

#
# @app.route('/dashbord', methods=['GET','POST'])
# def dashbord():
#
#     if 'users' in session and session['users'] == params['aduser']:
#         return render_template('dashbord.html', params=params)
#
#     if request.method == "POST":
#         username = request.form.get('uname')
#         adpass = request.form.get('pass')
#
#         if username == params['aduser'] and adpass == params['adpass']:
#             session['users'] = username
#             return render_template('dashbord.html', params = params)
#     return render_template('login.html', params=params)



@app.route('/dashbord', methods=['GET','POST'])
def dashbord():
    if 'users' in session and session['users'] == params['aduser']:
        post = Post.query.all()
        return render_template('dashbord.html', params=params, post = post)
    if request.method == "POST":
        username = request.form.get('uname')
        adpass = request.form.get('pass')

        if username == params['aduser'] and adpass == params['adpass']:
            session['users'] = username
            post = Post.query.all()
            return render_template('dashbord.html', params = params, post = post)
    return render_template('login.html', params = params)

@app.route('/data')
def visualize():
    # labels = 'a', 'b', 'c'
    # sizes = [15, 30, 45]
    sizes = []
    a = text('select count(names) as count from contact group by names')
    sql_data = db.engine.execute(a)
    list_data = db.engine.execute(a)

    # my_list =  list(text('select count(names) as count from contact group by names'))
    for i in list_data:
        sizes.append(i)
    #  result = []
    # query = text('select count(names) as count from contact group by names')
    #
    # for i in query:
    #     result.append(i)


    # explode = (0, 0.1, 0)
    fig1, ax1 = plt.subplots()
    # ax1.pie(sizes, explode=explode, labels = labels , autopct='%1.1f%%', shadow=True, startangle=90)
    ax1.pie(sizes,   autopct='%1.1f%%', shadow=True, startangle=90)

    ax1.axis('equal')
    plot = plt.show()
    return render_template('data.html', params=params, plot = plot, sql_data =  sql_data, list_data =  list_data,  sizes =  sizes)


@app.route("/edit/<string:id>", methods=['GET','POST'])
def edit(id):
    if 'users' in session and session['users'] == params['aduser']:
        if request.method == 'POST':
            post_title = request.form.get('title')
            post_slug = request.form.get('slug')
            post_content = request.form.get('content')
            post_image = request.form.get('image')
            date = datetime.now()

            if id=='0':
                post = Post(title=post_title, slug=post_slug, content=post_content, image = post_image, date=date)
                db.session.add(post)
                db.session.commit()
                return render_template('edit.html', params=params, post=post)

            else:
                post = Post.query.filter_by(id=id).first()
                post.title = post_title
                post.slug = post_slug
                post.content = post_content
                post.image = post_image
                post.date = date
                # db.session.add(post)
                db.session.commit()
                return redirect('/edit/'+id)
        post = Post.query.filter_by(id=id).first()
        return render_template('edit.html', params=params, post=post)

        #     else:
        #         post = Post.query.filter_by(id=id).first()
        #         post.title = post_title
        #         post.slug = post_slug
        #         post.content = post_content
        #         # post_image = post_image
        #         post.date = date
        #         # db.session.add(post)
        #         db.session.commit()
        #         return redirect('/edit/'+id)
        # post = Post.query.filter_by(id = id).first()

#     post=post,




# auto session ends in one minute
# @app.before_request
# def make_session_permanent():
#     session.permanent = True
#     app.permanent_session_lifetime = timedelta(minutes=1)




@app.route("/delete/<string:id>", methods=['GET','POST'])
def delete(id):
    if 'users' in session and session['users'] == params['aduser']:
        post = Post.query.filter_by(id=id).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/dashbord')




@app.route("/upload", methods=['GET','POST'])
def uploader():
    if 'users' in session and session['users'] == params['aduser']:
        if (request.method == 'POST'):
            f=request.files['file']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
            return "Uploaded successfully"

@app.route("/logout")
def logout():
    session.pop('users')
    return redirect('/dashbord')



app.run(debug=True)