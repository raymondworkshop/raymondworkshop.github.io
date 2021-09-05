---
layout: post
title: "note on Python, and typescript programming"
date: 2018-01-16 
comments: true
categories: [programming]
abstract: "note on Python, and typescript programming"
---

>notes on Python, and typescript programming   



#### Python Data Model -> A Framework/API for core language constructs

Python interpreter invokes special methods to perform basic object operations.

By using and implementing **special methods of Python Data Model** in your objects, your objects can **behave like the built-in types**, enabling the expressive coding style **Pythonic**.

##### Data Sturctures
  * sequences - Python sequences are often categorized as **mutalbe or immutable**, and also could be considered as **flat sequences and container sequences**.
    + container sequences -> hold **references** to the objects
    + flat sequences (like str, bytes) -> more compact because of the physically store the value
    + 
    + **list** -> mutable and mixed-type
      - list comprehensions and generator expression

    + **tuples** -> immutable lists
      - tuples can hold records
      - tuple unpacking -> parallel assignment

    + array -> efficient because of only **the packed bytes for numeric data**
      - for large sequences of numbers, this saves a lot of memory
      - NumPy lib
  
  * dict and set
    + **hash tables** are the engines for the high performance dicts
    + hash tables must be sparse to work, they are **not space efficient**
  
  * str versus bytes

##### Functions as objects
  * Functions, like integers, strings, and dictionaries, also can be a **program entity**, this enables programming in a **functional style**. 
    - The main ideas are that we can assign functions to variables, pass them to other functions, store them in data structures and access function attributes.
    
  * function decorators and closures
  
    
##### Object Oriented


##### Control flow  
  * Generators - declare a function that behaves like an iterator 
    + yield -> return the generator object 
      - yield pauses the function and saves the local state so that it can be resumed right where it left off 
  * Concurrency 


##### Metaprogramming 
  * 



#### typescript


#### Notes
 * Reload modules problem in Emacs Python Shell
   - use importlib to reload(models) 
   - or use ipython and  %autoreload

 * virtualenvs setup for python3 -> pipenv
   - New a project: >pipenv --python 3.6
   - Install all dependencies:  >pipenv install
   - Locate the virtualenv: >pipenv --venv
   - Use the shell: >pipenv shell
   - Uninstall everything:  >pipenv uninstall --all

 * <del>Your environment contains PYTHONPATH=/usr/local/lib/python2.7/site-packages
This doesn't work with Python 3 for obvious reasons. To remove it:  unset PYTHONPATH 
</del>


#### reference
* Fluent python
* <del>[win2018- CS140e Operating Systems](https://web.stanford.edu/class/cs140e/)</del>
* <del>[Writing an OS in Rust (Second Edition)](https://os.phil-opp.com/)</del>
