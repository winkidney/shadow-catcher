#!/usr/bin/env python
# coding:utf-8
# celeryconfig -
# author : winkidney - 14-9-12
__author__ = 'winkidney'


BROKER_URL = 'amqp://localhost'
CELERY_RESULT_BACKEND = 'redis://localhost/1'

CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']  # Ignore other content
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Europe/Oslo'
CELERY_ENABLE_UTC = True
