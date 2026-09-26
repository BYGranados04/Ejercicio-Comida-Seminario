import json

from django.test import TestCase

from .models import Pedido, Producto


class ApiPedidosTests(TestCase):
    def test_crear_cliente_pedido_y_cambiar_estado(self):
        respuesta_cliente = self.client.post(
            "/api/clientes/",
            data=json.dumps({"nombre": "Ana"}),
            content_type="application/json",
        )
        self.assertEqual(respuesta_cliente.status_code, 201)

        producto = Producto.objects.get(nombre="Hamburguesa")
        respuesta_pedido = self.client.post(
            "/api/pedidos/",
            data=json.dumps(
                {
                    "cliente": respuesta_cliente.json()["id"],
                    "producto": producto.id,
                    "cantidad": 2,
                    "observaciones": "Sin cebolla",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(respuesta_pedido.status_code, 201)
        self.assertEqual(respuesta_pedido.json()["total"], "50.00")

        pedido = Pedido.objects.get()
        respuesta_estado = self.client.post(
            f"/api/pedidos/{pedido.id}/estado/",
            data=json.dumps({"estado": "Preparando"}),
            content_type="application/json",
        )
        self.assertEqual(respuesta_estado.status_code, 200)
        pedido.refresh_from_db()
        self.assertEqual(pedido.estado, "Preparando")
