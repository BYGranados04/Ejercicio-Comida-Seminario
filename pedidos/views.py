import json
from decimal import Decimal

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

from .models import Cliente, Pedido, Producto


def leer_json(request):
    try:
        return json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


def pedido_a_json(pedido):
    return {
        "id": pedido.id,
        "cliente": pedido.cliente.nombre,
        "producto": pedido.producto.nombre,
        "cantidad": pedido.cantidad,
        "observaciones": pedido.observaciones,
        "total": str(pedido.total),
        "estado": pedido.estado,
        "fecha": timezone.localtime(pedido.fecha).strftime("%d/%m/%Y %H:%M"),
    }


@ensure_csrf_cookie
def index(request):
    return render(request, "pedidos/index.html")


@require_http_methods(["GET", "POST"])
def api_clientes(request):
    if request.method == "GET":
        clientes = list(Cliente.objects.order_by("nombre").values("id", "nombre"))
        return JsonResponse(clientes, safe=False)

    datos = leer_json(request)
    nombre = datos.get("nombre", "").strip() if datos else ""
    if not nombre:
        return JsonResponse({"error": "El nombre es obligatorio."}, status=400)

    cliente = Cliente.objects.create(nombre=nombre)
    return JsonResponse({"id": cliente.id, "nombre": cliente.nombre}, status=201)


@require_http_methods(["GET"])
def api_productos(request):
    productos = [
        {"id": producto.id, "nombre": producto.nombre, "precio": str(producto.precio)}
        for producto in Producto.objects.order_by("id")
    ]
    return JsonResponse(productos, safe=False)


@require_http_methods(["GET", "POST"])
def api_pedidos(request):
    if request.method == "GET":
        pedidos = Pedido.objects.select_related("cliente", "producto").order_by("-fecha")
        return JsonResponse([pedido_a_json(pedido) for pedido in pedidos], safe=False)

    datos = leer_json(request)
    if not datos:
        return JsonResponse({"error": "Los datos enviados no son válidos."}, status=400)

    try:
        cliente = Cliente.objects.get(id=datos.get("cliente"))
        producto = Producto.objects.get(id=datos.get("producto"))
        cantidad = int(datos.get("cantidad", 0))
    except (Cliente.DoesNotExist, Producto.DoesNotExist, TypeError, ValueError):
        return JsonResponse({"error": "Cliente, producto o cantidad no válidos."}, status=400)

    if cantidad < 1:
        return JsonResponse({"error": "La cantidad debe ser mayor que cero."}, status=400)

    pedido = Pedido.objects.create(
        cliente=cliente,
        producto=producto,
        cantidad=cantidad,
        observaciones=str(datos.get("observaciones", "")).strip(),
        total=producto.precio * Decimal(cantidad),
    )
    return JsonResponse(pedido_a_json(pedido), status=201)


@require_http_methods(["POST"])
def api_cambiar_estado(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    datos = leer_json(request)
    estado = datos.get("estado") if datos else None
    estados_validos = [opcion[0] for opcion in Pedido.ESTADOS]

    if estado not in estados_validos:
        return JsonResponse({"error": "El estado no es válido."}, status=400)

    pedido.estado = estado
    pedido.save(update_fields=["estado"])
    return JsonResponse({"id": pedido.id, "estado": pedido.estado})
