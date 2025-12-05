# SloTax ETF Manager - Installation Guide

This guide will walk you through the steps to get the SloTax ETF Manager application running on your computer.

## 1. Prerequisite: Install Python

This application is written in Python and requires Python 3 to be installed on your system.

- **Download Python:** Go to the official Python website: [https://www.python.org/downloads/](https://www.python.org/downloads/)
- **Install Python:** Run the installer.
- **Important (for Windows users):** On the first screen of the installer, make sure to check the box that says **"Add Python to PATH"**. This will make it much easier to run the script.

To verify that Python is installed correctly, you can open a terminal (Command Prompt, PowerShell, or Terminal) and type:
```sh
python --version
```
You should see a version number like `Python 3.x.x`.

## 2. Dependencies

The application is built using only standard Python libraries that come included with the Python installation.

**You do not need to install any additional packages.** The `requirements.txt` file is empty for this reason.

## 3. Running the Application

1.  **Download the Code:**
    Save the `SloTax_ETF_Manager.py` file to a folder on your computer.

2.  **Navigate to the Directory:**
    Open a terminal or Command Prompt and use the `cd` command to navigate to the folder where you saved the application. For example, if you saved it in a folder named `SloTax` on your Desktop, you would do:
    ```sh
    cd Desktop/SloTax
    ```

3.  **Run the Script:**
    Execute the following command in your terminal:
    ```sh
    python SloTax_ETF_Manager.py
    ```

The application window should now open, and you can begin adding transactions. The `portfolio.json` file will be created automatically in the same folder as soon as you add your first transaction.