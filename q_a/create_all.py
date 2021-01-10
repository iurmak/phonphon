from q_a.models import db, Role_types, User, Role_assignment, Group, Email,\
    Assignment_status, Assignment_types, Action_types, Tags

db.create_all()

for role in ['Студент', 'Преподаватель или ассистент']:
    db.session.add(Role_types(type=role))
db.session.add(User(id=1,
                    username='admin',
                    firstname='admin',
                    surname='admin',
                    email='n@n.n',
                    password='admin',
                    group=Group(id=1, group=None),
                    role=Role_assignment(id=1, role=2)))
db.session.add(User(id=2,
                    username='Студент',
                    firstname='Вася',
                    surname='Пупкин',
                    email=f'aeretrew@bk.ru',
                    password='123',
                    group=Group(id=2, group=205),
                    role=Role_assignment(id=2, role=1)))
db.session.add(Email(user_id=2,
                         confirmed=False))
for type in ['домашнее задание', 'контрольная работа']:
    db.session.add(Assignment_types(text=type))
for status in ['не сдано', 'сдано', 'сдано с опозданием', 'не требует сдачи']:
    db.session.add(Assignment_status(text=status))
for type in ['ответ на вопрос', 'упоминание', 'задание проверено', 'вопрос по заданию', 'ответ на вопрос по заданию']:
    db.session.add(Action_types(type=type))
for type in ['ссылка на лекцию', 'объявление']:
    db.session.add(Tags(host='f',
                        text=type))
db.session.add(Email(user_id=1,
                     confirmed=False))
db.session.commit()
