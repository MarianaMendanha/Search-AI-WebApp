from multiprocessing.managers import BaseManager

class MyManager(BaseManager):
    pass

# Registrar o dicionário para ser acessado remotamente
MyManager.register('get_dict')

def client_access():
    # Conecta ao servidor BaseManager
    manager = MyManager(address=('127.0.0.1', 5002), authkey=b'password')
    manager.connect()  # Conecta ao servidor

    # Acessa o dicionário remoto
    shared_dict = manager.get_dict()

    # Insere um novo valor no dicionário
    shared_dict['key'] = 'value'
    print(f"O valor de 'key' é: {shared_dict['key']}")

if __name__ == '__main__':
    client_access()
