from q_a.models import db, Role_types, User, Role_assignment, Group, Email,\
    Assignment_status, Assignment_types, Action_types

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
for i in range(1,31):
    db.session.add(User(username=f'Студент_{str(i)}',
                        firstname='Вася',
                        surname='Пупкин',
                        email=f'aeretrew{str(i)}@bk.ru',
                        password='123',
                        group=Group(id=i, group=201),
                        role=Role_assignment(id=i, role=1)))
    db.session.add(Email(user_id=i+2,
                         confirmed=False))
for i in range(31,61):
    db.session.add(User(username=f'Студент_{str(i)}',
                        firstname='Вася',
                        surname='Пупкин',
                        email=f'aeretrew{str(i)}@bk.ru',
                        password='123',
                        group=Group(id=i, group=202),
                        role=Role_assignment(id=i, role=1)))
    db.session.add(Email(user_id=i+2,
                         confirmed=False))
for i in range(61,91):
    db.session.add(User(username=f'Студент_{str(i)}',
                        firstname='Вася',
                        surname='Пупкин',
                        email=f'aeretrew{str(i)}@bk.ru',
                        password='123',
                        group=Group(id=i, group=203),
                        role=Role_assignment(id=i, role=1)))
    db.session.add(Email(user_id=i+2,
                         confirmed=False))
for i in range(91,121):
    db.session.add(User(username=f'Студент_{str(i)}',
                        firstname='Вася',
                        surname='Пупкин',
                        email=f'aeretrew{str(i)}@bk.ru',
                        password='123',
                        group=Group(id=i, group=204),
                        role=Role_assignment(id=i, role=1)))
    db.session.add(Email(user_id=i+2,
                         confirmed=False))
for type in ['домашнее задание', 'контрольная работа', 'устный ответ']:
    db.session.add(Assignment_types(text=type))
for status in ['не сдано', 'сдано', 'сдано с опозданием', 'не требует сдачи']:
    db.session.add(Assignment_status(text=status))
for type in ['новый вопрос', 'ответ на вопрос', 'упоминание', 'подписка на вопрос', 'отписка от вопроса']:
    db.session.add(Action_types(type=type))
db.session.add(Email(user_id=1,
                     confirmed=False))
db.session.commit()
