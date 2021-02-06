from markdown import markdown
from flask import session, url_for, Markup, redirect, flash
from q_a.models import User, Assignment_status, Ping, Handed_assignment
from flask_mail import Mail, Message
from q_a import app
from bs4 import BeautifulSoup
from time import strftime, gmtime
from calendar import timegm

mail = Mail(app)

class Amend:
    def anti_html(self):
        if self:
            return BeautifulSoup(self, features='html.parser').get_text()
    def md(self, html=False):
        if self:
            if html:
                string = markdown(self)
            else:
                string = markdown(Amend.anti_html(self))
            for tag in ['<p>', '</p>']:
                string = string.replace(tag, '')
            string = string.replace('  ', '<br>')
            string = string.replace('<img', '<img class="img-fluid"')
            string = string.replace('--', '–')
            return Markup(string)
    def username(self, question=None, answer=None):
        if session.get('status') == 2:
            if User.query.filter_by(username=self).first().role.role == 2:
                username = Markup(f"""<a href="{url_for('profile', user_id=User.query.filter_by(username=self).first().id)}" class="link-success">{self}</a>""")
            else:
                username = Markup(f"""<a href="{url_for('profile', user_id=User.query.filter_by(username=self).first().id)}" class="link-dark">{self}</a>""")
        elif User.query.filter_by(username=self).first().role.role == 2:
            username = Markup(f'''<span class="text-success">{self}</span>''')
        else:
            username = self
        if question:
            if question.is_anon and session.get('status') == 2:
                username = Markup(str(username).replace(f'{self}</a>', f'{self}</a> (анонимно)'))
            elif question.is_anon:
                username = Markup(str(username).replace(self, 'Аноним').replace('"text-success"', '"text-dark"'))
        if answer:
            if answer.is_anon and session.get('status') == 2:
                username = Markup(str(username).replace(f'{self}</a>', f'{self}</a> (анонимно)'))
            elif answer.is_anon:
                username = Markup(str(username).replace(self, 'Аноним').replace('"text-success"', ''))
        return username
    def assignment_status(self):
        if self == 1:
            return Markup(f'<span class="text-danger">{Assignment_status.query.get(self).text}</span>')
        elif self == 2:
            return Markup(f'<span class="text-success">{Assignment_status.query.get(self).text}</span>')
        elif self == 3:
            return Markup(f'<span class="text-warning">{Assignment_status.query.get(self).text}</span>')
        elif self == 4:
            return Markup(f'<span class="text-secondary">{Assignment_status.query.get(self).text}</span>')
        else:
            return None
    def flash(self, type, url=None):
        flash(Markup(self), f'alert alert-{type}')
        if url:
            return redirect(url)
    def datetime(self):
        return strftime('%d.%m.%Y %H:%M', gmtime(self+10800))

class Check():
    def time(self=None):
        return timegm(gmtime())
    def update(self=None):
        if session.get('user_id'):
            session['user'] = User.query.filter_by(id=session.get('user_id')).first().username
            session['status'] = User.query.filter_by(id=session.get('user_id')).first().role.role
            session['notifications'] = Ping.query.filter_by(target_id=session.get('user_id'), seen=False).count()
            if session.get('status') == 2:
                session['todo'] = Handed_assignment.query.filter(Handed_assignment.status_id.in_([2, 3]), Handed_assignment.is_checked == 0, Handed_assignment.grade == None).count()
            else:
                session['todo'] = Handed_assignment.query.filter_by(status_id=1, assignee=session.get('user_id')).count()
    def status(self=None):
        return Amend.flash('У вас недостаточно прав для этого действия.', 'danger', url_for('profile'))
    def login(self=None):
        return Amend.flash('Для выполнения этого действия нужно войти.', 'danger', url_for('login'))
    def page(url='/'):
        return Amend.flash('Такой страницы не существует.', 'danger', url)


class Emails():
    def send(about, what, emails):
        if isinstance(emails, list):
            msg = Message(about, sender="yurmkrv@gmail.com", recipients=emails)
        else:
            msg = Message(about, sender="yurmkrv@gmail.com", recipients=[emails])
        msg.html = what
        mail.send(msg)