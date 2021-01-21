from q_a import app
from flask import render_template, Markup, request, url_for, redirect, session
from q_a.models import Post, Tags, db
from q_a.supplement import Amend, Check

@app.route('/materials', methods=['GET', 'POST'])
def materials(page=1):
    Check.update()
    if request.method == 'GET':
        if not session.get('user_id'):
            Check.login()
        materials = Post.query.filter_by(tag=3).all()
        return render_template('materials.html',
                               Amend=Amend,
                               materials=materials)
    elif request.method == 'POST':
        if request.form.get('parameter'):
            if request.form.get('parameter'):
                page_of_news = Post.query.filter_by(tag=int(request.form.get('parameter'))).order_by(Post.datetime.desc()).paginate(page, 10)
            else:
                page_of_news = Post.query.order_by(Post.datetime.desc()).paginate(page, 10)
            news = page_of_news.items
            return render_template('main.html',
                                   items=page_of_news,
                                   Amend=Amend,
                                   Markup=Markup,
                                   Tags=Tags,
                                   posts=news,
                                   current=int(request.form.get('parameter')))
        if request.form.get('delete_post') and session.get('status') == 2:
            db.session.delete(Post.query.get(request.form.get('delete_post')))
            db.session.commit()
            return Amend.flash('Пост удалён.', 'success', url_for('main'))
        elif request.form.get('edit_post') and session.get('status') == 2:
            return redirect(url_for('edit_post', post_id=request.form.get('edit_post')))
        return Check.status()
