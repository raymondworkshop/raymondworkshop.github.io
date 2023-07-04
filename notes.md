
### notes 
* ideas  
    - some like pinboard app  
        + TODO  
    
    - Blog on what your learning or tutorial  
        + [Rust-101](https://www.ralfj.de/projects/rust-101/)  

    - markdown -> slides/pdf  

    - [Writing a Pollen lexer in Pygments](https://www.jonashietala.se/blog/2020/04/30/writing_a_pollen_lexer_in_pygments/)

    -  personal wiki system to help with the management of a repository of records which includes {daily logs}, notes on {various projects} and {curated pages of general knowledge}
        +  [https://wiki.xxiivv.com/site/home.html](https://wiki.xxiivv.com/site/about.html)  



* Tech stack   
    - Aws S3 with Docker 
    - Our web UI is built in React.js, Jinja, and SCSS, and served by Python Flask through a GraphQL API. The bulk of the engineering work is in systems to fetch and process large amounts of data, e.g. from the Twitter API; we use Celery for this asynchronous task work. The persistent layer is backed by PostgreSQL with SQLAlchemy/Alembic as the ORM. We use staging environments and CI to ensure we continue to deliver a consistent user experience. We are hosted on Render and AWS.

* a search feature
    - search docs by word, name, date 
    - grep -riln "上司" _posts/  


#### 2022-06-20 
* update into 'vs' code style  
    - generate vs code style, and update into style.py  
    > pygmentize -f html -a .highlight -S vs > vs.css  


#### 2021-06-08  
* tag  
    - use subdir to replace tag function 
    - BUG: only get the a child dir  

* TODO  
    - deploy all docs on github  
        + DONE  

    - show tags 
        + use subdir to replace tag

    - cannot deal with chinese - DONE  
        + the HTML coding 
        + <meta charset="utf-8">  

    - check the code & math highlight function  - DONE 
        + use Pygments highlight function 
        + ~~TODO - USE MKDocs pkg~~ 
        + use the original code : style.py, highlighting.py  

    - check more nox pkg  
    

#### 2021-06-07  
* TODO  
    - tag functions 
        + index as a 'home' tag  
        + the current soluton is to include a index in each subdirs 

    - check how to deploy all on github  

    - check more nox pkg  

    - the code & math highlight function 

#### 2021-06-06  

* the blog works locally  
  > python3 -m serve 

* TODO  
    - fix how to deploy on github  
    
    - fix the index function  
        + Done  
        + tricks: store the generated html in /docs/{}/index.html
    - check more on livereload pkg  
    

#### 2021-06-05  
* programming on my blog 

* write the test, and how to build functions firstly  
    - this could give you a direct result, and feedbacks  
    - don't write the functions firstly if you don't undersand fully  

* TODO  
    - finish the building functions 
        + fix the build errors  
        > python3 -m nox  
        >  site-packages in some virtual env 
        + Done, nox is only for the test function 

    - write the test functions  
    - [code reference from thea.codes](https://github.com/theacodes/blog.thea.codes)


#### 2021-06-03  

* build the blog on github, and python  
    - [Writing a small static site generator](https://blog.thea.codes/a-small-static-site-generator/)  

* more engineering project, not just book project   

#### rebuild blog inspired by [Writing a small static site generator](https://blog.thea.codes/a-small-static-site-generator/) from Thea

#### TODO 
    - code & math highlight functions 
    - support chinese 
    - check nox pkg 
