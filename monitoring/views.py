# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import TemplateView


class MainView(TemplateView):
    template_name = "monitoring/index.html"





