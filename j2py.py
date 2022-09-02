# ## P2J - Python 2 Jupyter utility script
# ## TODO LIST
# ### j2py
# - add options
# - build shebangs from python version info
# - improve matches
# ### GUI
# -   add icon
# -   add options
# -   add confirmation button if a file is going to be overwritten

# run this script to convert easily and reversably scripts and notebooks, while keeping the formatted cells, comments and outputs
# In[1]:
import os
import sys
import re
import random as rnd
import json
from copy import deepcopy
from pathlib import Path

TITLE = r"""
______  ___
| ___ \|_  |
| |_/ /  | |
|  __/2  | |
| |  /\__/ /
\_|  \____/
"""


class reg():
    """Store here all the regexes used in the script"""
    blank = r"^\s*$"
    code_separator = r"^# In\[([\d\s]*)\]:?.*"
    markdown = r"# (#.*\n)"
    scriptrow = r"^(\s*)(.+)$"
    start = r"(#.*!\/usr\/.*)|# coding.*|^$"


OPTIONS = {
    'noisy': True,
    'confirm_overwrite': False,
    'j2p': {
        # TODO implement options for j2py
        'keep_outputs': False,  # NA
        'separate_markdown': True,  # NA
        'keep_separators': True,  # NA
    },
    'p2j': {
        'blank_separators': False,  # use blank rows to separate cells
        'in_separators': True,  # use In[ ] to separate code
        'markdown_separators': True,  # use # #text to separate markdown
    }
}

script_cell_template = {
    "cell_type": "",  # code, markdown or raw
    "execution_count": None,
    "id": "",
    "metadata": {},
    "outputs": [],
    "source": []
}

notebook_info = {
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3 (ipykernel)",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "codemirror_mode": {
                "name": "ipython",
                "version": sys.version_info.major
            },
            "file_extension": ".py",
            "mimetype": "text/x-python",
            "name": "python",
            "nbconvert_exporter": "python",
            "pygments_lexer": "ipython3",
            "version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        }
    },
    "nbformat": 4,
    "nbformat_minor": 5
}


def pairwise(ls):
    it = iter(ls)
    for el in it:
        yield el, next(it)


def gen_id(chars: str = "abcdefghijklmnopqrstuvwxyz0123456789",
           lens: list = [8, 4, 4, 4, 12],
           sep: str = "-"):
    return sep.join("".join(rnd.choice(chars) for i in range(l)) for l in lens)


def convert_name(s):
    if '.ipynb' in s:
        return s.replace('.ipynb', '.py')
    elif '.py' in s:
        return s.replace('.py', '.ipynb')
    elif s == 'demo':
        return s
    else:
        raise BaseException(
            f"{s} not recognized among the possible parameters - py or ipynb")


def p(*args, noise=2, **kwargs):
    if OPTIONS['noisy']:
        print(*args, **kwargs)


# In[3]:
def py2j(dir_input: str, dir_output: str):
    print(dir_input, '->', dir_output)
    with open(dir_input) as py:
        rows = py.readlines()
        iterrows = iter(rows)
        # print(rows)

    split_cells = []
    cur = deepcopy(script_cell_template)  # cur is a single Jupyter cell
    cur['id'] = gen_id()
    cur['cell_type'] = 'code'
    cur['source'] = []
    start = True
    for row in iterrows:
        # if a cell at the beginning contains only comments, transform it into a markdown cell
        # ignore all beginning rows containing shebangs (for now, TODO improve using the info for the script itself?)
        if start:
            if re.match(reg.start, row):
                continue
            else:
                start = False
        # check if the rows contain the console separator '# In[int]:', or a markdown title separator '# #something'
        space_sep = re.match(reg.blank, row)
        # when a blank space is encountered, iterate next cells and evaluate whether the next one is a valid py script
        if space_sep and OPTIONS['p2j']['blank_separators']:
            temp = ['\n']
            for temprow in iterrows:
                if re.match(reg.blank, temprow):
                    temp.append(temprow)
                else:
                    # TODO duplicate match definition. not soo good
                    rowmatch = re.match(reg.scriptrow, temprow).groups()
                    if rowmatch[0] == '':
                        # all the past rows are just useless blank
                        # a new cell is created here
                        if cur['source']:
                            split_cells.append(cur)
                        cur = deepcopy(script_cell_template)
                        cur['id'] = gen_id()
                        cur['cell_type'] = 'code'
                        # p(f'BLANK ROWS DELETION!')
                    else:
                        # this row and the previous ones are part of a function
                        # better not break them
                        ...
                        # p(f'BLANK ROWS SAVED! {rowmatch[1:]}')

                    cur['source'].extend(temp)
                    break
            row = temprow
            # p(temprow)

        cell_sep = re.match(reg.code_separator, row)
        mkdn_sep = re.match(reg.markdown, row)
        # when a cell separator is hit, split_cells gets updated and a new cell is generated
        if cell_sep and OPTIONS['p2j']['in_separators']:
            if cur['source']:
                split_cells.append(cur)
            cur = deepcopy(script_cell_template)
            cur['id'] = gen_id()
            cur['cell_type'] = 'code'
            cur['execution_count'] = cell_sep[1] if cell_sep[1] != ' ' else None
            continue
        # when a markdown separator is hit, a new cell is generated only if the current one isn't already a md cell
        elif mkdn_sep and cur['cell_type'] != 'markdown' and OPTIONS['p2j']['markdown_separators']:
            if cur['source']:
                split_cells.append(cur)
            cur = deepcopy(script_cell_template)
            cur['id'] = gen_id()
            cur['cell_type'] = 'markdown'
            cur['source'].append(mkdn_sep[1])
            # p(repr(mkdn_sep[1]), repr(mkdn_sep), repr(row))
        else:
            if cur['cell_type'] != 'markdown':
                cur['source'].append(row)
            else:
                try:
                    cur['source'].append(re.match(r"# (.*)", row)[1])
                except:
                    cur['source'].append(row)
            # p('--added', repr(row), end='\n')
    else:
        split_cells.append(cur)

    # final json output
    json_output = {
        "cells": split_cells,
        **notebook_info
    }

    with open(dir_output, 'w') as out_file:
        out_file.write(json.dumps(json_output, indent=True))
        p(f"saved to file {dir_output}")


def j2py(dir_input: str, dir_output: str):
    print(dir_input, '->', dir_output)
    with open(dir_input) as nb:
        nb_dict = json.loads(nb.read())
    cells: list = nb_dict['cells']
    cell_rows = []
    for cell in cells:
        if cell['cell_type'] == 'code':
            exec_count = cell.get('execution_count', None)
            exec_count = exec_count if exec_count else ' '
            cell_rows.append(f"# In[{exec_count}]:\n")

            for row in cell.get('source', []):
                cell_rows.append(fixrow(row))

        else:
            for row in cell.get('source', []):
                cell_rows.append(f"# {fixrow(row)}")

    with open(dir_output, 'w') as py_out:
        py_out.write(''.join(cell_rows))


def runconversion(dir_input: str, dir_output: str):
    print(f"Script conversion started")
    print(f"{dir_input} --> {dir_output}")

    if dir_input.endswith('.py') and dir_output.endswith('.ipynb'):
        py2j(dir_input, dir_output)
    elif dir_input.endswith('.ipynb') and dir_output.endswith('.py'):
        j2py(dir_input, dir_output)
    elif dir_input != '' and dir_output == '':
        runconversion(dir_input, convert_name(dir_input))
    else:
        raise Exception(
            f"Invalid names for conversion: {dir_input} and {dir_output}")


def demo(truename=False):
    # TODO deprecate
    py2j('j2py.py', 'j2py_demo.ipynb')
    j2py('j2py_demo.ipynb', 'j2py_demo.py')
    for i in range(50):
        py2j('j2py_demo.py', 'j2py_demo.ipynb')
        j2py('j2py_demo.ipynb', 'j2py_demo.py')


def fixrow(s):
    '''add a newline at the end of a row, if missing'''
    if s == '' or s is None:
        return '\n'
    if s[-1] != '\n':
        return s + '\n'
    return s


def simplewindowselect():
    # TODO deprecate
    import tkinter as tk
    from tkinter import ttk
    from tkinter.filedialog import askopenfilename
    from tkinter.simpledialog import askstring
    # Store the path to the selected file
    tk.Tk().withdraw()  # Do not show root window as tk
    start_folder = Path('.')
    startfile = askopenfilename(initialdir=start_folder)

    if startfile == '':
        print('You did not select any file.')
        input('Press enter to close...')
    else:
        print('Source selected: ' + startfile)
        outputfile = askstring(
            "Output file name",
            prompt=f"Select the name for the output file",
            initialvalue=convert_name(startfile))
        print(outputfile)
        runconversion(startfile, outputfile)

    print("Done")


def guimode():
    import tkinter as tk
    from tkinter import ttk
    from tkinter.filedialog import askopenfilename, askdirectory

    # configure UI
    gui = tk.Tk()
    gui.resizable(True, True)
    gui.title("P2J")
    gui.rowconfigure(0, weight=10)
    gui.columnconfigure(0, weight=10)

    # input
    inputframe = ttk.Frame(gui, height=10, width=10,
                           padding="3 3 20 20")
    inputframe.grid(column=0, row=0, sticky="nw")
    inputvalue = tk.StringVar(master=inputframe)
    inputtext = ttk.Entry(inputframe, width=50,
                          textvariable=inputvalue)
    inputtext.grid(column=1, row=0, sticky='nwe')
    inputbutton = ttk.Button(inputframe, text="Input file",
                             command=lambda: openfile('in'))
    inputbutton.grid(column=0, row=0)

    # output
    outputvalue = tk.StringVar(master=inputframe)
    outputtext = ttk.Entry(inputframe, width=50,
                           textvariable=outputvalue)
    outputtext.grid(column=1, row=1, sticky='nwe')
    outputbutton = ttk.Button(inputframe, text="Output file",
                              command=lambda: openfile('out'))
    outputbutton.grid(column=0, row=1)

    runbutton = ttk.Button(inputframe, text="Convert",
                           command=lambda: runconversion(inputvalue.get(),
                                                         outputvalue.get()))
    runbutton.grid(column=0, row=2, sticky="nw")

    # option buttons
    p2joptions = ttk.Frame(gui, height=10, width=10, padding="3 3 20 20")
    p2joptions.grid(column=1, row=0, sticky='nw', rowspan=3)
    tk.Label(p2joptions, text="Py->J Options").grid(row=0,
                                                    column=0, sticky='nw')
    p2jboxes = {}
    j2poptions = ttk.Frame(gui, height=10, width=10, padding="3 3 20 20")
    j2poptions.grid(column=2, row=0, sticky='nw', rowspan=3)
    tk.Label(j2poptions, text="J->Py Options").grid(row=0,
                                                    column=0, sticky='nw')
    j2pboxes = {}

    def refresh_options(var, index, mode):
        """Callback for option editing"""
        print("OPTIONS EDITED")
        for k, v in p2jboxes.items():
            OPTIONS['p2j'][k] = p2jboxes[k].get()
        for k, v in j2pboxes.items():
            OPTIONS['j2p'][k] = j2pboxes[k].get()
        print(OPTIONS)

    for i, k in enumerate(OPTIONS['p2j'].keys()):
        bol = tk.BooleanVar(value=OPTIONS['p2j'][k])
        tk.Checkbutton(p2joptions,
                       text=k,
                       variable=bol,
                       onvalue=True,
                       offvalue=False,
                       ).grid(column=0, row=i+1, sticky="nw")
        bol.trace_add(mode='write',
                      callback=refresh_options)
        p2jboxes[k] = bol
    for i, k in enumerate(OPTIONS['j2p'].keys()):
        bol = tk.BooleanVar(value=OPTIONS['j2p'][k])
        tk.Checkbutton(j2poptions,
                       text=k,
                       variable=bol,
                       onvalue=True,
                       offvalue=False,
                       state=tk.DISABLED,
                       ).grid(column=0, row=i+1, sticky="nw")
        bol.trace_add(mode='write',
                      callback=refresh_options)
        j2pboxes[k] = bol

    def openfile(var='in'):
        # TODO REWRITE HORRIBLE METHOD
        if var == 'in':
            out = Path(askopenfilename(initialdir='.'))
            inputvalue.set(out)
            outputvalue.set(convert_name(str(out)))
        else:
            out = Path(askdirectory(initialdir='.'))
            outputvalue.set(
                out.parent / convert_name(str(Path(inputvalue.get()).name)))

    gui.mainloop()
    print("Gui closed")
    print("END")


# In[4]:


def print_help():
    print(TITLE)
    print("P2J conversion utility")
    print("Instructions for use")

# In[13]:


def main():
    if len(sys.argv) == 1:
        print("Window select called")
        # simplewindowselect()
        guimode()
        return

    # parse arguments
    iargs = iter(sys.argv[1:])
    dargs = {'files': []}
    for a in iargs:
        print(a)
        if a in ['-h', '--h']:
            print_help()
            return
        elif a == '-w':
            # simplewindowselect()
            guimode()
            return
        elif a == '-m':
            # MANUAL MODE
            print(TITLE)
            print('Manual Mode')
            dir_input = input(
                "Please insert the input file name (must be a .py or .ipynb file).")
            dir_output = input(
                f"Please insert the name of the output file (same name by default).")
            if dir_output == '':
                dir_output = convert_name(dir_input)
            dargs['files'] = [dir_input, dir_output]
        elif a in ['--use-blanks']:
            OPTIONS['p2j']['blank_separators'] = True
        elif a in ['--ignore-ins']:
            OPTIONS['p2j']['in_separators'] = True
        elif a in ['--no-markdown']:
            OPTIONS['p2j']['markdown_separators'] = True
        else:
            dargs['files'].append(a)

    print(dargs)

    assert len(dargs['files']) > 0, "You must select at 1 file to convert"

    if len(dargs['files']) & 1 == 1:  # evenize the file arguments
        dargs['files'].append(convert_name(dargs[-1]))

    for inputfile, outputfile in pairwise(dargs['files']):
        runconversion(inputfile, outputfile)


if __name__ == '__main__':
    main()
