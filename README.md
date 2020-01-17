# gpt2-poetry

Summary: This software generates free verse poetry interactively using GPT-2, a transformer-based neural network. A human user accepts or rejects generated chunks of text until poem is complete.


To Install:

1) Install python version >= 3.6.8 from: https://www.python.org/downloads/ . (To install a specific Python version, i.e. '3.6.8', you can just go to this url, command-f then type your version, i.e. '3.6.8' - there will only be one match.)
This software has been tested and confirmed compatible with Python 3.6.8 and Python 3.7.4.

2) Download this Github repository. Open a shell (i.e. the application called 'Terminal' if you are using a Mac), type 'git clone https://github.com/joemeyer1/gpt2-poetry.git', and hit enter.

3) Install library dependencies. The easiest way to do this is to navigate to this repository (i.e. type 'cd gpt2-poetry' into a shell then hit enter), then type 'pip install -r requirements.txt' and hit enter.



To Launch:

1) Navigate to this repository (i.e. open a shell and type 'cd gpt2-poetry' - or 'cd downloads/gpt2-poetry' if you downloaded this repository as a .zip instead of cloning it directly to your home directory).

2) Once you have opened a shell and navigated to this repository, type 'python main.py'. Assuming you have followed the installation instructions the program should start running.



To Use:

Basic Interface: The program will offer generated chunks of text, which you can accept ('enter' key), reject ('delete' key), or replace with custom text (arrowkey). You can also delete previously accepted chunks of text (backslash). Press 's' to save or 'r' to reset poems.


You can press 'h' at any time to view instructions:

press 'enter' to accept

press 'delete' to reject

press an arrowkey to edit

press backslash to delete chunk

press 's' to save

press 'r' to reset prompt

press 'q' to quit
