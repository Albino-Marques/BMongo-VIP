# import threading
# import customtkinter as ctk
# from database_validator.database_validator import DatabaseValidator
# from bson import ObjectId
#
# class FindIds:
#     def __init__(self, db_connection, log):
#         self.db = db_connection.db
#         self.log = log
#         self.running = True
#         self.database_validator = DatabaseValidator(db_connection, log)
#
#     def run_find_ids(self, search_id):
#
#         if not self.database_validator.connect_to_db():
#             self.log.see(ctk.END)
#             return
#
#         if not self.running:
#             self.log.see(ctk.END)
#             return
#
#         self.log.insert(ctk.END, f"Buscando o ObjectId {search_id} em todas as coleções...\n")
#         all_collections = self.db.list_collection_names()
#         for collection_name in all_collections:
#             collection = self.db[collection_name]
#             for document in collection.find():
#                 doc_array = [{'key': key, 'value': value} for key, value in document.items()]
#                 for pair in doc_array:
#                     if isinstance(pair['value'], ObjectId) and str(pair['value']) == search_id:
#                         self.log.insert(ctk.END, f"Encontrado na coleção {collection_name}, campo {pair['key']}\n")
#
#     def cancel_operation(self):
#         self.running = False
#
#     def run_thread_find_ids(self, search_id):
#         thread = threading.Thread(target=self.run_find_ids, args=(search_id,))
#         thread.start()


from config.config import running_operations, running_operations_lock, cancel_event
from database_validator.database_validator import DatabaseValidator
from bson import ObjectId
import threading
import customtkinter as ctk

class FindIds:
    def __init__(self, db_connection, log):
        self.db = db_connection.db
        self.log = log
        self.database_validator = DatabaseValidator(db_connection, log)

    def run_find_ids(self, search_id):
        if not self.database_validator.connect_to_db():
            self.log.see(ctk.END)
            return

        with running_operations_lock:
            if not running_operations:
                self.log.insert(ctk.END, "Operação cancelada.\n")
                self.log.see(ctk.END)
                return

        self.log.insert(ctk.END, f"Buscando o ObjectId {search_id} em todas as coleções...\n")
        all_collections = self.db.list_collection_names()

        for collection_name in all_collections:
            collection = self.db[collection_name]
            if cancel_event.is_set():
                self.log.insert(ctk.END)
                self.log.see(ctk.END)
                return
            for document in collection.find():
                doc_array = [{'key': key, 'value': value} for key, value in document.items()]
                for pair in doc_array:
                    if isinstance(pair['value'], ObjectId) and str(pair['value']) == search_id:
                        self.log.insert(ctk.END, f"Encontrado na coleção {collection_name}, campo {pair['key']}\n")
                        self.log.see(ctk.END)

    def cancel_operation(self):
        with running_operations_lock:
            global running_operations
            running_operations = False

    def run_thread_find_ids(self, search_id):
        thread = threading.Thread(target=self.run_find_ids, args=(search_id,))
        thread.start()
