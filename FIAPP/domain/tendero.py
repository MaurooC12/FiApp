from domain.usuario import Usuario


class Tendero(Usuario):
    def __init__(self, uid, email):
        super().__init__(uid, email, "tendero")
        self.locales = []

    def agregar_local(self, local_id):
        self.locales.append(local_id)
