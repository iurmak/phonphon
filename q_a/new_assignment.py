from q_a import app
from flask import request, render_template, \
    url_for, session
from q_a.supplement import Amend, Check
from q_a.models import db, Handed_assignment, Assignment, Assignment_types, User, Role_assignment, Group
from time import mktime, strptime

@app.route('/assignments/add', methods=['POST', 'GET'])
def new_assignment():
    Check.update()
    if not session.get('user_id'):
        return Check.login()
    if request.method == 'GET':
        if session.get('user_id') is None:
            return Check.login()
        types = Assignment_types.query.all()
        return render_template('new_assignment.html', types=types, Amend=Amend, Check=Check)
    elif request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        deadline = request.form.get('deadline')
        assignees = str(request.form.get('assignees'))
        assigner = session['user_id']
        type_id = request.form.get('type_id')
        if request.form.get('is_grade'):
            is_grade = True
        else:
            is_grade = False
        if not request.form.get('is_draft'):
            datetime = Check.time()
        else:
            datetime = None
        if 'all' in assignees.split():
            assignees = 'all'
        assignment = Assignment(assigner=assigner,
                                assignees=assignees,
                                title=title,
                                description=description,
                                type_id=type_id,
                                is_grade=is_grade,
                                datetime=datetime
                                )
        if deadline:
            assignment.deadline = mktime(strptime(deadline, '%d.%m.%Y %H:%M'))
        db.session.add(assignment)
        db.session.commit()
        if assignment.is_grade:
            status_id = 4
        else:
            status_id = 1
        if 'all' in assignment.assignees.split():
            for user in Role_assignment.query.filter(Role_assignment.role != 2).all():
                user_assignment = Handed_assignment(
                    source_assignment_id=assignment.assignment_id,
                    assignee=user.id,
                    status_id=status_id)
                db.session.add(user_assignment)
                db.session.commit()
            return Amend.flash('Задание добавлено.', 'success', url_for('assignment', id=assignment.assignment_id))
        else:
            for assignee in assignment.assignees.split():
                if assignee.startswith('*'):
                    user_assignment = Handed_assignment(source_assignment_id=assignment.assignment_id,
                                                        assignee=User.query.filter_by(username=assignee.replace('*', '')).first().id,
                                                        status_id=status_id)
                    db.session.add(user_assignment)
                else:
                    try:
                        if int(assignee) in [i[0] for i in db.session.query(Group.group).all()]:
                            for user in Group.query.filter_by(group=int(assignee)).all():
                                user_assignment = Handed_assignment(
                                    source_assignment_id=assignment.assignment_id,
                                    assignee=user.id,
                                    status_id=status_id)
                                db.session.add(user_assignment)
                            continue
                        else:
                            return Amend.flash('Такой группы не найдено.', 'danger',
                                               url_for('edit', type='assignment', id=assignment.assignment_id))
                    except:
                        return Amend.flash('Адресаты указаны неверно.', 'danger', url_for('new_assignment'))
        db.session.commit()
        return Amend.flash('Задание добавлено.', 'success', url_for('assignment', id=assignment.assignment_id))