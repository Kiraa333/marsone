from flask import Flask, render_template, redirect
from flask_login import login_user
from flask_login import LoginManager
from data import db_session
from data.users import User
from data.jobs import Jobs
from data import register
from data.login import LoginForm
from data.register import RegisterForm


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
@app.route('/works')
def works():
    db_session.global_init("db/mars_explorer.db")
    session = db_session.create_session()
    jobs = session.query(Jobs)
    return render_template('jobs.html', jobs=jobs)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.hashed_password == form.password.data:
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    db_session.global_init("db/mars_explorer.db")
    session = db_session.create_session()
    if form.validate_on_submit():
        if not form.age.data.isdigit():
            return render_template('register.html',
                                   agemassage="Неправильно введён возраст",
                                   form=form)
        if not form.password1.data == form.password2.data:
            return render_template('register.html',
                                   passwordmassage="Пароли не совпадают",
                                   form=form)
        user1 = User()
        user1.name = form.name.data
        user1.surname = form.surname.data
        user1.age = int(form.age.data)
        user1.position = form.position.data
        user1.speciality = form.speciality.data
        user1.address = form.address.data
        user1.email = form.email.data
        user1.hashed_password = form.password1.data

        session.add(user1)
        session.commit()
        return redirect("/login")
    return render_template('register.html', title='Регистрация', form=form)


def main():
    db_session.global_init("db/mars_explorer.db")
    #капитан
    user = User()
    user.name = "Ridley"
    user.surname = "Scott"
    user.age = 21
    user.position = "captain"
    user.speciality = "research engineer"
    user.address = "module_1"
    user.email = "scott_chief@mars.org"
    db_sess = db_session.create_session()
    db_sess.add(user)
    db_sess.commit()
    #первая работа
    job = Jobs()
    job.team_leader = 1
    job.job = "deployment of residential modules 1 and 2"
    job.work_size = 15
    job.collaborators = "2, 3"
    job.is_finished = False
    db_sess.add(job)
    db_sess.commit()
    app.run()


if __name__ == '__main__':
    main()