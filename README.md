# pyplagdetect
detect plagiarism based on a local set of pdf files

## Usage
### Preparations
The script is placed in a folder, together with two other folders. In one folder, all the "old" reports are placed (can also be in subdirectories), while in the second folder, the reports to be tested are stored. The names of those two folders should be specified in the configuration part of the script.
### Running
Run the script in the current directory without further options. Status messages are printed if all "old" documents have been scanned and for each "new" document that has been finalized.
### Results
For each .pdf file in the directory with new reports, a text file is created, stating all occurences of copying found with corresponding text fragment and the "old" report it is copied from.
