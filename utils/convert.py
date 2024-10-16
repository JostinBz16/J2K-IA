class Convert:
    @staticmethod
    def convert_price_to_float(precio_str):
        # Eliminar el símbolo de moneda y las comas
        precio = (
            precio_str.replace("$", "").replace(",", "").replace(".", "").strip()
        )  # Eliminar espacios en blanco

        try:
            # Convertir a float
            return float(precio)
        except ValueError:
            # Manejo de errores si la conversión falla
            print(f"Error al convertir '{precio}' a float.")
            return 0.0  # Retornar un valor predeterminado en caso de error
