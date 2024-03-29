from q_a import app
from flask import request, render_template, \
    url_for, session, make_response
from q_a.models import Assignment, db, Handed_assignment, Ping, User, Group
from q_a.supplement import Amend, Check
import csv
import io

@app.route('/assignments/<int:id>/grades', methods=['GET', 'POST'])
def massive_assessment(id):
    Check.update()
    if not session.get('user_id'):
        return Check.login()
    if not Assignment.query.get(id):
        return Check.page(url_for('assignments'))
    if request.method == 'GET':
        if session.get('status') == 2:
            assignment = Assignment.query.get(id)
            handed_assignments = Handed_assignment.query.filter_by(source_assignment_id=id).\
                join(User, Handed_assignment.assignee==User.id).join(Group, User.id==Group.id).\
                order_by(Group.group.asc()).order_by(User.surname.asc()).all()
            return render_template('massive_assessment.html',
                                   assignment=assignment,
                                   handed_assignments=handed_assignments,
                                   Amend=Amend,
                                   Check=Check)
    if request.method == 'POST':
        if session.get('status') == 2:
            if request.form.get('download'):
                si = io.StringIO()
                cw = csv.writer(si)
                cw.writerow(['Фамилия', 'Имя', 'Группа', 'Отметка'])
                for student in Handed_assignment.query.filter_by(source_assignment_id=id).\
                join(User, Handed_assignment.assignee==User.id).join(Group, User.id==Group.id).\
                order_by(Group.group.asc()).order_by(User.surname.asc()).all():
                    cw.writerow([student.user.surname, student.user.firstname, student.user.group.group, student.grade])
                response = make_response(si.getvalue())
                response.headers['Content-Disposition'] = \
                    f'attachment; filename={Amend.datetime(Check.time())} – task{Assignment.query.get(id).assignment_id}.csv'.encode('utf-8')
                response.headers["Content-type"] = "text/csv; charset=utf-8"
                return response
            for student in request.form.items():
                student_id = student[0]
                grade = student[-1]
                if grade:
                    Handed_assignment.query.filter_by(assignee=student_id, source_assignment_id=id).update({'grade': grade})
                    db.session.add(Ping(datetime=Check.time(),
                                        actor_id=session.get('user_id'),
                                        action_id=3,
                                        target_id=student_id,
                                        result_url=url_for('assignment', id=id)
                                        ))
            db.session.commit()
            return Amend.flash('Отметки обновлены.', 'success', url_for('assignment', id=id))

