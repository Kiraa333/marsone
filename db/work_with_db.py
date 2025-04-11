import sqlalchemy
from data import db_session
from data.users import User
from data.jobs import Jobs


def main():
    db_name = input("")
    db_session.global_init(db_name)
    db_sess = db_session.create_session()
    max = 0
    for j in db_sess.query(Jobs):
        if len(j.collaborators.split()) > max:
            max = len(j.collaborators.split())
    for job in db_sess.query(Jobs).filter(len(Jobs.collaborators.split()) == max):
        for name in job.collaborators.split():
            print()


if __name__ == '__main__':
    main()