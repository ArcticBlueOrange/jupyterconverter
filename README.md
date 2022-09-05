______  ___
| ___ \|_  |
| |_/ /  | |
|  __/2  | |
| |  /\__/ /
\_|  \____/

P2J conversion utility

----------------------------------------------------------------------
This simple script provides a cli and gui for converting .py <--> .ipynb files.  
I made this because I wasn't fully satisfied by the current options available on PyPI.  



The GUI contains all the options available in the text interface and have the same defaults enabled, although some command names may change.  


----------------------------------------------------------------------

USAGE OPTIONS (Command Line)

j2py.py [input_file] [output_file] -w -h -m --use-blanks --ignore-ins --no-markdown --overwrite
 (no arguments) or -w (windowed)
        Will open the gui mode (suggested)
 -h --help
        Prints this message and exits
 -m
        Allows user to insert manually the input and output file
  Jupyter --> Python options:  
--use-blanks
        SPLIT code whenever there are blank lines
--ignore-ins
        IGNORE the In[#] separators when
--no-markdown
        Will NOT try to convert markdown snippets to code
  Python --> Jupyter options:  

  Other options:  
    --overwrite
        Will OVERWRITE the destination file if already in the system