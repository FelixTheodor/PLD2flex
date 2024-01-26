# PLD2flex

## Description
PLD2flex is a GUI-tool for establishing the phonological Levenshtein distance between phonological word forms. This can apply to pairs of word forms, word forms that are compared to lists of other words, including data bases like CELEX (Reference), if available, and any other combination of word forms. PLD2flex takes written (orthographic) input that is transcribed to a phonological form by means of the BAS services and computes PLD scores on the basis of these. By implication, PLD2flex can be used with any language that is supported by the BAS or for that phonological transcripts are provided. 

## How to run the tool

**1. Install python3.12: https://www.python.org/downloads/**

**2. Install (ana)conda: https://conda.io/projects/conda/en/latest/index.html** 

**3. Clone this repo, open a new terminal (for Windows: Powershell Prompt) in the main directory of it**

-3.1 Create a new env with this command:
'conda create --name PLD2flex python=3.12'

-3.2 Activate the new environment:
'conda activate PLD2flex'

-3.3 Install pip in your new environment:
'conda install pip'

**4. Install all required packages via pip:**

'pip install -r requirements.txt'

**5. Update the config.txt**

(see section 2.2 of User Guide) 
For instance, you need to specify the paths for the result / database files. Make sure that you use the right path format for your operating system.

**6. Run the main.py:**

'python main.py'


## Installation Troubleshooting

### General:
- usage of conda is recommended
- make sure that you use python >=v3.12
- depending on your system config, you might need to install qt 5.15: 
https://www.qt.io/offline-installers 
- should the installation of a package fail, try to install the missing_package manually via pip:
'pip install missing_package'

### For macOS users:
- you might need to install another package: 
'pip install PyObjC'

### For windows users:
- you might run into this error: Microsoft Visual C++ 14.0 or greater is required
- if you do, head to the link below and install via the build tools the C++ desktop development component
https://visualstudio.microsoft.com/visual-cpp-build-tools/



## Usage

For further information how to use the program, consider the User-Manual in this repo.