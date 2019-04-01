# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from monitoring import choices


class PupilModel(models.Model):
    last_name = models.CharField(
        max_length=64,
    )
    first_name = models.CharField(
        max_length=64,
    )
    middle_name = models.CharField(
        max_length=64,
    )
    birthday = models.DateField()
    gender = models.CharField(
        max_length=1,
        choices=choices.GENDER_CHOICES,
        default='f',
    )
    address = models.CharField(
        max_length=128,
    )
    phone = models.CharField(
        max_length=20,
    )
    group = models.IntegerField(
        choices=choices.GROUP_CHOICES,
        default=1,
    )
    vision_defect = models.BooleanField(
        default=False,
    )
    discount = models.IntegerField(
        choices=choices.DISCOUNT_CHOICES,
        default=1,
    )
    pupil_class = models.ForeignKey(
        'ClassModel',
        on_delete=models.CASCADE,
    )
    parent = models.ManyToManyField('ParentModel')


class ParentModel(models.Model):
    last_name = models.CharField(
        max_length=64,
    )
    first_name = models.CharField(
        max_length=64,
    )
    middle_name = models.CharField(
        max_length=64,
    )
    job_place = models.CharField(
        max_length=256,
    )
    phone = models.CharField(
        max_length=20,
    )


class TeacherModel(models.Model):
    last_name = models.CharField(
        max_length=64,
    )
    first_name = models.CharField(
        max_length=64,
    )
    middle_name = models.CharField(
        max_length=64,
    )


class ClassModel(models.Model):
    name = models.CharField(
        max_length=8,
    )
    teacher = models.ForeignKey(
        TeacherModel,
        on_delete=models.CASCADE,
    )


class AbsenceModel(models.Model):
    cause = models.IntegerField(
        choices=choices.CAUSE_CHOICES,
        default=1,
    )
    day = models.DateField()
    time = models.IntegerField(
        default=0,
    )
    pupil = models.ForeignKey(
        PupilModel,
        on_delete=models.CASCADE,
    )
