# AOT-Productivity-Display

An always on top productivity display for SAC1 - Inovations Project

# Getting Started

To get started, first clone the repository by doing 1 of the following.

- Download the source code zip from GitHub and then extract everything from the archive, or alternatively;

- Run in a terminal:

    ```
    git clone https://github.com/BUR0263/AOT-Productivity-Display.git
    ```

    Note: The command line approach requires you have git installed.

Then ensure you have all of the required dependencies installed by reading below:

# Dependencies

Any unix-like — including Linux and macOS — or Windows based system should work fine, however these docs and the guides within assume you are running Windows 10 or 11.

## Python 3.14 or later

Ensure you have a recent version of Python — version 3.14 or later — installed and configured. To check your version on windows, run in command prompt:

```
python --version
```

Note: You may have to use "python3" or "py" instead of "python"

If your version is out of date, visit [python.org](https://www.python.org/) to download and install the latest applicable version for your system.

## Python Module: PyQt6

This project makes use of the [PyQt6](https://pypi.org/project/PyQt6/) module.

It is recommended to not install this module to your system python environment, but to instead make use of a virtual environment. To do so in windows, create a virtual environment at your project root by opening command prompt, navigating to the project root directory, and running the following commands:

1. Create a virtual environment:

    ```
    python -m venv venv
    ```

    Note: You may have to use "python3" or "py" instead of "python"

2. Activate the environment by running:

    ```
    venv\scripts\activate
    ```

    Note: Activating the environment is also required before running the program

3. And then install PyQt6 by running:

    ```
    pip install PyQt6
    ```

    Note: You may have to use "python -m pip" instead of pip, and you may also have to use "python3" or "py" instead of "python"

## Font: LCD5x8H - _OPTIONAL_

This dependency is optional as this program can fall back to the most appropriate available font installed on your system.

As I was unable to find appropriate licensing information for a font file used in this project — LCD5X8H.TTF — with the following copyright metadata attributing the font to Fr. Thomas McGahee:

> "Prepared by Fr. Thomas McGahee. Based on Hitachi HD44780 chip. Added typographical single and double quotes."

I have not included a copy of this font in this repository, as is consistent the advice provided by fontsgeek.com, where I originally sourced my copy of this font.

The font, as of writing, is publicly available for free at: `https://fontsgeek.com/fonts/LCD5x8H-Normal`

To install this dependency, download and extract the .TTF file, and either place the font file in the project root directory (where this README.md file is located), or install the font to your system.

# Running

To run this program, once all required dependencies are installed, on Windows:

Open command prompt and navigate to the project root directory, alternatively you can navigate to the root directory using File Explorer, then right click on some empty space and click "Open in Terminal".

Then run the following commands:

1. Activate your virtual environment that you created in the dependencies stage:

    ```
    venv\scripts\activate
    ```

    Note: This is not required if you chose to install PyQt6 to your system Python environment. In which case, you may be able to simply double click the main.py file in File Explorer, or right click and "Open with" -> "python"

2. Then, run the main.py file:
    
    ```
    python main.py
    ```

    Alternatively, you may want to run in development mode, 
    which disables window transparency and adds a standard window frame. To do so use one of the following:

    ```
    python main.py -d
    ```
    ```
    python main.py --development-mode
    ```