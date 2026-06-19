from django.contrib import admin
from django.urls import path
from chess import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('game/start/', views.start_game, name='start_game'),
    path('game/<int:game_id>/', views.game_view, name='game'),
    path('game/<int:game_id>/move/', views.make_move, name='make_move'),
    path('game/<int:game_id>/position/', views.get_position, name='get_position'),
    path('game/<int:game_id>/result/', views.post_game, name='post_game'),
]
