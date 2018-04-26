from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from hashutils import make_pw_hash, check_pw_hash


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'IrZa5wBxtL'

#~~~~~~~~~~~~~~~~~~~ CLASSES GO HERE ~~~~~~~~~~~~~~~~~~~~~~~~~~

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    pw_hash = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.pw_hash = make_pw_hash(password)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1200))
    owner_name = db.Column(db.String(30))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner, owner_name):
        self.title = title
        self.body = body
        self.owner = owner
        self.owner_name = owner_name

#~~~~~~~~~~~~~~~~~~ HANDLERS GO HERE ~~~~~~~~~~~~~~~~~~~~~~~~

""" @app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login') 
 """




@app.route('/logout', methods=['POST'])
def logout():
    del session['username']
    return redirect('/login')






@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_pw_hash(password, user.pw_hash):
            session['username'] = username
            flash("Logged in", 'info')
            return redirect('/blog')
        else:
            flash('User password incorrect, or user does not exist', 'danger')

    return render_template('login.html')






@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        errors_present = False


        if username == "":
            flash("You must enter a username!")

        # Here we validate the password. It follows the same rules as the username.
        if len(password)<3 or  len(password)>30:
            flash("That is not a valid password. Passwords must be at least 3 characters long.")
            errors_present = True
        
       

        # Here we validate the 'verify password' field. If it does not match the passowrd it throws an error
        ver_pass_err_stat = verify != password
        if ver_pass_err_stat == True:
            flash("Passwords do not match")
            errors_present = True
       

        # If there are any errors present it will rerender the form with a blanket display of any present errors. If there are no errors present then it will render the 'Welcome' template instead. 


        if errors_present == True:
            return render_template('signup.html')
        else:
            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/blog')
            else:
                flash("The username <strong>{0}</strong> is already registered".format(email), 'danger')

    return render_template('signup.html')






@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    owner = User.query.filter_by(username=session['username']).first()
    owner_name = owner.username
    error = False

    if request.method == 'POST':
        if request.form['title'] == "":
            error = True
            error1 = "You must enter a title!"
        else:
            error1 = ""

        if request.form['body'] == "":
            error = True
            error2 = "You must enter a body!"
        else:
            error2 = ""

        if error == True:
            return render_template('newpost.html', error1 = error1, error2 = error2)
        else:
            blog_title = request.form['title']      
            blog_body = request.form['body']


        blog = Blog(blog_title, blog_body, owner, owner_name)
        db.session.add(blog)
        db.session.commit()
        post_id = blog.id
        return redirect('/blog?id=' + str(post_id))

    return render_template('newpost.html')





@app.route('/blog', methods=['GET'])
def blog():

    #owner = User.query.filter_by(username=session['username']).first()

    post_id = request.args.get('id')
    username = request.args.get('user')

    print("@@@@@@@@@@@@@@@@@@@@@@@@", username, "@@@@@@@@@@@@@@@@@@@@@@@")


   # Here the aim is to see if the url contains either 'id' or 'user'

    if post_id is not None or username is not None:   

        # If we made it to here then we have established that either 'id' or 'user'
        # is in the url and now we need to check to see which one it is

        if username is not None:

            # Url contains 'user'


            owner = User.query.filter_by(username=username).first()
            print("@@@@@@@@@@@@@@@@@@@@@@@@", owner, "@@@@@@@@@@@@@@@@@@@@@@@")
            posts = Blog.query.filter_by(owner=owner).order_by(desc(Blog.id)).all()
            return render_template('blog.html', posts=posts) 

        else:  #url does not contain 'user'

            if post_id is not None:

            #Url contains 'id'

                post = Blog.query.get(int(post_id))
                return render_template('blogpost.html', post=post)
        
 
    else:

        # Since we established the url does NOT contain 'id' or 'user' then we should
        # display /blog with all posts from all users. 

            posts = Blog.query.all()
            return render_template('blog.html', posts=posts)



        




@app.route('/', methods=['POST', 'GET'])
def index():

    users = User.query.all()

    return render_template('index.html', users=users)

if __name__ == '__main__':
    app.run()