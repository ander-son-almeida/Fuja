# -*- coding: utf-8 -*-
"""
Created on Mon Aug 21 12:45:54 2023

@author: Anderson Almeida
"""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
]