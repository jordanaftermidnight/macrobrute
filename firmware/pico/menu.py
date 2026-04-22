"""MACROBRUTE Pico WH — Menu system for OLED + encoder navigation."""

import config


class MenuItem:
    """Single menu entry."""

    def __init__(self, label, action=None, submenu=None, value_fn=None, adjust_fn=None):
        self.label = label
        self.action = action         # Callable on select
        self.submenu = submenu       # Menu instance for sub-navigation
        self.value_fn = value_fn     # Callable returning current value string
        self.adjust_fn = adjust_fn   # Callable(delta) for encoder adjustment


class Menu:
    """Scrollable menu with cursor, drawn on OLED."""

    def __init__(self, title, items):
        self.title = title
        self.items = items
        self.cursor = 0
        self.scroll_offset = 0

    def move(self, delta):
        self.cursor = max(0, min(len(self.items) - 1, self.cursor + delta))
        # Keep cursor visible
        if self.cursor < self.scroll_offset:
            self.scroll_offset = self.cursor
        elif self.cursor >= self.scroll_offset + config.MENU_VISIBLE_ITEMS:
            self.scroll_offset = self.cursor - config.MENU_VISIBLE_ITEMS + 1

    def select(self):
        if 0 <= self.cursor < len(self.items):
            return self.items[self.cursor]
        return None

    @property
    def current(self):
        if 0 <= self.cursor < len(self.items):
            return self.items[self.cursor]
        return None


class MenuSystem:
    """Stack-based menu navigation."""

    def __init__(self, root_menu):
        self._stack = [root_menu]
        self._editing = False       # True when adjusting a value
        self._edit_item = None

    @property
    def current_menu(self):
        return self._stack[-1]

    @property
    def editing(self):
        return self._editing

    @property
    def at_root(self):
        return len(self._stack) == 1

    def on_rotate(self, delta):
        if self._editing and self._edit_item and self._edit_item.adjust_fn:
            self._edit_item.adjust_fn(delta)
        else:
            self.current_menu.move(delta)

    def on_press(self):
        if self._editing:
            # Exit edit mode
            self._editing = False
            self._edit_item = None
            return

        item = self.current_menu.select()
        if item is None:
            return

        if item.submenu:
            self._stack.append(item.submenu)
        elif item.adjust_fn:
            # Enter edit mode for adjustable values
            self._editing = True
            self._edit_item = item
        elif item.action:
            item.action()

    def on_back(self):
        if self._editing:
            self._editing = False
            self._edit_item = None
        elif len(self._stack) > 1:
            self._stack.pop()

    def draw(self, oled):
        menu = self.current_menu

        # Title bar
        oled.fill_rect(0, 0, config.OLED_WIDTH, 10, 1)
        oled.text(menu.title, 2, 1, 0)

        # Menu items
        visible = menu.items[menu.scroll_offset:menu.scroll_offset + config.MENU_VISIBLE_ITEMS]
        for i, item in enumerate(visible):
            y = 14 + i * config.FONT_HEIGHT
            idx = menu.scroll_offset + i
            is_selected = idx == menu.cursor

            if is_selected:
                oled.fill_rect(0, y - 1, config.OLED_WIDTH, config.FONT_HEIGHT, 1)

            # Label
            label = item.label
            color = 0 if is_selected else 1
            oled.text(label, 2, y, color)

            # Value (right-aligned)
            if item.value_fn:
                val = str(item.value_fn())
                vx = config.OLED_WIDTH - len(val) * 8 - 2
                if self._editing and item == self._edit_item:
                    oled.text("[" + val + "]", vx - 8, y, color)
                else:
                    oled.text(val, vx, y, color)

        # Scroll indicators
        if menu.scroll_offset > 0:
            oled.text("^", 120, 14, 1)
        if menu.scroll_offset + config.MENU_VISIBLE_ITEMS < len(menu.items):
            oled.text("v", 120, 14 + (config.MENU_VISIBLE_ITEMS - 1) * config.FONT_HEIGHT, 1)
