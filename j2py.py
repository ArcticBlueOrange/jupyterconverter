# ## P2J - Python 2 Jupyter utility script

#

# run this script to convert easily and reversably scripts and notebooks, while keeping the formatted cells, comments and outputs
# In[1]:
from asyncio import windows_events
import os
import sys
import re
import datetime as dt
import random as rnd
import json
from pprint import pprint
from copy import deepcopy
from operator import xor
from pathlib import Path
from types import SimpleNamespace

TITLE = r"""
______  ___ 
| ___ \|_  |
| |_/ /  | |
|  __/2  | |
| |  /\__/ /
\_|  \____/ 
"""


class reg():
    blank = r"^\s*$"
    code_separator = r"^# In\[([\d\s]*)\]:?.*"
    markdown = r"# (#.*\n)"
    scriptrow = r"^(\s*)(.+)$"
    start = r"(#.*!\/usr\/.*)|# coding.*|^$"


OPTIONS = {
    'noisy': True,
    'j2p': {
        # TODO implement options for j2py
        # 'keep_outputs': False, #NA
        # 'separate_markdown': True, #NA
        # 'keep_separators':True ,#NA
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


# windowselect()
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
    # pprint(cells)
    for cell in cells:
        if cell['cell_type'] == 'code':
            exec_count = cell.get('execution_count', None)
            exec_count = exec_count if exec_count else ' '
            cell_rows.append(f"# In[{exec_count}]:\n")

            for row in cell.get('source', []):
                cell_rows.append(fixrow(row))

        else:
            # p(f"appending noncode rows:")
            # p(cell.get('source', []))
            for row in cell.get('source', []):
                cell_rows.append(f"# {fixrow(row)}")

    with open(dir_output, 'w') as py_out:
        py_out.write(''.join(cell_rows))

    # TODO use the last parts of the script to build a valid shebang


def demo(truename=False):
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


def windowselect():
    import tkinter
    from tkinter import ttk
    from tkinter.filedialog import askopenfilename
    from tkinter.simpledialog import askstring
    # Store the path to the selected file
    tkinter.Tk().withdraw()  # Do not show root window
    start_folder = Path('.')
    startfile = askopenfilename(initialdir=start_folder)

    if startfile == '':
        print('You did not select any file.')
        input('Press enter to close...')
        # sys.exit()
    else:
        print('Source selected: ' + startfile)
        outputfile = askstring(
            "Output file name",
            prompt=f"Select the name for the output file",
            initialvalue=convert_name(startfile))
        print(outputfile)
        if re.search(r"\.ipynb", startfile):
            j2py(startfile, outputfile)
        else:
            py2j(startfile, outputfile)
        # return (startfile, outputfile)
    print("Done")

# In[4]:


# In[13]:
def main():
    print(TITLE)
    print("P2J conversion utility")
    # demo()
    windowselect()
    return

    if len(sys.argv) == 1 or re.search(r"ipy(nb|kernel)", sys.argv[0]):
        print("Prompt launch")
        dir_input = input(
            "Please insert the input file name (must be a .py or .ipynb file) ")
        dir_output = input(
            f"Please insert the name of the output file ({convert_name(dir_input)} by default) ")
        if dir_output == '':
            dir_output = convert_name(dir_input)
    else:
        dir_input = sys.argv[1]
        if len(sys.argv) >= 2:
            dir_output = sys.argv[2]
        else:
            dir_output = convert_name(dir_input)

    assert dir_input and dir_output, "Missing input and/or output file names"
    if dir_input == 'demo':
        demo(True)

    if '.py' in dir_input and '.ipynb' in dir_output:
        py2j(dir_input, dir_output)
    elif '.ipynb' in dir_input and '.py' in dir_output:
        j2py(dir_input, dir_output)

    p(f"{dir_input}->{dir_output}")


if __name__ == '__main__':
    main()
