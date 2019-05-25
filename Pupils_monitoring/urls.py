"""Pupils_monitoring URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from monitoring import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.MainView.as_view(), name='main page'),
    url(r'^login$', views.LoginView.as_view(), name='login'),

    url(r'^pupils$', views.PupilsView.as_view(), name='pupils base'),
    url(r'^pupils_archive$', views.pupils_archive_view, name='download pupils archive'),
    url(r'^add_pupil$', views.AddPupilView.as_view(), name='add pupil'),
    url(r'^edit_pupil/(?P<pk>\d+)$', views.EditPupilView.as_view(), name='edit_pupil'),
    url(r'^delete_pupil$', views.DeletePupilView.as_view(), name='delete_pupil'),

    url(r'^teachers$', views.TeachersView.as_view(), name='teachers base'),
    url(r'^add_teacher$', views.AddTeacherView.as_view(), name='add teacher'),
    url(r'^edit_teacher/(?P<pk>\d+)$', views.EditTeacherView.as_view(), name='edit teacher'),
    url(r'^delete_teacher$', views.DeleteTeacherView.as_view(), name='delete teacher'),

    url(r'^absence$', views.AbsenceView.as_view(), name='absence base'),
    url(r'^add_absence$', views.AddAbsenceView.as_view(), name='add absence'),
    url(r'^add_group$', views.AddGroupView.as_view(), name='add group'),
    url(r'^add_discount$', views.AddDiscountView.as_view(), name='add discount'),

    url(r'^reports$', views.ReportsView.as_view(), name='reports'),
    url(r'^report_group$', views.ReportGroupView.as_view(), name='report group'),
    url(r'^report_food$', views.ReportFoodView.as_view(), name='report food'),


]
