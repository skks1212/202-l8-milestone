import email
import time
import datetime

from django.contrib.auth.models import User
from django.core.mail import send_mail
from numpy import delete
from tasks.models import Task, Reports
from datetime import timedelta
from django.db.models import Q

from celery.decorators import periodic_task

from task_manager.celery import app

@periodic_task(run_every=timedelta(hours=1))
def send_email_reminder():
    print("Starting to process Emails")
    now = datetime.datetime.now()
    get_reports = Reports.objects.filter(timing=now)
    for report in get_reports:
    
        non_deleted_qs = Task.objects.filter(user=report.user, deleted = False).order_by('priority')

        pending_qset = non_deleted_qs.filter(status = "PENDING")
        in_progress_qset = non_deleted_qs.filter(status = "IN_PROGRESS")
        completed_qset = non_deleted_qs.filter(status = "COMPLETED")
        cancelled_qset = non_deleted_qs.filter(status = "CANCELLED")

        email_content = f'Hey there {report.user.username}\nHere is your daily task summary:\n\n'
        email_content += f"{pending_qset.count()} Pending Tasks:\n"
        for q in pending_qset:
            email_content+= f"-> {q.title} ({q.priority}): \n | {q.description} \n | Created on {q.created_date} \n \n"

        email_content += f"{in_progress_qset.count()} In Progress Tasks:\n"
        for q in in_progress_qset:
            email_content+= f"-> {q.title} ({q.priority}): \n | {q.description} \n | Created on {q.created_date} \n \n"

        email_content += f"{completed_qset.count()} Completed Tasks:\n"
        for q in completed_qset:
            email_content+= f"-> {q.title} ({q.priority}): \n | {q.description} \n | Created on {q.created_date} \n \n"

        email_content += f"{cancelled_qset.count()} Cancelled Tasks:\n"
        for q in cancelled_qset:
            email_content+= f"-> {q.title} ({q.priority}): \n | {q.description} \n | Created on {q.created_date} \n \n"

        send_mail(f"You have {pending_qset.count()} pending and {in_progress_qset.count()} in progress tasks", email_content, "tasks@task_manager.org", [report.user.email])
        print(f"Completed Processing User {report.user.id}")


