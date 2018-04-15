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
        post_id = blog.id
        return redirect('/blog?id=' + str(post_id))

    return render_template('newpost.html')

@app.route('/blog', methods=['GET'])
def blog():

    post_id = request.args.get('id')
    
    if post_id is None:   
        posts = Blog.query.order_by(desc(Blog.id)).all()

        return render_template('blog.html',title="Build-a-Blog", posts=posts) 

    else:
        
        post = Blog.query.get(int(post_id))
        return render_template('blogpost.html', post=post)



@app.route('/', methods=['POST', 'GET'])
def index():
    return redirect('/blog')

if __name__ == '__main__':
    app.run()