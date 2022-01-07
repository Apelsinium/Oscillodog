# Oscillodog
A simple one channel oscilloscope with autotrigger and averaging function I made while learning Python. It takes data from your audio input device (usually microphone)
It uses several libraries: Tkinter, pyaudio, matplotlib and numpy

Functionality:

You can see main controls on the right side of the main screen. From top to bottom:

TRIGGER MENU

There are three options: no trigger, trigger by ascending signal and trigger by descending signal. Trigger by ascending is set by default.

> No trigger: the oscilloscope ignores a piece of code used for synchronization. In this mode it is impossible to determine frequency and averaging is virtually useless.

> By ascending: the progran sets the starting point of the green plot in the first intersection point of signal (green plot) and treshold value (red triangle) on ascending side of the signal.

> By descending: the progran sets the starting point of the green plot in the first intersection point of signal (green plot) and treshold value (red triangle) on descending side of the signal.

FREQUENCY MEASUREMENT OPTIONS

When the input signal is too noisy you can use the averaging feature. Radiobuttons in this menu allow you to choose to measure frequency based on the averaged signal.

THRESHOLD VALUE

The trigger level of the signal, marked by red arrow on the left side of the oscilloscope screen. Determines the level of signal used by the trigger option to detect the ascending (descending) side of te signal. Can lead to synchronization failue if set too high or low.

AVERAGING SECTION

If "Enable averaging" checkbox is checked and "Averaging samples" field is more than 0, turns on the second, white plot on the oscilloscope screen. This white plot corresponds to the averaged signal.

The program memorizes the number of last n (the Averaging samples field value) chunks of data taken from the input device and averages theminto more smooth plot. It is useful when the input signal is too noisy and it's hard to distinguish details.

ADVANCED SETTINGS

This button leads to the advanced settings window described below.

SAVE PLOT

This button saves the plot in form of a *.txt file. This file can be used as an input file in programs such as Microsoft Office Excel or Wolfram Mathematica.

An example of the output data:

File name: plot 07-Jan-2022 15-00-03.txt

>1, -3.8471875, -2.4700564

>2, -3.180088, -1.7942296666666666

>3, -2.0846875000000002, -1.1943312333333331

>4, -1.0163875, -0.7192025999999999

>5, -0.2278195, -0.21489176666666665

>6, 0.3243645, 0.2170092333333333

>7, 0.3724805, 0.40000923333333344

>8, 0.649458, 0.4429432666666667

>9, 1.0236125, 0.5258409

>10, 0.9028125, 0.6405232000000002

><...>

>3096, 2.0422805, -0.7216291333333332

As you can see, there are three rows in each line separated by comma: the first number corresponds to the number of the plot's point, the second is raw signal value and the third one is an averaged signal. This data can be used for further analysis of the gathered data using third party software.

PLOT FRAME

Inside the oscilloscope (plot) frame you can see a black screen divided by four sections by a zero voltage and a middle time lines. For readability there are secondary (gray) lines separating obscissus and ordinate axes into ten equal pieces. On the left you can see zero, maximum and minimum values for voltage. Beneath the plot screen you can see a value of division for time scale and full length of the input signal on the lower right side.

You can change the voltage amplitude values on the input field top left and time range on the low right.

There is also a stop button to freeze the picture for closer examination and/or saving the data via "Save plot" button.

STATUS BAR

There is a status bar on the lower side of the screen. On the right you can see calculated frequency and on the left there is an error messages window.

ADVANCED SETTINGS WINDOW

Advanced settings window can be called by pressing "Advanced settings" button on the right. There are three main options in there:

-Audio sampling settings

These settings are used to change two main parameters of pyaudio extensions: Sampling frequency and Data chunk size.

>Sampling frequency is the frequency in Hz (how many times every second) with which the oscilloscope gets the data from your input device. For example, the value of 48000 means that every second the program will take 48000 points for the plot and put them into the data chunk. Typical sampling rate of modern sound cards is 44100 or 48000 Hz.
>Data chunk size determines how many points will be taken before further processing. By default it set 4096 which means that after the program took 4096 samples (with sample frequency mentioned above) they will converted into the python list and put on the screen.

OSCILLOSCOPE SETTINGS

These settings are used to determine if an intersection of the signal and trigger line is ascending or descending by defining the sign of derivative in a given point. If you don't know what exactly a derivative is then probably you don't need this section.

>Freq detecting indent is a delta for time axis. In calculus we use the smallest piece of function called "d" for that. Since the given signal can be noisy we (probably) can't use d=1 but it should be quite insignificant comparing to the cluster size. The default value of 5 is okay.
>Freq detecting cluster size. The program usually takes more than one ascending or descending points for triggering and frecuency detecting. Instead, because of possible noise and subsequently big delta it takes a cluster of "points of interest": data points satisfying derivative requirements. However, we need only one of them. This variable determines the maximum size of the "points of interest". The default value is 200. If there is more than 200 points in a cluster (5% of the default chunk size) then probably your function in vicinity of the given point is flat.

QUADRATIC APPROXIMATION FUNCTION a*x^2+b*x

One of the big problems of semiconductors used in the computer is their nonlinear current-voltage line. Initially the sound card operates not with milivolts but with abstract data values. Unlike expectations (I expected exponent function) my observations showed that the dependancy between the real input value in millivolts (measured by another device) and these abstract data values can be well described as a quadratic function a*x^2+b*x where a=0.0000005 and b=0.012. Feel free to play with these.
