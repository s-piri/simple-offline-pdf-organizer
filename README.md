# Simple Offline PDF Organizer
A simple python software GUI that let you perform basic pdf organizing functions locally.

## Inspiration
I wanted to delete some pages from my pdf by I did not want to 
* Download trial pdf softwares
* Upload my pdfs to "free" online pdf editor (Data Privacy concern!)

## Features
* Load multiples PDF
* Delete Pages
* Rotate Pages
* Rearrange pages

## Requirements
Python>=3.10

## Installation
```
pip install -re requirements
```
## How to Use

Other than "Rearrange pages", most are self-explanatory.

### Rearrange pages

Fill the entry form with the new page order separated by commas.<br>
The page number not written will be automatically deleted.<br>
As examples, for a 3-page pdf:<br>

> 3, 2, 1

the order of the pages where the originally 1st page will become the 3rd and vice versa
> 1, 2

the 3rd page will be removed

> 3, 1

 the 3rd page will become the first page, the 1st will become the last, and the 2nd page will be removed

## ToDo

* Make .exe
