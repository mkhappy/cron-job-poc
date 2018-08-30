from flask import Flask
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from flask_apscheduler import APScheduler
from flask_apscheduler.json import jsonify
from flask_restful import Resource, Api, reqparse
from twilio.rest import Client
from dotenv import load_dotenv
import os

load_dotenv()

scheduler = APScheduler()
jobstore = 'sqlalchemy'


class Job(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('args',
                        type=list,
                        required=True,
                        help='This field cannot be blank!',
                        location='json'
                        )
    parser.add_argument('day_of_week',
                        type=str,
                        required=True,
                        help='This field cannot be blank!'
                        )
    parser.add_argument('hour',
                        type=str,
                        required=True,
                        help='This field cannot be blank!'
                        )
    parser.add_argument('minute',
                        type=str,
                        required=True,
                        help='This field cannot be blank!'
                        )

    @classmethod
    def post(cls, job_id):
        data = cls.parser.parse_args()
        DEFAULTS = {'trigger': 'cron'}
        job_params = {**data, **DEFAULTS}

        job = scheduler.add_job(job_id, send_sms, **job_params)

        return {'success': 'ok'}, 201

    def get(self, job_id):
        job = scheduler.get_job(job_id)
        return jsonify(job)


class Jobs(Resource):
    def get(self):
        jobs = scheduler.get_jobs()
        return jsonify(jobs)


def send_sms(name, to_number):
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')

    client = Client(account_sid, auth_token)

    greeting = f'Hello, {name}!'

    client.messages.create(
        body=greeting, from_=from_number, to='+19045620299')


class Config(object):
    SCHEDULER_JOBSTORES = {
        'default': SQLAlchemyJobStore(url='sqlite:///twilio_test.db')
    }

    SCHEDULER_API_ENABLED = True


def test(name, to_number):
    greeting = f'Hi, {name}!'
    print(greeting)


if __name__ == '__main__':
    app = Flask(__name__)
    app.config.from_object(Config())

    scheduler.init_app(app)
    scheduler.start()

    api = Api(app)
    api.add_resource(Job, '/api/job/<string:job_id>')
    api.add_resource(Jobs, '/api/jobs')

    app.run()
