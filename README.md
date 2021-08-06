## PLD20

# Description
PLD20 is a tool for computing the phonological Levenshtein distance between word forms. These can be one-to-one and multiple-one-to-one, one-to-many, and many-to-many comparisons of word forms. The tool can be used with a database of word forms of the user's choice, such as CELEX or the Subtlex databases. It takes written (orthographic) input that is transcribed by means of the BAS services, which enables users to work with any language of that is supported by the BAS or for which phonological transcriptions are provided.

# How to run the tool

1. Install python3
2. Install (ana)conda
3. Install qt (?)
4. Clone this repo, open a new terminal in the main directory of it
5. Create a new env with this command:
'conda create --name pld20'
6. Activate the new environment:
'conda activate pld20'
7. Install all required packages via pip:
'pip install -r requirements.txt'
8. Run the main.py:
'python main.py'

# Usage

For further information how to use the program, consider the User-Manual in this repo.