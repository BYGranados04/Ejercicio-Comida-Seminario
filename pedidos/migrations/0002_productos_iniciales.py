from decimal import Decimal

from django.db import migrations


def crear_productos(apps, schema_editor):
    Producto = apps.get_model("pedidos", "Producto")
    productos = [
        ("Hamburguesa", Decimal("25.00")),
        ("Pizza", Decimal("40.00")),
        ("Hot Dog", Decimal("20.00")),
        ("Papas fritas", Decimal("15.00")),
        ("Gaseosa", Decimal("10.00")),
    ]

    for nombre, precio in productos:
        Producto.objects.get_or_create(nombre=nombre, defaults={"precio": precio})


class Migration(migrations.Migration):
    dependencies = [
        ("pedidos", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(crear_productos, migrations.RunPython.noop),
    ]
