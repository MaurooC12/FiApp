from domain.usuario import Usuario


class Cliente(Usuario):
    def __init__(self, uid, email):
        super().__init__(uid, email, "cliente")
        self.deuda = 0.0

    def actualizar_deuda(self, monto):
        self.deuda += monto
