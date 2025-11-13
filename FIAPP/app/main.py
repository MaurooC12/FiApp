from database.firebase_config import init_firebase
from database.auth_service import AuthService
from presentation.presentation import ViewModel
from ui.tkinter_ui import App #Inicializar Vista Tkinter
#from ui.console import ConsoleUI # Inicializar Vista Consola

def main():
    init_firebase()
    auth_service = AuthService()
    view_model = ViewModel(auth_service)
    app = App(view_model)
    app.mainloop()
    #app = ConsoleUI(view_model)
    #app.run()

if __name__ == "__main__":
    main()
