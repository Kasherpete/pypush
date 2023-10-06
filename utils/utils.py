import curses
import os

from npyscreen import wgtitlefield as titlefield, Checkbox
from npyscreen.wgtextbox import Textfield
from npyscreen import wgmultiline as multiline
from npyscreen import wgcheckbox as checkbox
import npyscreen


class PasswordEntry(Textfield):
    def _print(self):
        strlen = len(self.value)
        if self.maximum_string_length < strlen:
            tmp_x = self.relx
            for i in range(self.maximum_string_length):
                self.parent.curses_pad.addch(self.rely, tmp_x, '*')
                tmp_x += 1

        else:
            tmp_x = self.relx
            for i in range(strlen):
                self.parent.curses_pad.addstr(self.rely, tmp_x, '*')
                tmp_x += 1


class TitlePassword(titlefield.TitleText):
    _entry_type = PasswordEntry


class RoundCheckBox(Checkbox):
    False_box = ''
    True_box = ''

#-----------------------------------------------------------
class SelectOne(multiline.MultiLine):
    _contained_widgets = RoundCheckBox

    def __init__(self, screen, kasher, **keywords):

        super().__init__(screen, **keywords)

        self.kasher_update = kasher

    def update(self, clear=True):
        if self.hidden:
            self.clear()
            return False
        # Make sure that self.value is a list
        if not hasattr(self.value, "append"):
            if self.value is not None:
                self.value = [self.value, ]
            else:
                self.value = []

        super(SelectOne, self).update(clear=clear)

    def kasher_update(self):
        pass

    def h_select(self, ch):
        self.value = [self.cursor_line, ]
        self.kasher_update()
        # os.system(f'osascript -e \'display notification "{self.value}"\'')

    def _print_line(self, line, value_indexer):
        try:
            display_this = self.display_value(self.values[value_indexer])
            line.value = display_this
            line.hide = False
            if hasattr(line, 'selected'):
                if (value_indexer in self.value and (self.value is not None)):
                    line.selected = True
                else:
                    line.selected = False
            # Most classes in the standard library use this
            else:
                if (value_indexer in self.value and (self.value is not None)):
                    line.show_bold = True
                    line.name = display_this
                    line.value = True
                else:
                    line.show_bold = False
                    line.name = display_this
                    line.value = False

            if value_indexer in self._filtered_values_cache:
                line.important = True
            else:
                line.important = False


        except IndexError:
            line.name = None
            line.hide = True

        line.highlight = False


class TitleSelectOne(multiline.TitleMultiLine):
    _entry_type = SelectOne

#-------------------------------------------------

class FormWithMenus(npyscreen.fmForm.FormBaseNew, npyscreen.wgNMenuDisplay.HasMenus):
    """The Form class, but with a handling system for menus as well.  See the HasMenus class for details."""

    def __init__(self, *args, **keywords):
        super(FormWithMenus, self).__init__(*args, **keywords)
        self.initialize_menus()

    def display_menu_advert_at(self):
        return self.lines - 1, 1

    def draw_form(self):
        super(FormWithMenus, self).draw_form()
        menu_advert = " " + self.__class__.MENU_KEY + ": Menu "
        y, x = self.display_menu_advert_at()
        if isinstance(menu_advert, bytes):
            menu_advert = menu_advert.decode('utf-8', 'replace')
        self.add_line(y, x,
            menu_advert,
            self.make_attributes_list(menu_advert, curses.A_NORMAL),
            self.columns - x - 1
            )


def username_legit(username: str):
    if '@' not in username:
        return False
    r = username.split('@')
    if len(r[0]) < 2 or len(r[1]) < 3:
        return False
    if '.' not in r[1]:
        return False
    return True


def password_legit(password: str):
    if len(password) < 4:
        return False
    return True
