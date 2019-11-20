"""Утиліта що форматує HTML файли за вказаними шаблонами

"""

__version__ = "0.0.7"

from os import system
from os import walk
from os import makedirs
from os import listdir
from os.path import exists
from os.path import join
from json import dump
from json import load
from re import search

from typing import List


class Template:
    """Клас шаблону форматування
    
    Attributes
    ----------
    name : str
        Ім'я шаблону
    TEMPLATES_DIR : str
        Шлях до каталогу з шаблонами

    Methods
    -------
    create_template(name: str) : Template
        Метод для створення нових шаблонів
    save()
        Метод для зберігання шаблонів
    get_templates() : List[str]:
        Метод для отримання доступних шаблонів
    load(name: str) : Template:
        Метод для завантаження шаблонів
    """

    TEMPLATES_DIR: str = 'templates'

    def __init__(self):
        self.name: str = 'default'

    @classmethod
    def create_template(cls, name: str) -> 'Template':
        """Метод для створення нових шаблонів
        
        Parameters
        ----------
        name : str
            Ім'я нового шаблону
        """

        new_template = cls()
        new_template.name = name
        new_template.save()

        return new_template

    def save(self):
        """Метод для зберігання шаблонів"""

        makedirs(self.TEMPLATES_DIR, exist_ok=True)

        data = {
            'name': self.name,
        }

        with open(join(self.TEMPLATES_DIR, self.name + '.json'), 'w') as file:
            dump(data, file)

    @staticmethod
    def get_templates() -> List[str]:
        """Метод для отримання доступних шаблонів
        
        Returns
        -------
        templates : List[str]
            Назви шаблонів які доступні для програми
        """

        templates: List[str] = ['default']

        for filename in listdir(Template.TEMPLATES_DIR):
            if filename.count('.') == 1:
                name, extension = filename.split('.')
                if extension == 'json':
                    templates.append(name)
        
        return templates

    @classmethod
    def load(cls, name: str) -> 'Template':
        """Метод для завантаження шаблонів

        Returns
        -------
        template : 'Template'
            Об'єкт цього класу, завантажений з файлу
        """

        with open(join(cls.TEMPLATES_DIR, name + '.json'), 'r') as file:
            data: dict = load(file)

        template = Template()

        template.name = data.get('name', template.name)

        return template


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
    _create_template_menu(self):
        Відображає в консолі меню для створення шаблону
    _select_template_menu(self):
        Відображає в консолі меню для вибору шаблону
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
            elif command == '1':
                self._select_template_menu()
            elif command == '3':
                self._create_template_menu()
            else:
                print('Невірна команда.')
                input('\nНатисніть Enter щоби продовжити.')
                continue

    def _create_template_menu(self):
        """Відображає в консолі меню для створення шаблону"""

        while True:
            system('cls')
            print('HTML Linter v{}'.format(__version__))

            name = input(('\nВведить назву шаблону, або нічого щоб '
                          'повернутися до попереднього меню: ')).strip()

            if not name:
                break
            
            search_match = search(r'[^ `\w]', name)
            if search_match:
                print('Ім`я повинно містити тільки літери, '
                      'числа, пробіл або апостроф.')

                input('\nНатисніть Enter щоби продовжити.')
                continue

            self.current_template = Template.create_template(name)
            break

    def _select_template_menu(self):
        """Відображає в консолі меню для вибору шаблону"""

        while True:
            system('cls')
            print('HTML Linter v{}'.format(__version__))

            templates = Template.get_templates()
            for num, template in enumerate(templates, start=1):
                print('{}. {}'.format(num, template))

            print('\n0. Назад')

            try:
                command = int(input('\nВиберіть шаблон: ').strip())
            except ValueError:
                print('Невірна команда.')

                input('\nНатисніть Enter щоби продовжити.')
                continue

            if command == 0:
                break
            elif 1 <= command <= len(templates):
                self.current_template = Template.load(templates[command - 1])
                break
            else:
                print('Невірна команда.')

                input('\nНатисніть Enter щоби продовжити.')
                continue


if __name__ == "__main__":
    linter = Linter()
    linter.start_menu()
