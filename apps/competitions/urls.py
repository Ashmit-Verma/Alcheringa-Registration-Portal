
from django.contrib import admin
from django.urls import path, include
from . import views
from registrationportal import views as regviews
urlpatterns = [
    path('', regviews.home, name='home'),
    path('register/<slug>/',
         views.registercompetition, name='registercomp'),
#     path('update/<slug>',
#          views.UpdateRegistration, name='updateComp'),
#     path('cancelreg/<slug>',
#          views.CancelRegistration, name='cancelReg'),
     # path('viewrules/<slug>',views.viewrules, name='viewrules'),
     path('eventRegistered/', views.all_registrations, name='RegisteredEvents'),
     path('TeamMembers/', views.teamMembers, name='TeamMembers'),
     path('add_member/', views.add_member, name='add_member'), 
     path('add_member/<slug>/', views.add_member, name='add_member'), 
     path('competitions/edit_member/<member_id>/', views.memberedit, name='edit_member'),
     path('competitions/delete_member/<member_id>/', views.delete_member, name='delete_member'),
     path('data',views.data,name='datacomp'),
     path('data/<slug>/',views.data,name='data'),
     path('data/leaders',views.all_leaders,name='leaders'),


]
 

