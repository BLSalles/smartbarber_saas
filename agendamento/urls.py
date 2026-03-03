from django.urls import path
from . import views
urlpatterns = [
    path("", views.agendar, name="agendar"),
    path("sucesso/", views.sucesso, name="sucesso"),

]