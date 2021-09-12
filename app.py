# -*- coding: utf-8 -*- #

import sqlite3
import os

from flask import Flask, render_template, request, g, flash, abort, redirect, url_for, make_response
from FDataBase import FDataBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from UserLogin import UserLogin


# конфигурация
DATABASE = 'mydb.db'
DEBUG = True
SECRET_KEY = 'fdgfh78@#5?>gfhf89dx,v06k'
MAX_CONTENT_LENGTH = 1024 * 1024

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://anohin_r_b:NewPass21@localhost'
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path,'mydb.db')))
# manager = Manager(app)
# db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Авторизуйтесь для доступа к закрытым страницам"
login_manager.login_message_category = "success"


@login_manager.user_loader
def load_user(user_id):
    print("load_user")
    return UserLogin().fromDB(user_id, dbase)


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def create_db():
    """Вспомогательная функция для создания таблиц БД"""
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()

def get_db():
    '''Соединение с БД, если оно еще не установлено'''
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


dbase = None
@app.before_request
def before_request():
    """Установление соединения с БД перед выполнением запроса"""
    global dbase
    db = get_db()
    dbase = FDataBase(db)


@app.teardown_appcontext
def close_db(error):
    '''Закрываем соединение с БД, если оно было установлено'''
    if hasattr(g, 'link_db'):
        g.link_db.close()


@app.route("/", methods=["POST", "GET"])
def index():
    # session['logged_in'] = True
    students = dbase.getStudentProfiles()
    list_users=[]
    for s in students:
        print(s[4])
        user = dbase.getUser(s[4])
        list_users.append(user)
    admin = False
    if current_user.is_authenticated:
        print("authent")
        admin = 0
        if current_user.getStatus() == 1:
            print("admin")
            admin = 1
            # return render_template('index-admin.html', students=dbase.getStudentAnonce(), users=list_users)
        # else:
    return render_template('index.html', menu=dbase.getMenu(), students=dbase.getStudentProfiles(), users=list_users, admin=admin)

@app.route("/index_admin", methods=["POST", "GET"])
@login_required
def index_admin():
    admin = False
    if current_user.is_authenticated:
        print("authent")
        admin = 0
        if current_user.getStatus() == 1:
            print("admin")
            admin = 1
    return render_template('index-admin.html', menu=dbase.getMenu(), users=dbase.getUsers(), admin=admin)


@app.route("/add_info", methods=["POST", "GET"])
@login_required
def addInfo():
    if dbase.getInfo_by_id(current_user.get_id())[0]:
        flash('Информация о студенте уже существует. Можете изменить существующую информацию', category='error')
        return redirect(url_for("change"))
    else:
        if request.method == "POST":
            if dbase.getInfo_by_id(current_user.get_id()[0]):
                res = dbase.addPost(request.form['study'], request.form['work'], request.form['about_student'], current_user.get_id())
                if not res:
                    flash('Ошибка добавления статьи', category='error')
                else:
                    flash('Информация добавлена успешно', category='success')
            else:
                flash('Информация о студенте уже существует', category='error')
                return redirect(url_for("change"))

    return render_template('add_post.html', menu=dbase.getMenu(), title="Добавление информации о студенте")


@app.route("/post/<user_id>", methods=["POST", "GET"])
@login_required
def showPost(user_id):
    study, work, about_student = dbase.getInfo_by_id(user_id)
    res = dbase.getUser(user_id)
    name = res[1]
    email = res[2]
    if not (res or study):
        abort(404)
    allComments = dbase.getComments(user_id)
    allUsers = dbase.getUsers()
    admin = 0
    if current_user.is_authenticated:
        admin = 0
        if current_user.getStatus() == 1:
            admin = 1
    return render_template("post.html",
                                      menu=dbase.getMenu(),
                                      study=study,
                                      work=work,
                                      about_student=about_student,
                                      name=name,
                                      email=email,
                                      title="Информация о студенте",
                                      allComments=allComments,
                                      allUsers=allUsers,
                                      curr_user_id=current_user.get_id(), user_id=user_id, admin=admin)

@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    if request.method == "POST":
        user = dbase.getUserByEmail(request.form['email'])
        if user and check_password_hash(user['psw'], request.form['psw']):
            userlogin = UserLogin().create(user)
            rm = True if request.form.get('remainme') else False
            login_user(userlogin, remember=rm)
            return redirect(request.args.get("next") or url_for("profile"))
        flash("Неверная пара логин/пароль", "error")
    return render_template("login.html", menu=dbase.getMenu(), title="Авторизация")


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        if len(request.form['name']) > 4 and len(request.form['email']) > 4 \
            and len(request.form['psw']) > 4 and request.form['psw'] == request.form['psw2']:
            hash = generate_password_hash(request.form['psw'])
            res = dbase.addUser(request.form['name'], request.form['email'], hash)
            if res:
                flash("Вы успешно зарегистрированы", "success")
                return redirect(url_for('login'))
            else:
                flash("Ошибка при добавлении в БД", "error")
        else:
            flash("Неверно заполнены поля", "error")
    return render_template("register.html", menu=dbase.getMenu(), title="Регистрация")

@app.route("/add_comment/<author_id>/<user_id>", methods=["POST", "GET"])
@login_required
def add_comment(author_id, user_id):
    study, work, about_student = dbase.getInfo_by_id(user_id)
    user = dbase.getUser(user_id)
    name = user[1]
    email = user[2]
    if not (user or study):
        abort(404)
    res = dbase.add_comment(author_id, user_id, request.form['text_comment'])
    if not res:
        flash('Ошибка добавления комментария', category='error')
    else:
        flash('Комментарий добавлен успешно', category='success')
    allComments = dbase.getComments(user_id)
    allUsers = dbase.getUsers()
    return render_template("post.html",
                           menu=dbase.getMenu(),
                           study=study,
                           work=work,
                           about_student=about_student,
                           name=name,
                           email=email,
                           title="Информация о студенте",
                           allComments=allComments,
                           allUsers=allUsers,
                           curr_user_id=current_user.get_id(),
                           user_id=user_id,
                           admin = current_user.getStatus())


@app.route("/change", methods=["POST", "GET"])
@login_required
def change():
    user_id = current_user.get_id()
    study, work, about_student = dbase.getInfo_by_id(user_id)
    if not study:
        study = ''
    if not work:
        work = ''
    if not about_student:
        about_student = ''
    if request.method == "POST":
        res = dbase.updateInfo(request.form['study'], request.form['work'], request.form['info'], user_id)
        if res:
            flash("Информация успешно изменена", "success")
            return redirect(url_for('profile'))
        else:
            flash("Ошибка при попытке изменения информации", "error")

    return render_template("change.html", menu=dbase.getMenu(), title="Профиль", study=study, work=work,
                           about_student=about_student)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    return redirect(url_for('login'))

@app.route('/profile')
@login_required
def profile():
    if not current_user:
        return render_template("login.html", menu=dbase.getMenu(), title="Авторизация")
    else:
        study, work, about_student = dbase.getInfo_by_id(current_user.get_id())
        if not study:
            study = ''
        if not work:
            work = ''
        if not about_student:
            about_student = ''
        title="Профиль студента"
        if current_user.getStatus():
            title = "Профиль администратора"
        return render_template("profile.html", menu=dbase.getMenu(), title=title, study=study, work=work, about_student=about_student, admin=current_user.getStatus())


@app.route('/userava2/<user_id>', methods=["POST", "GET"])
@login_required
def userava(user_id):
    user = UserLogin().fromDB(user_id, dbase)
    img = user.getAvatar(app)
    print(user)
    if not img:
        return ""
    h = make_response(img)
    h.headers['Content-Type'] = 'image/png'
    return h

@app.route('/upload', methods=["POST", "GET"])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and current_user.verifyExt(file.filename):
            try:
                img = file.read()
                res = dbase.updateUserAvatar(img, current_user.get_id())
                if not res:
                    flash("Ошибка обновления аватара", "error")
                flash("Аватар обновлен", "success")
            except FileNotFoundError as e:
                flash("Ошибка чтения файла", "error")
        else:
            flash("Ошибка обновления аватара", "error")
    return redirect(url_for('profile'))

@app.route("/delete_user/<user_id>", methods=["POST", "GET"])
@login_required
def delete_user(user_id):
    dbase.delete_user(user_id)
    students = dbase.getStudentProfiles()
    list_users = []
    for s in students:
        user = dbase.getUser(s[4])
        list_users.append(user)

    return render_template('index.html', menu=dbase.getMenu(), students=dbase.getStudentProfiles(), users=list_users)

@app.route("/delete_comment/<com_id>", methods=["POST", "GET"])
@login_required
def delete_comment(com_id):
    print("com_id")
    print(com_id)
    user_id = dbase.getAuthorCom(com_id)
    dbase.delete_com(com_id)
    print("user_id")
    print(user_id[0])
    study, work, about_student = dbase.getInfo_by_id(user_id)
    user = dbase.getUser(user_id[0])
    name = user[1]
    email = user[2]
    if not (user or study):
        abort(404)
    allComments = dbase.getComments(user_id[0])
    allUsers = dbase.getUsers()
    return render_template("post.html",
                           menu=dbase.getMenu(),
                           study=study,
                           work=work,
                           about_student=about_student,
                           name=name,
                           email=email,
                           title="Информация о студенте",
                           allComments=allComments,
                           allUsers=allUsers,
                           curr_user_id=current_user.get_id(),
                           user_id=user_id[0],
                           admin=current_user.getStatus())

@app.route("/delete_info/<info_id>", methods=["POST", "GET"])
@login_required
def delete_info(info_id):
    # dbase.delete_info(info_id)
    students = dbase.getStudentProfiles()
    list_users = []
    for s in students:
        user = dbase.getUser(s[4])
        list_users.append(user)

    return render_template('index.html', menu=dbase.getMenu(), students=dbase.getStudentProfiles(), users=list_users)


if __name__ == "__main__":
    app.run(debug=True)
