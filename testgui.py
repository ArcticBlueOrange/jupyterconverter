def runconversion(inputval, outputval):
    print(f"{inputval} ----> {outputval}")

def guimode():
    import tkinter as tk
    from tkinter import ttk
    from tkinter.filedialog import askopenfilename

    # configure UI
    gui = tk.Tk()
    gui.resizable(True, True)
    gui.title("P2J")

    # INPUT
    inputframe = ttk.Frame(gui, height=10, width=10, padding="3 3 20 20")
    inputframe.grid(column=0, row=0)
    inputvalue = tk.StringVar()
    inputtext = ttk.Entry(inputframe, width=30, textvariable=inputvalue)
    inputtext.grid(column=1, row=0)

    # OUTPUT
    outputframe = ttk.Frame(gui, height=10, width=10, padding="3 3 20 20")
    outputframe.grid(column=0, row=1)
    outputvalue = tk.StringVar()
    outputtext = ttk.Entry(outputframe, width=30, textvariable=inputvalue)
    outputtext.grid(column=1, row=1)

    runbutton = ttk.Button(gui, text="Convert",
                           command=lambda: runconversion(inputvalue.get(), outputvalue.get()))
    runbutton.grid(column=0, row=2)

    gui.mainloop()
    print("Gui closed")


guimode()
