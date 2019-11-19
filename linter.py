"""Утиліта що форматує HTML файли за вказаними шаблонами

"""

__version__ = "0.0.5"

from os import system
from os import walk
from os.path import exists
from os.path import join


class Template:
    """Клас шаблону форматування
    
    Attributes
    ----------
    name : str
        Ім'я шаблону
    """

    def __init__(self):
        self.name = 'default'


class Html:
    """Клас який перевіряє та форматує Html файли
    
    Methods
    -------
    check(path: str, template: Template)
        Перевіряє html файл за вказаним шаблоном
    """
    
    @classmethod
    def check(cls, path: str, template: Template):
        """Перевіряє html файл за вказаним шаблоном
        
        Parameters
        ----------
        path : str
            Шлях до файлу
        template : Template
            Шаблон перевірки
        """
        pass


class Linter:
    """Головний клас утиліти
    
    Клас який керує шаблонами, настройками та форматуванням
    
    Attributes
    ----------
    current_template : Template
        Активний шаблон

    Methods
    -------
    start_menu()
        Відображає в консолі головне меню
    _check_folder_menu()
        Відображає в консолі меню для вибору каталогу з Html файлами
    _check_folder(path: str)
        Перевіряє вибраний каталог з Html файлами
    _templates_menu()
        Відображає в консолі меню для операції з шаблонами
    """

    def __init__(self):
        self.current_template: Template = Template()

    def start_menu(self):
        """Відображає в консолі головне меню"""

        while True:
            system('cls')
            print('HTML Linter v{}'.format(__version__))
            print('Вибраний шаблон: {}'.format(self.current_template.name))
            print('\n1.Перевірити каталог з Html файлами')
            print('2.Шаблони')
            print('\n0.Вихід')

            command = input('\nВиберіть пункт: ').strip()
            
            if command == '0':
                exit()
            elif command == '1':
                self._check_folder_menu()
            elif command == '2':
                self._templates_menu()
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
                    Html.check(join(root, file), self.current_template)
                    html_files_count += 1

        print('Перевірено {} файлів'.format(html_files_count))
        input('\nНатисніть Enter щоби продовжити.')

    def _templates_menu(self):
        """Відображає в консолі меню для операції з шаблонами"""

        while True:
            system('cls')
            print('HTML Linter v{}'.format(__version__))
            print('Вибраний шаблон: {}'.format(self.current_template.name))
            print('\n1. Вибрати шаблон')
            print('2. Редагувати шаблон')
            print('3. Створити шаблон')
            print('4. Видалити шаблон')
            print('\n0. Назад')

            command = input('\nВиберіть пункт: ').strip()

            if command == '0':
                break
            else:
                print('Невірна команда.')
                input('\nНатисніть Enter щоби продовжити.')
                continue

if __name__ == "__main__":
    linter = Linter()
    linter.start_menu()
