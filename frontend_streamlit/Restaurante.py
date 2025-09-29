from Menu import Menu
from Pedido import Pedido

class Restaurante:
    def __init__(self):  
        self.mesas = []
        self.clientes = []
        self.pedidos_activos = []
        self.menu = Menu()
        self._inicializar_menu()
       
    def _inicializar_menu(self):  # CORREGIDO: _inicializar_menu
        # Agrega algunas entradas
        self.menu.agregar_entrada("Ensalada César", 5.99)
        self.menu.agregar_entrada("Sopa de Tomate", 4.99)
       
        # Agrega platos principales
        self.menu.agregar_platoprincipal("Pollo a la Parrilla", 12.99)
        self.menu.agregar_platoprincipal("Pasta Alfredo", 11.99)
       
        # Agrega postres
        self.menu.agregar_postre("Tiramisú", 6.49)
        self.menu.agregar_postre("Helado", 4.49)
       
        # Agrega bebidas
        self.menu.agregar_bebida("Coca-Cola", 1.99)
        self.menu.agregar_bebida("Agua Mineral", 1.49)
       
    def agregar_mesa(self, mesa):
        self.mesas.append(mesa)
        return f"Mesa {mesa.numero} (Capacidad: {mesa.tamaño}) agregada exitosamente"
   
    def asignar_cliente_a_mesa(self, cliente, numero_mesa):
        mesa = self.buscar_mesa(numero_mesa)
        if not mesa:
            return "Mesa no encontrada"
        if mesa.ocupada:
            return "Mesa no disponible"
        if cliente.tamaño_grupo > mesa.tamaño:
            return f"Grupo demasiado grande para la mesa(capacidad maxima: {mesa.tamaño})"
        if mesa.asignar_cliente(cliente):
            self.clientes.append(cliente)
            return f"Cliente {cliente.id} asignado a mesa {numero_mesa}"
        return "No se pudo asignar el cliente a la mesa"
       
    def buscar_mesa(self, numero_mesa):  
        for mesa in self.mesas:
            if mesa.numero == numero_mesa:
                return mesa
        return None
   
    def crear_pedido(self, numero_mesa):
        mesa = self.buscar_mesa(numero_mesa)
        if mesa and mesa.ocupada:
            pedido = Pedido(mesa)
            self.pedidos_activos.append(pedido)
            mesa.pedido_actual = pedido
            mesa.cliente.asignar_pedido(pedido)
            return pedido
        return None
   
    def liberar_mesa(self, numero_mesa):
        mesa = self.buscar_mesa(numero_mesa)
        if mesa:
            cliente = mesa.cliente
            if cliente:
                cliente.limpiar_pedido()
                if cliente in self.clientes:
                    self.clientes.remove(cliente)
                if mesa.pedido_actual in self.pedidos_activos:
                    self.pedidos_activos.remove(mesa.pedido_actual)
                   
            mesa.liberar()
            return f"Mesa {numero_mesa} liberada"
        return "Mesa no encontrada"
   
    def obtener_item_menu(self, tipo, nombre):
        return self.menu.obtener_item(tipo, nombre)