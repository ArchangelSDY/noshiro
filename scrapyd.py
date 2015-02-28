import requests

import settings


def build_url(path):
    return 'http://%s:%d%s' % (
        settings.SCRAPYD_HOST, settings.SCRAPYD_PORT, path)


def list_projects():
    r = requests.get(build_url('/listprojects.json'))
    if r.status_code == 200:
        return r.json().get('projects', [])
    else:
        return []


def list_spiders(project):
    r = requests.get(build_url('/listspiders.json'), params={
        'project': project,
    })
    if r.status_code == 200:
        return r.json().get('spiders', [])
    else:
        return []


def list_jobs(project):
    r = requests.get(build_url('/listjobs.json'), params={
        'project': project,
    })
    if r.status_code == 200:
        data = r.json()
        jobs = []

        for item in data.get('pending', []):
            item['state'] = 'pending'
            jobs.append(item)

        for item in data.get('running', []):
            item['state'] = 'running'
            jobs.append(item)

        for item in data.get('finished', []):
            item['state'] = 'finished'
            jobs.append(item)

        return jobs
    else:
        return []


def schedule_spider(project, spider):
    r = requests.post(build_url('/schedule.json'), data={
        'project': project,
        'spider': spider,
    })
    return r.status_code == 200


def cancel_job(project, job_id):
    r = requests.post(build_url('/cancel.json'), data={
        'project': project,
        'job': job_id,
    })
    return r.status_code == 200
