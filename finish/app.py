
from tkinter import Y
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from matplotlib.ft2font import BOLD 
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy  import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import zlib
from werkzeug.utils import secure_filename
from flask import Response
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session ,url_for
from flask_session.__init__ import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import face_recognition
from PIL import Image
from base64 import b64encode, b64decode
import re
import cv2

app = Flask(__name__)

app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.db'
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])

class Question:
    q_id=-1
    question=""
    option1=""
    option2=""
    option3=""
    correctOption=-1
    def __init__(self,q_id,question,option1,option2,option3,correctOption):
        self.q_id=q_id
        self.question=question
        self.option1=option1
        self.option2=option2
        self.option3=option3
        self.correctOption=correctOption

    def get_correct_option(self):
        if self.correctOption == 1:
            return self.option1
        elif self.correctOption == 2:
            return self.option2
        elif self.correctOption == 3:
            return self.option3
           

q1=Question(1,"Which of the following is a linear data structure?","Array","AVL Trees","Graph",1)
q2=Question(2,"Which of the following is not the type of queue?","Priority","single-ended","Circular-queue",2)
q3=Question(3,"How are String represented in memory in C?","an array of characters","linkedlist of characters","the object of some class",1)
q4=Question(4,"Which of the following is the advantage of the array data structure?","Elements of mixed data-types can be stored","Easier to access the elements in an array","elements of array cannot be sorted",2)
q5=Question(5,"What function is used to append a character at the back of a string in C++?","push_back()","append()","insert()",1)
q6=Question(6,"Which one of the following is an application of queue data structure","Load Balancing","When data is transferred asynchronously","All of the Above",3)
q7=Question(7,"When a pop() operation is called on an empty queue, what is the condition called?","overflow","underflow","syntax-error",2)
q8=Question(8,"Which of the following data structures finds its use in recursion?","Stack","Arrays","LinkedList",1)
q9=Question(9,"Which of the following data structures allow insertion and deletion from both ends?","Queue","Stack","String",1)
q10=Question(10,"Which of the following sorting algorithms provide the best time complexity in the worst-case scenario?","Merge Sort","Bubble Sort","Quick Sort",1)


questions_list=[q1,q2,q3,q4,q5,q6,q7,q8,q9,q10]
@app.route("/quiz")
def quiz():
    return render_template("index2.html",questions_list=questions_list)
global correct_count
correct_count=0

@app.route("/submitquiz", methods=["GET", "POST"])
def submit():
    global correct_count
    correct_count=0
    for question in questions_list:
        question_id=str(question.q_id)
        selected_option = request.form[question_id]
        correct_option = question.get_correct_option()
        if selected_option==correct_option:
            correct_count=correct_count+1
    correct_count=str(correct_count)
    return render_template("complete.jinja2",correct_count=correct_count) 

faceDetect=cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
class Video(object):
    
    def __init__(self):
        self.video=cv2.VideoCapture(0)
    def __del__(self):
        self.video.release()
    global count
    global BOL
    BOL=0
    count=0
    def get_frame(self):
        global count
        ret,frame=self.video.read()
        faces=faceDetect.detectMultiScale(frame, 1.3, 5)
        if len(faces) == 0:
            count=count+1
            print(count)
            
            
        for x,y,w,h in faces:
            x1,y1=x+w, y+h
            cv2.rectangle(frame, (x,y), (x+w, y+h), (255,0,255), 1)
            
        ret,jpg=cv2.imencode('.jpg',frame)
        return jpg.tobytes()



@app.route('/index2')
def index2():
    print("this happened")
    return render_template('index2.html',questions_list=questions_list)

def gen(Video):
    global count
    print("genvideo ke andar")
    while count<=30:
        
        frame=Video.get_frame()
        yield(b'--frame\r\n'
       b'Content-Type:  image/jpeg\r\n\r\n' + frame +
         b'\r\n\r\n')
    
    
    
    

@app.route('/video')

def video():
    global BOL
    print("video ke andar")
    return Response(gen(Video()),mimetype='multipart/x-mixed-replace; boundary=frame')
    


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('dashboard'))

        return '<h1>Invalid username or password</h1>'
   

    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return '<h1>New user has been created!</h1>'
     

    return render_template('signup.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.username)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/timer", methods=["GET", "POST"])
def setup():
    if request.method == "POST":
        rest = int(request.form["rest"])
        session["rest"] = rest
        return redirect(url_for("rest"))
    return render_template("home.jinja2")


@app.route("/rest")
def rest():
    return render_template("index2.html", rest=session["rest"])

@app.route("/complete")
def complete():
    return render_template("complete.jinja2" )

@app.route("/facereg", methods=["GET", "POST"])
def facereg():
    session.clear()
    if request.method == "POST":


        encoded_image = (request.form.get("pic")+"==").encode('utf-8')
        username = request.form.get("name")
        name = db.execute("SELECT * FROM users WHERE username = :username",
                        username=username)
              
        if len(name) != 1:
            return render_template("camera.html",message = 1)

        id_ = name[0]['id']    
        compressed_data = zlib.compress(encoded_image, 9) 
        
        uncompressed_data = zlib.decompress(compressed_data)
        
        decoded_data = b64decode(uncompressed_data)
        
        new_image_handle = open('./static/face/unknown/'+str(id_)+'.jpg', 'wb')
        
        new_image_handle.write(decoded_data)
        new_image_handle.close()
        try:
            image_of_bill = face_recognition.load_image_file(
            './static/face/'+str(id_)+'.jpg')
        except:
            return render_template("camera.html",message = 5)

        bill_face_encoding = face_recognition.face_encodings(image_of_bill)[0]

        unknown_image = face_recognition.load_image_file(
        './static/face/unknown/'+str(id_)+'.jpg')
        try:
            unknown_face_encoding = face_recognition.face_encodings(unknown_image)[0]
        except:
            return render_template("camera.html",message = 2)



        results = face_recognition.compare_faces(
        [bill_face_encoding], unknown_face_encoding)

        if results[0]:
            username = db.execute("SELECT * FROM users WHERE username = :username",
                              username="swa")
            session["user_id"] = username[0]["id"]
            return redirect("/")
        else:
            return render_template("camera.html",message=3)


    else:
        return render_template("camera.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return render_template("error.html",e = e)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

if __name__ == '__main__':
    app.run(debug=True)
