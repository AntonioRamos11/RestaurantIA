"""Streamlit version of the restaurant operational console (replaces Flet)."""
import streamlit as st
import sys, os

# --- Guard: if executed with 'python app.py' instead of 'streamlit run', exit gracefully ---
try:
    from streamlit.runtime.scriptrunner import get_script_run_ctx  # type: ignore
    if get_script_run_ctx() is None:
        print("\n⚠️  This is a Streamlit application.\nRun it with:\n    streamlit run frontend_streamlit/app.py\nOr from project root:\n    streamlit run frontend_streamlit/app.py --server.port=8501\n")
        raise SystemExit(0)
except Exception:
    # If the internal API path changes, we just proceed (Streamlit CLI will set context later)
    pass

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)
from POO_restaurante import Restaurante, Mesa, Cliente  # type: ignore

st.set_page_config(page_title="Restaurant Console", layout="wide")

# --- Initialization (one-time) ---
if "restaurante" not in st.session_state:
    r = Restaurante()
    capacidades = [2, 2, 4, 4, 6, 6]
    for i in range(1, 7):
        r.agregar_mesa(Mesa(i, capacidades[i - 1]))
    # mesa virtual (99) para pedidos App
    r.agregar_mesa(Mesa(99, 1))
    st.session_state.restaurante = r
if "mesa_sel" not in st.session_state:
    st.session_state.mesa_sel = None
if "filtro_tipo" not in st.session_state:
    st.session_state.filtro_tipo = "Entrada"
if "busqueda" not in st.session_state:
    st.session_state.busqueda = ""

r: Restaurante = st.session_state.restaurante

st.title("🍽️ RestaurantIA – Operaciones")
tabs = st.tabs(["Mesera", "Cocina", "Caja", "Admin Menú"])

# ------------- Helpers -------------
TIPOS = ["Entrada", "Plato Principal", "Postre", "Bebida"]

def get_items_by_type(tipo):
    if tipo == "Entrada":
        return r.menu.entradas
    if tipo == "Plato Principal":
        return r.menu.platos_principales
    if tipo == "Postre":
        return r.menu.postres
    if tipo == "Bebida":
        return r.menu.bebidas
    return []

def resumen_pedido(p):
    return p.obtener_resumen() if p else "Sin pedido"

def color_estado(estado: str):
    mapping = {"Pendiente": "orange", "En preparacion": "yellow", "Listo": "green", "Entregado": "blue"}
    return mapping.get(estado, "gray")

def mesa_label(m):
    return "App" if m.numero == 99 else f"Mesa {m.numero}" 

# ------------- Tab Mesera -------------
with tabs[0]:
    st.subheader("Mesas")
    cols = st.columns(7)
    for i, mesa in enumerate(sorted(r.mesas, key=lambda m: m.numero)):
        if mesa.numero == 99:
            # Render virtual after physical ones in its own column
            continue
        c = cols[i % len(cols)]
        status = "🟢 Libre" if not mesa.ocupada else "🔴 Ocupada"
        if c.button(f"{mesa_label(mesa)}\nCap:{mesa.tamaño}\n{status}", key=f"mesa_btn_{mesa.numero}"):
            st.session_state.mesa_sel = mesa.numero
    # Virtual table button
    if cols[-1].button("App\nVirtual", key="mesa_virtual"):
        st.session_state.mesa_sel = 99

    sel_num = st.session_state.mesa_sel
    st.markdown("---")
    if sel_num is not None:
        mesa = r.buscar_mesa(sel_num)
        st.markdown(f"### Gestión {mesa_label(mesa)}")
        # Asignar cliente / crear pedido
        if mesa.numero != 99:
            grupo = st.number_input("Tamaño grupo", min_value=1, max_value=12, value=2, key="grupo_size")
            if not mesa.ocupada and st.button("Asignar cliente y crear pedido", key="asignar_cliente"):
                cliente = Cliente(grupo)
                res = r.asignar_cliente_a_mesa(cliente, mesa.numero)
                if "asignado" in res:
                    r.crear_pedido(mesa.numero)
                    st.success("Pedido creado")
        else:
            if (not mesa.ocupada) and st.button("Nuevo pedido App", key="nuevo_pedido_app"):
                mesa.cliente = Cliente(1)
                mesa.ocupada = True
                r.crear_pedido(99)
                st.success("Pedido App creado")

        pedido = mesa.pedido_actual
        st.markdown("#### Items")
        colf1, colf2 = st.columns([1,2])
        with colf1:
            st.session_state.filtro_tipo = st.selectbox("Tipo", TIPOS, index=TIPOS.index(st.session_state.filtro_tipo))
            st.session_state.busqueda = st.text_input("Buscar", value=st.session_state.busqueda)
            items_tipo = get_items_by_type(st.session_state.filtro_tipo)
            if st.session_state.busqueda:
                items_tipo = [i for i in items_tipo if st.session_state.busqueda.lower() in i.nombre.lower()]
            nombres = [i.nombre for i in items_tipo]
            if nombres:
                elegido = st.selectbox("Item", nombres, key="item_elegido")
                if pedido and st.button("Agregar", key="btn_agregar_item"):
                    item = r.obtener_item_menu(st.session_state.filtro_tipo, elegido)
                    if item:
                        pedido.agregar_item(item)
                        st.success("Agregado")
            else:
                st.info("Sin items")
        with colf2:
            if pedido:
                st.text_area("Resumen", value=resumen_pedido(pedido), height=220, key="resumen_area")
            else:
                st.write("No hay pedido.")

        col_actions = st.columns(3)
        if pedido and col_actions[0].button("Liberar mesa", key="liberar_mesa"):
            if mesa.numero == 99:
                mesa.pedido_actual = None
                mesa.cliente = None
                mesa.ocupada = False
            else:
                r.liberar_mesa(mesa.numero)
            st.success("Mesa liberada")
        if pedido and col_actions[1].button("Marcar 'Pendiente'", key="to_pend"):
            pedido.cambiar_estado("Pendiente")
        if pedido and col_actions[2].button("Marcar 'En preparación'", key="to_prep"):
            pedido.cambiar_estado("En preparacion")

# ------------- Tab Cocina -------------
with tabs[1]:
    st.subheader("Cocina")
    activos = [p for p in r.pedidos_activos if p and len(sum(p.items.values(), [])) > 0]
    if not activos:
        st.info("No hay pedidos en cocina.")
    for p in activos:
        c1, c2, c3, c4 = st.columns([2,3,2,2])
        with c1:
            st.markdown(f"**{mesa_label(p.mesa)}**")
            st.write(p.estado)
        with c2:
            with st.expander("Detalles", expanded=False):
                st.code(resumen_pedido(p))
        with c3:
            if p.estado == "Pendiente" and st.button("→ En preparación", key=f"prep_{id(p)}"):
                p.cambiar_estado("En preparacion")
        with c4:
            if p.estado == "En preparacion" and st.button("→ Listo", key=f"listo_{id(p)}"):
                p.cambiar_estado("Listo")
    st.caption("Refresca la página para actualizar estados (o activa recarga automática del navegador).")

# ------------- Tab Caja -------------
with tabs[2]:
    st.subheader("Caja")
    cobrables = [p for p in r.pedidos_activos if p and p.estado in ("Listo", "En preparacion", "Pendiente") and len(sum(p.items.values(), [])) > 0]
    if not cobrables:
        st.info("No hay pedidos activos.")
    for p in cobrables:
        total = p.calcular_total()
        col1, col2, col3 = st.columns([2,4,1])
        with col1:
            st.markdown(f"**{mesa_label(p.mesa)}**")
            st.write(f"Estado: {p.estado}")
            st.write(f"Total: ${total:.2f}")
        with col2:
            st.code(resumen_pedido(p))
        with col3:
            if st.button("Pago", key=f"pago_{id(p)}"):
                # Liberar mesa y quitar pedido
                if p in r.pedidos_activos:
                    r.pedidos_activos.remove(p)
                if p.mesa and p.mesa.numero != 99:
                    r.liberar_mesa(p.mesa.numero)
                else:
                    p.mesa.pedido_actual = None
                    p.mesa.cliente = None
                    p.mesa.ocupada = False
                st.success("Pago registrado")

# ------------- Tab Admin Menú -------------
with tabs[3]:
    st.subheader("Administración de Menú")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("### Agregar Item")
        tipo_new = st.selectbox("Tipo", TIPOS, key="adm_tipo_add")
        nombre_new = st.text_input("Nombre", key="adm_nombre")
        precio_new = st.number_input("Precio", min_value=0.0, format="%.2f", key="adm_precio")
        if st.button("Agregar", key="adm_add_btn"):
            if nombre_new and precio_new > 0:
                if tipo_new == "Entrada":
                    r.menu.agregar_entrada(nombre_new, precio_new)
                elif tipo_new == "Plato Principal":
                    r.menu.agregar_platoprincipal(nombre_new, precio_new)
                elif tipo_new == "Postre":
                    r.menu.agregar_postre(nombre_new, precio_new)
                elif tipo_new == "Bebida":
                    r.menu.agregar_bebida(nombre_new, precio_new)
                st.success("Item agregado")
            else:
                st.error("Datos inválidos")
    with col_b:
        st.markdown("### Eliminar Item")
        tipo_del = st.selectbox("Tipo a listar", TIPOS, key="adm_tipo_del")
        items_del = get_items_by_type(tipo_del)
        if items_del:
            nombre_del = st.selectbox("Item", [it.nombre for it in items_del], key="adm_item_del")
            if st.button("Eliminar", key="adm_del_btn"):
                r.menu.eliminar_item(tipo_del, nombre_del)
                st.warning("Item eliminado")
        else:
            st.info("No hay items en esa categoría")

st.caption("UI Streamlit – reemplaza la versión previa en Flet. Los datos son in-memory por sesión.")

def _debug_state():
    if st.sidebar.checkbox("Mostrar debug", value=False):
        st.sidebar.write({
            "mesas": [(m.numero, m.ocupada) for m in r.mesas],
            "pedidos_activos": len(r.pedidos_activos),
            "mesa_sel": st.session_state.mesa_sel,
        })

_debug_state()