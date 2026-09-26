from django.db import models


class Cliente(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return self.nombre


class Pedido(models.Model):
    ESTADOS = [
        ("Recibido", "Recibido"),
        ("Preparando", "Preparando"),
        ("Entregado", "Entregado"),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    observaciones = models.TextField(blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADOS, default="Recibido")
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido {self.id} - {self.cliente.nombre}"
