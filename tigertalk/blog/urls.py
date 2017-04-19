from django.conf.urls import url

from . import views

app_name = 'blog'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'update/', views.update, name='update'),
    #url(r'answer/', views.answer, name='answer'),
    url(r'^(?P<question_id>[0-9]+)/$', views.getq, name='questions'),
    # ex: /polls/5/results/                                                                
    #url(r'^(?P<question_id>[0-9]+)/answers/$', views.getans, name='answers'),
    # ex: /polls/5/vote/                                                                   
    url(r'^(?P<question_id>[0-9]+)/answer/$', views.answer, name='post_answer'),
]
