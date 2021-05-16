from django.urls import include, path
from . import views

urlpatterns = [
    path('',views.index,name="home"),

    path('statistics',views.statistics,name="statistics"),
    path('statistics_chart/', views.statistics_chart, name='statistics_chart'),
    path('total_miles_traveled_by_user_chart/', views.total_miles_traveled_by_user_chart, name='total_miles_traveled_by_user_chart'),
    

    path('trips',views.trips,name="trips"),
    path('create_trip',views.create_trip,name="create_trip"),
    path(r'^view_trip/(?P<trip_id>\d+)$', views.view_trip, name="view_trip"),
    path(r'^edit_trip/(?P<trip_id>\d+)$', views.edit_trip, name="edit_trip"),
    path(r'^delete_trip/(?P<trip_id>\d+)$', views.delete_trip, name="delete_trip"),

    path(r'^create_visit/(?P<trip_id>\d+)$', views.create_visit, name="create_visit"),
    path(r'^edit_visit/(?P<trip_id>\d+)$/(?P<visit_id>\d+)$', views.edit_visit, name="edit_visit"),
    path(r'^delete_visit/(?P<trip_id>\d+)$/(?P<visit_id>\d+)$', views.delete_visit, name="delete_visit"),

    path(r'^create_comment/(?P<trip_id>\d+)$', views.create_comment, name="create_comment"),
    path(r'^delete_comment/(?P<trip_id>\d+)$/(?P<comment_id>\d+)$', views.delete_comment, name="delete_comment"),

    path(r'^like/(?P<trip_id>\d+)$', views.like, name="like"),

    path('sign_up', views.sign_up, name="sign-up"),
    path('log_out', views.log_out, name="log_out"),
    path('log_in', views.log_in, name="log_in"),

    path(r'^account_edit/(?P<traveler_id>\d+)$', views.traveler_update, name="account_edit"),
    path(r'^account/(?P<traveler_id>\d+)$', views.traveler_profile, name="account"),
    path(r'^friend/(?P<traveler_id>\d+)$', views.friend, name="friend"),
    path(r'^unfriend/(?P<traveler_id>\d+)$', views.unfriend, name="unfriend"),

    path('users', views.users, name='users'),
    path(r'^edit/(?P<traveler_id>\d+)$', views.edit, name='edit'),
    path(r'^delete_user/(?P<traveler_id>\d+)$', views.delete_user, name='delete_user'),
    
    path('destinations/', views.destinations, name='destinations'),
    path(r'^destination_update/(?P<destination_id>\d+)$', views.destination_update, name='destination_update'),
    path(r'^destination_delete/(?P<destination_id>\d+)$', views.destination_delete, name='destination_delete'),
    path(r'^favorite/(?P<destination_id>\d+)$', views.favorite, name='favorite'),
    path(r'^unfavorite/(?P<destination_id>\d+)$', views.unfavorite, name='unfavorite'),

    path('attractions/', views.attractions, name='attractions'),
    path(r'^attractions_form/(?P<trip_id>\d+)$', views.attractions_form, name='attractions_form'),

    #zipcode_form
    path('zipcode_form/', views.zipcode_form, name='zipcode_form'),
]


