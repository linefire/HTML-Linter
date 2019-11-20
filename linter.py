"""Утиліта що форматує HTML файли за вказаними шаблонами

"""

__version__ = "0.0.8"

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
    use_tab_character : bool
        Застосовувати табуляцію замість пробілів?
    smart_tab : bool
        Застосовувати розумну табуляцію?
    indent : int
        Кількість пробілів на кожному рівні вложення
    continuation_indend : int
        Кількість пробілів у кожному тегу після indent
    keep_indents_on_empty_lines : bool
        Зберігати пробіли у порожніх строчках?
    hard_wrap_column : int
        Стовбчик після якого потрібно переносити код
    keep_line_breaks : bool
        Переносити <br /> на нову строку?
    keep_line_breaks_in_text : bool
        Зберігати перенос строки у тексті тега?
    keep_blank_lines : int
        Кількість порожніх ліній які зберегаются
    wrap_attributes : int
        Варіанти переносу атрібутів:
            DO_NOT_WRAP - не переносити строки атрібутів.
            WRAP_IF_LONG - переносити якщо атрібут 
                           заходить за hard_wrap_column.
            CHOP_DOWN_IF_LONG - якщо атрібут виходить за hard_wrap_column,
                                всі атрібути переносятся на послідуючи 
                                строчки, один за одним.
            WRAP_ALWAYS - всі атрібути завжди переносятся на послідуючи 
                          строчки, один за одним.
    wrap_text : bool
        Переносити текст в тэгі? 
    align_attributes : bool
        Вирівнювати атрибути на послідуючих строках?
    align_text : bool
        Вирівнювати текст на послідуючих строках?
    keep_white_spaces : bool
        Заборонити операції з відступами?
    space_around_eq_in_attribute : bool
        Добавити відступи навколо знака "=" у атрібутах тега?
    space_after_tag_name : bool
        Добавити відступи після назви тега?
    space_in_empty_tag : bool
        Добавити відступ в тегах без атрібутів?
    insert_new_line_before : List[str]
        Вставити нову строку перед тегами у списку
    remove_new_line_before : List[str]
        Видалити нову строку перед тегами у списку
    dont_indent_child : List[str]
        Дочірні елементи списку тегів не довжни мати відступ
    dont_indent_child_tag_size : int
        Розмір тега у строчках, 
        дочірні елементи списку тегів не довжни мати відступ
    inline_elements : List[str]
        Дочірні теги які не повинні переноситися на нову строчку
    keep_white_space_inside : List[str]
        Зберігати відступи у тегах цього списку
    dont_break_if_inline_content : List[str]
        Не переносити теги якщо вони встроєні
    new_line_before_first_attr : bool
        Вставляти нову строку перед першим тегом, 
        якщо тег занімає більше ніж 1 строку?
    new_line_before_last_attr : bool
        Вставляти нову строку після останнього тега, 
        якщо тег занімає більше ніж 1 строку?
    generate_quote_marks : int
        Замінити лапки навколо атрібутів:
            SINGLE - Замінти на одинарні
            DOUBLE - Замінити на подвійні
            NONE - Не заміняти
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

    # Параметри для wrap_attributes
    DO_NOT_WRAP: int = 0
    WRAP_IF_LONG: int = 1
    CHOP_DOWN_IF_LONG: int = 2
    WRAP_ALWAYS: int = 3

    # Параметри для generate_quote_marks
    SINGLE: int = 0
    DOUBLE: int = 1
    NONE: int = 3

    def __init__(self):
        self.name: str = 'default'
        self.use_tab_character: bool = False
        self.smart_tab: bool = False
        self.indent: int = 4
        self.continuation_indend: int = 8
        self.keep_indents_on_empty_lines: bool = False
        self.hard_wrap_column: int = 120
        self.keep_line_breaks: bool = True
        self.keep_line_breaks_in_text: bool = True
        self.keep_blank_lines: int = 2
        self.wrap_attributes: int = self.WRAP_IF_LONG
        self.wrap_text: bool = True
        self.align_attributes: bool = True
        self.align_text: bool = False
        self.keep_white_spaces: bool = False
        self.space_around_eq_in_attribute: bool = False
        self.space_after_tag_name: bool = False
        self.space_in_empty_tag: bool = False
        self.insert_new_line_before: List[str] = ['body', 'div', 'p', 'form',
                                                  'h1', 'h2', 'h3']
        self.remove_new_line_before: List[str] = ['br']
        self.dont_indent_child: List[str] = ['html', 'body', 'thead',
                                                     'tbody', 'tfoot']
        self.dont_indent_child_tag_size: int = 0
        self.inline_elements: List[str] = ['a', 'abbr', 'acronym', 'b',
            'basefont', 'bdo', 'big', 'br', 'cite', 'cite', 'code', 'dfn',
            'em', 'font', 'i', 'img', 'input', 'kbd', 'label', 'q', 's',
            'samp', 'select', 'small', 'span', 'strike', 'strong', 'sub',
            'sup', 'textarea', 'tt', 'u', 'var']
        self.keep_white_space_inside: List[str] = ['span', 'pre', 'textarea']
        self.dont_break_if_inline_content: List[str] = ['title', 'h1', 'h2',
                                                'h3', 'h4', 'h5', 'h6', 'p']
        self.new_line_before_first_attr: bool = False
        self.new_line_before_last_attr: bool = False
        self.generate_quote_marks: int = self.DOUBLE

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
            'use_tab_character': self.use_tab_character,
            'smart_tab': self.smart_tab,
            'indent': self.indent,
            'continuation_indend': self.continuation_indend,
            'keep_indents_on_empty_lines': self.keep_indents_on_empty_lines,
            'hard_wrap_column': self.hard_wrap_column,
            'keep_line_breaks': self.keep_line_breaks,
            'keep_line_breaks_in_text': self.keep_line_breaks_in_text,
            'keep_blank_lines': self.keep_blank_lines,
            'wrap_attributes': self.wrap_attributes,
            'wrap_text': self.wrap_text,
            'align_attributes': self.align_attributes,
            'align_text': self.align_text,
            'keep_white_spaces': self.keep_white_spaces,
            'space_around_eq_in_attribute': self.space_around_eq_in_attribute,
            'self.space_after_tag_name': self.space_after_tag_name,
            'space_in_empty_tag': self.space_in_empty_tag,
            'insert_new_line_before': self.insert_new_line_before,
            'remove_new_line_before': self.remove_new_line_before,
            'dont_indent_child': self.dont_indent_child,
            'dont_indent_child_tag_size': self.dont_indent_child_tag_size,
            'inline_elements': self.inline_elements,
            'keep_white_space_inside': self.keep_white_space_inside,
            'dont_break_if_inline_content': self.dont_break_if_inline_content,
            'new_line_before_first_attr': self.new_line_before_first_attr,
            'new_line_before_last_attr': self.new_line_before_last_attr,
            'generate_quote_marks': self.generate_quote_marks,
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

        template.name = data.get(
            'name', 
            template.name,
        )
        template.use_tab_character = data.get(
            'use_tab_character', 
            template.use_tab_character,
        )
        template.smart_tab = data.get(
            'smart_tab', 
            template.smart_tab,
        )
        template.indent = data.get(
            'indent', 
            template.indent,
        )
        template.continuation_indend = data.get(
            'continuation_indend', 
            template.continuation_indend,
        )
        template.keep_indents_on_empty_lines = data.get(
            'keep_indents_on_empty_lines', 
            template.keep_indents_on_empty_lines,
        )
        template.hard_wrap_column = data.get(
            'hard_wrap_column', 
            template.hard_wrap_column,
        )
        template.keep_line_breaks = data.get(
            'keep_line_breaks', 
            template.keep_line_breaks,
        )
        template.keep_line_breaks_in_text = data.get(
            'keep_line_breaks_in_text', 
            template.keep_line_breaks_in_text,
        )
        template.keep_blank_lines = data.get(
            'keep_blank_lines', 
            template.keep_blank_lines,
        )
        template.wrap_attributes = data.get(
            'wrap_attributes', 
            template.wrap_attributes,
        )
        template.wrap_text = data.get(
            'wrap_text', 
            template.wrap_text,
        )
        template.align_attributes = data.get(
            'align_attributes', 
            template.align_attributes,
        )
        template.align_text = data.get(
            'align_text', 
            template.align_text,
        )
        template.keep_white_spaces = data.get(
            'keep_white_spaces', 
            template.keep_white_spaces,
        )
        template.space_around_eq_in_attribute = data.get(
            'space_around_eq_in_attribute', 
            template.space_around_eq_in_attribute,
        )
        template.space_after_tag_name = data.get(
            'space_after_tag_name', 
            template.space_after_tag_name,
        )
        template.space_in_empty_tag = data.get(
            'space_in_empty_tag', 
            template.space_in_empty_tag,
        )
        template.insert_new_line_before = data.get(
            'insert_new_line_before', 
            template.insert_new_line_before,
        )
        template.remove_new_line_before = data.get(
            'remove_new_line_before', 
            template.remove_new_line_before,
        )
        template.dont_indent_child = data.get(
            'dont_indent_child', 
            template.dont_indent_child,
        )
        template.dont_indent_child_tag_size = data.get(
            'dont_indent_child_tag_size', 
            template.dont_indent_child_tag_size,
        )
        template.inline_elements = data.get(
            'inline_elements', 
            template.inline_elements,
        )
        template.keep_white_space_inside = data.get(
            'keep_white_space_inside', 
            template.keep_white_space_inside,
        )
        template.dont_break_if_inline_content = data.get(
            'dont_break_if_inline_content', 
            template.dont_break_if_inline_content,
        )
        template.new_line_before_first_attr = data.get(
            'new_line_before_first_attr', 
            template.new_line_before_first_attr,
        )
        template.new_line_before_last_attr = data.get(
            'new_line_before_last_attr', 
            template.new_line_before_last_attr,
        )
        template.generate_quote_marks = data.get(
            'generate_quote_marks', 
            template.generate_quote_marks,
        )

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
