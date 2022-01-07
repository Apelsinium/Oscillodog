from tkinter import *
import pyaudio
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import messagebox
import datetime
import sys

#Defining default settings and settings
default_settings = {
    "RATE": 44100,
    "CHUNK": 4096,
    "treshold": 0,
    "d": 5,
    "cluster_size": 200,
    "avg_samples": 15
}

settings = default_settings

#Some basic technical vars for pyaudio
FORMAT=pyaudio.paInt16                      #Input format
CHANNELS=1                                  #Number of channels
RATE=settings["RATE"]               #Sampling frequency
CHUNK=settings["CHUNK"]             #Number of points taken each stream cycle

#Initialisation of pyaudio, opening the stream
p = pyaudio.PyAudio()
def stream_open():
    global stream
    stream=p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        output=True,
        frames_per_buffer=CHUNK
    )
stream_open()


# X screen margin and therefore X screen size (in points)
xmarg=1000
SCR=CHUNK-xmarg

# Defining some oscilloscope var
a=0.0000005
b=0.012
treshold=settings["treshold"]
d=settings["d"]
cluster_size=settings["cluster_size"]
k=0
avg_samples=settings["avg_samples"]
avgbuffer=[]
input_raw=np.frombuffer(stream.read(CHUNK),dtype=np.int16).tolist()
avg=((0,)*CHUNK)
errormsg=""
Ymax=50
Xmax=SCR

# Variable changer function
def update_vars():
    global RATE, CHUNK, avg_samples, cluster_size, treshold, d
    RATE=settings["RATE"]               #Sampling frequency
    CHUNK=settings["CHUNK"]             #Number of points taken each stream cycle
    avg_samples=settings["avg_samples"]
    cluster_size=settings["cluster_size"]
    treshold=settings["treshold"]
    d=settings["d"]

# OSCILLOSCOPE FUNCTIONS

# Finding ascending points near a treshold
def phase(inp):
    global sync, errormsg, on_off, a, b
    try:
        treshold_raw = int((np.sqrt(b**2+4*a*treshold)-b)/(2*a)) # Since phase function works with raw data in abstract units which are not a linear function from woltage, we need to solve a quadratic equasion
    except ValueError:
        messagebox.showerror("Input error", "Input error: please enter a non-zero value")
        on_off = not on_off
        a=0.0000005
        b=0.012
        treshold_raw=0
        var_changer("treshold", 0, False)
    #No sync
    if sync=="0":
        return [0]
    #Ascending sync
    if sync=="up":
        out=[]
        for i, n in enumerate(inp[d:-d]):
            if n>treshold_raw and inp[i+d]>treshold_raw and inp[i-d]<treshold_raw:
                out.append(i)
        length=len(out)
        if length<1:
            errormsg="Sync error: check treshold or unperiodic signal"
            return [0]
        if  out[0]>0:
            out.append(out[0])
        for i in range(len(out)-1):
            if out[i+1]-out[i]>cluster_size:     #Checking if the points are in the same cluster of points. If not - the next one is the first from another cluster
                out.append(out[i+1])
        out=out[length:]
        if len(out)<1:
            errormsg="Sync error: check treshold or unperiodic signal"
            return [0]
        return out
    #Descending sync
    if sync=="dwn":
        out=[]
        for i, n in enumerate(inp[d:-d]):
            if n<treshold_raw and inp[i+d]<treshold_raw and inp[i-d]>treshold_raw:
                out.append(i)
        length=len(out)
        if length<1:
            errormsg="Sync error: check treshold or unperiodic signal"
            return [0]
        # !!!WARNING!!! CRIPPLED FUNCTION!
        if  out[0]>0:
            out.append(out[0])
        for i in range(len(out)-1):
            if out[i+1]-out[i]>cluster_size:     #Checking if the points are in the same cluster of points. If not - the next one is the first from another cluster
                out.append(out[i+1])
        out=out[length:]
        if len(out)<1:
            errormsg="Sync error: check treshold or unperiodic signal"
            return [0]
        return out
    

#Detecting the period of our function
def T(inp):
    if len(inp)>1:
        return (inp[-1]-inp[0])//(len(inp)-1)
    else:
        return "N/A"


# Averaging modules
# Collecting an array for averaging
def avarray(inp, array,samples):
    global k
    if len(array)<samples:
        array.append(inp)
    else:
        if k<samples:
            array[k]=inp
            k+=1
        else:
            k=0
            array[k]=inp
            k+=1
    return array


# Averaging
def averaging(inp):
    return [sum(i)/len(i) for i in zip(*inp)]

# PLOTTING

def plot():
    global on_off
    global start_button
    global avgbuffer
    global avg_samples
    global freqstate
    global errormsg
    onoff()
    start_button.grid_forget()
    stop_button = Button(command = onoff,
                     height = 2, 
                     width = 10,
                     text = "STOP",
                     padx=5, pady=5)
    stop_button.grid(row=8, column=0)

    # Save plot button
    saveplot_button = Button(command = lambda: save_plot(plotinput, avg),
                     text = "Save plot",
                     width=20)
    saveplot_button.grid(row=8, column=1, sticky=N, pady=5)

    # Oscilloscope loop
    while on_off:
        input_raw=np.frombuffer(stream.read(CHUNK),dtype=np.int16).tolist()
        # Synchronization module
        dfi=phase(input_raw)
        if dfi[0]>xmarg:
            dfi[0]=0
            errormsg="Sync error: signal frequency is too low. Check scale"
        plotinput=input_raw[dfi[0]:SCR+dfi[0]]
        
        plotinput=transit(plotinput)

        # This thing is responsible for averaging
        if avg_samples>0 and sync_check.get()==1:
            average.set_visible(True) # Maybe find an alternative? A some kind of check maybe?
            avgbuffer=avarray(plotinput,avgbuffer,avg_samples)
            avg=averaging(avgbuffer)
            average.set_ydata(avg)
        else:
            average.set_visible(False)
        signal.set_ydata(plotinput)

        # Period and therefore frequency detecting
        if freqstate=="main":
            t=T(dfi)
        elif freqstate=="avg":
            t=T(phase(avg))
        try:
            freq=format(RATE/t, ".2f")
        except TypeError:
            freq="N/A"

        # Status bar
        statusbar=Label(root, text=errormsg, fg="red", bd=1, relief=SUNKEN, anchor=W)
        statusbar.grid(row=9, column=0, sticky=W+E)
        statusbar=Label(root, text=f"Freq= {freq}", bd=1, relief=SUNKEN, anchor=E)
        statusbar.grid(row=9, column=1, sticky=W+E)
        errormsg=""

        # Drawing on the canvas object
        fig.canvas.flush_events()
        fig.canvas.draw()


    stop_button.grid_forget()
    start_button.grid(row=8, column=0)


# "Translating" raw data from sound card to milivolts. ADD CUSTOM FUNCTION!
def transit(inp):
    out=[]
    for n in inp:
        out.append(a*n**2+b*n)
    return out

# Plot initialization

def plot_init():
    global fig, signal, average, cut, SCR, avgbuffer, Y_entry, X_entry, treshold
    SCR=CHUNK-xmarg
    # !!!WIDGET!!!
    input_raw=np.frombuffer(stream.read(CHUNK),dtype=np.int16).tolist()
    avg=((0,)*CHUNK)
    fig = Figure(figsize = (7, 7), dpi = 100, facecolor="#f0f0f0")
    graph = fig.add_subplot(111, facecolor='#000000')
    signal, = graph.plot(input_raw[:SCR], color="#00ff7f", linewidth=0.75)
    average, = graph.plot(avg[:SCR], color="white", linewidth=0.75)
    cut, = graph.plot(0, treshold, linestyle="", marker=">", markersize=15, color="red")

    canvas = FigureCanvasTkAgg(fig, master = plot_frame)  

    Xseconds=round(1000*Xmax/RATE)
    graph.set_ylim([-Ymax, Ymax])
    graph.set_xlim([0,Xmax])
    avgbuffer=[]

    # Grid management
    ticks=[np.arange(0, Xmax, Xmax//10),np.arange(-Ymax, Ymax, Ymax//5)]
    #Major ticks
    graph.set_xticks([0,Xmax//2,Xmax])
    graph.set_xticklabels(["",f"{Xseconds//10} msec between ticks",f"{Xseconds} msec"])
    graph.set_yticks([-Ymax,0,Ymax])
    graph.grid(which="major", axis="both")
    #Minor ticks
    graph.set_xticks(ticks[0], minor=True)
    graph.set_yticks(ticks[1], minor=True)
    graph.grid(which="minor", axis="both", alpha=0.3)

    # Y scale entry widget
    Label(plot_frame, text="Voltage range").grid(row=0, column=0, sticky=NW)
    Y_entry = Entry(plot_frame, borderwidth=1)
    Y_entry.bind('<Return>', change_Ymax)
    Y_entry.grid(row=1, column=0, sticky=NW)
    Y_entry.insert(0, Ymax)

    # X scale entry widget
    Label(plot_frame, text="Time range, msec").grid(row=2, column=1, sticky=SE)
    X_entry = Entry(plot_frame, borderwidth=1)
    X_entry.bind('<Return>', change_Xmax)
    X_entry.grid(row=3, column=1, sticky=SE)
    X_entry.insert(0, f"{Xseconds}")

    canvas.draw()
    # !!!WIDGET!!!
    canvas.get_tk_widget().grid(row=1, column=0, rowspan=2, columnspan=2)


# GUI functions

def var_changer(var, value, reset):
    global settings
    global avgbuffer
    try:
        settings[var] = int(value)
    except ValueError:
        messagebox.showerror("Input error", "Input error: please enter an integer value")
    if reset==True:
        stream_open()
        plot_init()
        for widget in plot_frame.winfo_children():
            widget.forget()

    if var=="avg_samples":
        avgbuffer=[]
    update_vars()
    if var=="treshold":
        cut.set_ydata(treshold)

def change_Xmax(inp):
    global Xmax
    try:
        Xmax=int(float(X_entry.get())*RATE/1000)
    except ValueError:
        messagebox.showerror("Input error", "Input error: please enter an integer value")
    stream_open()
    for widget in plot_frame.winfo_children():
        widget.forget()
    plot_init()

def change_Ymax(inp):
    global Ymax
    try:
        Ymax=int(Y_entry.get())
    except ValueError:
        messagebox.showerror("Input error", "Input error: please enter an integer value")
    for widget in plot_frame.winfo_children():
        widget.forget()
    plot_init()

def onoff():
    global on_off
    on_off=not on_off

def change_sync(inp):
    global sync
    sync=inp

def change_freq(inp):
    global freqstate
    freqstate=inp

def save_plot(inp1, inp2):
    filename=datetime.datetime.now().strftime("%d-%b-%Y %H-%M-%S")
    output_file=open(f"plot {filename}.txt","w")
    for i, n in enumerate(map(list, zip(*[inp1,inp2]))):
        output_file.write(str(i+1)+", "+str(n[0])+", "+str(n[1])+"\n")

# Starting GUI
root=Tk()
root.title("Oscillodog")
root.iconbitmap('oscillodog.ico')

def on_closing():
    global on_off
    on_off=not on_off
    sys.exit()

root.protocol("WM_DELETE_WINDOW", on_closing)

# GUI variables
on_off=FALSE
syncmode=StringVar()
syncmode.set("up")
sync_modes=[
    ("No trigger, no sync","0"),
    ("By ascending edge","up"),
    ("By descending edge","dwn")
]
sync="up"

freqmode=StringVar()
freqmode.set("main")
freq_modes=[
    ("By main signal", "main"),
    ("By averaged signal", "avg")
]
freqstate="main"


# Sync frame widget
sync_frame = LabelFrame(root, text="Trigger by:", padx=15, pady=15)
sync_frame.grid(row=0, column=1, padx=10, pady=10, sticky=W+E)

# Sync radiobuttons
for text, mode in sync_modes:
    Radiobutton(sync_frame,
        text=text,
        variable=syncmode,
        value=mode,
        command=lambda: change_sync(syncmode.get())
    ).pack(anchor=W)


# Freq type widget frame
freq_frame = LabelFrame(root, text="Frequency measurment", padx=10, pady=10)
freq_frame.grid(row=1, column=1, padx=10, pady=10, sticky=W+E)

# Freq type radiobuttons
for text, mode in freq_modes:
    Radiobutton(freq_frame,
        text=text,
        variable=freqmode,
        value=mode,
        command=lambda: change_freq(freqmode.get())
    ).pack(anchor=W)


# treshold menu
treshold_label = Label(root, text="Treshold value:")
treshold_label.grid(row=2, column=1, sticky=S)
treshold_entry = Entry(root, borderwidth=1)
treshold_entry.bind('<Return>', lambda x: var_changer("treshold", treshold_entry.get(), False))
treshold_entry.grid(row=3, column=1, sticky=N)
treshold_entry.insert(0, treshold)

# Averaging menu
sync_check = IntVar()
avg_check = Checkbutton(root, text = "Enable averaging", variable = sync_check)
avg_check.grid(row=4, column=1, sticky=S)

avg_label = Label(root, text="Averaging samples:")
avg_label.grid(row=5, column=1, sticky=S)

avg_entry = Entry(root, borderwidth=1)
avg_entry.bind('<Return>', lambda x: var_changer("avg_samples", avg_entry.get(), False))
avg_entry.grid(row=6, column=1, sticky=N)
avg_entry.insert(0, avg_samples)

# Advanced settings window
def adv_settings():
    global sampling_entry, a_entry, b_entry, chunk_entry, d_entry, cluster_entry
    menu = Toplevel()
    menu.title("Advanced settings")
    menu.iconbitmap('oscillodog.ico')
    #menu.iconbitmap('/path/to/ico/icon.ico')
    Label(menu,
        text="Warning! These settings CAN break the program.\nChange them on your own risk!"
    ).grid(row=0, column=0, columnspan=3)

    # Audiosettings frame
    audiosettings_frame = LabelFrame(menu, text="Audio sampling settings", padx=15, pady=15)

    Label(audiosettings_frame, text="Sampling frquency").grid(row=0, column=0)
    sampling_entry = Entry(audiosettings_frame, borderwidth=1)
    sampling_entry.bind('<Return>', lambda x: var_changer("RATE", sampling_entry.get(), True))
    sampling_entry.grid(row=0, column=1)
    sampling_entry.insert(0, RATE)

    Label(audiosettings_frame, text="Data chunk size").grid(row=1, column=0)
    chunk_entry = Entry(audiosettings_frame, borderwidth=1)
    chunk_entry.bind('<Return>', lambda x: var_changer("CHUNK", chunk_entry.get(), True))
    chunk_entry.grid(row=1, column=1)
    chunk_entry.insert(0, CHUNK)

    # Oscilloscope frame
    scope_frame = LabelFrame(menu, text="oscilloscope settings", padx=15, pady=15)

    Label(scope_frame, text="Freq detecting indent").grid(row=0, column=0)
    d_entry = Entry(scope_frame, borderwidth=1)
    d_entry.bind('<Return>', lambda x: var_changer("d", d_entry.get(), False))
    d_entry.grid(row=0, column=1)
    d_entry.insert(0, d)

    Label(scope_frame, text="Freq detecting cluster size").grid(row=1, column=0)
    cluster_entry = Entry(scope_frame, borderwidth=1)
    cluster_entry.bind('<Return>', lambda x: var_changer("cluster_size", cluster_entry.get(), False))
    cluster_entry.grid(row=1, column=1)
    cluster_entry.insert(0, cluster_size)

    audiosettings_frame.grid(row=1, column=0, sticky=W+E)
    scope_frame.grid(row=2, column=0, sticky=W+E)

    # Approximation function frame
    approx_frame = LabelFrame(menu, text="Quadratic approximation function a*x^2+b*x", padx=15, pady=15)
    Label(approx_frame, text="a").grid(row=0, column=0)
    a_entry = Entry(approx_frame, borderwidth=1)
    a_entry.bind('<Return>', approx_changer)
    a_entry.grid(row=0, column=1)
    a_entry.insert(0, format(a, ".7f"))

    Label(approx_frame, text="a").grid(row=0, column=2)
    b_entry = Entry(approx_frame, borderwidth=1)
    b_entry.bind('<Return>', approx_changer)
    b_entry.grid(row=0, column=3)
    b_entry.insert(0, format(b, "f"))

    Label(scope_frame, text="Freq detecting cluster size").grid(row=1, column=0)
    cluster_entry = Entry(scope_frame, borderwidth=1)
    cluster_entry.bind('<Return>', lambda x: var_changer("cluster_size", cluster_entry.get(), False))
    cluster_entry.grid(row=1, column=1)
    cluster_entry.insert(0, cluster_size)

    audiosettings_frame.grid(row=1, column=0, sticky=W+E)
    scope_frame.grid(row=2, column=0, sticky=W+E)
    approx_frame.grid(row=3, column=0, sticky=W+E)

    Button(menu, text="Done", command=menu.destroy).grid(row=7, column=0)

def approx_changer(x):
    global a, b
    try:
        a=float(a_entry.get())
        b=float(b_entry.get())
    except ValueError:
        messagebox.showerror("Input error", "Input error: please enter an integer value")

# Advanced settings button
settings_button = Button(command = adv_settings,
                     text = "Advanced settings",
                     width=20)
settings_button.grid(row=7, column=1, sticky=S)

# Plot frame widget
plot_frame = LabelFrame(root, text="Plot", padx=5, pady=5)
plot_frame.grid(row=0, column=0, rowspan=9, padx=10, pady=0)

start_button = Button(command = plot,
                     height = 2, 
                     width = 10,
                     text = "START",
                     padx=5, pady=5)
start_button.grid(row=8, column=0)

plot_init()
plot()

root.mainloop()
p.terminate()