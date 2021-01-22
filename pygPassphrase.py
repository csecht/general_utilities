#!/usr/bin/env python3

"""
A utility to create random passphrases and passwords.
Inspired by code from @codehub.py via Instagram.
"""
import os
import random
import re
import sys
from string import digits, punctuation, ascii_letters, ascii_uppercase
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import messagebox
    import tkinter.ttk as ttk
except (ImportError, ModuleNotFoundError) as error:
    print('GUI requires tkinter, which is included with Python 3.7 and higher'
          '\nInstall 3.7+ or re-install Python and include Tk/Tcl.'
          f'\nSee also: https://tkdocs.com/tutorial/install.html \n{error}')

PROGRAM_VER = '0.2.2'
STUBRESULT = 'Result can be copied and pasted'
SYMBOLS = "~!@#$%^&*_-"
MY_OS = sys.platform[:3]
# MY_OS = 'win' # TESTING
SYSWORDS_PATH = Path('/usr/share/dict/words')
EFFWORDS_PATH = Path('eff_large_wordlist.txt')


class Generator:
    """
    A GUI window for user to specify length of passphrases and passwords.
    """
    def __init__(self, master):
        """Window layout and default values are set up here.
        """
        self.master = master
        self.master.bind("<Escape>", lambda q: quit_gui())
        self.master.bind("<Control-q>", lambda q: quit_gui())
        self.master.bind("<Control-g>", lambda q: self.make_pass())

        # main window background color, also used for some labels.
        self.master_bg = 'SkyBlue4'
        self.master_fg = 'LightCyan2'  # foreground for user entry labels
        self.frame_bg = 'grey40'  # background for data labels and frame
        self.frame_fg = 'grey90'
        self.passstub_fg = 'grey60'
        self.pass_fg = 'brown4'
        self.pass_bg = 'khaki2'

        # Variables used in setup_window(), in order of appearance:
        #  Don't make an EFF checkbutton in Windows b/c EFF words are default.
        if MY_OS in 'lin, dar':
            self.eff = tk.BooleanVar()
            self.eff_chk = tk.Checkbutton()
        self.numwords_label = tk.Label()
        self.numwords_entry = tk.Entry()
        self.numchars_label = tk.Label()
        self.numchars_entry = tk.Entry()

        # There are problems of tk.Button text showing up on MacOS, so ttk
        self.generate_btn = ttk.Button(self.master)
        self.quit_btn = ttk.Button(self.master)

        self.result_frame = tk.Frame(self.master)

        self.length_header = tk.Label(self.result_frame)
        self.passphrase_header = tk.Label(self.result_frame)
        self.any_describe = tk.Label(self.result_frame)
        self.any_lc_describe = tk.Label(self.result_frame)
        self.select_describe = tk.Label(self.result_frame)
        self.length_any = tk.IntVar()
        self.length_lc = tk.IntVar()
        self.length_select = tk.IntVar()
        self.length_any_label = tk.Label(self.result_frame)
        self.length_lc_label = tk.Label(self.result_frame)
        self.length_select_label = tk.Label(self.result_frame)
        self.phrase_any = tk.StringVar()
        self.phrase_lc = tk.StringVar()
        self.phrase_select = tk.StringVar()
        self.phrase_any_display = tk.Entry(self.result_frame,
                                           textvariable=self.phrase_any)
        self.phrase_lc_display = tk.Entry(self.result_frame,
                                          textvariable=self.phrase_lc)
        self.phrase_sel_display = tk.Entry(self.result_frame,
                                           textvariable=self.phrase_select)
        self.pw_label = tk.Label(self.result_frame)
        self.pw_any_describe = tk.Label(self.result_frame)
        self.pw_select_describe = tk.Label(self.result_frame)
        self.pw_any = tk.StringVar()
        self.pw_select = tk.StringVar()
        self.pw_any_display = tk.Entry(self.result_frame,
                                       textvariable=self.pw_any,)
        self.pw_select_display = tk.Entry(self.result_frame,
                                          textvariable=self.pw_select)

        # Variables used in get_words():
        self.use_effwords = True
        self.system_words = 'Null'
        self.eff_wordlist = 'None'
        self.eff_list = ['None']
        self.system_list = ['None']

        self.setup_window()

    def setup_window(self) -> None:
        """
        Layout the main window and assign starting values to labels.

        :return: A nice looking interactive graphic.
        """
        self.master.minsize(800, 340)
        self.master.configure(bg=self.master_bg)

        self.result_frame.config(borderwidth=3, relief='sunken',
                                 background=self.frame_bg)
        # self.result_frame.grid(column=0, row=2, columnspan=4, padx=5, pady=5)

        # Create menu instance and add pull-down menus
        menu = tk.Menu(self.master)
        self.master.config(menu=menu)

        file = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="File", menu=file)
        file.add_command(label="Generate", command=self.make_pass,
                         accelerator="Ctrl+G")
        file.add_command(label="Quit", command=quit_gui, accelerator="Ctrl+Q")

        help_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="What are passphrases?",
                              command=self.explain)
        help_menu.add_command(label="About", command=about)

        # Set up user entry and control:
        if MY_OS in 'lin, dar':
            self.eff_chk.config(text='Use EFF word list ',
                                variable=self.eff,
                                fg=self.master_fg, bg=self.master_bg,
                                activebackground='grey80',
                                selectcolor=self.frame_bg)
            # self.eff_chk.grid(column=2, row=0, pady=5, sticky=tk.W)

        if self.use_effwords is False:
            self.eff_chk.config(state='disabled')
        # TODO: adjust griding so these don't move with changing col2 width.
        # OR Freeze Frame size so no geometries change. Widgets in col0 in rows
        #  BELOW the frame stay anchored E, but not in col1.
        self.numwords_label.config(text='Enter # words for passphrase',
                                   fg=self.master_fg, bg=self.master_bg)
        self.numwords_entry.config(width=2)
        self.numwords_entry.insert(0, '5')
        self.numwords_entry.focus()
        self.numchars_label.config(text='Enter # characters for password',
                                   fg=self.master_fg, bg=self.master_bg)
        self.numchars_entry.config(width=3)
        self.numchars_entry.insert(0, 0)

        style = ttk.Style()
        style.map("G.TButton",
                  foreground=[('active', self.pass_fg)],
                  background=[('pressed', self.frame_bg),
                              ('active', self.pass_bg)])
        style.map("Q.TButton",
                  foreground=[('active', 'red')],
                  background=[('pressed', self.frame_bg),
                              ('active', self.pass_bg)],
                  highlightcolor=[('focus', 'green')])
        self.generate_btn.configure(style="G.TButton", text='Generate!',
                                    command=self.make_pass)
        self.quit_btn.configure(style="Q.TButton", text='Quit',
                                command=quit_gui, width=5)

        # Passphrase results section: ########################################
        self.length_header.config(text='Length',
                                  fg=self.frame_fg, bg=self.frame_bg)
        self.passphrase_header.config(text='Passphrases',
                                      fg=self.frame_fg, bg=self.frame_bg)

# TODO: Consider a more readable way to group these variable categories.
        # Set up OS-specific statements.
        if MY_OS in 'lin, dar':
            self.any_describe.config(text="Any words from dictionary",
                                     fg=self.frame_fg, bg=self.frame_bg)
            self.any_lc_describe.config(text="... lower case + 3 characters",
                                        fg=self.frame_fg, bg=self.frame_bg)
            self.select_describe.config(text="... words of 3 to 8 letters",
                                        fg=self.frame_fg, bg=self.frame_bg)

            self.length_select.set(0)
            self.length_select_label.config(textvariable=self.length_select,
                                            width=3)
            # self.length_select_label.grid(column=1, row=5)

            self.phrase_select.set(STUBRESULT)
            self.phrase_sel_display.config(width=50, font='TkFixedFont',
                                           fg=self.passstub_fg,
                                           bg=self.pass_bg)
            # self.phrase_sel_display.grid(column=2, row=5, columnspan=1,
            #                              ipadx=5, padx=5, pady=3, sticky=tk.EW)
        elif MY_OS == 'win':
            self.any_describe.config(   text="Any words from EFF wordlist",
                                        fg=self.frame_fg, bg=self.frame_bg)
            self.any_lc_describe.config(text="...plus 3 characters",
                                        fg=self.frame_fg, bg=self.frame_bg)
            self.select_describe.config(text=" ",
                                        fg=self.frame_fg, bg=self.frame_bg)

        # Statements common to all OS.
        self.length_any.set(0)
        self.length_lc.set(0)
        self.length_any_label.config(textvariable=self.length_any, width=3)
        self.length_lc_label.config( textvariable=self.length_lc,  width=3)
        self.phrase_any.set(STUBRESULT)
        self.phrase_lc.set(STUBRESULT)
        self.phrase_any_display.config(width=50, font='TkFixedFont',
                                       fg=self.passstub_fg, bg=self.pass_bg)
        self.phrase_lc_display.config(width=50, font='TkFixedFont',
                                      fg=self.passstub_fg, bg=self.pass_bg)
        # End passphrase results section: #####################################

        # Password results section:
        self.pw_label.config(text='Passwords',
                             fg=self.frame_fg, bg=self.frame_bg)

        self.pw_any_describe.config(text="Any characters",
                                    fg=self.frame_fg, bg=self.frame_bg)
        self.pw_select_describe.config(text="More likely usable characters ",
                                       fg=self.frame_fg, bg=self.frame_bg)
        self.pw_any.set(STUBRESULT)
        self.pw_select.set(STUBRESULT)
        self.pw_any_display.config(width=50, font='TkFixedFont',
                                   fg=self.passstub_fg, bg=self.pass_bg)
        self.pw_select_display.config(width=50, font='TkFixedFont',
                                      fg=self.passstub_fg, bg=self.pass_bg)

        # Grid structure:
        self.result_frame.grid(      column=0, row=2, padx=5, pady=5,columnspan=4)

        self.numwords_label.grid(    column=0, row=0, padx=5, pady=(5, 0),
                                     sticky=tk.E)
        self.numwords_entry.grid(    column=1, row=0, pady=(5, 0), sticky=tk.W)
        self.numchars_label.grid(    column=0, row=1, padx=5, pady=3,
                                     sticky=tk.E)
        self.numchars_entry.grid(    column=1, row=1, sticky=tk.W)

        self.generate_btn.grid(      column=2, row=1, sticky=tk.W)
        self.quit_btn.grid(          column=0, row=9, padx=5, pady=(2, 5),
                                     sticky=tk.W)

        self.length_header.grid(     column=1, row=2, padx=5, sticky=tk.EW)
        self.passphrase_header.grid( column=2, row=2, padx=5, sticky=tk.W)

        self.any_describe.grid(      column=0, row=3, sticky=tk.E)
        self.any_lc_describe.grid(   column=0, row=4, sticky=tk.E)
        self.select_describe.grid(   column=0, row=5, sticky=tk.E)

        self.length_any_label.grid(  column=1, row=3)
        self.length_lc_label.grid(   column=1, row=4)
        self.phrase_any_display.grid(column=2, row=3, columnspan=1,
                                     ipadx=5, padx=5, pady=3, sticky=tk.EW)
        self.phrase_lc_display.grid( column=2, row=4, columnspan=1,
                                     ipadx=5, padx=5, pady=3, sticky=tk.EW)
        if MY_OS in 'lin, dar':
            self.eff_chk.grid(            column=2, row=0, pady=5, sticky=tk.W)
            self.length_select_label.grid(column=1, row=5)
            self.phrase_sel_display.grid( column=2, row=5, columnspan=1,
                                          ipadx=5, padx=5, pady=3, sticky=tk.EW)

        self.pw_label.grid(          column=2, row=6, padx=5, sticky=tk.W)
        self.pw_select_describe.grid(column=0, row=8,
                                     padx=5, sticky=tk.E)
        self.pw_any_describe.grid(   column=0, row=7,
                                     padx=5, sticky=tk.E)
        self.pw_any_display.grid(    column=2, row=7, columnspan=2, ipadx=5,
                                     padx=5, pady=(6, 3), sticky=tk.EW)
        self.pw_select_display.grid( column=2, row=8, columnspan=2, ipadx=5,
                                     padx=5, pady=(3, 6), sticky=tk.EW)

    def get_words(self) -> None:
        """
        Check which word files are available; populate lists for make_pass().
        """
        # Need to first confirm that required files are present.
        fnf_msg = (
            '\n*** Cannot locate either the system dictionary or EFF wordlist\n'
            'At a minimum, the file eff_large_wordlist.txt should be in '
            'the working directory.\nThat file can is included with:\n'
            'https://github.com/csecht/general_utilities\n'
            'Exiting now...')
        if MY_OS in 'lin, dar':
            if Path.is_file(SYSWORDS_PATH) is False and \
                    Path.is_file(EFFWORDS_PATH) is False:
                print(fnf_msg)
                sys.exit(1)
        elif MY_OS == 'win' and Path.is_file(EFFWORDS_PATH) is False:
            print(fnf_msg)
            sys.exit(1)

        # Need to populate lists with words to randomize in make_pass().
        if MY_OS == 'win':
            self.eff_wordlist = Path(EFFWORDS_PATH).read_text()

        if MY_OS in 'lin, dar':
            if Path.is_file(SYSWORDS_PATH):
                self.system_words = Path(SYSWORDS_PATH).read_text()
            elif Path.is_file(SYSWORDS_PATH) is False:
                notice = ('*** NOTICE: The system dictionary cannot be found.\n'
                          'Using EFF word list ... ***')
                self.system_words = 'Null'
                self.eff_chk.config(state='disabled')
                print(notice)
                messagebox.showinfo(title='File not found',
                                    detail=notice)
            if Path.is_file(EFFWORDS_PATH):
                self.eff_wordlist = Path(EFFWORDS_PATH).read_text()
            elif Path.is_file(EFFWORDS_PATH) is False:
                self.use_effwords = False  # Used in window_setup().
                notice = (
                    '*** EFF large wordlist cannot be found.\n'
                    'That file is included with:\n'
                    'https://github.com/csecht/general_utilities\n'
                    'Using system dictionary... ***\n'
                )
                self.eff_chk.config(state='disabled')
                print(notice)
                messagebox.showinfo(title='File not found',
                                    detail=notice)
            self.system_list = self.system_words.split()

        self.eff_list = self.eff_wordlist.split()

    def make_pass(self) -> None:
        """Generate various forms of passphrases and passwords.
        """
        # Need different passphrase descriptions for sys dict and EEF list.
        # Initial label texts are for sys. dict. and are set in
        # window_setup(), but are modified here if EFF option is used.
        # OS label descriptors are written each time "Generate" command is run.
        if MY_OS in 'lin, dar':
            if self.eff.get() is False:
                self.any_describe.config(   text="Any words from dictionary",
                                            fg=self.frame_fg, bg=self.frame_bg)
                self.any_lc_describe.config(text="... lower case + 3 characters",
                                            fg=self.frame_fg, bg=self.frame_bg)
                self.select_describe.config(text="... words of 3 to 8 letters",
                                            fg=self.frame_fg, bg=self.frame_bg)
                # Show widgets (in case they were removed by EFF True option).
                self.length_select_label.grid()
                self.phrase_sel_display.grid()

            elif self.eff.get() is True:
                self.any_describe.config(   text="Any words from EFF wordlist",
                                            fg=self.frame_fg, bg=self.frame_bg)
                self.any_lc_describe.config(text="...plus 3 characters",
                                            fg=self.frame_fg, bg=self.frame_bg)
                self.select_describe.config(text=" ",
                                            fg=self.frame_fg, bg=self.frame_bg)
                # Hide widgets when EFF option is True.
                self.length_select_label.grid_remove()
                self.phrase_sel_display.grid_remove()

        secure_random = random.SystemRandom()

        # Need to remove words having the possessive form (English dictionary).
        # Remove hyphenated words (~4) from EFF wordlist.
        uniq_words = \
            [word for word in self.system_list if re.search(r"'s", word) is None]
        trim_words = [word for word in uniq_words if 8 >= len(word) >= 3]
        eff_words = [word for word in self.eff_list if word.isalpha()]

        caps = ascii_uppercase
        string1 = ascii_letters + digits + punctuation
        string2 = ascii_letters + digits + SYMBOLS

        allwords = "".join(secure_random.choice(uniq_words) for
                           _ in range(int(self.numwords_entry.get())))
        somewords = "".join(secure_random.choice(trim_words) for
                            _ in range(int(self.numwords_entry.get())))
        effwords = "".join(secure_random.choice(eff_words) for
                           _ in range(int(self.numwords_entry.get())))
        addsymbol = "".join(secure_random.choice(SYMBOLS) for _ in range(1))
        addcaps = "".join(secure_random.choice(caps) for _ in range(1))
        addnum = "".join(secure_random.choice(digits) for _ in range(1))

        # 1st condition evaluates eff checkbutton on, 2nd if no sys dict found.
        # 3rd, if EFF is only choice in Linux/Mac, disable eff checkbutton.
        # There is probably a less confusing way to work these conditions.
        if MY_OS in 'lin, dar' and self.eff.get() is True:
            allwords = effwords
            somewords = effwords
        elif MY_OS == 'win' or self.system_words == 'Null':
            allwords = effwords
            somewords = effwords
            if MY_OS in 'lin, dar':
                self.eff_chk.config(state='disabled')

        passphrase1 = allwords.lower() + addsymbol + addnum + addcaps
        passphrase2 = somewords.lower() + addsymbol + addnum + addcaps
        password1 = "".join(secure_random.choice(string1) for
                            _ in range(int(self.numchars_entry.get())))
        password2 = "".join(secure_random.choice(string2) for
                            _ in range(int(self.numchars_entry.get())))

        # Need to reduce font size of long pass* length in attempt to keep
        # window on screen, then reset to default font size when pass*
        # length is shortened. On Mac Retina monitors, fonts can be very small.
        # Adjust width of results entry widgets to THE longest result string.
        # B/c 'width' is character, not pixel, units, length is not perfect
        #   when font sizes change.
        if len(passphrase1) > 75:
            self.phrase_any_display.config(font=('TkFixedFont', 8),
                                           width=len(passphrase1))
            self.phrase_lc_display.config(font=('TkFixedFont', 8))
            self.phrase_sel_display.config(font=('TkFixedFont', 8))
        elif len(passphrase1) <= 75:
            self.phrase_any_display.config(font='TkFixedFont',
                                           width=len(passphrase1))
            self.phrase_lc_display.config(font='TkFixedFont')
            self.phrase_sel_display.config(font='TkFixedFont')
        if len(password1) > 75:
            self.pw_any_display.config(font=('TkFixedFont', 8),
                                       width=len(password1))
            self.pw_select_display.config(font=('TkFixedFont', 8),
                                          width=len(password2))
        elif len(password1) <= 75:
            self.pw_any_display.config(font='TkFixedFont',
                                       width=len(password1))
            self.pw_select_display.config(font='TkFixedFont',
                                          width=len(password2))

        # No need to set sys dictionary variables or provide eff checkbutton
        # condition for Windows.
        if MY_OS in 'lin, dar':
            if self.eff.get() is False:
                self.phrase_select.set(passphrase2)
                self.length_select.set(len(passphrase2))
            elif self.eff.get() is True:
                self.phrase_select.set('')
                self.length_select.set('')

        elif MY_OS == 'win':
            self.phrase_select.set('')
            self.length_select.set('')

        # Set statements common to all OS eff conditions:
        self.phrase_any.set(allwords)
        self.phrase_lc.set(passphrase1)
        self.length_any.set(len(allwords))
        self.length_lc.set(len(passphrase1))
        self.pw_any.set(password1)
        self.pw_select.set(password2)

        # Change font colors of results from the initial self.passstub_fg.
        self.phrase_any_display.config(fg=self.pass_fg)
        self.phrase_lc_display.config(fg=self.pass_fg)
        self.phrase_sel_display.config(fg=self.pass_fg)
        self.pw_any_display.config(fg=self.pass_fg)
        self.pw_select_display.config(fg=self.pass_fg)

    def explain(self) -> None:
        """Provide information about words used to create passphrases.
        """
        # This duplicates statements from make_pass().  Would require
        # separate method for these variables to consolidate?...
        word_list = self.system_words.split()
        uniq_words = [word for word in word_list if
                      re.search(r"'s", word) is None]
        trim_words = [word for word in uniq_words if 8 >= len(word) >= 3]

        # The formatting of this is a pain.  There must be a better way.
        info = (
"""A passphrase is a random string of words that can be more secure and
easier to remember than a shorter or complicated password.
For more information on passphrases, see, for example, a discussion of
diceware and wordlist selection at the Electronic Frontier Foundation:
https://www.eff.org/deeplinks/2016/07/new-wordlists-random-passphrases

pygPassphrase.py users have an option to use the EFF long wordlist. Windows 
users, however, will use only that list.

The (non-Windows) system dictionary on this computer provides:
"""
f"    {len(word_list)} words of any length, of which\n"
f"    {len(uniq_words)} are unique (not possessive forms of nouns and \n"
f"    {len(trim_words)} unique words of 3 to 8 letters."
"""
Only the unique and size-limited word subsets are used here for passphrases.

Passphrases may include proper names and diacritics found in the dictionary.
There is a choice for three added characters to accommodate password 
requirements of some sites and applications: one symbol, one upper case 
letter, and one number. The symbols used are from this set: """
f'{SYMBOLS}\n'
"""
The word list from Electronic Frontier Foundation (EFF),
https://www.eff.org/files/2016/07/18/eff_large_wordlist.txt, does not contain
proper names or diacritics. Its words are generally shorter and easier to 
spell. Although the EFF list contains 7776 selected words, only 7772 are used 
here by excluding four hyphenated words.
"""
)

        infowin = tk.Toplevel()
        infowin.title('A word about passphrases')
        num_lines = info.count('\n')
        infotxt = tk.Text(infowin, width=85, height=num_lines + 2,
                          background='SkyBlue4', foreground='grey98',
                          relief='groove', borderwidth=5, padx=5)
        infotxt.insert('1.0', info)
        infotxt.pack()


def about() -> None:
    """
    Basic information for count-tasks; called from GUI Help menu.

    :return: Information window.
    """
    # msg separators use em dashes.
    boilerplate = ("""
pygPassphrase.py privately generates passphrases and passwords.
Download the most recent version from: 
https://github.com/csecht/general_utilities

————————————————————————————————————————————————————————————————————
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.\n
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.\n
You should have received a copy of the GNU General Public License
along with this program. If not, see https://www.gnu.org/licenses/
————————————————————————————————————————————————————————————————————\n
            Author:     cecht
            Copyright:  Copyright (C) 2021 C. Echt
            Development Status: 4 - Beta
            Version:    """)  # The version number is appended here.

    num_lines = boilerplate.count('\n')
    aboutwin = tk.Toplevel()
    # aboutwin.minsize(600, 460)
    aboutwin.title('About count-tasks')
    colour = ['SkyBlue4', 'DarkSeaGreen4', 'DarkGoldenrod4', 'DarkOrange4',
              'grey40', 'blue4', 'navy', 'DeepSkyBlue4', 'dark slate grey',
              'dark olive green', 'grey2', 'grey25', 'DodgerBlue4',
              'DarkOrchid4']
    bkg = random.choice(colour)
    abouttxt = tk.Text(aboutwin, width=72, height=num_lines + 2,
                       background=bkg, foreground='grey98',
                       relief='groove', borderwidth=5, padx=5)
    abouttxt.insert('1.0', boilerplate + PROGRAM_VER)
    # Center text preceding the Author, etc. details.
    abouttxt.tag_add('text1', '1.0', float(num_lines - 5))
    abouttxt.tag_configure('text1', justify='center')
    abouttxt.pack()


def quit_gui() -> None:
    """Safe and informative exit from the program.
    """
    print(f'\n  *** User has quit {__file__}. Exiting...\n')
    root.destroy()
    sys.exit(0)


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    root = tk.Tk()
    root.title("Passphrase Generator")
    Generator(root).get_words()
    root.mainloop()
