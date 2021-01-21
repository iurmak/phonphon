from q_a import app
from flask import render_template, session, redirect, url_for
from q_a.models import Handed_assignment
from q_a.supplement import Amend, Check

@app.route('/todo', methods=['GET'])
@app.route('/todo/page/<int:page>', methods=['GET'])
def todo_student(page=1):
    Check.update()
    if not session.get('user_id'):
        return Check.login()
    if session.get('status') == 2:
        return redirect(url_for('todo_teacher'))
    else:
        try:
            page_of_assignments = Handed_assignment.query.filter_by(assignee=session.get('user_id')).order_by(Handed_assignment.status_id.asc()).paginate(page, 10)
        except:
            return Check.page(url_for('todo_student'))
        assignments = page_of_assignments.items
        return render_template('todo_student.html',
                               assignments=assignments,
                               items=page_of_assignments,
                               Amend=Amend,
                               Check=Check)
