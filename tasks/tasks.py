import datetime

from django.contrib.auth.models import User
from django.core.mail import send_mail
from tasks.models import Task, Report
from datetime import timedelta, datetime, timezone
from django.db.models import Q
from itertools import chain

from celery.decorators import periodic_task

from task_manager.celery import app

@periodic_task(run_every=timedelta(seconds=5))
def send_reports():
    this_hour = datetime.now().hour

    #reports that were not sent in 1 day, but not for this hour
    get_unsent_reports = Report.objects.select_for_update().filter(last_report__lte = (datetime.now(timezone.utc) - timedelta(days=1))).filter(~Q(timing = this_hour))

    #reports that are supposed to be sent at this hour
    get_this_hour_reports = Report.objects.select_for_update().filter(timing = this_hour)

    concat_reports = list(chain(get_unsent_reports, get_this_hour_reports))
    
    stat_choices = [
        ["Pending", "PENDING"],
        ["In Progress", "IN_PROGRESS"],
        ["Completed", "COMPLETED"],
        ["Cancelled", "CANCELLED"]
    ]

    for report in concat_reports:
        base_qs = Task.objects.filter(user=report.user, deleted = False).order_by('priority')

        email_content = f'Hey there {report.user.username}\nHere is your daily task summary:\n\n'

        for status in stat_choices:
            stat_name = status[0]
            stat_id = status[1]

            stat_qs = base_qs.filter(status = stat_id)

            stat_count = stat_qs.count()
            status.append(stat_count)

            email_content += f"{stat_count} {stat_name} Tasks:\n"
            for q in stat_qs:
                email_content+= f" -> {q.title} ({q.priority}): \n  | {q.description} \n  | Created on {q.created_date} \n \n"

        send_mail(f"You have {stat_choices[0][2]} pending and {stat_choices[1][2]} in progress tasks", email_content, "tasks@task_manager.org", [report.user.email])

        report.last_report = datetime.now(timezone.utc)
        report.save()

        print(f"Completed Processing User {report.user.id}")