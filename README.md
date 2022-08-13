# PLD2flex

## Description
PLD2flex is a GUI-tool for establishing the phonological Levenshtein distance between phonological word forms. This can apply to pairs of word forms, word forms that are compared to lists of other words, including data bases like CELEX (Reference), if available, and any other combination of word forms. PLD2flex takes written (orthographic) input that is transcribed to a phonological form by means of the BAS services and computes PLD scores on the basis of these. By implication, PLD2flex can be used with any language that is supported by the BAS or for that phonological transcripts are provided. 

## How to run the tool

1. Install python3: https://www.python.org/downloads/
2. Install (ana)conda: https://conda.io/projects/conda/en/latest/index.html

If you are not using windows:
2.1 Install qt 5.15: https://www.qt.io/offline-installers  

3. Clone this repo, open a new terminal in the main directory of it

(recommended) If you want to use (ana)conda:
3.1 Create a new env with this command:
'conda create --name PLD2flex'
3.2 Activate the new environment:
'conda activate PLD2flex'
3.3 Install pip in your new environment:
'conda install pip'

4. Install all required packages via pip:
'pip install -r requirements.txt'

If you are using macOS:
4.1 Install another package: 'pip install PyObjC'

5. Should the installation of a package fail, try to install the missing_package manually via pip:
'pip install missing_package'
6. Run the main.py:
'python main.py'

## Usage

For further information how to use the program, consider the User-Manual in this repo.