"""Утиліта що форматує HTML файли за вказаними шаблонами

"""

__version__ = "0.1.14"

from os import system
from os import walk
from os import makedirs
from os import listdir
from os.path import exists
from os.path import join
from json import dump
from json import load
from re import search
from re import compile as re_compile
from re import Pattern
from re import sub
from html.parser import HTMLParser

from typing import List
from typing import Optional


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
        self.wrap_attributes: int = self.CHOP_DOWN_IF_LONG
        self.wrap_text: bool = True
        self.align_attributes: bool = True
        self.align_text: bool = True
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
        self.new_line_before_first_attr: bool = True
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


class Tag:
    """Класс який описує тег
    
    Attributes
    ----------
    name : str
        Ім'я тегу
    text : str
        Текст тегу
    childs : List[Tag]
        Список дочірніх тегів
    parent : Optional[Tag]
        Батько тегу

    Methods
    -------
    get_pos() : (int, int)
        Метод який визначає лінію та стовбчик де починається тег
    _get_text_before_target(target: 'Tag') : (str, bool)
        Метод вертає текст до пошукового тега
    get_root_tag() : Tag
        Метод вертає корневий тег дерева тегів
    lint(template: Template)
        Метод який послідовно запускає методи форматування текста
    get_text() : str
        Вертає текст тегу з дочірніми элементами
    lint_use_tab_character(template: Template)
        Метод для Template.use_tab_character
    lint_indents(template: Template)
        Method який робить відступи від батька
    replace_space_before_tag(space: str)
        Метод який заставляє батька замінити пространство перед тегом
    _replace_space_before_tag(target: Tag, new_space: str)
        Метод який замінює відступи перед тегом
    get_space_before_tag() : str
        Метод який вертає відступи перед тегом
    _get_space_before_tag(target: Tag) : str
        Метод який вертає відступи перед пошуковим тегом
    get_lines_count() : int
        Метод який віддає кількість строчок цього тега
    lint_continuation_indend(template: Template)
        Робить відступи перед атрибутами тегу на нових строчках
    lint_insert_new_line_before(template: Template)
        Метод який переносить на нову строку тег якщо він є 
        у списку тегів які треба переносити на нову строку
    lint_remove_new_line_before(template: Template)
        Метод видаляє перенос на нову строку якщо тег є 
        у списку тегів які не треба переносити на нову строку
    get_indent_col() : int
        Метод визначає відступи на лінії
    get_max_col_in_text_tag() : int
        Метод визначає максимальну дліну текста тега
    lint_hard_wrap(template: Template)
        Метод переносить тег на строку, якщо длліна тексту тега завелика
    lint_wrap_attributies(template: Template)
        Метод форматування для Template.wrap_attributes
    lint_wrap_attributies_if_long(template: Template)
        Переносить атрібут тега якщо він залазить за ліміт
    lint_chop_down_attributies_if_long(template: Template)
        Якщо дліна тегу завелика то переносить теги послідовно на 
        наступні строчки
    lint_chop_down_attributies_always(template: Template)
        Переносить всі атрибути послідовно на наступні строчки
    lint_align_attributes(template: Template)
        Метод для вирівнювання атрібутів на наступних строчках
    get_text_string() : str
        Віддає текст тегу, без дочірніх тегів
    get_length_first_line() : (int, bool)
        Метод вертає дліну першої строчки тега
    lint_wrap_text(template: Template)
        Метод який форматує текст в тегах
    lint_space_around_eq_in_attribute(template: Template)
        Метод добавляє відступи біля знака '=' у атрібутах тегу
    lint_space_after_tag_name(template: Template)
        Метод добавляє відступ після імені тегу
    lint_space_in_empty_tag(template: Template)
        Метод добавляє відступ після імені тегу у пустих тегах
    lint_new_line_before_first_attr(template: Template)
        Метод добавляє перенос строки перед першим атрібутом якщо 
        тег не на одній строчці
    """

    def __init__(self, name: str, text: str, parent: Optional['Tag']):
        """Конструктор класу
        
        Parameters
        ----------
        name : str
            Ім'я тегу
        text : str
            Текст тегу
        parent : Optional[Tag]
            Батько тегу
        """

        self.name: str = name
        self.text: str = text
        self.childs: List[Tag] = []
        self.parent: Optional[Tag] = parent

    def lint(self, template: Template):
        """Метод який послідовно запускає методи форматування текста"""

        
        self.lint_space_in_empty_tag(template)
        self.lint_space_after_tag_name(template)
        self.lint_space_around_eq_in_attribute(template)
        self.lint_hard_wrap(template)
        self.lint_remove_new_line_before(template)
        self.lint_insert_new_line_before(template)
        self.lint_indents(template)
        self.lint_wrap_attributies(template)
        self.lint_new_line_before_first_attr(template)
        self.lint_continuation_indend(template)
        self.lint_align_attributes(template)
        self.lint_wrap_text(template)
        self.lint_keep_indents_on_empty_lines(template)
        self.lint_smart_tab(template)
        self.lint_use_tab_character(template)

        for child in self.childs:
            child.lint(template)

    def lint_new_line_before_first_attr(self, template: Template):
        """Метод добавляє перенос строки перед першим атрібутом якщо 
        тег не на одній строчці"""

        tag_string = self.get_tag_string()
        if tag_string.__contains__('\n'):
            if template.new_line_before_first_attr:
                new_tag_string = sub(r'(<\w+)(\s+)(\w+)',
                    '\g<1>\n\g<3>', tag_string)
            else:
                new_tag_string = sub(r'(<\w+)(\s+)(\w+)', 
                    '\g<1> \g<3>', tag_string)
            self.text = self.text.replace(tag_string, new_tag_string)

    def lint_space_in_empty_tag(self, template: Template):
        """Метод добавляє відступ після імені тегу у пустих тегах"""
        if template.space_in_empty_tag:
            self.text = sub(r'\s*(?=\/\>)', ' ', self.text)
        else:
            self.text = sub(r'\s*(?=\/\>)', '', self.text)

    def lint_space_after_tag_name(self, template: Template):
        """Метод добавляє відступ після імені тегу"""
        if template.space_after_tag_name:
            self.text = sub(r'\s*(?=(\/\>|(?<!\/)\>))', ' ', self.text)
        else:
            self.text = sub(r'\s*(?=(\/\>|(?<!\/)\>))', '', self.text)

    def lint_space_around_eq_in_attribute(self, template: Template):
        """Метод добавляє відступи біля знака '=' у атрібутах тегу"""
        tag_string = self.get_tag_string()
        if template.space_around_eq_in_attribute:
            new_tag_string = sub(r'\s*\=\s*(\"|\')', r' = \g<1>', tag_string)
        else:
            new_tag_string = sub(r'\s*\=\s*(\"|\')', r'=\g<1>', tag_string)
        self.text = self.text.replace(tag_string, new_tag_string)

    def lint_wrap_text(self, template: Template):
        """Метод який форматує текст в тегах"""

        if not template.wrap_text:
            return

        tag_col = self.get_col()
        tag_string = self.get_tag_string()
        if tag_string.endswith('/>'):
            return
        source_text = self.get_text_string()
        begin_col = tag_col + len(tag_string)
        if template.align_text:
            indents = begin_col - 1
            for char in source_text:
                if char == '\n':
                    indents = 0
                elif char == ' ':
                    indents += 1
                else:
                    break
        else:
            indents = self.get_indent_col() + template.indent - 1
        
        text = source_text
        text = sub(r'\n\s+', '\n' + ' ' * indents, text)
        while True:
            child = 0
            col = begin_col
            last_space = 0
            for i, char in enumerate(text[:]):
                if char == '\n':
                    col = 0
                elif char == ' ':
                    last_space = i
                    col += 1
                elif char == '{':
                    if text[i + 1] != '}':
                        col += 1
                        continue
                    
                    length, _ = self.childs[child].get_length_first_line()
                    col = length + col - 1                
                    child += 1
                else:
                    col += 1

                if col > template.hard_wrap_column:

                    check_new_line = False
                    for c in reversed(text[:last_space]):
                        if c == '\n':
                            check_new_line = True
                            break
                        elif c != ' ':
                            break

                    if check_new_line:
                        continue
                    
                    if last_space != 0:
                        text = (
                            text[:last_space] + '\n' +
                            ' ' * indents + text[last_space + 1:]
                        )
                    else:
                        text = '\n' + ' ' * indents + text
                    break
            
            else:
                break
        
        self.text = self.text.replace(source_text, text)

    def get_length_first_line(self) -> (int, bool):
        """Метод вертає дліну першої строчки тега"""

        length = 0
        current_child = 0
        for i, char in enumerate(self.text):
            if char == '{' and self.text[i + 1] == '}':
                (
                    length_child, 
                    is_end,
                ) = self.childs[current_child].get_length_first_line()
                length += length_child
                if is_end:
                    return length, True
                else:
                    current_child += 1
                    length -= 1
            elif char == '\n':
                return length, True
            else:
                length += 1
        else:
            return length, False

    def get_text_string(self) -> str:
        """Віддає текст тегу, без дочірніх тегів"""

        tag_string = self.get_tag_string()
        end_tag = search(r'\s+\<\/' ,self.text)
        if end_tag:
            text_string = self.text[len(tag_string):end_tag.start()]
        else:
            text_string = self.text[len(tag_string):]
        return text_string
    
    def lint_align_attributes(self, template: Template):
        """Метод для вирівнювання атрібутів на наступних строчках"""

        if not template.align_attributes:
            return

        tag_string = self.get_tag_string()
        first_tag_space_match = search(
            r'(\s+)(?=[\w-]+\=(\"|\')[^\"\']*(\"|\'))', 
            tag_string,
        )

        if not first_tag_space_match:
            return

        if first_tag_space_match.group(1).__contains__('\n'):
            indents = len(first_tag_space_match.group(1)) - 1
        else:
            indents = self.get_col() + first_tag_space_match.end(1) - 1
        
        new_tag_string = sub(
            r'(?<=\n)(\s+)([\w-]+\=(\"|\')[^\"\']*(\"|\'))',
            r'{}\g<2>'.format(' ' * indents),
            tag_string,
        )

        self.text = self.text.replace(tag_string, new_tag_string)
        
    def lint_wrap_attributies(self, template: Template):
        """Метод форматування для Template.wrap_attributes"""
        if template.wrap_attributes == template.NONE:
            return

        elif template.wrap_attributes == template.WRAP_IF_LONG:
            self.lint_wrap_attributies_if_long(template)

        elif template.wrap_attributes == template.CHOP_DOWN_IF_LONG:
            self.lint_chop_down_attributies_if_long(template)

        elif template.wrap_attributes == template.WRAP_ALWAYS:
            self.lint_chop_down_attributies_always(template)

    def lint_wrap_attributies_if_long(self, template: Template):
        """Переносить атрібут тега якщо він залазить за ліміт"""

        tag_col = self.get_col()
        tag_string = self.get_tag_string()
        new_tag_string = tag_string
        last_space_index = -1
        lock_quote = False
        lock_double_qoute = False
        while True:
            col = tag_col
            for index, char in enumerate(new_tag_string[:]):
                if char == '\n':
                    col = 0
                    continue

                if char == ' ':
                    if not lock_quote and not lock_double_qoute:
                        last_space_index = index
                elif char == '"':
                    lock_double_qoute = not lock_double_qoute
                elif char == "'":
                    lock_quote = not lock_quote
                
                col += 1

                if col > template.hard_wrap_column:
                    if last_space_index != -1:
                        new_tag_string = (new_tag_string[:last_space_index] +
                                '\n' + new_tag_string[last_space_index + 1:])
                        break
            else:
                break

        self.text = self.text.replace(tag_string, new_tag_string)

    def lint_chop_down_attributies_if_long(self, template: Template):
        """Якщо дліна тегу завелика то переносить теги послідовно на 
        наступні строчки"""

        col = self.get_col()
        tag_string = self.get_tag_string()
        if col + len(tag_string) > template.hard_wrap_column:
            self.lint_chop_down_attributies_always(template)

    def lint_chop_down_attributies_always(self, template: Template):
        """Переносить всі атрибути послідовно на наступні строчки"""

        tag_string = self.get_tag_string()
        saved_match = search(r'<\w+\s+', tag_string)
        if not saved_match:
            return

        saved_tag_string = tag_string[:saved_match.end()]
        attributies_string = tag_string[saved_match.end():]

        attributies_string = sub(r'(\s+)([\w-]+\=(\"|\')[^\"\']*(\"|\'))',
                                 r'\n\g<2>', attributies_string)

        new_tag_string = saved_tag_string + attributies_string

        self.text = self.text.replace(tag_string, new_tag_string)


    def get_max_col_in_text_tag(self) -> int:
        """Метод визначає максимальну дліну текста тега"""

        text = self.get_text()
        max_col = 0
        col = self.get_col()
        for char in text:
            if col > max_col:
                max_col = col
            if char == '\n':
                col = 0
            else:
                col += 1
        return max_col

    def lint_hard_wrap(self, template: Template):
        """Метод переносить тег на строку, якщо дліна тексту тега завелика"""

        if self.name in template.inline_elements:
            return

        if self.get_max_col_in_text_tag() <= template.hard_wrap_column:
            return

        if not self.get_space_before_tag().__contains__('\n'):
            if self.name in template.dont_break_if_inline_content:
                return

        self.replace_space_before_tag('\n')
        self.text = sub(r'\s*(?=<\/)', '\n', self.text)

    def lint_remove_new_line_before(self, template: Template):
        """Метод видаляє перенос на нову строку якщо тег є 
        у списку тегів які не треба переносити на нову строку"""

        if self.name in template.remove_new_line_before:
            self.replace_space_before_tag('')

    def lint_insert_new_line_before(self, template: Template):
        """Метод який переносить на нову строку тег якщо він є 
        у списку тегів які треба переносити на нову строку"""

        if self.name in template.insert_new_line_before:
            self.replace_space_before_tag('\n')

    def lint_continuation_indend(self, template: Template):
        """Робить відступи перед атрибутами тегу на нових строчках"""

        old_tag_string = self.get_tag_string()
        indents = ' ' * (self.get_indent_col() - 1 + 
                         template.continuation_indend)
        new_tag_string = sub(r'(?<=\n)\s*', indents, old_tag_string)
        self.text = self.text.replace(old_tag_string, new_tag_string)

    def get_lines_count(self) -> int:
        """Метод який віддає кількість строчок цього тега"""

        return 1 + self.get_text().count('\n')

    def get_indent_col(self) -> int:
        """Метод визначає відступи на лінії"""

        if not self.parent:
            return 1
        if self.get_space_before_tag().__contains__('\n'):
            return self.get_col()
        else:
            return self.parent.get_indent_col()

    def lint_indents(self, template: Template):
        """Method який робить відступи від батька"""

        if not self.parent:
            return

        space_before_tag = self.get_space_before_tag()
        if not space_before_tag.__contains__('\n'):
            return

        indents = int((self.parent.get_indent_col() - 1) / template.indent)

        # Не відступати якщо родич є у списку тегів від яких не відступати
        dont_indent = (self.parent.name in template.dont_indent_child + [''])
        # Якщо задано розмір тегу у строчках і тег більше за цей розмір
        if template.dont_indent_child_tag_size:
            if (self.parent.get_lines_count() 
                        > template.dont_indent_child_tag_size):
                dont_indent = True
        
        if not dont_indent:
            indents += 1

        new_space = '\n' + ((' ' * template.indent) * indents)

        self.replace_space_before_tag(new_space)

        self.text = sub(r'(?<=\n)\s*(?=<\/)', new_space, self.text)

    def replace_space_before_tag(self, space: str):
        """Метод який заставляє батька замінити пространство перед тегом"""

        if not self.parent:
            return
        self.parent._replace_space_before_tag(self, space)

    def _replace_space_before_tag(self, target: 'Tag', new_space: str):
        """Метод який замінює відступи перед тегом
        
        Parameters
        ----------
        target : Tag
            Тег перед яким треба замінити відступи
        new_space: str
            Відступи на які треба замінити
        """

        start = 0
        for child in self.childs:
            index = self.text.find('{}', start)
            start = index + 2

            if child == target:
                space = search(r'\s*', self.text[index - 1::-1]).group(0)
                space_len = len(space)

                self.text = (self.text[:index - space_len] + new_space + 
                             self.text[index:])

                break

    def get_space_before_tag(self) -> str:
        """Метод який вертає відступи перед тегом"""

        if self.parent:
            return self.parent._get_space_before_tag(self)
        return ''

    def _get_space_before_tag(self, target: 'Tag') -> str:
        """Метод який вертає відступи перед пошуковим тегом"""

        start = 0
        for child in self.childs:
            index = self.text.find('{}', start)
            start = index + 2

            if child == target:
                return search(r'\s*', self.text[index - 1::-1]).group(0)

    def lint_keep_indents_on_empty_lines(self, template: Template):
        """Метод для Template.keep_indents_on_empty_lines
        
        Якщо Template.keep_indents_on_empty_lines == False
        Видаляє відступи на пустих строках
        """

        if not template.keep_indents_on_empty_lines:
            self.text = sub(r'(?<=\n)\s*(?=\n)', '', self.text)

    def lint_smart_tab(self, template: Template):
        """Метод для Template.smart_tabs
        
        Якщо Template.smart_tabs == True
        розумно замінює пробіли на табуляцію перед атрибутами в тегах

        Якщо Template.smart_tabs == False
        розумно замінює табуляцію на пробіли перед атрибутами в тегах
        
        """

        if not self.parent:
            return

        tag_string = self.get_tag_string()
        new_tag_string = tag_string
        tag_col = self.get_col()
        start = 0
        while True:
            end_char_index = new_tag_string.find('\n', start)

            if end_char_index == -1:
                break
            start = end_char_index + 1

            space = search(r'\s*', new_tag_string[end_char_index + 1:])
            space_len = len(space.group(0))
            space_str = space.group(0).replace('\t', '    ')
            if len(space_str) >= tag_col:
                if template.use_tab_character:
                    if template.smart_tab:
                        count_tabs = int(tag_col / 4)
                        space_str = ('\t' * count_tabs + 
                                     space_str[4 * count_tabs:])
                    else:
                        count_tabs = int(len(space_str) / 4)
                        space_str = ('\t' * count_tabs + 
                                     space_str[4 * count_tabs:])
            else:
                if template.use_tab_character:
                    count_tabs = int(len(space_str) / 4)
                    space_str = ('\t' * count_tabs + 
                                 space_str[4 * count_tabs:])

            
            new_tag_string = (new_tag_string[:start] + space_str + 
                              new_tag_string[start + space_len:])

        self.text = self.text.replace(tag_string, new_tag_string)
            
        
    def lint_use_tab_character(self, template: Template):
        """Метод для Template.use_tab_character
        
        Якщо Template.use_tab_character == True
        замінює пробіли на табуляцію перед тегами

        Якщо Template.use_tab_character == False
        замінює табуляцію на пробіли перед тегами
        
        """
        start = 0
        while True:
            space_before_tag = search(
                r'(?<=\n)\s+(?={}|<[\s\S]*?>)', 
                self.text[start:],
            )

            if not space_before_tag:
                break
            
            space_before_tag_text = space_before_tag.group(0)

            if template.use_tab_character:
                space_before_tag_text = sub(
                    r'    ', 
                    r'\t', 
                    space_before_tag_text,
                )   
            else:
                space_before_tag_text = sub(
                    r'\t', 
                    r'    ', 
                    space_before_tag_text,
                )

            self.text = (
                self.text[:start + space_before_tag.start()] +
                space_before_tag_text + 
                self.text[start + space_before_tag.end():]
            )

            start += space_before_tag.start() + len(space_before_tag_text)

    def get_tag_string(self):
        """Вертає текст тега та атрібутів"""
        return search(r'<[\s\S]*?>', self.text).group(0)

    def get_text(self) -> str:
        """Вертає текст тегу з дочірніми элементами"""
        text = self.text.format(
            *[c.get_text() for c in self.childs]
        )
        return text

    def get_pos(self) -> (int, int):
        """Метод який визначає лінію та стовбчик де починається тег
        
        Метод робить запрос текста до себе у корневого тега, 
        потім рахує лінії та стовбчики.

        Returns
        -------
        line, col : (int, int)
            Лінія та стовбчик де починається тег
        """

        root_tag = self.get_root_tag()
        text_before, _ = root_tag._get_text_before_target(self)

        line = 1
        col = 1
        for char in text_before:
            if char == '\n':
                line += 1
                col = 1
            elif char == '\t':
                col += 4
            else:
                col += 1

        return line, col

    def get_col(self) -> int:
        """Вертає позицію тега на лінії"""
        if not self.parent:
            return 1
        return self.parent._get_col(self)

    def _get_col(self, target: 'Tag') -> int:
        """Вертає позицію пошукового тега на лінії
        
        Шукає у себе або батька '\n', коли знайде 
        вертає позицію до пошукового тега 

        Returns
        -------
        col : int
            Позиція пошукового тега на лінії
        """

        col: int = 1
        text: str = ''
        current_child_index = 0
        i = 0
        while True:
            if self.text[i] == '{' and self.text[i + 1] == '}':
                current_child = self.childs[current_child_index]
                if current_child == target:
                    break

                text += current_child.get_text()

                i += 2
                current_child_index += 1
            else:
                text += self.text[i]
                i += 1

        text = text.replace('\t', '    ')
        end_line_char_pos = text.rfind('\n')
        if end_line_char_pos == -1:
            if not self.parent:
                return len(text)

            col = self.parent._get_col(self)
            for _ in text:
                col += 1
        else:
            col = len(text[end_line_char_pos:])

        return col

    def _get_text_before_target(self, target: 'Tag') -> (str, bool):
        """Метод вертає текст до пошукового тега
        
        Метод рекурсивно шукає тег в дереві тегів, 
        та паралельно собирає текст до нього.
        Коли знаходить, вертає текст.

        Parameters
        ----------
        target : Tag
            Тег перед яким треба вернути текст

        Returns
        -------
        text, target_is_found : (str, bool)
            Вертає текст та True якщо тег було знайдено
        """

        text: str = ''
        if self.childs:
            current_child_index = 0
            i = 0
            while True:
                if i >= len(self.text):
                    return text, False

                if self.text[i] == '{' and self.text[i + 1] == '}':
                    current_child = self.childs[current_child_index]
                    if current_child == target:
                        return text, True

                    (
                        child_text, target_is_found
                    ) = current_child._get_text_before_target(target)
                    text += child_text
                    if target_is_found:
                        return text, True

                    i += 2
                    current_child_index += 1
                else:
                    text += self.text[i]
                    i += 1
        else:
            return text + self.text, False

    def get_root_tag(self) -> 'Tag':
        """Метод вертає корневий тег дерева тегів"""

        if self.parent:
            return self.parent.get_root_tag()
        return self


class Html(HTMLParser):
    """Клас який перевіряє та форматує Html файли

    Attributes
    ----------
    path : str
        Шлях до файлу
    _root_tag : Tag
        Корневий тег дерева тегів
    _opened_tags : List[Tag]
        Список відкритих тегів (для аналізу файла)
    break_html : bool
        Змііня якщо виявилося що Html код недійсний

    Methods
    -------
    check_file(path: str, template: Template)
        Перевіряє html файл за вказаним шаблоном
    error_no_closed_tags(tag_name: str)
        Метод друкує інформацію про плоху розмітку Html
    handle_starttag(tag: str, attrs: dict)
        Метод ловить початкові теги
    handle_endtag(tag: str)
        Метод ловить кінцеві теги
    handle_startendtag(tag: str, attrs: dict)
        Метод ловить початково-кінцеві теги
    handle_data(data: str)
        Метод ловить текст
    handle_comment(data: str)
        Метод ловить коментарії
    handle_decl(data: str):
        Метод ловить інформацію файла
    """

    def __init__(self, path: str):
        """Конструктор класу
        
        Parameters
        ----------
        path : str
            Шлях до файлу
        """
        super().__init__()

        self.path: str = path
        self._root_tag: Tag = Tag('', '', None)
        self._opened_tags: List[Tag] = [self._root_tag]
        self.break_html = False

    def handle_starttag(self, tag: str, attrs: dict):
        """Метод ловить початкові теги"""

        tag = Tag(tag, self.get_starttag_text(), self._opened_tags[-1])
        self._opened_tags[-1].childs.append(tag)
        self._opened_tags[-1].text += '{}'
        self._opened_tags.append(tag)

    def handle_endtag(self, tag: str):
        """Метод ловить кінцеві теги"""

        tag_text = '</{}>'.format(tag)
        if self._opened_tags[-1].name == tag:
            self._opened_tags[-1].text += tag_text
        else:
            if not self.break_html:
                self.error_no_closed_tags(tag)
                self.break_html = True
        del self._opened_tags[-1]

    def handle_startendtag(self, tag: str, attrs: dict):
        """Метод ловить початково-кінцеві теги"""

        tag = Tag(tag, self.get_starttag_text(), self._opened_tags[-1])
        self._opened_tags[-1].text += '{}'
        self._opened_tags[-1].childs.append(tag)  

    def handle_data(self, data: str):
        """Метод ловить текст"""

        self._opened_tags[-1].text += data
    
    def handle_comment(self, data: str):
        """Метод ловить коментарії"""

        self._opened_tags[-1].text += '<!-- {} -->'.format(data)

    def handle_decl(self, data: str):
        """Метод ловить інформацію файла"""

        self._opened_tags[-1].text += '<!{}>'.format(data)

    @classmethod
    def check_file(cls, path: str, template: Template):
        """Перевіряє html файл за вказаним шаблоном
        
        Parameters
        ----------
        path : str
            Шлях до файлу
        template : Template
            Шаблон перевірки
        """

        html = cls(path)

        with open(path, 'r') as file:
            data = file.read()

        html.feed(data)

        if not html.break_html:
            if len(html._opened_tags) != 1:
                html.error_no_closed_tags('')
                html.break_html = True
                return
        else:
            return
        
        html._root_tag.lint(template)

        with open(path, 'w') as file:
            file.write(html._root_tag.get_text())

    def error_no_closed_tags(self, tag_name: str):
        """Метод друкує інформацію про плоху розмітку Html
        
        Parameters
        ----------
        tag_name : str
            Ім'я тегу після якого існують не закриті теги.
        """

        print('Error: Нейдійсна розмітка "{}"'.format(self.path))
        for tag in reversed(self._opened_tags):
            if tag.name == tag_name:
                break
        
        tag_index = self._opened_tags.index(tag)
        for bad_tag in self._opened_tags[tag_index + 1:]:
            line, col = bad_tag.get_pos()
            print('Незакритий тег "{}" на лінії {} та стовбчику {}'.format(
                bad_tag.name, line, col
            ))


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
                    Html.check_file(join(root, file), self.current_template)
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
