from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("listings/add", views.create, name="add_listing"),
    path("listings/watch", views.watchlist, name="watchlist"),
    path("listings/edit/<str:listing>", views.edit, name="edit_listing"),
    path("listings/<str:listing>", views.listings, name="listings"),
    path("categories", views.categories, name="categories")

]
