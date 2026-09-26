let productos = [];

function obtenerCookie(nombre) {
    const cookie = document.cookie
        .split(";")
        .map(valor => valor.trim())
        .find(valor => valor.startsWith(nombre + "="));
    return cookie ? decodeURIComponent(cookie.split("=")[1]) : "";
}

async function enviarJson(url, datos) {
    const respuesta = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": obtenerCookie("csrftoken")
        },
        body: JSON.stringify(datos)
    });
    const resultado = await respuesta.json();
    if (!respuesta.ok) {
        throw new Error(resultado.error || "Ocurrió un error.");
    }
    return resultado;
}

function mostrarMensaje(texto, esError = false) {
    const mensaje = document.getElementById("mensaje");
    mensaje.textContent = texto;
    mensaje.style.color = esError ? "#b00020" : "#1769aa";
}

async function cargarClientes(clienteSeleccionado = null) {
    const respuesta = await fetch("/api/clientes/");
    const clientes = await respuesta.json();
    const select = document.getElementById("cliente");
    select.innerHTML = '<option value="">Seleccione un cliente</option>';

    clientes.forEach(cliente => {
        const opcion = document.createElement("option");
        opcion.value = cliente.id;
        opcion.textContent = cliente.nombre;
        opcion.selected = cliente.id === clienteSeleccionado;
        select.appendChild(opcion);
    });
}

async function cargarProductos() {
    const respuesta = await fetch("/api/productos/");
    productos = await respuesta.json();
    const select = document.getElementById("producto");
    select.innerHTML = '<option value="">Seleccione un producto</option>';

    productos.forEach(producto => {
        const opcion = document.createElement("option");
        opcion.value = producto.id;
        opcion.textContent = `${producto.nombre} - Q${producto.precio}`;
        select.appendChild(opcion);
    });
}

function calcularTotal() {
    const productoId = Number(document.getElementById("producto").value);
    const cantidad = Number(document.getElementById("cantidad").value) || 0;
    const producto = productos.find(item => item.id === productoId);
    const total = producto ? Number(producto.precio) * cantidad : 0;
    document.getElementById("total").value = `Q${total.toFixed(2)}`;
}

async function cargarPedidos() {
    const respuesta = await fetch("/api/pedidos/");
    const pedidos = await respuesta.json();
    const tabla = document.getElementById("tabla-pedidos");
    tabla.innerHTML = "";

    if (pedidos.length === 0) {
        const fila = tabla.insertRow();
        const celda = fila.insertCell();
        celda.colSpan = 8;
        celda.textContent = "Todavía no hay pedidos.";
        return;
    }

    pedidos.forEach(pedido => {
        const fila = tabla.insertRow();
        [
            pedido.id,
            pedido.cliente,
            pedido.producto,
            pedido.cantidad,
            pedido.observaciones || "-",
            `Q${pedido.total}`
        ].forEach(valor => {
            const celda = fila.insertCell();
            celda.textContent = valor;
        });

        const celdaEstado = fila.insertCell();
        const selectEstado = document.createElement("select");
        ["Recibido", "Preparando", "Entregado"].forEach(estado => {
            const opcion = document.createElement("option");
            opcion.value = estado;
            opcion.textContent = estado;
            opcion.selected = estado === pedido.estado;
            selectEstado.appendChild(opcion);
        });
        selectEstado.addEventListener("change", async () => {
            try {
                await enviarJson(`/api/pedidos/${pedido.id}/estado/`, {
                    estado: selectEstado.value
                });
                mostrarMensaje("Estado actualizado.");
            } catch (error) {
                mostrarMensaje(error.message, true);
                cargarPedidos();
            }
        });
        celdaEstado.appendChild(selectEstado);

        const celdaFecha = fila.insertCell();
        celdaFecha.textContent = pedido.fecha;
    });
}

document.getElementById("form-cliente").addEventListener("submit", async evento => {
    evento.preventDefault();
    try {
        const cliente = await enviarJson("/api/clientes/", {
            nombre: document.getElementById("nombre").value
        });
        evento.target.reset();
        await cargarClientes(cliente.id);
        mostrarMensaje("Cliente guardado.");
    } catch (error) {
        mostrarMensaje(error.message, true);
    }
});

document.getElementById("form-pedido").addEventListener("submit", async evento => {
    evento.preventDefault();
    try {
        await enviarJson("/api/pedidos/", {
            cliente: document.getElementById("cliente").value,
            producto: document.getElementById("producto").value,
            cantidad: document.getElementById("cantidad").value,
            observaciones: document.getElementById("observaciones").value
        });
        evento.target.reset();
        document.getElementById("cantidad").value = 1;
        calcularTotal();
        await cargarPedidos();
        mostrarMensaje("Pedido creado.");
    } catch (error) {
        mostrarMensaje(error.message, true);
    }
});

document.getElementById("producto").addEventListener("change", calcularTotal);
document.getElementById("cantidad").addEventListener("input", calcularTotal);

async function iniciar() {
    try {
        await Promise.all([cargarClientes(), cargarProductos(), cargarPedidos()]);
        calcularTotal();
    } catch (error) {
        mostrarMensaje("No se pudieron cargar los datos.", true);
    }
}

iniciar();
