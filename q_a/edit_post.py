from q_a import app
from flask import request, render_template, \
    url_for, session
from q_a.supplement import Check, Amend
from q_a.models import db, Post, Tags

@app.route('/edit/post/<int:post_id>', methods=['POST', 'GET'])
def edit_post(post_id):
    Check.update()
    if not session.get('user_id'):
        return Check.login()
    if session.get('status') != 2:
        return Check.status()
    if request.method == 'GET':
        return render_template('edit_post.html',
                               Tags=Tags,
                               Post=Post.query.get(post_id))
    elif request.method == 'POST':
        text = request.form.get('text')
        title = request.form.get('title')
        tag_id = request.form.get('tag')
        user_id = session.get('user_id')
        Post.query.filter_by(post_id=post_id).update({'text': text, 'tag': tag_id, 'user_id': user_id, 'last_edited': Check.time(), 'title': title})
        db.session.commit()
        if title:
            return Amend.flash('Пост изменён.', 'success', url_for('materials'))
        else:
            return Amend.flash('Пост изменён.', 'success', url_for('main'))