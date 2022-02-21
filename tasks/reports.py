from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView

from django.forms import ModelForm, ValidationError

from tasks.models import Task, TaskHistory, Reports

from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.auth.mixins import LoginRequiredMixin

class ReportForm(ModelForm):

    class Meta:
        model = Reports
        fields = ["timing"]
    
    def __init__(self, *args, **kwargs):
       super(ReportForm, self).__init__(*args, **kwargs)

       input_styling = "p-3 bg-gray-200 rounded-xl block w-full my-2 text-base text-black"

       self.fields['timing'].widget.attrs.update({'class' : input_styling})

class GenericReportUpdateView(UpdateView):
    model = Reports
    form_class = ReportForm
    template_name = "report_update.html"
    success_url = "/tasks"

    def get_queryset(self):
        return Reports.objects.filter(user=self.request.user)
