from django.conf.urls import url

from . import views

app_name = 'blog'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'update_responses/', views.update_responses, name='update_responses'),
    #url(r'answer/', views.answer, name='answer'),
    url(r'^(?P<question_id>\d+)/$', views.getq, name='questions'),
    url(r'^(?P<question_id>[0-9]+)/$', views.getq, name='questions'),
    url(r'postaquestion/', views.postaq, name='postaq'),
    url(r'createprofile/', views.createprofile, name='createprofile'),
    url(r'filter/', views.filter, name='filter'),
    url(r'loginpage/', views.loginpage, name='loginpage'),
    url(r'mod/', views.mod, name='mod'),
	url(r'inappropriate_qs/', views.inappropriate_qs, name='inappropriate_qs'),
	url(r'inappropriate_rs/', views.inappropriate_rs, name='inappropriate_rs'),
	url(r'flagged_users/', views.flagged_users, name='flagged_users'),
]
