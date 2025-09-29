from Menu import Item_menu

class Pedido:
    def __init__(self, mesa):  
        self.mesa = mesa
        self.items = {
            "entradas": [],
            "platos_principales": [],
            "postres": [],
            "bebidas": [],
        }
        self.estado = "Pendiente"
       
    def agregar_item(self, item):
        if isinstance(item, Item_menu):  
            if item.tipo == "Entrada":
                self.items["entradas"].append(item) 
               
            elif item.tipo == "Plato Principal":
                self.items["platos_principales"].append(item)
               
            elif item.tipo == "Postre":
                self.items["postres"].append(item)
           
            elif item.tipo == "Bebida":
                self.items["bebidas"].append(item)
               
    def calcular_total(self):
        total = 0
        for categoria in self.items.values():
            for item in categoria:
                total += item.calcular_subtotal()
        return round(total, 2)
   
    def cambiar_estado(self, nuevo_estado):
        estados_validos = ["Pendiente", "En preparacion", "Listo", "Entregado"]
        if nuevo_estado in estados_validos:
            self.estado = nuevo_estado
            return True
        return False
   
    def obtener_resumen(self):
        resumen = []
        for categoria, items in self.items.items():
            if items:
                resumen.append(f"\n{categoria.replace('_', ' ').title()}:")
                for item in items:
                    resumen.append(f"- {item.nombre} x{item.cantidad}: ${item.calcular_subtotal():.2f}")
       
        resumen.append(f"\nTotal: ${self.calcular_total():.2f}")
        return "\n".join(resumen)
                    

                
        
