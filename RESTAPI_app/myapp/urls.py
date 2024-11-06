from django.urls import path
from . import views

urlpatterns = [
    
    path('index/<int:discussion_id>/',views.comm_insert,name='index'),
    path('',views.admin_index,name='admin-index'),
    path('disc-insert/',views.disc_insert,name='disc-insert'),
    path('comm-insert/<int:discussion_id>/',views.comm_insert,name='comm-insert'),
    path('rem-comm/<int:discussion_id>/<int:comment_id>/',views.rem_comm,name='rem-comm'),

    

]