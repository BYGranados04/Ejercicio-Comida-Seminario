from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("api/clientes/", views.api_clientes, name="api_clientes"),
    path("api/productos/", views.api_productos, name="api_productos"),
    path("api/pedidos/", views.api_pedidos, name="api_pedidos"),
    path("api/pedidos/<int:pedido_id>/estado/", views.api_cambiar_estado, name="api_cambiar_estado"),
]
