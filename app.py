from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = "wanderverse-secret"

basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db = SQLAlchemy(app)


# USER MODEL
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))


# POST MODEL
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    category = db.Column(db.String(50))
    image = db.Column(db.String(200))
    likes = db.Column(db.Integer, default=0)
    author = db.Column(db.String(100))


@app.route('/')
def home():
    posts = Post.query.all()
    return render_template('index.html', posts=posts)


@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        user = User(
            username=request.form['username'],
            email=request.form['email'],
            password=request.form['password']
        )
        db.session.add(user)
        db.session.commit()
        return redirect('/login')

    return render_template('register.html')


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(
            email=request.form['email'],
            password=request.form['password']
        ).first()

        if user:
            session['user'] = user.username
            return redirect('/')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')


@app.route('/create', methods=['GET','POST'])
def create():

    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':

        title = request.form['title']
        content = request.form['content']
        category = request.form['category']

        image = request.files.get('image')
        filename = None

        if image and image.filename:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        post = Post(
            title=title,
            content=content,
            category=category,
            image=filename,
            author=session['user']
        )

        db.session.add(post)
        db.session.commit()

        return redirect('/')

    return render_template('create.html')


@app.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('post.html', post=post)


@app.route('/like/<int:id>')
def like(id):
    post = Post.query.get_or_404(id)
    post.likes += 1
    db.session.commit()
    return redirect('/')


@app.route('/delete/<int:id>')
def delete(id):
    post = Post.query.get_or_404(id)

    if post.author == session.get('user'):
        db.session.delete(post)
        db.session.commit()

    return redirect('/')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    app.run(host='0.0.0.0', port=5000)