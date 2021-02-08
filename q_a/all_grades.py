from q_a import app
from flask import request, render_template, \
    url_for, session, make_response
from q_a.models import Assignment, db, Handed_assignment, User, Ping, Group
from q_a.supplement import Amend, Check
import csv
import io

@app.route('/assignments/grades', methods=['GET', 'POST'])
def all_grades():
    Check.update()
    if not session.get('user_id'):
        return Check.login()
    if request.method == 'GET':
        if session.get('status') == 2:
            return render_template('all_grades.html',
                                   Assignment=Assignment,
                                   Handed_assignment=Handed_assignment,
                                   User=User,
                                   Group=Group,
                                   Amend=Amend,
                                   Check=Check)
    if request.method == 'POST':
        if session.get('status') == 2:
            if request.form.get('download'):
                si = io.StringIO()
                cw = csv.writer(si)
                cw.writerow(['Фамилия', 'Имя', 'Группа'] + [f'{assignment.type.text} {assignment.title} {Amend.datetime(assignment.datetime)}' for assignment in Assignment.query.all()])
                for student in User.query.join(Group, User.id==Group.id).order_by(Group.group.asc()).order_by(User.surname.asc()).all():
                    result = []
                    if student.role.role != 2:
                        value = student.id
                        for assignment in Assignment.query.all():
                            if Handed_assignment.query.filter_by(source_assignment_id=assignment.assignment_id, assignee=value).first():
                                result.append(Handed_assignment.query.filter_by(source_assignment_id=assignment.assignment_id,
                                                                  assignee=value).first().grade)
                            else:
                                result.append('N/A')
                        cw.writerow([student.surname, student.firstname, student.group.group] + result)
                response = make_response(si.getvalue())
                response.headers['Content-Disposition'] = f'attachment; filename=all_grades_{Amend.datetime(Check.time())}.csv'
                response.headers["Content-type"] = "text/csv; charset=utf-8"
                return response
            for student in request.form.items():
                id = int(student[0].split('_')[-1])
                student_id = int(student[0].split('_')[0])
                grade = student[-1]
                if grade:
                    Handed_assignment.query.filter_by(assignment_id=id).update({'grade': grade})
                    db.session.add(Ping(datetime=Check.time(),
                                        actor_id=session.get('user_id'),
                                        action_id=3,
                                        target_id=student_id,
                                        result_url=url_for('assignment', id=Handed_assignment.query.get(id).source_assignment_id)
                                        ))
            db.session.commit()
            return Amend.flash('Отметки обновлены.', 'success', url_for('all_grades'))

