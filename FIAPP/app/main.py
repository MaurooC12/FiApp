from database.firebase_config import init_firebase
from database.auth_service import AuthService
from presentation.viewmodel import ViewModel
from ui.console import ConsoleUI


def main():
    print("=== FIAPP - Sistema de Administración para Tenderos ===\n")

    init_firebase()
    auth_service = AuthService()
    view_model = ViewModel(auth_service)
    ui = ConsoleUI(view_model)

    ui.run()


if __name__ == "__main__":
    main()
