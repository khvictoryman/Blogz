from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1200))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        blog = Blog(blog_title, blog_body)
        db.session.add(blog)
        db.session.commit()


    return render_template('newpost.html')

@app.route('/blog', methods=['GET'])
def blog():
    #posts = Blog.query.order_by(DESC).all()
    posts = Blog.query.order_by(desc(Blog.id)).all()

    return render_template('blog.html',title="Build-a-Blog", posts=posts)


@app.route('/', methods=['POST', 'GET'])
def index():
    return redirect('/blog')
"""         posts = Blog.query.all()

        return render_template('blog.html',title="Build-a-Blog", posts=posts)
 """
if __name__ == '__main__':
    app.run()