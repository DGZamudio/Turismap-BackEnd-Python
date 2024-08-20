class Usuario:
    def __init__(self, nombreUsuario, correoUsuario, contrasenaUsuario, estadoUsuario, rolUsuario):
        self.set_nombreUsuario(nombreUsuario)
        self.set_correoUsuario(correoUsuario)
        self.set_contrasenaUsuario(contrasenaUsuario)
        self.set_estadoUsuario(estadoUsuario)
        self.set_rolUsuario(rolUsuario)

    # Setters
    def set_nombreUsuario(self, name):
        self.__nombreUsuario = name

    def set_correoUsuario(self, email):
        self.__correoUsuario = email

    def set_contrasenaUsuario(self, password):
        self.__contrasenaUsuario = password

    def set_estadoUsuario(self, state):
        self.__estadoUsuario = state

    def set_rolUsuario(self, role):
        self.__rolUsuario = role

    # Getters
    def get_nombreUsuario(self):
        return self.__nombreUsuario

    def get_correoUsuario(self):
        return self.__correoUsuario

    def get_contrasenaUsuario(self):
        return self.__contrasenaUsuario

    def get_estadoUsuario(self):
        return self.__estadoUsuario

    def get_rolUsuario(self):
        return self.__rolUsuario

    def toDBCollection(self):
        return {
            'nombreUsuario': self.get_nombreUsuario(),
            'correoUsuario': self.get_correoUsuario(),
            'contrasenaUsuario': self.get_contrasenaUsuario(),
            'estadoUsuario': self.get_estadoUsuario(),
            'rolUsuario': self.get_rolUsuario()
        }
