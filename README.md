# Oscillodog
A simple one channel oscilloscope with autotrigger and averaging function I made while learning Python. It takes data from your audio input device (usually microphone)
It uses several libraries: Tkinter, pyaudio, matplotlib and numpy

Functionality:

You can see main controls on the right side of the main screen. From top to bottom:

TRIGGER MENU

There are three options: no trigger, trigger by ascending signal and trigger by descending signal. Trigger by ascending is set by default.

> No trigger: the oscilloscope ignores a piece of code used for synchronization. In this mode it is impossible to determine frequency and averaging is virtually useless

> By ascending: the progran sets the starting point of the green plot in the first intersection point of signal (green plot) and treshold value (red triangle) on ascending side of the signal

> By descending: the progran sets the starting point of the green plot in the first intersection point of signal (green plot) and treshold value (red triangle) on descending side of the signal

FREQUENCY MEASUREMENT OPTIONS

When the input signal is too noisy you can use the averaging feature. Radiobuttons in this menu allow you to choose to measure frequency lean on the averaged signal

TRESHOLD VALUE

The trigger level of the signal, marked by red arrow on the left side of the oscilloscope screen. Determines the level of signal used by the trigger option to detect the ascending (descending) side of te signal. Can lead to syncronyzation failue if set too high or low

AVERAGING SECTION

If "Enable averaging" checkbox is checked and "Averaging samples" field is more than 0, turns on the second, white plot on the oscilloscope screen. This white plot corresponds to the averaged signal

The program memorizes the number of last n (the Averaging samples field value) chunks of data taken from the input device and averages theminto more smooth plot. It is useful when the input signal is too noisy and it's hard to distinguish details

ADVANCED SETTINGS

This button leads to the advanced settings window described below.

SAVE PLOT

This button saves the plot in form of a *.txt file. This file can be used as an input file in programs such as Microsoft Office Excel or Wolfram Mathematica

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

As you can see, there are three rows in each line separated by comma: the first number corresponds to the number of the plot's point, the second is raw signal value and the third one is an averaged signal. This data can be used for further analysis of the gathered data using third party software

