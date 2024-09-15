from werkzeug.security import generate_password_hash

class Usuario:
    def __init__(self, nombreUsuario, correoUsuario, contrasenaUsuario, estadoUsuario, rolUsuario):
        self.set_nombreUsuario(nombreUsuario)
        self.set_correoUsuario(correoUsuario)
        self.encryptPass(contrasenaUsuario)
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

    def encryptPass(self, contrasena):
        return self.set_contrasenaUsuario(generate_password_hash(contrasena))

    def toDBCollection(self):
        return {
            'nombreUsuario': self.get_nombreUsuario(),
            'correoUsuario': self.get_correoUsuario(),
            'contrasenaUsuario': self.get_contrasenaUsuario(),
            'estadoUsuario': self.get_estadoUsuario(),
            'rolUsuario': self.get_rolUsuario()
        }

class SitiosTuristicos:
    def __init__(self, nombreSitiosTuristicos, descripcionSitiosTuristicos, altitudSitiosTuristicos, latitudSitiosTuristicos, horariosSitiosTuristicos, estadoSitiosTuristicos, tipoSitiosTuristicos, image_id):
        self.set_nombreSitiosTuristicos(nombreSitiosTuristicos)
        self.set_descripcionSitiosTuristicos(descripcionSitiosTuristicos)
        self.set_estadoSitiosTuristicos(estadoSitiosTuristicos)
        self.set_altitudSitiosTuristicos(altitudSitiosTuristicos)
        self.set_latitudSitiosTuristicos(latitudSitiosTuristicos)
        self.set_horariosSitiosTuristicos(horariosSitiosTuristicos)
        self.set_tipoSitiosTuristicos(tipoSitiosTuristicos)
        self.__image_id = image_id
    
    #Setters
    def set_nombreSitiosTuristicos(self, nombreSitiosTuristicos):
        self.__nombreSitiosTuristicos = nombreSitiosTuristicos
    def set_descripcionSitiosTuristicos(self, descripcionSitiosTuristicos):
        self.__descripcionSitiosTuristicos = descripcionSitiosTuristicos
    def set_altitudSitiosTuristicos(self, altitudSitiosTuristicos):
        self.__altitudSitiosTuristicos = altitudSitiosTuristicos
    def set_latitudSitiosTuristicos(self, latitudSitiosTuristicos):
        self.__latitudSitiosTuristicos = latitudSitiosTuristicos
    def set_horariosSitiosTuristicos(self, horariosSitiosTuristicos):
        self.__horariosSitiosTuristicos = horariosSitiosTuristicos
    def set_estadoSitiosTuristicos(self, estadoSitiosTuristicos):
        self.__estadoSitiosTuristicos = estadoSitiosTuristicos
    def set_tipoSitiosTuristicos(self, tipoSitiosTuristicos):
        self.__tipoSitiosTuristicos = tipoSitiosTuristicos

    #Getters
    def get_nombreSitiosTuristicos(self):
        return self.__nombreSitiosTuristicos
    def get_descripcionSitiosTuristicos(self):
        return self.__descripcionSitiosTuristicos
    def get_altitudSitiosTuristicos(self):
        return self.__altitudSitiosTuristicos
    def get_latitudSitiosTuristicos(self):
        return self.__latitudSitiosTuristicos
    def get_horariosSitiosTuristicos(self):
        return self.__horariosSitiosTuristicos
    def get_estadoSitiosTuristicos(self):
        return self.__estadoSitiosTuristicos
    def get_tipoSitiosTuristicos(self):
        return self.__tipoSitiosTuristicos

    def toDBCollection(self):
        return{
            'nombreSitiosTuristicos': self.get_nombreSitiosTuristicos(),
            'descripcionSitiosTuristicos': self.get_descripcionSitiosTuristicos(),
            'altitudSitiosTuristicos': self.get_altitudSitiosTuristicos(),
            'latitudSitiosTuristicos': self.get_latitudSitiosTuristicos(),
            'horariosSitiosTuristicos': self.get_horariosSitiosTuristicos(),
            'estadoSitiosTuristicos': self.get_estadoSitiosTuristicos(),
            'tipoSitiosTuristicos': self.get_tipoSitiosTuristicos(),
            'image_id': self.__image_id
        }