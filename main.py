import os
import time
from datetime import date, datetime
from google.appengine.api import users
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db

TEMPLATES_PATH = os.path.join(os.path.dirname(__file__), 'templates/')
TASK_LIMIT = 10
MAIN_URL = '/taskit'

class Task(db.Model):
    name = db.StringProperty()
    date = db.DateTimeProperty(auto_now_add=True)
    complete_by = db.DateProperty()
    completed = db.BooleanProperty(default=False)
    completed_date = db.DateTimeProperty()
    notes = db.StringProperty()
    user = db.UserProperty(auto_current_user_add=True)
    private = db.BooleanProperty(default=False)
    
class Preferences(db.Model):
    user = db.UserProperty(required=True)
    expiration = db.DateProperty()
    date_joined = db.DateProperty()

class MainHandler(webapp.RequestHandler):

    def get(self):
        user = users.get_current_user()
        template_values = {}
        if user:
            template_values['nickname'] = user.nickname()
            template_values['logout_url'] = users.create_logout_url(MAIN_URL)
            query = Task.all()
            query.filter('user =', user)
            query.order('date')
            tasks = query.fetch(10)
            for task in tasks:
                task.id = task.key()
            template_values['tasks'] = tasks
        else:
            template_values['login_url'] = users.create_login_url(MAIN_URL)
        template_path = TEMPLATES_PATH + 'index.html'
        template_values.update({})
        output = template.render(template_path, template_values)
        self.response.out.write(output)
        
    def post(self):
        u = users.get_current_user()
        query = Task.all()
        query.filter("user =", u)
        tasks = query.fetch(TASK_LIMIT + 1)
        if u and len(tasks) < TASK_LIMIT:
            n = self.request.get('notes')
            d = self.request.get('complete-by')
            if d == "": 
                d = date.today()
            else:
                d = datetime.strptime(d,"%m/%d/%Y").date()
            if n == "": n = None
            t = Task(
                name = self.request.get('task'),
                notes = n,
                complete_by = d,
            )
            t.put()
        self.redirect(MAIN_URL)

class TaskHandler(webapp.RequestHandler):

    def get(self, command, id):
        user = users.get_current_user()
        if command == "complete":
            task = db.get(id)
            task.completed = True
            if task.user == user: task.put()
            self.redirect(MAIN_URL)
        elif command == "delete":
            task = db.get(id)
            if task.user == user: task.delete()
            self.redirect(MAIN_URL)
            
class AjaxHandler(webapp.RequestHandler):
    
    def post(self, command):
        user = users.get_current_user()
        if not user: return False
        query = Task.all()
        query.filter('user =', user)
        if command == 'delete':
            task = db.get(self.request.get('id'))
            if task.user == user: task.delete()
        elif command == 'complete':
            task = db.get(self.request.get('id'))
            task.completed = True
            task.complete_date = date.today()
            if task.user == user: task.put()
        elif command == 'sort-priority':
            pass
        elif command == 'sort-completeby-date':
            query.order('complete_by')
            tasks = query.fetch(10)
            for task in tasks:
                task.id = task.key()
            template_path = TEMPLATES_PATH + 'task-list.html'
            output = template.render(template_path, {'tasks': tasks})
            self.response.out.write(output)
        elif command == 'sort-date':
            query.order('date')
            tasks = query.fetch(10)
            for task in tasks:
                task.id = task.key()
            template_path = TEMPLATES_PATH + 'task-list.html'
            output = template.render(template_path, {'tasks': tasks})
            self.response.out.write(output)
        elif command == 'sort-name':
            query.order('name')
            tasks = query.fetch(10)
            for task in tasks:
                task.id = task.key()
            template_path = TEMPLATES_PATH + 'task-list.html'
            output = template.render(template_path, {'tasks': tasks})
            self.response.out.write(output)
        elif command == 'submit-task':
            tasks = query.fetch(TASK_LIMIT + 1)
            if len(tasks) < TASK_LIMIT:
                n = self.request.get('notes')
                d = self.request.get('complete-by')
                if d == "": 
                    d = date.today()
                else:
                    d = datetime.strptime(d,"%m/%d/%Y").date()
                if n == "": n = None
                t = Task(
                    name = self.request.get('task'),
                    notes = n,
                    complete_by = d,
                )
                t.put()
                key = t.key()
                task = db.get(key)
                task.id = key
                template_path = TEMPLATES_PATH + 'single-task.html'
                output = template.render(template_path, {'task': task})
                self.response.out.write(output)
        else:
            self.error(303)

class SortHandler(webapp.RequestHandler):

    def get(self, command, ajax):
        user = users.get_current_user()
        if command == "":
            pass
        elif command == "":
            pass
        elif command == "":
            pass
            
        if ajax == "ajax":
            # Do ajax stuff here
            pass
        else:
            # Do normal stuff
            self.redirect(MAIN_URL)
        
def main():
    application = webapp.WSGIApplication([
        ('/taskit', MainHandler),
        ('/taskit/ajax/(?P<command>.*)', AjaxHandler),
        ('/taskit/(?P<command>.*)/(?P<id>.*)', TaskHandler),
        ],
        debug=True
    )
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()