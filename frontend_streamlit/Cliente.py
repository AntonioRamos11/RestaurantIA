class Cliente:
    _next_id = 1  # CORREGIDO: _next_id con guiones bajos simples
    
    def __init__(self, tamaño_grupo):  # CORREGIDO: __init__
        self.id = f"C{Cliente._next_id:03d}"  # Formato: C001, C002 ETC
        Cliente._next_id += 1
        self.tamaño_grupo = tamaño_grupo
        self.pedido_actual = None
       
    def asignar_pedido(self, pedido):
        self.pedido_actual = pedido
       
    def obtener_total_actual(self):
        return self.pedido_actual.calcular_total() if self.pedido_actual else 0
       
    def limpiar_pedido(self):
        self.pedido_actual = None
       
    @classmethod
    def reiniciar_contador(cls):
        cls._next_id = 1
        
        