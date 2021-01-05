from q_a import app
from flask import render_template, Markup, request, url_for, redirect
from q_a.models import Post, Tags, db
from q_a.supplement import Amend, Check

@app.route('/about', methods=['GET', 'POST'])
def about():
    Check.update()
    if request.method == 'GET':
        return render_template('about.html')
    elif request.method == 'POST':
        if request.form.get('delete_post'):
            db.session.delete(Post.query.get(request.form.get('delete_post')))
            db.session.commit()
            return Amend.flash('Пост удалён.', 'success', url_for('main'))
        elif request.form.get('edit_post'):
            return redirect(url_for('edit_post', post_id=request.form.get('edit_post')))
