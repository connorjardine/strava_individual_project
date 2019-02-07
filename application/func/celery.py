from __future__ import absolute_import
from celery import Celery

run_celery = Celery('application',
                    broker='amqp://connor:connor2110@localhost/connor_vhost',
                    backend='rpc://',
                    include=['application.func.handle_runs'])
