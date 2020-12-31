from q_a import app
from flask import request, render_template, \
    url_for, session
from q_a.models import db, Handed_assignment, Comment, User
from time import localtime, strftime
from q_a.supplement import Amend, Check

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
            handed_assignment = Handed_assignment.query.get(id)
            if request.form.get('grade') or request.form.get('main_comment'):
                handed_assignment.is_checked = True
                handed_assignment.checked_by = session.get('user_id')
                handed_assignment.when_checked = Check.time()
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
                db.session.commit()
                return Amend.flash('Зачёт поставлен.', 'success', url_for('check_assignment', id=id))
            if request.form.get('new_comment'):
                db.session.add(Comment(assignment_id=handed_assignment.assignment_id,
                                       user_id=session.get('user_id'),
                                       datetime=Check.time(),
                                       text=request.form.get('new_comment')
                                       ))
                db.session.commit()
                return Amend.flash('Сообщение добавлено.', 'success', url_for('check_assignment', id=id))
