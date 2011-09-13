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
    
    Orders list by Task properties specified in order_by list.
    Filters list by Task properties specified as tuples in filters
    list. Each tuple will be a property, value pair (property, value).
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
    
def putTask():
    pass
#----------------------------------------------------------------
    
class MainHandler(webapp.RequestHandler):

    def get(self):
        user = users.get_current_user()
        template_values = {}
        
        if user:
            # Gets task information for valid user
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
        '''
        Only called when ajax calls not working.
        '''
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
    '''
    Handles completing and deleting tasks when ajax calls
    are not working.
    '''
    
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
        if not user:
            self.redirect(MAIN_URL)
            return False
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
            # This dictionary is all that needs to be extended to add
            # more task list sorting or filtering functionality.
            command_params = {
                'show-completed': {'filters': [('completed',True)]},
                'show-not-completed': {'filters': [('completed',False)]},
                'sort-completeby-date': {'order_by': ['complete_by']},
                'sort-date': {'order_by': ['date']},
                'sort-name': {'order_by': ['name']},
            }
            try:
                params = command_params[command]
            except KeyError:
                self.error(303)
            if 'filters' in params:
                f = params['filters']
            else:
                f = []
            if 'order_by' in params:
                o = params['order_by']
            else:
                o = []
            self.response.out.write(taskQuery(filters = f, order_by = o))

class AjaxMethods(object):
    pass
                    
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