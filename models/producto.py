class Producto:
    def __init__(self, nombre, descripcion, precio, image_url, url_producto):
        # Atributos privados
        self.__nombre = nombre
        self.__descripcion = descripcion
        self.__precio = precio
        self.__image_url = image_url
        self.__url_producto = url_producto

    # Getter para 'nombre' usando property
    @property
    def nombre(self):
        return self.__nombre

    # Setter para 'nombre'
    @nombre.setter
    def nombre(self, value):
        self.__nombre = value

    # Getter para 'descripcion' usando property
    @property
    def descripcion(self):
        return self.__descripcion

    # Setter para 'descripcion'
    @descripcion.setter
    def descripcion(self, value):
        self.__descripcion = value

    # Getter para 'precio' usando property
    @property
    def precio(self):
        return self.__precio

    # Setter para 'precio', con validación
    @precio.setter
    def precio(self, value):
        if value > 0:
            self.__precio = value
        else:
            raise ValueError("El precio debe ser mayor que 0.")

    # Getter para 'image_url' usando property
    @property
    def image_url(self):
        return self.__image_url

    # Setter para 'image_url'
    @image_url.setter
    def image_url(self, value):
        self.__image_url = value
        
    # Getter para 'url_producto' usando property
    @property
    def url_producto(self):
        return self.__url_producto

    # Setter para 'url_producto'
    @url_producto.setter
    def url_producto(self, value):
        self.__url_producto = value
