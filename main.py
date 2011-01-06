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
    PRIORITY_CHOICES = ["high","medium","low"]
    
    name = db.StringProperty()
    date = db.DateTimeProperty(auto_now_add=True)
    complete_by = db.DateProperty()
    completed = db.BooleanProperty(default=False)
    completed_date = db.DateTimeProperty()
    notes = db.StringProperty()
    user = db.UserProperty(auto_current_user_add=True)
    priority = db.StringProperty(choices = PRIORITY_CHOICES)
    private = db.BooleanProperty(default=False)
    
class Preferences(db.Model):
    user = db.UserProperty(required=True)
    expiration = db.DateProperty()
    date_joined = db.DateProperty(auto_now_add=True)

#----------------Utility Functions-------------------------------
def taskQuery(order_by = [], filters = [], limit = 10):
    '''
    Queries the Task model and returns a rendered task-list.
    
    Takes a list of strings to order query and a list of tuples to
    filter query.
    '''
    user = users.get_current_user()
    query = Task.all()
    query.filter('user =', user)    
    for order in order_by: query.order(order)
    for filter in filters: query.filter(filter[0], filter[1])
    tasks = query.fetch(limit)
    for task in tasks:
        task.id = task.key()
    template_path = TEMPLATES_PATH + 'task-list.html'
    output = template.render(template_path, {'tasks': tasks})
    return output
#----------------------------------------------------------------
    
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
            self.response.out.write(taskQuery(order_by=['complete_by']))
        elif command == 'sort-date':
            self.response.out.write(taskQuery(order_by=['date']))
        elif command == 'sort-name':
            self.response.out.write(taskQuery(order_by=['name']))
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
        elif command == 'show-completed':
            self.response.out.write(taskQuery(filters=[('completed',True)]))
        elif command == 'show-not-completed':
            self.response.out.write(taskQuery(filters=[('completed',False)]))
        else:
            self.error(303)

class AjaxMethods(object):
    pass
            
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