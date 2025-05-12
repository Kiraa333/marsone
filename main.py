from flask import Flask, render_template, redirect, request, abort
from flask_login import login_user, current_user, login_required
from flask_login import LoginManager
from data import db_session
from data.add_job import AddJobForm
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


@app.route('/addjob', methods=['GET', 'POST'])
def addjob():
    add_form = AddJobForm()
    if add_form.validate_on_submit():
        session = db_session.create_session()
        jobs = Jobs(
            job=add_form.job.data,
            team_leader=add_form.team_leader.data,
            work_size=add_form.work_size.data,
            collaborators=add_form.collaborators.data,
            is_finished=add_form.is_finished.data
        )
        session.add(jobs)
        session.commit()
        return redirect('/')
    return render_template('job_add.html', title='Adding a job', form=add_form)


@app.route('/editjob/<int:id>', methods=['GET', 'POST'])
@login_required
def editjob(id):
    form = AddJobForm()
    db_sess = db_session.create_session()

    job = db_sess.query(Jobs).filter(Jobs.id == id,
                                     (Jobs.team_leader == current_user.id) |
                                     (current_user.id == 1)
                                     ).first()

    if not job:
        abort(404)

    if request.method == "GET":
        form.job.data = job.job
        form.team_leader.data = job.team_leader
        form.work_size.data = job.work_size
        form.collaborators.data = job.collaborators
        form.is_finished.data = job.is_finished

    if form.validate_on_submit():
        job.job = form.job.data
        job.team_leader = form.team_leader.data
        job.work_size = form.work_size.data
        job.collaborators = form.collaborators.data
        job.is_finished = form.is_finished.data
        db_sess.commit()
        return redirect('/')

    return render_template('job_add.html',
                           title='Редактирование работы',
                           form=form)


@app.route('/deletejob/<int:id>', methods=['GET', 'POST'])
@login_required
def deletejob(id):
    db_sess = db_session.create_session()
    job = db_sess.query(Jobs).filter(Jobs.id == id,
                                     (Jobs.team_leader == current_user.id) |
                                     (current_user.id == 1)
                                     ).first()

    if not job:
        abort(404)

    db_sess.delete(job)
    db_sess.commit()
    return redirect('/')


def main():
    db_session.global_init("db/mars_explorer.db")
    # капитан
    user = User()
    user.id = 1
    user.name = "Ridley"
    user.surname = "Scott"
    user.age = 21
    user.position = "captain"
    user.speciality = "research engineer"
    user.address = "module_1"
    user.email = "scott_chief@mars.org"
    user.hashed_password = 123
    db_sess = db_session.create_session()
    db_sess.add(user)
    db_sess.commit()


    # первая работа
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