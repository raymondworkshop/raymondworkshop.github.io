---
layout: post
title: "Notes on programing languages"
date: 2021-04-06 
update: 2022-01-22  
comments: true
categories: [home, programming]
abstract: "[Updating] Notes on programing languages"
---

#### Systematic program design  
* problem analysis -> data definitions 


#### Python Data Model -> A Framework/API for core language constructs
We can leverage the Python Data Model to build new classes.  

By using and implementing **special methods of Python Data Model** in your objects, your objects can **behave like the built-in types**, enabling the expressive coding style **Pythonic**.

##### Data Sturctures
* sequences - Python sequences are often categorized as **mutalbe or immutable**, and also could be considered as **flat sequences and container sequences**.
    + container sequences -> hold **references** to the objects
    + flat sequences (like str, bytes) -> more compact because of the physically store the value
    
    + **list** -> mutable and mixed-type
        - list comprehensions and generator expression

    + **tuples** -> immutable lists
        - tuples can hold records
        - tuple unpacking -> parallel assignment

    + array -> efficient because of only **the packed bytes for numeric data**
        - for large sequences of numbers, this saves a lot of memory
        - NumPy lib
  
* collections  
    + dict and set  
        - **hash tables** are the engines for the high performance dicts
        - hash tables must be sparse to work, they are **not space efficient**, compared to a low-level array a pointers to its elements (more compact but also much lower to search)  

    + Data class as a collection of fields  
  
* str versus bytes  

* Variables are mere labels  
    - the parameters in the function are **aliases** of the actual arguments  


##### Functions as objects
* Functions, like integers, strings, and dictionaries, also can be a **program entity**, this enables programming in a **functional style**. 
    + The main ideas are that we can assign functions to variables, pass them to other functions, store them in data structures and access function attributes.
    
* function decorators and closures 
    + a decorator is a function with the decorated function parameter 

``` python
target = deco(target)
```
    
``` python  
def deco(func):
    def inner():
        print("running inner()")
    return inner

@deco
def target():
    print("running target()")
    return
 ```
  
    
##### Object Oriented


##### Control flow  
* Generators - declare a function that behaves like an iterator 
    + yield -> return the generator object 
        - yield pauses the function and saves the local state so that it can be resumed right where it left off 

* Concurrency 


##### Metaprogramming 



#### Standard ML 
*  functional programming

*  sml-ch1
    - syntax is how you write sth
    - **semantics** is what that something means
        + **Type-checking** rules (before program runs) in current static environment
            - what type a binding has
            - produces a type or fail
        

    - **Evaluating** the bindings (in the dynamic environment)
        + a value or an error or an infinite loop of the preceding bindings
        +  look up value in current dynamic environment

    - **idioms** are the common approaches to using langguage features
        + Recursion
        + Let -> local binding

    - libraries
        + standard

    - tools
        + REPL  -> quick try-something-out
        + debugger

    - **immutation data**
        + **it is just a mapping, not assignment statement**, a tuple, or a list
        + No constructs for mutating the data we have build. No way to change the contents of a binding, a tuple,or a list
        + don't worry about the alias or copy like in java
        + or, like java, you have to care whether alias or copy, and in order to avoid the mutable data is been changed

* sml-ch2
    - tuples are syntactic sugar for records with field names 1, 2, ...

    - type synonyms -> a convenience for talking about types
    - datatypes bindings
        + patter-matching over one-of types
        + better to use pattern-matching to access list and option

    - patter matching over **each-of types**
        + value binding -> a val-binding **can use a pattern**, not just a variable
        + function binding
            - in ML, every function takes **exactly one tuple arg**, implemented with a tuple pattern in the function binding
            - a **function argument** can also be a pattern

        + Type-checker can **figure out the types of things you're matching against**,
      no longer need to write down any explicit types for the arguments to functions or any variables

        + type inference
            - **more general** can replace its type variables consistently

    - nested pattern-matching
        + elegantly recursive

    - **Recursion**
        + **tail-recursive** -> recursive calls are tail-calls
        + call-stacks -> pop the caller before the call, allowing callee to reuse the same stack space

* sml-ch3
    - first-class functions
    - TODO

#### note  
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
* [How to Design Programs, 2nd](https://htdp.org/2018-01-06/Book/index.html)  
* [Fluent Python, 2nd](https://book.douban.com/subject/34990079/) by Luciano Ramalho 