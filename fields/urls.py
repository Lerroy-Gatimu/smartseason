from django.urls import path
from . import views

# All URLs here are mounted under /dashboard/ (see smartseason/urls.py)
urlpatterns = [
    # Dashboard — root of the authenticated area
    path('',                          views.dashboard,    name='dashboard'),

    # Field list, create, detail, edit, delete
    path('fields/',                   views.field_list,   name='field_list'),
    path('fields/new/',               views.field_create, name='field_create'),
    path('fields/<int:pk>/',          views.field_detail, name='field_detail'),
    path('fields/<int:pk>/edit/',     views.field_edit,   name='field_edit'),
    path('fields/<int:pk>/delete/',   views.field_delete, name='field_delete'),

    # Log a new update on a field
    path('fields/<int:pk>/update/',   views.log_update,   name='log_update'),
]
