from q_a import app
from flask import request, render_template, \
    url_for, session, redirect
from q_a.models import db, Handed_assignment, Comment, User, Ping, Email
from time import localtime, strftime
from q_a.supplement import Amend, Check, Emails
from re import sub

@app.route('/assignments/check/<int:id>', methods=['GET', 'POST'])
def check_assignment(id):
    Check.update()
    if not session.get('user_id') or session.get('status') != 2:
        return Check.status()
    if not Handed_assignment.query.get(id):
        return Check.page(url_for('todo_teacher'))
    if request.method == 'GET':
        if session.get('status') == 2:
            assignment = Handed_assignment.query.get(id)
            assignment.assignment.title = Amend.md(assignment.assignment.title)
            assignment.assignment.description = Amend.md(assignment.assignment.description)
            assignment.assignment.datetime = strftime('%d.%m.%Y %H:%M', localtime(assignment.assignment.datetime))
            assignment.datetime = strftime('%d.%m.%Y %H:%M', localtime(assignment.datetime))
            if not assignment.main_comment:
                assignment.main_comment = ''
            if assignment.assignment.deadline:
                assignment.assignment.deadline = strftime('%d.%m.%Y %H:%M', localtime(assignment.assignment.deadline))
            else:
                assignment.assignment.deadline = 'нет'
            return render_template('check_assignment.html',
                                   assignment=assignment,
                                   Amend=Amend,
                                   Check=Check,
                                   Comment=Comment,
                                   User=User)
    if request.method == 'POST':
        if session.get('status') == 2:
            if not Handed_assignment.query.get(id):
                return Amend.flash('Такого задания не существует.', 'danger', url_for('todo_teacher'))
            if request.form.get('delete_comment'):
                db.session.delete(Comment.query.get(int(request.form.get('delete_comment'))))
                db.session.commit()
                return Amend.flash('Сообщение удалено.', 'success', url_for('check_assignment', id=id))
            if request.form.get('edit_comment'):
                return redirect(url_for('edit', id=request.form.get('edit_comment'), type='comment'))
            handed_assignment = Handed_assignment.query.get(id)
            if request.form.get('grade') or request.form.get('main_comment'):
                handed_assignment.is_checked = True
                handed_assignment.checked_by = session.get('user_id')
                handed_assignment.when_checked = Check.time()
                db.session.add(Ping(datetime=Check.time(),
                                    actor_id=session.get('user_id'),
                                    action_id=3,
                                    target_id=handed_assignment.assignee,
                                    result_url=url_for('assignment', id=id)
                                    ))
                if Email.query.get(handed_assignment.assignee).confirmed and Email.query.get(handed_assignment.assignee).assignments:
                    Emails.send(f'Задание «{handed_assignment.assignment.title}» проверено',
                                f'''Здравствуйте. Ваш ответ на задание «{handed_assignment.assignment.title}» проверен. Подробности: {url_for('assignment', id=id)}.''',
                                User.query.get(handed_assignment.assignee).email)
                if request.form.get('grade') != '':
                    handed_assignment.grade = request.form.get('grade')
                if request.form.get('main_comment'):
                    handed_assignment.main_comment = Amend.md(request.form.get('main_comment'))
                db.session.commit()
                return Amend.flash('Информация обновлена.', 'success', url_for('check_assignment', id=id))
            elif not request.form.get('new_comment'):
                handed_assignment.is_checked = True
                handed_assignment.checked_by = session.get('user_id')
                handed_assignment.when_checked = Check.time()
                db.session.add(Ping(datetime=Check.time(),
                                    actor_id=session.get('user_id'),
                                    action_id=3,
                                    target_id=handed_assignment.assignee,
                                    result_url=url_for('assignment', id=id)
                                    ))
                if Email.query.get(handed_assignment.assignee).confirmed and Email.query.get(handed_assignment.assignee).assignments:
                    Emails.send(f'Задание «{handed_assignment.assignment.title}» проверено',
                                f'''Здравствуйте. Ваш ответ на задание «{handed_assignment.assignment.title}» проверен. Подробности: {url_for('assignment', id=id)}.''',
                                User.query.get(handed_assignment.assignee).email)
                db.session.commit()
                return Amend.flash('Зачёт поставлен.', 'success', url_for('check_assignment', id=id))
            if request.form.get('new_comment'):
                text = request.form.get('new_comment')
                user_id = session.get('user_id')
                url = url_for('assignment', id=id, _external=True)
                if '@' in text:
                    for token in text.split():
                        if token.startswith('@'):
                            username = sub(r'\W', '', token)
                            if User.query.filter_by(username=username).first():
                                if User.query.filter_by(username=username).first().role.role == 2:
                                    url = url_for('check_assignment', id=id, _external=True)
                                db.session.add(Ping(datetime=Check.time(),
                                                    actor_id=user_id,
                                                    action_id=2,
                                                    target_id=User.query.filter_by(username=username).first().id,
                                                    result_url=url
                                                    ))
                                if Email.query.get(User.query.filter_by(username=username).first().id).confirmed and Email.query.get(User.query.filter_by(username=username).first().id).new_mentions:
                                    Emails.send('Новое упоминание', f'Здравствуйте. Вас упомянули на сайте курса фонетики и фонологии. Вероятно, стоит обратить внимание: {url}.', User.query.filter_by(username=username).first().email)
                db.session.add(Ping(datetime=Check.time(),
                                    actor_id=user_id,
                                    action_id=5,
                                    target_id=handed_assignment.assignee,
                                    result_url=url_for('assignment', id=id, _external=True)
                                    ))
                db.session.add(Comment(assignment_id=handed_assignment.assignment_id,
                                       user_id=session.get('user_id'),
                                       datetime=Check.time(),
                                       text=request.form.get('new_comment')
                                       ))
                db.session.commit()
                return Amend.flash('Сообщение добавлено.', 'success', url_for('check_assignment', id=id))

