class Mesa:
    def __init__(self, numero, tamaño):  # CORREGIDO: __init__
        self.numero = numero
        self.tamaño = tamaño
        self.ocupada = False
        self.cliente = None
        self.pedido_actual = None
       
    def asignar_cliente(self, cliente):
        if cliente.tamaño_grupo <= self.tamaño:
            self.cliente = cliente
            self.ocupada = True
            return True
        return False
   
    def liberar(self):
        self.cliente = None
        self.ocupada = False
        self.pedido_actual = None
       
    def tiene_pedido_activo(self):
        return self.pedido_actual is not None
        
        
        
        
    
    