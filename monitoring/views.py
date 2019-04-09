# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sqlite3
from zipfile import ZipFile
from django.shortcuts import redirect
from django.http import FileResponse
from django.views.generic import TemplateView, ListView, View
from monitoring.models import PupilModel, TeacherModel, AbsenceModel, ClassModel


class MainView(TemplateView):
    template_name = "monitoring/index.html"


class PupilsView(ListView):
    model = PupilModel
    template_name = "monitoring/pupils.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        pupils = PupilModel.objects.all()
        context['pupils'] = pupils

        classes = set(ClassModel.objects.all())
        context['classes'] = classes

        return context


class TeachersView(ListView):
    model = TeacherModel
    template_name = "monitoring/teachers.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        teachers = TeacherModel.objects.all()
        context['teachers'] = teachers

        return context


class AbsenceView(ListView):
    model = AbsenceModel
    template_name = 'monitoring/absence.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        absence = AbsenceModel.objects.all()
        context['absence'] = absence

        return context


class AddAbsenceView(TemplateView):
    template_name = 'monitoring/add_absence.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        pupils = PupilModel.objects.all()
        causes = AbsenceModel._meta.get_field('cause').choices

        context['pupils'] = pupils
        context['causes'] = causes

        return context

    def post(self, request, *args, **kwargs):
        cause = request.POST.get('cause').split()[0]
        day = request.POST.get('day')
        time = request.POST.get('time')
        pupil = request.POST.get('pupil').split()[0]

        AbsenceModel.objects.create(
            cause=cause,
            day=day,
            time=time,
            pupil=PupilModel.objects.get(id=pupil),
        ).save()

        return redirect('/absence')


class AddGroupView(TemplateView):
    template_name = "monitoring/add_group.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        pupils = PupilModel.objects.all()
        groups = PupilModel._meta.get_field('group').choices

        context['pupils'] = pupils
        context['groups'] = groups

        return context

    def post(self, request, *args, **kwargs):
        pupil_id = request.POST.get('pupil').split()[0]
        group = request.POST.get('group').split()[0]

        pupil = PupilModel.objects.get(id=pupil_id)
        pupil.group = group
        pupil.save()

        return redirect('/pupils')


class AddDiscountView(TemplateView):
    template_name = "monitoring/add_discount.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        pupils = PupilModel.objects.all()
        discounts = PupilModel._meta.get_field('discount').choices

        context['pupils'] = pupils
        context['discounts'] = discounts

        return context

    def post(self, request, *args, **kwargs):
        pupil_id = request.POST.get('pupil').split()[0]
        discount = request.POST.get('discount').split()[0]

        pupil = PupilModel.objects.get(id=pupil_id)
        pupil.discount = discount
        pupil.save()

        return redirect('/pupils')


def pupils_archive_view(request):

    connection = sqlite3.connect('db.sqlite3')

    with open('pupils.csv', 'wb') as file:
        cursor = connection.cursor()
        for row in cursor.execute('SELECT * FROM monitoring_pupilmodel'):
            write_row = ','.join([str(i) for i in row])
            write_row = write_row + '\n'
            file.write(write_row.encode())

    with ZipFile('pupils.zip', 'w') as myzip:
        myzip.write('pupils.csv')

    return FileResponse(open('pupils.zip', 'rb'), as_attachment=True)
