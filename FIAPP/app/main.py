from database.firebase_config import init_firebase
from database.auth_service import AuthService
from presentation.presentation import ViewModel
from ui.tkinter_ui import TkinterUI


def main():
    init_firebase()
    auth_service = AuthService()
    view_model = ViewModel(auth_service)
    ui = TkinterUI(view_model)

    ui.run()


if __name__ == "__main__":
    main()
