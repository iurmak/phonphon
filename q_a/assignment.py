from q_a import app
from flask import request, render_template, \
    url_for, session
from q_a.models import Assignment, db, Handed_assignment, Comment, User, Ping
from time import localtime, strftime
from q_a.supplement import Amend, Check
from re import sub

@app.route('/assignments/<int:id>', methods=['GET', 'POST'])
def assignment(id):
    Check.update()
    if not session.get('user_id'):
        return Check.login()
    if not Assignment.query.get(id):
        return Check.page(url_for('assignments'))
    if request.method == 'GET':
        if session.get('status') == 2:
            assignment = Assignment.query.get(id)
            assignment.title = Amend.md(assignment.title)
            assignment.description = Amend.md(assignment.description)
            if assignment.deadline:
                assignment.deadline = strftime('%d.%m.%Y %H:%M', localtime(assignment.deadline))
            else:
                assignment.deadline = 'нет'
            assignment.assigner = Amend.username(assignment.author.username)
            assignment.assignees = ', '.join(assignment.assignees.split()).replace('*', '')
            return render_template('assignment.html',
                                   assignment=assignment,
                                   Amend=Amend,
                                   Check=Check)
        else:
            assignment = Handed_assignment.query.filter_by(source_assignment_id=id, assignee=session.get('user_id')).first()
            assignment.assignment.title = Amend.md(assignment.assignment.title)
            assignment.assignment.description = Amend.md(assignment.assignment.description)
            assignment.assignment.datetime = strftime('%d.%m.%Y %H:%M', localtime(assignment.assignment.datetime))
            if assignment.assignment.deadline:
                assignment.assignment.deadline = strftime('%d.%m.%Y %H:%M', localtime(assignment.assignment.deadline))
            else:
                assignment.assignment.deadline = 'нет'
            return render_template('hand_in.html',
                                   assignment=assignment,
                                   Amend=Amend,
                                   Check=Check,
                                   Comment=Comment)
    if request.method == 'POST':
        if session.get('status') == 2:
            if request.form.get('delete'):
                if not Assignment.query.get(request.form.get('delete')):
                    return Amend.flash('Такого задания не существует.', 'danger', url_for('assignments'))
                db.session.delete(Assignment.query.get(request.form.get('delete')))
                db.session.commit()
                return Amend.flash('Задание удалено.', 'success', url_for('assignments'))
        if session.get('status') != 2:
            handed_assignment = Handed_assignment.query.filter_by(source_assignment_id=id,
                                                                  assignee=session.get('user_id')).first()
            if request.form.get('answer'):
                if handed_assignment.answer is not None:
                    return Amend.flash('Ответ на это задание уже дан.', 'warning', url_for('assignment', id=handed_assignment.source_assignment_id))
                else:
                    answer = Amend.anti_html(request.form.get('answer'))
                    handed_assignment.answer = answer
                    handed_assignment.datetime = Check.time()
                    if handed_assignment.assignment.deadline and handed_assignment.assignment.deadline < Check.time():
                        handed_assignment.status_id = 3
                    else:
                        handed_assignment.status_id = 2
                    db.session.commit()
                    return Amend.flash('Ответ отправлен.', 'success', url_for('assignment', id=id))
            if request.form.get('new_comment'):
                text = request.form.get('new_comment')
                user_id = session.get('user_id')
                url = url_for('check_assignment', id=id)
                if handed_assignment.checked_by:
                    teacher = handed_assignment.checked_by
                else:
                    teacher = handed_assignment.assignment.assigner
                if '@' in text:
                    for token in text.split():
                        if token.startswith('@'):
                            username = sub(r'\W', '', token)
                            if User.query.filter_by(username=username).first() and username != teacher:
                                db.session.add(Ping(datetime=Check.time(),
                                                    actor_id=user_id,
                                                    action_id=2,
                                                    target_id=User.query.filter_by(username=username).first().id,
                                                    result_url=url
                                                    ))
                db.session.add(Ping(datetime=Check.time(),
                                    actor_id=user_id,
                                    action_id=4,
                                    target_id=teacher,
                                    result_url=url
                                    ))
                db.session.add(Comment(assignment_id=handed_assignment.assignment_id,
                                       user_id=session.get('user_id'),
                                       datetime=Check.time(),
                                       text=request.form.get('new_comment')
                                       ))
                db.session.commit()
                return Amend.flash('Сообщение отправлено.', 'success', url_for('assignment', id=id))
