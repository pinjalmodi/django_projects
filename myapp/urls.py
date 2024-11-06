from django.urls import path
from . import views
from .views import create_order, payment_success, payment_failed

urlpatterns = [
    
    path('',views.index,name='index'),
    path('member-index/',views.member_index,name='member-index'),
    path('admin-index/',views.admin_index,name='admin-index'),
    path('contact/',views.contact,name='contact'),
    path('register/',views.register,name='register'),
    path('login/',views.login,name='login'),
    path('logout/',views.logout,name='logout'),
    path('forgot-password/',views.forgot_password,name='forgot-password'),
    path('verify-otp/',views.verify_otp,name='verify-otp'),
    path('new-password/',views.new_password,name='new-password'),
    path('make-requests/',views.make_requests,name='make-requests'),
    path('profile/',views.profile,name='profile'),
    path('change-password/',views.change_password,name='change-password'),
    path('admin-profile/',views.admin_profile,name='admin-profile'),
    path('admin-change-password/',views.admin_change_password,name='admin-change-password'),
    path('admin-member-information/',views.admin_member_information,name='admin-member-information'),
    path('admin-member-information-view/',views.admin_member_information_view,name='admin-member-information-view'),
    path('notices/',views.notices,name='notices'),
    path('member-notices/',views.member_notices,name='member-notices'),
    path('admin-maintenance/',views.admin_maintenance,name='admin-maintenance'),
    path('add-maintenance/',views.add_maintenance,name='add-maintenance'),
    path('DiscussionList/',views.Discussion_List,name='DiscussionList'),
    path('discussion-detail/<int:discussion_id>/',views.discussion_detail,name='discussion-detail'),
    path('approve/<int:user_id>/',views.approve_user, name='approve_user'),
    path('decline/<int:user_id>/',views.decline_user, name='decline_user'),
    path('create-order/',views.create_order, name='create-order'),
    path('payment/',views.payment , name='payment'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('payment-failed/', views.payment_failed, name='payment_failed'),
    path('confirm_payment/',views.confirm_payment, name='confirm_payment'),
    path('gallery/',views.gallery,name='gallery'),
    path('create_gallery/',views.create_gallery,name='create_gallery'),
    path('payment_all/',views.payment_all,name='payment_all'),

    ]