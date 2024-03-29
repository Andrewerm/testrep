from django.urls import path
from . import views
app_name = 'restapi'

urlpatterns = [
    path('subject/', views.SubjectListView.as_view(), name='subject_list'),
    path('subject/<pk>/',  views.SubjectDetailView.as_view(), name='subject_detail'),
    ]