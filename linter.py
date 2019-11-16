"""Утиліта що форматує HTML файли за вказаними шаблонами

"""

__version__ = "0.0.3"

from os import system
from os import walk
from os.path import exists
from os.path import join


class Html:
    """Класс який перевіряє та форматує Html файли
    
    Methods
    -------
    check(path: str)
        Перевіряє html файл
    """
    
    @classmethod
    def check(cls, path):
        """Перевіряє html файл"""
        pass


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
            system('cls')
            print('HTML Linter v{}'.format(__version__))
            print('1.Перевірити каталог з Html файлами')
            print('0.Вихід')

            try:
                command = int(input('Введіть номер команди: '))
            except ValueError:
                print('Введіть НОМЕР команди.')
                input('\nНатисніть Enter щоби продовжити.')
                continue
            
            if command == 0:
                exit()
            elif command == 1:
                self._check_folder_menu()
            else:
                print('Невірна команда.')
                input('\nНатисніть Enter щоби продовжити.')
                continue

    def _check_folder_menu(self):
        """Відображає в консолі меню для вибору каталогу з Html файлами"""

        while True:
            system('cls')
            path = input('Введіть шлях до каталогу: ')
            
            if not exists(path):
                print('Шлях "{}" не знайдено.')
                input('\nНатисніть Enter щоби продовжити.')
                continue

            self._check_folder(path)
            break

    def _check_folder(self, path: str):
        """Перевіряє вибраний каталог з Html файлами
        
        Parameters
        ----------
        path : str
            Шлях до каталогу який потрібно перевірити
        
        """

        html_files_count = 0
        for root, _, files in walk(path):
            for file in files:
                if file.__contains__('.') and file.split('.')[1] == 'html':
                    Html.check(join(root, file))
                    html_files_count += 1

        print('Перевірено {} файлів'.format(html_files_count))
        input('\nНатисніть Enter щоби продовжити.')


if __name__ == "__main__":
    linter = Linter()
    linter.start_menu()
