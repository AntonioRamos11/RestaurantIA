class Item_menu():
    def __init__(self, nombre, precio, cantidad=1):  
        self.nombre = nombre
        self.precio = precio
        self.cantidad = cantidad
       
    def calcular_subtotal(self):
        return self.precio * self.cantidad
       
class Entrada(Item_menu):
    def __init__(self, nombre, precio, cantidad=1):  
        super().__init__(nombre, precio, cantidad)
        self.tipo = "Entrada"
       
class PlatoPrincipal(Item_menu):
    def __init__(self, nombre, precio, cantidad=1):  
        super().__init__(nombre, precio, cantidad)
        self.tipo = "Plato Principal"
       
class Postre(Item_menu):
    def __init__(self, nombre, precio, cantidad=1):  
        super().__init__(nombre, precio, cantidad)
        self.tipo = "Postre"
       
class Bebida(Item_menu):
    def __init__(self, nombre, precio, cantidad=1):  
        super().__init__(nombre, precio, cantidad)
        self.tipo = "Bebida"
       
class Menu:
    def __init__(self):  
        self.entradas = []
        self.platos_principales = []
        self.postres = []
        self.bebidas = []
   
    def agregar_entrada(self, nombre, precio):
        entrada = Entrada(nombre, precio)
        self.entradas.append(entrada)
       
    def agregar_platoprincipal(self, nombre, precio):
        plato_principal = PlatoPrincipal(nombre, precio)
        self.platos_principales.append(plato_principal)
        return plato_principal
   
    def agregar_postre(self, nombre, precio):
        postre = Postre(nombre, precio)
        self.postres.append(postre)
       
    def agregar_bebida(self, nombre, precio):  # CORREGIDO: removido self extra
        bebida = Bebida(nombre, precio)
        self.bebidas.append(bebida)
       
    def eliminar_item(self, tipo, nombre):
        if tipo == "Entrada":
            items = self.entradas
        elif tipo == "Plato Principal":
            items = self.platos_principales
        elif tipo == "Postre":
            items = self.postres
        elif tipo == "Bebida":
            items = self.bebidas
        else:
            return False
       
        for item in items[:]:
            if item.nombre == nombre:
                items.remove(item)
                return True
        return False
   
    def eliminar_entrada(self, nombre):
        return self.eliminar_item("Entrada", nombre)
   
    def eliminar_platoprincipal(self, nombre):
        return self.eliminar_item("Plato Principal", nombre)
   
    def eliminar_postre(self, nombre):
        return self.eliminar_item("Postre", nombre)
   
    def eliminar_bebida(self, nombre):
        return self.eliminar_item("Bebida", nombre)
   
    def obtener_item(self, tipo, nombre):
        if tipo == "Entrada":
            items = self.entradas
        elif tipo == "Plato Principal":
            items = self.platos_principales
        elif tipo == "Postre":
            items = self.postres
        elif tipo == "Bebida":
            items = self.bebidas
        else:
            return None
        
        for item in items:
            if item.nombre == nombre:
                return item
        return None
          
                
            
        
        
    
    
        
        
