import logging
from datetime import datetime,timedelta
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.jobstores.memory import MemoryJobStore
from flask_apscheduler import APScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from sqlalchemy import create_engine
from flask_apscheduler import APScheduler
from app import settings, extensions
import app

'''
flask_apscheduler的JOBS可以在Config中配置，
也可以通过装饰器调用，还可以通过flask_apschedule的api进行添加
job stores 默认为内存， 可以下在flask的Config中配置为存储在数据库中
'''
import app
from app.view import *

flask_app = Flask(__name__)


@flask_app.route('/')
def index():
    print(111111111111111111111111111111111111111111111111111111111111)
    return '<h1>Hello World!</h1>'


@flask_app.route('/addCron', methods=['post'])
def add_cron():
    jobargs = request.json
    print(jobargs)
    jobargsKeys = jobargs.keys()
    if 'job_name' not in jobargsKeys:
        return jsonify(msg="请添加函数名")
    jobName = jobargs['job_name']
    if 'task_id' not in jobargsKeys:
        id = f'{datetime.now().replace(microsecond=0)}_{jobName}'
    else:
        id = jobargs['task_id']
    if 'trigger_type' not in jobargsKeys:
        trigger_type = 'cron'
    else:
        trigger_type = jobargs['trigger_type']
    if trigger_type == "date":
        run_time = jobargs['run_time']
        job = scheduler.add_job(func="task:my_job",
                                trigger=trigger_type,
                                run_date=run_time,
                                replace_existing=True,
                                coalesce=True,
                                id=id)
        print("添加一次性任务成功---[ %s ] " % id)
    elif trigger_type == 'interval':
        seconds = jobargs['interval_time']
        seconds = int(seconds)
        if seconds <= 0:
            raise TypeError('请输入大于0的时间间隔！')
        scheduler.add_job(func="task:my_job",
                          trigger=trigger_type,
                          seconds=seconds,
                          replace_existing=True,
                          coalesce=True,
                          id=id)
    elif trigger_type == "cron":
        # day_of_week = jobargs["run_time"]["day_of_week"]
        # hour = jobargs["run_time"]["hour"]
        # minute = jobargs["run_time"]["minute"]
        day = jobargs["run_time"]["second"]
        scheduler.add_job(func="func:request_nickname", id=id,
                          trigger=trigger_type,
                          second=day, replace_existing=True)
        print("添加周期执行任务成功任务成功---[ %s ] " % id)
    return jsonify(msg="新增任务成功")


# 暂停
@flask_app.route('/<task_id>/pause', methods=['GET'])
def pause_job(task_id):
    response = {'status': False}
    try:
        scheduler.pause_job(task_id)
        response['status'] = True
        response['msg'] = "job[%s] pause success!" % task_id
    except Exception as e:
        response['msg'] = str(e)
    return jsonify(response)


# 启动
@flask_app.route('/<task_id>/resume', methods=['GET'])
def resume_job(task_id):
    response = {'status': False}
    try:
        scheduler.resume_job(task_id)
        response['status'] = True
        response['msg'] = "job[%s] resume success!" % task_id
    except Exception as e:
        response['msg'] = str(e)
    return jsonify(response)


# 删除
@flask_app.route('/<task_id>/remove', methods=['GET'])
def remove_job(task_id):
    response = {'status': False}
    try:
        scheduler.remove_job(task_id)
        response['status'] = True
        response['msg'] = "job[%s] remove success!" % task_id
    except Exception as e:
        response['msg'] = str(e)
    return jsonify(response)


@flask_app.route('/123')
def index123():
    print(111111111111111111111111111111111111111111111111111111111111)
    return '<h1>Hello World!</h1>'


@flask_app.route('/get_jobs')
def get_jobs():
    from flask_apscheduler.utils import job_to_dict
    # 将job转化成可json的对象
    jobList = scheduler.get_jobs()
    allInfo = {}
    for _job_ in jobList:
        oneJob = job_to_dict(_job_)
        jobId = oneJob['id']
        oneJob['next_run_time'] = datetime.strftime(oneJob['next_run_time'],'%Y-%m-%d %H:%M:%S')
        if 'start_date' in oneJob.keys():
            oneJob['start_date'] = datetime.strftime(oneJob['start_date'],'%Y-%m-%d %H:%M:%S')
        allInfo[jobId] = oneJob
    return jsonify(allInfo)


if __name__ == '__main__':
    flask_app.config.from_object(app.settings.Config())
    app.extensions.scheduler.init_app(flask_app)
    app.extensions.scheduler.start()
    flask_app.run(host='0.0.0.0', port=5000, debug=True)
