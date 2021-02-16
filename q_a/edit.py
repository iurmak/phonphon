from q_a import app
from flask import request, render_template, redirect, \
    url_for, Markup, session
from q_a.models import db, Question, Answer, Assignment, Assignment_types, Role_assignment, Handed_assignment, User,\
    Group, Comment
from q_a.supplement import Amend, Check
from time import mktime, strptime


@app.route('/edit/<string:type>/<int:id>', methods=['POST', 'GET'])
def edit(type, id):
    Check.update()
    if not session.get('user_id'):
        return Check.update()
    if request.method == 'GET':
        if type == 'a':
            if session.get('status') != 2 and session.get('user_id') != Answer.query.get(id).user_id:
                return Check.status()
            return render_template('edit.html',
                                   question=Markup(Amend.md(Answer.query.get(id).question.text)),
                                   current_text=Answer.query.get(id).text,
                                   question_author=Amend.username(Answer.query.get(id).question.user.username),
                                   answer_author=Amend.username(Answer.query.get(id).answerer.username)
                                   )
        if type == 'q':
            if session.get('status') != 2 and session.get('user_id') != Question.query.get(id).user_id:
                return Check.status()
            return render_template('edit.html',
                                   question=Question.query.get(id).title,
                                   current_text=Question.query.get(id).text,
                                   question_author=Amend.username(Question.query.get(id).user.username),
                                   answer_author=None
                                   )
        if type == 'assignment':
            if session.get('status') != 2:
                return Check.status()
            assignment = Assignment.query.get(id)
            if assignment.datetime:
                datetime = assignment.datetime
                is_draft = False
            else:
                datetime = None
                is_draft = True
            if assignment.deadline:
                deadline = Amend.datetime(assignment.deadline)
            else:
                deadline = ''
            return render_template('edit_assignment.html',
                                   title=assignment.title,
                                   description=assignment.description,
                                   datetime=datetime,
                                   deadline=deadline,
                                   assignees=assignment.assignees,
                                   types=Assignment_types.query.all(),
                                   current_type=assignment.type_id,
                                   is_grade=assignment.is_grade,
                                   is_draft=is_draft,
                                   Check=Check,
                                   Amend=Amend
                                   )
        if type == 'comment':
            if session.get('status') != 2:
                return Check.status()
            return render_template('edit.html',
                                   question=None,
                                   current_text=Comment.query.get(id).text,
                                   question_author=None,
                                   answer_author=Amend.username(Comment.query.get(id).user.username)
                                   )
    if request.method == 'POST':
        if type == 'a' and (session.get('user_id') == Answer.query.get(id).user_id or session.get('status') == 2):
            changed_text = request.form.get('changed_text')
            answer = Answer.query.get(id)
            answer.text = changed_text
            answer.last_edited = Check.time()
            db.session.commit()
            return redirect(url_for('question',
                                    question_id=answer.question_id))
        if type == 'q' and (session.get('user_id') == Question.query.get(id).user_id or session.get('status') == 2):
            changed_text = request.form.get('changed_text')
            question = Question.query.get(id)
            question.text = changed_text
            question.title = request.form.get('changed_title')
            question.last_edited = Check.time()
            db.session.commit()
            return redirect(url_for('question',
                                    question_id=question.question_id))
        if type == 'comment' and session.get('status') == 2:
            changed_text = request.form.get('changed_text')
            comment = Comment.query.get(id)
            comment.text = changed_text
            comment.last_edited = Check.time()
            db.session.commit()
            return Amend.flash('Сообщение изменено.', 'success', url_for('check_assignment', id=comment.assignment_id))
        if type == 'assignment' and session.get('status') == 2:
            changed_assignment = Assignment.query.get(id)
            changed_assignment.title = request.form.get('title')
            changed_assignment.description = request.form.get('description')
            if request.form.get('deadline'):
                if changed_assignment.deadline != mktime(strptime(request.form.get('deadline'), '%d.%m.%Y %H:%M')):
                    Handed_assignment.query.filter(Handed_assignment.datetime < mktime(
                        strptime(request.form.get('deadline'), '%d.%m.%Y %H:%M'))).update({"status_id": 2})
                    Handed_assignment.query.filter(Handed_assignment.datetime > mktime(
                        strptime(request.form.get('deadline'), '%d.%m.%Y %H:%M'))).update({"status_id": 3})
                    changed_assignment.deadline = mktime(strptime(request.form.get('deadline'), '%d.%m.%Y %H:%M'))
            changed_assignment.type_id = request.form.get('type_id')
            if request.form.get('is_grade') and changed_assignment.is_grade is False:
                changed_assignment.is_grade = True
                Handed_assignment.query.filter_by(source_assignment_id=id).update({"status_id": 4})
            if changed_assignment.datetime:
                if request.form.get('assignees'):
                    if changed_assignment.is_grade:
                        status_id = 4
                    else:
                        status_id = 1
                    if 'all' in changed_assignment.assignees.split():
                        return Amend.flash('Задание уже назначено всем студентам.', 'warning',
                                           url_for('edit', type='assignment', id=id))
                    elif 'all' in request.form.get('assignees').split():
                        changed_assignment.assignees = 'all'
                        for user in Role_assignment.query.filter(Role_assignment.role != 2).all():
                            if Handed_assignment.query.filter_by(assignee=user.id, source_assignment_id=id).first():
                                continue
                            user_assignment = Handed_assignment(
                                source_assignment_id=id,
                                assignee=user.id,
                                status_id=status_id)
                            db.session.add(user_assignment)
                        db.session.commit()
                        return Amend.flash('Задание назначено всем студентам.', 'success',
                                           url_for('edit', type='assignment', id=id))
                    for assignee in request.form.get('assignees').split():
                        if assignee not in list(changed_assignment.assignees):
                            if assignee.startswith('*'):
                                if User.query.filter_by(username=assignee[1:]).first():
                                    if Handed_assignment.query.filter_by(assignee=User.query.filter_by(username=assignee[1:]).first().id, source_assignment_id=id).first():
                                        continue
                                else:
                                    return Amend.flash('Такого профиля не существует.', 'danger', url_for('edit', type='assignment', id=id))
                                changed_assignment.assignees += f' {assignee[1:]}'
                                user_assignment = Handed_assignment(source_assignment_id=id,
                                                                    assignee=User.query.filter_by(username=assignee[1:]).first().id,
                                                                    status_id=status_id)
                                db.session.add(user_assignment)
                            else:
                                try:
                                    if int(assignee) in [i[0] for i in db.session.query(Group.group).all()]:
                                        changed_assignment.assignees += f' {assignee}'
                                        for user in Group.query.filter_by(group=int(assignee)).all():
                                            if Handed_assignment.query.filter_by(assignee=user.id,
                                                                                 source_assignment_id=id).first():
                                                continue
                                            user_assignment = Handed_assignment(
                                                source_assignment_id=id,
                                                assignee=user.id,
                                                status_id=status_id)
                                            db.session.add(user_assignment)
                                        continue
                                    else:
                                        return Amend.flash('Такой группы не найдено.', 'danger',
                                                           url_for('edit', type='assignment', id=id))
                                except:
                                    return Amend.flash('Адресаты указаны неверно.', 'danger', url_for('edit', type='assignment', id=id))
                        else:
                            return Amend.flash('Здание уже адресовано этим студентам.', 'warning', url_for('edit', type='assignment', id=id))
            if not request.form.get('is_draft') and not changed_assignment.datetime:
                changed_assignment.datetime = Check.time()
                if changed_assignment.is_grade:
                    status_id = 4
                else:
                    status_id = 1
                if 'all' in changed_assignment.assignees.split():
                    for user in Role_assignment.query.filter(Role_assignment.role != 2).all():
                        user_assignment = Handed_assignment(
                            source_assignment_id=changed_assignment.assignment_id,
                            assignee=user.id,
                            status_id=status_id)
                        db.session.add(user_assignment)
                        db.session.commit()
                    return Amend.flash('Задание добавлено.', 'success',
                                       url_for('assignment', id=changed_assignment.assignment_id))
                else:
                    for assignee in changed_assignment.assignees.split():
                        if assignee.startswith('*'):
                            user_assignment = Handed_assignment(source_assignment_id=changed_assignment.assignment_id,
                                                                assignee=User.query.filter_by(
                                                                    username=assignee.replace('*', '')).first().id,
                                                                status_id=status_id)
                            db.session.add(user_assignment)
                        else:
                            try:
                                if int(assignee) in [i[0] for i in db.session.query(Group.group).all()]:
                                    for user in Group.query.filter_by(group=int(assignee)).all():
                                        user_assignment = Handed_assignment(
                                            source_assignment_id=changed_assignment.assignment_id,
                                            assignee=user.id,
                                            status_id=status_id)
                                        db.session.add(user_assignment)
                                    continue
                                else:
                                    return Amend.flash('Такой группы не найдено.', 'danger',
                                                       url_for('edit', type='assignment', id=changed_assignment.assignment_id))
                            except:
                                return Amend.flash('Адресаты указаны неверно.', 'danger', url_for('new_assignment'))
            db.session.commit()
            return Amend.flash(f'Задание № {id} изменено.', 'success', url_for('assignment', id=id))
