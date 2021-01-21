from q_a import app
from flask import render_template, request, url_for, redirect, session
from q_a.models import Post, db
from q_a.supplement import Amend, Check

@app.route('/materials', methods=['GET', 'POST'])
def materials():
    Check.update()
    if request.method == 'GET':
        if not session.get('user_id'):
            Check.login()
        materials = Post.query.filter_by(tag=3).all()
        return render_template('materials.html',
                               Amend=Amend,
                               materials=materials)
    elif request.method == 'POST':
        if session.get('status') == 2:
            if request.form.get('edit'):
                return redirect(url_for('edit_post', post_id=request.form.get('edit')))
            elif request.form.get('delete'):
                db.session.delete(Post.query.get(request.form.get('delete')))
                db.session.commit()
            return Amend.flash('Материал удалён.', 'success', url_for('materials'))
        return Check.status()
