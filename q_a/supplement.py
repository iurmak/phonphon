from markdown import markdown
from flask import session, url_for, Markup, redirect, flash
from q_a.models import User, Assignment_status, Log, Action_types
from flask_mail import Mail, Message
from q_a import app
from bs4 import BeautifulSoup
from time import localtime, strftime, gmtime
from calendar import timegm

mail = Mail(app)

class Amend:
    def anti_html(self):
        if self:
            return BeautifulSoup(self, features='html.parser').get_text()
    def md(self):
        if self:
            string = markdown(Amend.anti_html(self))
            for tag in ['<p>', '</p>']:
                string = string.replace(tag, '')
            string = string.replace('<img', '<img class="img-fluid"')
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
                username = Markup(str(username).replace(self, 'Аноним').replace('"text-success"', '"text-dark"'))
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
        return strftime('%d.%m.%Y %H:%M', localtime(self))

class Check():
    def time(self=None):
        return timegm(gmtime())
    def update(self=None):
        if session.get('user_id'):
            session['user'] = User.query.filter_by(id=session.get('user_id')).first().username
            session['status'] = User.query.filter_by(id=session.get('user_id')).first().role.role
    def status(self=None):
        return Amend.flash('У вас недостаточно прав для этого действия.', 'danger', url_for('profile'))
    def login(self=None):
        return Amend.flash('Для выполнения этого действия нужно войти.', 'danger', url_for('login'))
    def page(url='/'):
        return Amend.flash('Такой страницы не существует.', 'danger', url)
    def log(actor_id, action_id, target_id=None, result_url=None):
        log = Log(actor_id=actor_id,
                  target_id=target_id,
                  action_id=action_id,
                  result_url=result_url,
                  datetime=Check.time())
        return log
    def notify(log):
        if log.action.subscribed.filter_by(user_id=log.target_id, action_id=log.action_id):
            return Emails.send(f'Уведомление: {Action_types.get(log.action_id).type}',
                               f'''Так как вы подписались на уведомления, сообщаем о новом событии:\
                               <table class="table table-hover"><thead>
                <tr>
                    <th>Кто</th>
                    <th>Действие</th>
                    <th>Ссылка</th>
                </tr>
              </thead>
            <tbody>
                <tr>
                    <td>{User.query.get(log.actor_id).username}</td>
                    <td>{log.action.type}</td>
                    <td>{log.result_url}</td>
                </tr>
            </tbody>
            </table>''', User.query.get(log.target_id).email)


class Emails():
    def send(about, what, emails):
        msg = Message(about, sender="yurmkrv@gmail.com", recipients=[emails])
        msg.html = what
        mail.send(msg)