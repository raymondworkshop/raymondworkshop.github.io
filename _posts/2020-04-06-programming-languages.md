---
layout: post
title: "note on programming language"
date: 2021-04-06
comments: true
categories: [programming]
abstract: "[Updating] note on the core ideas programming languages"
---

#### **scheme** 
TODO

#### Standard ML

  + functional programming

  + sml-ch1
    - syntax is how you write sth
    - **semantics** is what that something means
      + **Type-checking** rules (before program runs) in current static environment
        - what type a binding has
        - produces a type or fail
        

      + **Evaluating** the bindings (in the dynamic environment)
        - a value or an error or an infinite loop of the preceding bindings
        - look up value in current dynamic environment

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

  + sml-ch2
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

  + sml-ch3
    - first-class functions
    - TODO

#### reference
* [Lisp in Small Pieces](https://book.douban.com/subject/1456904/)
