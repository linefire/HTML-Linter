"""Утиліта що форматує HTML файли за вказаними шаблонами

"""

__version__ = "0.0.2"

from os import system


class Linter:
    """Головний клас утиліти
    
    Клас який керує шаблонами, настройками та форматуванням
    
    Methods
    -------
    start_menu()
        Відображає в консолі головне меню
    """

    def start_menu(self):
        """Відображає в консолі головне меню"""
        while True:
            system("cls")
            print("HTML Linter v{}".format(__version__))
            print("0.Вихід")

            try:
                command = int(input("Введіть номер команди: "))
            except ValueError:
                print("Введіть НОМЕР команди.")
                input("Натисніть Enter щоби продовжити.")
                continue
            
            if command == 0:
                exit()
            else:
                print("Невірна команда.")
                input("Натисніть Enter щоби продовжити.")
                continue
            

if __name__ == "__main__":
    linter = Linter()
    linter.start_menu()
