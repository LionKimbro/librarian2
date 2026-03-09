# ui/theme.py — dark mode color palette, fonts, icons, and ttk style setup
#
# All colors live here. No ad-hoc color strings elsewhere in the codebase.

# --- Color palette ---

DARK_BG       = '#1e1e1e'   # main background
DARK_BG2      = '#252526'   # panels, status bar
DARK_BG3      = '#2d2d30'   # button and selection highlight
DARK_FG       = '#d4d4d4'   # primary text
DARK_FG_DIM   = '#858585'   # labels, secondary text
DARK_ACCENT   = '#007acc'   # blue accent for primary action buttons
DARK_BORDER   = '#3e3e42'   # separator and border lines
DARK_INPUT_BG = '#3c3c3c'   # entry and text widget backgrounds

# Status bar text colors (foreground only; bg stays DARK_BG2)
STATUS_FG = {
    'default': DARK_FG,
    'green':   '#4ec9b0',
    'blue':    '#9cdcfe',
    'red':     '#f48771',
}

# Dirty indicator dot colors
DIRTY_RED   = '#f44747'
DIRTY_GREEN = '#4ec9b0'

# --- Fonts ---

FONT_MONO = ('Consolas', 11)
FONT_UI   = ('Segoe UI', 10)

# --- Unicode type icons (for the entry index) ---

ICON_FILE    = '\U0001F5CE'   # 🗎
ICON_FOLDER  = '\U0001F5C0'   # 🗀
ICON_URL     = '\U0001F517'   # 🔗
ICON_PROGRAM = '\u03BB'       # λ
ICON_UNKNOWN = '?'


def apply_theme(root):
    """Apply dark mode theme to root window and all ttk styles.

    Call once after the root window is created, before building widgets.
    root: tkinter.Tk
    """
    import tkinter.ttk as ttk

    root.configure(bg=DARK_BG)

    style = ttk.Style(root)
    style.theme_use('clam')

    style.configure('TFrame',      background=DARK_BG)
    style.configure('TLabel',      background=DARK_BG,   foreground=DARK_FG, font=FONT_UI)
    style.configure('TButton',     background=DARK_BG3,  foreground=DARK_FG, font=FONT_UI,
                    relief='flat', borderwidth=0)
    style.map('TButton',
              background=[('active', DARK_ACCENT)],
              foreground=[('active', '#ffffff')])

    style.configure('TEntry',      fieldbackground=DARK_INPUT_BG, foreground=DARK_FG,
                    insertcolor=DARK_FG)
    style.configure('TScrollbar',  background=DARK_BG3,  troughcolor=DARK_BG2,
                    arrowcolor=DARK_FG_DIM)
    style.configure('TSeparator',  background=DARK_BORDER)

    style.configure('TCombobox',
                    fieldbackground=DARK_INPUT_BG,
                    background=DARK_BG3,
                    foreground=DARK_FG,
                    selectbackground=DARK_ACCENT,
                    selectforeground='#ffffff',
                    arrowcolor=DARK_FG_DIM)
    style.map('TCombobox',
              fieldbackground=[('readonly', DARK_INPUT_BG)],
              foreground=[('readonly', DARK_FG)])

    style.configure('Treeview',
                    background=DARK_BG2,
                    foreground=DARK_FG,
                    fieldbackground=DARK_BG2,
                    font=FONT_UI,
                    rowheight=22)
    style.configure('Treeview.Heading',
                    background=DARK_BG3,
                    foreground=DARK_FG,
                    font=FONT_UI)
    style.map('Treeview',
              background=[('selected', DARK_ACCENT)],
              foreground=[('selected', '#ffffff')])
