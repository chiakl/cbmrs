
from django.urls import path, include
#from django.views.generic.base import RedirectView
from . import views
from .import adminViews, movieloverViews

#favicon_view = RedirectView.as_view(url='/static/favicon.ico', permanent=True)

urlpatterns = [
    #path('^favicon\.ico$', favicon_view),
    path('', views.loginPage, name="login"),
    # path('accounts/', include('django.contrib.auth.urls')),
    path('doLogin/', views.doLogin, name="doLogin"),
    path('get_user_details/', views.get_user_details, name="get_user_details"),
    path('logout_user/', views.logout_user, name="logout_user"),
    path('admin_home/', adminViews.admin_home, name="admin_home"),
    path('add_ml/', adminViews.add_ml, name="add_ml"),
    path('add_ml_save/', adminViews.add_ml_save, name="add_ml_save"),
    path('edit_ml/<student_id>', adminViews.edit_ml, name="edit_ml"),
    path('edit_movielover_save/', adminViews.edit_movielover_save, name="edit_movielover_save"),
    path('manage_ml/', adminViews.manage_ml, name="manage_ml"),
    path('delete_ml/<student_id>/', adminViews.delete_ml, name="delete_ml"),
    path('check_email_exist/', adminViews.check_email_exist, name="check_email_exist"),
    path('check_username_exist/', adminViews.check_username_exist, name="check_username_exist"),
    path('admin_profile/', adminViews.admin_profile, name="admin_profile"),
    path('admin_profile_update/', adminViews.admin_profile_update, name="admin_profile_update"),
    path('admin_ml/', adminViews.admin_ml, name="admin_ml"), #for admin
    

    # URSL for Movie Lover
    path('movielover_home/', movieloverViews.movielover_home, name="movielover_home"),
    path('movielover_profile/', movieloverViews.movielover_profile, name="movielover_profile"),
    path('movielover_profile_update/', movieloverViews.movielover_profile_update, name="movielover_profile_update"),
    path('movielover_view_result/', movieloverViews.movielover_view_result, name="movielover_view_result"),
    path('movielover_movie_list/', movieloverViews.movielover_movie_list, name="movielover_movie_list"),
    path('movielover_preference/', movieloverViews.movielover_preference, name="movielover_preference"),
    path('movielover_preference_update/', movieloverViews.movielover_preference_update, name="movielover_preference_update"),
    path('movielover_rec_name/', movieloverViews.movielover_rec_name, name="movielover_rec_name"),
    path('movielover_rec_genre/', movieloverViews.movielover_rec_genre, name="movielover_rec_genre"),
    path('movielover_rec/', movieloverViews.movielover_rec, name="movielover_rec"),
]
