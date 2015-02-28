from jinja2 import Environment, FileSystemLoader
import tornado.ioloop
import tornado.web

import scrapyd

jinja_env = Environment(loader=FileSystemLoader('templates'))


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        projects = scrapyd.list_projects()
        tpl = jinja_env.get_template('index.html')
        self.write(tpl.render(projects=projects))


class JobsHandler(tornado.web.RequestHandler):
    def get(self):
        project = self.get_argument('project')
        spiders = scrapyd.list_spiders(project)
        jobs = scrapyd.list_jobs(project)
        tpl = jinja_env.get_template('jobs.html')
        self.write(tpl.render(project=project, spiders=spiders, jobs=jobs))


class ScheduleSpiderHandler(tornado.web.RequestHandler):
    def get(self):
        project = self.get_argument('project')
        spider = self.get_argument('spider')
        scrapyd.schedule_spider(project, spider)
        self.redirect('/jobs?project=%s' % project)


class CancelJobHandler(tornado.web.RequestHandler):
    def get(self):
        project = self.get_argument('project')
        job_id = self.get_argument('job')
        scrapyd.cancel_job(project, job_id)
        self.redirect('/jobs?project=%s' % project)


app = tornado.web.Application([
    (r'/', IndexHandler),
    (r'/jobs', JobsHandler),
    (r'/schedule', ScheduleSpiderHandler),
    (r'/cancel', CancelJobHandler),
])

if __name__ == '__main__':
    app.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
