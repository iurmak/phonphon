from q_a import app
from flask import render_template, session, request, url_for
from q_a.models import Handed_assignment, User
from q_a.supplement import Amend, Check

@app.route('/todo/check/', methods=['POST', 'GET'])
@app.route('/todo/check/page/<int:page>', methods=['GET', 'POST'])
def todo_teacher(page=1):
    Check.update()
    if not session.get('user_id'):
        return Check.login()
    if session.get('status') == 2:
        if request.method == 'GET':
            try:
                page_of_assignments = Handed_assignment.query.filter(Handed_assignment.is_checked == 0, Handed_assignment.status_id.in_([2, 3]), Handed_assignment.grade == None).order_by(Handed_assignment.datetime.desc()).paginate(page, 10)
            except:
                return Check.page(url_for('todo_teacher'))
            assignments = page_of_assignments.items
            return render_template('todo_teacher.html',
                                   assignments=assignments,
                                   items=page_of_assignments,
                                   Amend=Amend)
        elif request.method == 'POST':
            if request.form.get('parameter') == 'ID':
                assignments = Handed_assignment.query.filter(Handed_assignment.is_checked == 0, Handed_assignment.status_id.in_([2, 3]), Handed_assignment.grade == None).order_by(Handed_assignment.datetime.desc()).all()
                page_of_assignments = None
                return render_template('todo_teacher.html',
                                       assignments=assignments,
                                       items=page_of_assignments,
                                       Amend=Amend,
                                       ID=int(request.form.get('query')))
            elif request.form.get('parameter') == 'group':
                assignments = Handed_assignment.query.filter(Handed_assignment.is_checked == 0, Handed_assignment.status_id.in_([2, 3]), Handed_assignment.grade == None).order_by(Handed_assignment.datetime.desc()).all()
                page_of_assignments = None
                return render_template('todo_teacher.html',
                                       assignments=assignments,
                                       items=page_of_assignments,
                                       Amend=Amend,
                                       group=int(request.form.get('query')))
