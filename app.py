from mongo_functions.base_clean import BaseClean
from mongo_functions.base_create import BaseCreate
from mongo_functions.change_tributation_for_ncm import ChangeTributationForNCM
from mongo_functions.find_ids import FindIds
from mongo_functions.inactive_products import InactiveProducts
from mongo_functions.mei_able import MeiAble
from mongo_functions.movimentations_clean import MovimentationsClean
from database_validator.db_access import DBConnection
from database_validator.database_validator import DatabaseValidator
from config.config import running_operations_lock, cancel_event
from PIL import Image
from dotenv import load_dotenv
import os
import sys
import customtkinter as ctk
import threading

from mongo_functions.reg_digisat_clean import RegDigisatClean
from utils.util_modal import Modal

extDataDir = os.getcwd()
if getattr(sys, 'frozen', False):
    extDataDir = sys._MEIPASS

dotenv_path = os.path.join(extDataDir, '.env')
load_dotenv(dotenv_path)


class UserInterface:
    db_user = os.getenv("DB_USER")
    db_pass = os.getenv("DB_PASS")
    db_host = os.getenv("DB_HOST")

    db_connection = DBConnection(db_user, db_pass, db_host, 12220)

    def __init__(self):
        if getattr(sys, 'frozen', False):
            # Variáveis de compilação
            ico_path = UserInterface.resource_path('BMongo-VIP\\src\\logo.ico')
            background_path = UserInterface.resource_path('BMongo-VIP\\src\\background.png')
        else:
            # Vairáveis de desenvolvimento
            ico_path = UserInterface.resource_path('src\\logo.ico')
            background_path = UserInterface.resource_path('src\\background.png')

        ctk.set_appearance_mode("dark")
        self.app = ctk.CTk()
        self.app.geometry('950x750')
        self.app.title("BMongo - VIP")
        self.app.wm_iconbitmap(ico_path)
        self.app.config(takefocus=True)

        self.image_background = ctk.CTkImage(dark_image=Image.open(background_path))
        self.background_label = ctk.CTkLabel(self.app, image=self.image_background, text='')
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

        def update_background(*args):
            width = self.app.winfo_width()
            height = self.app.winfo_height()
            self.image_background.configure(size=(width, height))
            self.background_label.configure(image=self.image_background)

        self.app.bind("<Configure>", update_background)
        self.log = ctk.CTkTextbox(self.app, width=500)
        self.log.pack(pady=50)

        self.inactive_products = InactiveProducts(self.db_connection, self.log)
        self.mei_able = MeiAble(self.db_connection, self.log)
        self.find_ids = FindIds(self.db_connection, self.log)
        self.movimentations_clean = MovimentationsClean(self.db_connection, self.log)
        self.change_tributation_for_ncm = ChangeTributationForNCM(self.db_connection, self.log)
        self.base_clean = BaseClean(self.db_connection, self.log)
        self.base_create = BaseCreate(self.db_connection, self.log)
        self.reg_digisat_clean = RegDigisatClean(self.db_connection, self.log)
        self.database_validator = DatabaseValidator(self.db_connection, self.log)

        thread = threading.Thread(target=self.check_database_connection)
        thread.start()

        button_change_tributation_for_ncm = ctk.CTkButton(
            self.app, text="Alterar A tributação de Itens por NCM",
            command=lambda: self.open_modal("Digite os NCM's e o ID da Tributação",
                                                 self.run_change_tributation_for_ncm,
                                                 operation_type="run_change_tributation_for_ncm",
                                                 show_second_entry=True),
            fg_color='#f6882d',
            hover_color='#c86e24',
            text_color='white',
            border_color='#123f8c')
        button_change_tributation_for_ncm.pack(pady=10)

        button_reg_digisat_clean = ctk.CTkButton(
            self.app, text="Elimina os registro do Digisat do Windows",
            command=self.reg_digisat_clean.run_thread_reg_digisat_clean, fg_color='#f6882d', hover_color='#c86e24',
            text_color='white',
            border_color='#123f8c')
        button_reg_digisat_clean.pack(pady=10)

        button_inactive_products = ctk.CTkButton(
            self.app, text="Inativar produtos Zerados ou Negativos",
            command=self.inactive_products.run_thread_inactive_products, fg_color='#f6882d', hover_color='#c86e24',
            text_color='white',
            border_color='#123f8c')
        button_inactive_products.pack(pady=10)

        button_movimentations_clean = ctk.CTkButton(
            self.app, text="Limpa movimentações da Base",
            command=self.movimentations_clean.run_thread_movimentations_clean, fg_color='#f6882d',
            hover_color='#c86e24',
            text_color='white',
            border_color='#123f8c')
        button_movimentations_clean.pack(pady=10)

        button_mei_able = ctk.CTkButton(
            self.app, text="Permitir o ajuste de Estoque",
            command=self.mei_able.run_thread_mei_able, fg_color='#f6882d', hover_color='#c86e24',
            text_color='white',
            border_color='#123f8c')
        button_mei_able.pack(pady=10)

        button_base_create = ctk.CTkButton(
            self.app, text="Criar base nova zerada!",
            command=self.base_create.run_thread_base_creator, fg_color='#f6882d', hover_color='#c86e24',
            text_color='white',
            border_color='#123f8c')
        button_base_create.pack(pady=10)

        button_find_ids = ctk.CTkButton(
            self.app, text="Localiza ID's no banco",
            command=lambda: self.open_modal("Digite o ID a buscar", self.run_find_ids,
                                            operation_type="run_find_ids",
                                            show_second_entry=False),
            fg_color='#f6882d',
            hover_color='#c86e24',
            text_color='white',
            border_color='#123f8c')
        button_find_ids.pack(pady=10)

        button_base_clean = ctk.CTkButton(
            self.app, text="Zera a base atual",
            command=self.base_clean.run_thread_base_clean, fg_color='#f6882d', hover_color='#c86e24',
            text_color='white',
            border_color='#123f8c')
        button_base_clean.pack(pady=10)

        cancel_button = ctk.CTkButton(
            self.app, text="Cancelar Operação", command=self.cancel_operation, fg_color='#031229',
            hover_color='#010c1c',
            text_color='white', border_color='#123f8c')
        cancel_button.pack(pady=25)

    def cancel_operation(self):
        with running_operations_lock:
            global running_operations
            running_operations = False
        cancel_event.set()
        self.log.insert(ctk.END, "Todas as operações foram canceladas.\n")
        self.log.see(ctk.END)
        self.app.after(1000, self.reset_operation_state)

    @staticmethod
    def reset_operation_state():
        with running_operations_lock:
            global running_operations
            running_operations = True
        cancel_event.clear()

    @classmethod
    def resource_path(cls, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)


    def open_modal(self, title, callback, operation_type=None, show_second_entry=False):
        modal = Modal(title, callback, operation_type=operation_type, show_second_entry=show_second_entry)

    def run_find_ids(self, search_id):
        self.find_ids.run_thread_find_ids(search_id)

    def run_change_tributation_for_ncm(self, ncms, tributation_id):
        self.change_tributation_for_ncm.run_thread_change_tributation_for_ncm(ncms, tributation_id)

    def check_database_connection(self):
        try:
            if not self.database_validator.connect_to_db():
                return
        except Exception as e:
            self.log.insert(ctk.END, str(e) + "\n")
            return

    def run(self):
        self.app.mainloop()


if __name__ == "__main__":
    user_interface = UserInterface()
    user_interface.run()
