# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from datetime import date

import matplotlib.pyplot as plt
from django.core import serializers
from django.db import connection
from zipfile import ZipFile
from django.shortcuts import redirect
from django.http import FileResponse
from django.views.generic import TemplateView, ListView, View
from monitoring.models import PupilModel, TeacherModel, AbsenceModel, ClassModel, ParentModel


class MainView(TemplateView):
    template_name = "monitoring/index.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        cursor = connection.cursor()
        data_abs = cursor.execute(
            'select pupils.pupil_class_id, count(pupils.id) '
            'from monitoring_absencemodel as absc '
            'inner join monitoring_pupilmodel as pupils '
            'on absc.pupil_id=pupils.id '
            'where absc.day = current_date '
            'group by pupils.pupil_class_id;'
        )
        data_abs = data_abs.fetchall() if data_abs is not None else []

        data_cls = cursor.execute(
            'select pupils.pupil_class_id, count(pupils.id) '
            'from monitoring_pupilmodel as pupils '
            'inner join monitoring_classmodel as cls '
            'on pupils.pupil_class_id=cls.id '
            'group by pupils.pupil_class_id;'
        )
        data_cls = data_cls.fetchall() if data_cls is not None else []

        abs = dict()
        class_model = set(ClassModel.objects.all())
        for cls in class_model:
            abs[cls.id] = [0, 0]

        for row in data_abs:
            abs[row[0]][0] = row[1]

        for row in data_cls:
            abs[row[0]][1] = row[1]

        class_model = set(ClassModel.objects.all())
        classes = list()
        all_pupils = 0
        abs_pupils = 0
        warn = 0
        for cls in class_model:
            perc_class = abs[cls.id][0] * 100 / abs[cls.id][1] if abs[cls.id][0] != 0 else 0
            classes.append([
                cls.id,
                cls.name,
                round(abs[cls.id][0]),
                perc_class
            ])
            all_pupils += abs[cls.id][1]
            abs_pupils += abs[cls.id][0]
            warn = warn + 1 if perc_class > 20 else warn

        perc_pupils = abs_pupils * 100 / all_pupils if all_pupils > 0 else 0
        perc_cls = warn * 100 / class_model.__len__()
        context['classes'] = classes
        context['all'] = all_pupils
        context['perc_pupils'] = round(perc_pupils)
        context['perc_cls'] = round(perc_cls)

        abs_gisto = cursor.execute(
            'select count(abs.cause) '
            'from monitoring_absencemodel as abs '
            'where abs.day = current_date '
            'group by abs.cause;'
        )
        abs_gisto = abs_gisto.fetchall() if abs_gisto is not None else []

        data_names = [
            'Хвороба',
            'Прогул',
            'Запізнення'
        ]

        try:
            data_values = [
                abs_gisto[0][0],
                abs_gisto[1][0],
                abs_gisto[2][0]
            ]
        except IndexError:
            data_values = [
                0,
                0,
                0,
            ]

        dpi = 80
        fig = plt.figure(dpi=dpi, figsize=(512 / dpi, 384 / dpi))

        plt.title('Розподіл відсутніх')

        ax = plt.axes()
        ax.yaxis.grid(True, zorder=1)

        xs = range(len(data_names))

        plt.bar(
            [x + 0.05 for x in xs],
            [d * 1.0 for d in data_values],
            width=0.2,
            color='green',
            alpha=0.7,
            zorder=2)

        plt.xticks(xs, data_names)
        fig.autofmt_xdate(rotation=25)
        fig.savefig('monitoring/static/monitoring/absence.png')

        return context


class PupilsView(ListView):
    model = PupilModel
    template_name = "monitoring/pupils.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        pupils = PupilModel.objects.all()
        context['pupils'] = pupils

        classes = set(ClassModel.objects.all())
        context['classes'] = classes

        groups = PupilModel._meta.get_field('group').choices
        context['groups'] = groups

        discounts = PupilModel._meta.get_field('discount').choices
        context['discounts'] = discounts

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

        classes = ClassModel.objects.order_by('id').all()
        pupils = PupilModel.objects.all()
        causes = AbsenceModel._meta.get_field('cause').choices

        today = date.today().strftime('%d/%m/%Y')

        context['classes'] = classes
        context['pupils'] = pupils
        context['causes'] = causes

        context['causes_json'] = json.dumps(causes)
        context['classes_json'] = serializers.serialize('json', classes)
        context['pupils_json'] = serializers.serialize('json', pupils)

        context['today'] = today

        return context

    def post(self, request, *args, **kwargs):
        cause = request.POST.get('cause')
        day = request.POST.get('day')
        lessons_skipped = request.POST.get('lessons_skipped')
        pupil = request.POST.get('pupil')

        AbsenceModel.objects.create(
            cause=cause,
            day=day,
            lessons_skipped=lessons_skipped,
            pupil=PupilModel.objects.get(id=pupil),
        ).save()

        return redirect('/absence')


class AddGroupView(TemplateView):
    template_name = "monitoring/add_group.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        pupils = PupilModel.objects.all()
        groups = PupilModel._meta.get_field('group').choices
        classes = ClassModel.objects.order_by('id').all()

        context['pupils'] = pupils
        context['groups'] = groups
        context['classes'] = classes

        context['classes_json'] = serializers.serialize('json', classes)
        context['pupils_json'] = serializers.serialize('json', pupils)

        return context

    def post(self, request, *args, **kwargs):
        pupil_id = request.POST.get('pupil')
        group = request.POST.get('group')
        vision_defect = request.POST.get('vision_defect')

        pupil = PupilModel.objects.get(id=pupil_id)
        pupil.group = group
        pupil.vision_defect = True if vision_defect == 'on' else False
        pupil.save()

        return redirect('/pupils')


class AddDiscountView(TemplateView):
    template_name = "monitoring/add_discount.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        classes = ClassModel.objects.order_by('id').all()
        pupils = PupilModel.objects.all()
        discounts = PupilModel._meta.get_field('discount').choices

        context['classes'] = classes
        context['pupils'] = pupils
        context['discounts'] = discounts

        context['classes_json'] = serializers.serialize('json', classes)
        context['pupils_json'] = serializers.serialize('json', pupils)

        return context

    def post(self, request, *args, **kwargs):
        pupil_id = request.POST.get('pupil')
        discount = request.POST.get('discount')

        pupil = PupilModel.objects.get(id=pupil_id)
        pupil.discount = discount
        pupil.save()

        return redirect('/pupils')


def pupils_archive_view(request):
    with open('pupils.csv', 'wb') as file:
        cursor = connection.cursor()
        for row in cursor.execute('SELECT * FROM monitoring_pupilmodel'):
            write_row = ','.join([str(i) for i in row])
            write_row = write_row + '\n'
            file.write(write_row.encode())

    with ZipFile('pupils.zip', 'w') as myzip:
        myzip.write('pupils.csv')

    return FileResponse(open('pupils.zip', 'rb'), as_attachment=True)


class EditPupilView(TemplateView):
    template_name = "monitoring/edit_pupil.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        pupil_id = self.kwargs.get('pk', None)
        pupil = PupilModel.objects.filter(id=pupil_id).first()
        context['pupil_data'] = pupil

        parents = ParentModel.objects.order_by('last_name').all()
        pupil_parents_pk = [parent.pk for parent in parents if pupil.parent.all().filter(pk=parent.pk).exists()]
        context['parents'] = parents
        context['pupil_parents_pk'] = pupil_parents_pk

        classes = set(ClassModel.objects.all())
        context['classes'] = classes

        groups = PupilModel._meta.get_field('group').choices
        context['groups'] = groups

        discounts = PupilModel._meta.get_field('discount').choices
        context['discounts'] = discounts

        gender = PupilModel._meta.get_field('gender').choices
        context['gender'] = gender

        return context

    def post(self, request, *args, **kwargs):
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        middle_name = request.POST.get('middle_name')
        birthday = request.POST.get('birthday')
        address = request.POST.get('address')
        gender = request.POST.get('gender')
        phone = request.POST.get('phone')
        group = request.POST.get('group')
        vision_defect = True if request.POST.get('vision_defect') == 'on' else False
        discount = request.POST.get('discount')
        pupil_class = request.POST.get('class')
        parents = request.POST.getlist('parents')

        user_id = self.kwargs.get('pk', None)
        user = PupilModel.objects.filter(id=user_id)

        user.get().parent.clear()
        for parent in parents:
            p = ParentModel.objects.filter(id=int(parent)).get()
            user.get().parent.add(p)
        user.get().save()

        user.update(
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            birthday=birthday,
            phone=phone,
            address=address,
            gender=gender,
            group=group,
            vision_defect=vision_defect,
            discount=discount,
            pupil_class=pupil_class,
        )

        return redirect('/pupils')


class AddPupilView(TemplateView):
    template_name = "monitoring/add_pupil.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        classes = set(ClassModel.objects.all())
        context['classes'] = classes

        groups = PupilModel._meta.get_field('group').choices
        context['groups'] = groups

        discounts = PupilModel._meta.get_field('discount').choices
        context['discounts'] = discounts

        gender = PupilModel._meta.get_field('gender').choices
        context['gender'] = gender

        parents = ParentModel.objects.order_by('last_name').all()
        context['parents'] = parents

        return context

    def post(self, request, *args, **kwargs):
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        middle_name = request.POST.get('middle_name')
        birthday = request.POST.get('birthday')
        address = request.POST.get('address')
        gender = request.POST.get('gender')
        phone = request.POST.get('phone')
        group = request.POST.get('group')
        vision_defect = True if request.POST.get('vision_defect') == 'on' else False
        discount = request.POST.get('discount')
        pupil_class = ClassModel.objects.get(id=request.POST.get('class'))
        parents = request.POST.getlist('parents')

        pupil = PupilModel.objects.create(
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            birthday=birthday,
            phone=phone,
            address=address,
            gender=gender,
            group=group,
            vision_defect=vision_defect,
            discount=discount,
            pupil_class=pupil_class,
        )
        pupil.save()

        for parent in parents:
            p = ParentModel.objects.filter(id=int(parent)).get()
            pupil.parent.add(p)
        pupil.save()

        return redirect('/pupils')
