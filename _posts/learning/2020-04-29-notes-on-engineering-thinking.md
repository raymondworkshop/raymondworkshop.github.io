---
layout: post
title: "Updating-notes-on-practical-engineering-thinking"
date: 2020-04-29
comments: true
categories: [learning, engineering, course, important, manager]
---

#### notes on software engineering  
* 规划力  
* 软件工程 = 过程 + 方法 + 工具
* **engineering thinking and project thinking** on every task
    - 想法 + 概念 + 计划 + 设计 + 开发 + 发布
    - **想法** : 识别问题 - **清晰地定义问题, 研究其可行性, 检查是否有可行方案**
    - **概念** - **提出概念性解决方案**, 可能有多个方案,最终确定一个
    - **可行性计划** - 如何实施, 人员,任务,时间, 预算
    - **设计** - 将解决方案细化, 设计架构和划分功能模块
    - 开发 - 根据设计方案, 实施构建, 并迭代
    - 发布

* 瀑布模型- 有序可控
    - 需求分析
        + 了解老板的想法 + 调研 + **设计原型**
        + 让老板给反馈, **写产品设计文档**, 划分不同模块
    -  軟件設計
        + 根據產品設計文檔, 把整体架构确定, **写技术方案**
        + 开会讨论, 确认整体技术方案, 按照功能模块拆分
    -  程序編碼

    - 軟件測試

* 原型开发,  增量模型(模块化小瀑布),  迭代模型
* 敏捷开发
    - scrum(过程管理) + 极限编程(工程实践) + 看板(可视化)

* 分而治之的策略
    - 拆分 + 流程

#### System Design and Software Engineering
* reference  
    - [Engineering Software as a Service](https://book.douban.com/subject/24316596/) by Armando Fox / David Patterson  
    - [Shape Up](https://book.douban.com/subject/34945817/) by Ryan Singer 
    - [The Mythical Man Month](https://book.douban.com/subject/1494471/)

##### 500L
* TODO 

* reference
    - [System Design Interview An Insider’s Guide](https://book.douban.com/subject/35246417/)
    - [How to Solve It](https://book.douban.com/subject/1456890/) by G. Polya  


#### Notes on soft-skills
* **tell the hard from the impossible**
    - **Find a solution** which is merely hard when it can be confidently **scheduled** and **the risks** are understood
    - make the requirement more **clear**
    - a clear definition of success - often become merely hards

* fight schedule pressure -> **time-to-market pressure** - reflect a financial reality
    - **visible between the available labor and the product**
    - maintain a concise and up-to-date **project plan**
        + mark progress
        + help make decisionss
    - how to estimate time
        + restate your **assumptions**
        + consider **prototyping the task** firstly
        + prepare **a written estimate** by **decomposing** the task into progressively smaller subtasks (less than a day)
        + **make this visible** to the manager
        + try to have the people to estimate, and have **team-wide consensus on estimate**
      

* Understand the user
    - figure out **what people really want**
    - spend more time with users, **understand them**
       + **propose** it to user
       + **test your ideas** against them as much as you can
      

* Gather support for a project
    - a prototype
    - demo real value


#### notes on engineering
* **Problem Solving**
    - Before you go rushing out to learn to code, figure out what your problem actually is.
        + Do you even have a problem?
        + Can you explain it to others in a way they can understand?
        + Have you researched the problem, and its **possible solutions, deeply**?
        + Does coding solve that problem? Are you sure?


* System thinking
    - Think about systems and how they **interoperate**. Systems Thinking is more important than coding.
    - Know what artifacts your system makes and what's needed for it to run. Know what kinds of things its good at and what it's bad at - in a non-zealous and non-egotistical way.
    - Understanding the basic building blocks are important.

* mini-project
    - 别做大项目。 从小项目开始，而且永远不要期望它变大。如果这么想（指做大型软件），就会做过度设计，把它想象得过于重要。更坏的情况是，你可能会被自己想象中的艰难工作所吓倒。

    - 所以要**从小处起步，着力考虑细节**。 别去想大图景和好设计。如果项目**没解决某些需求**，多半就是被过度设计了

* Think about Abstractions
    - learn how to think and when to dig deeper
    - learn how to question how things work
    - learn that everything new and simple **hides something large and complex** -> we are all standing on the shoulders of giants


* 总是想用不同的算法解决同一个数据问题，然后比较不同算法的效能
    - 不同应用场景对于算法的新奇度要求不一样
    - 在工业界，比起算法新奇度，**解决方案的 scalability 更重要**：能不能用到几个T的数据上，能不能当天内出结果，需要每天更新所有信息还是仅仅当天数据

#### Product Manager  
* it's having **the insights that lead to new products**  
    - the best of those come from working on hard tech problems  

    - **bulit the use case first** and **the protocol second**    
        + customers don't care about the technology, they care about the user experience  
        + choose the right tech architecture to solve a particular customer problem  

    - **focus on the users**, take moonshots and **have ambitious ideas**  
        + we **talk to our users** and **try to understand why there are gaps**. 
        + being a new area, we are building things that never existed before  

    - big & small goals take the same effort, why not go big?  

* confident  
    - "since this sytem is new, we **may face some challenges**. 
    Nevertheless, we are **confident that the challenges can be overcome**."  

* **builder**  
    - I am a builder at heart  
        + it gave me **the power to build things** and 
        when you **see what you build work in front of your eyes**, it can be quite powerful.  


* reference
    - [Inspired](https://book.douban.com/subject/27161852/) by Marty Cagan

##### ch4 Empathize with Stakeholders  - product manager  

*  Talk to the Right People  - who 
    - create a stakeholder Map -  a network diagram  

*  Discover the Business Goals - why they care  
    - **who wants it and what they want**
    - Record Business Goal Statements  
        + subject + measurable outcome + Context (the need)  
        + "(stakeholder) Mayor wanna (goal) reduce procurement costs by 30%, (context) to avoid making budget cuts to education or other essential services in an election year."  

##### ch5 - Architecturally Significant Requirements (ASR)
*  **planning** 
    - **problem definition**  from a user's point of view  
        + **a clear statement of the problem** that the sytem is supposed to solve   
        + understanding what you want to build  
    - **requirements prerequisite** ensure that the user drives the system's functionality   
        + **how to specify requirements well**   
        + the requirements checklist   

    - **system Architecture**   
        + determine the conceptual integrity of the system  
        + a architecture first needs **an overview** that describes the system in broadterm 
        + the architecture should **define the major buildign blocks** in a program 
        +  the communication rules for each buildign block should be well defined  


*  Define the **what**, the requirements from architecture  

*  Capture Constraints as Simple Statements  
    - like "Must build a browser-based web application, the context is to descreases concerns about software delivery and maintenance."  

*  Capture Quality Attributes as Scenarios  
    - Quality Attributes Scenarios describe **how the system is expected to operate within a certain environmental context**    
    - a quality attribute scenario **communicates the intent of the requirement** so anyone can understand it  
        + like "performace - A user sees research results within 5 seconds when the system is at an average load of 2 searchs per second."    
        + "Availability - A user's searches for open RFPs and receives a list of RFPs 99% of the time on average over the course of the year."  

    - precise and measurable 

*  Influential Functional Requirements  


#### **Design in Construction**   

##### ch6 - choose an Architecture  

* architects **choose structures to promote quality attributes** in the system  

* accept the constraints  

* **explore Patterns** to promote desired Quality Attributes  

*  find the functional requirements and ensure the architecture can achieve them 
    - **assign specific functional responsibilities to each element** 

##### ch7 - how to explore design concepts  

* collect published patterns catalogs  

* design exploration - how  
    - **survey** the existing ones 
    - **give a presentation** of the available ones 
    - share a brief demo 
    - **recommend** a technology that seemed reasonable 

* decision  
    - "how do the proposed solutions influence our **top-quality attributes**?"  


##### ch8 - how to create models  

* pick an appropriate pattern as meta-model 
    - meta-model defines the concepts and the rules of how the concepts are applied 


* **add new concepts** to the meta-model 
    - start the process by **asking a question**   
        + like "which components cost us the most if they are unavailable"  

    -  Name it  
        + the name describe the element's **responsibility but also its purpose** 
        + understanding **what it does and why it exists**      


* Organize code to make patterns obvious 
    - pair with diff teammates   
    - it would be wise to **explore our architecture options in a collaborative workshop**  
        + not everyone agrees with or understands the current architecture  

##### ch9 - how to make design decisions   
* plan and facilitate an architecture design studio  


##### ch10 - how to visualize design ideas  



#### reference
* **[軟件工程之美](https://time.geekbang.org/column/article/82337)**  
* **[许式伟的架构课](https://time.geekbang.org/column/article/94486)**
* [硅谷产品实战36讲](https://time.geekbang.org/column/article/6043)
* [AI技术内参](https://time.geekbang.org/column/article/153)
* [python 核心技术与实战](https://time.geekbang.org/column/article/116493)
* [HowToBeAProgrammer](https://github.com/braydie/HowToBeAProgrammer)
* [极客时间-python]
* [星球-陈老师每日精华]
* [软件工程之美](https://time.geekbang.org/column/158)
* [梁宁产品思维30讲]
* [Systems Thinking as important as ever for new coders](https://www.hanselman.com/blog/SystemsThinkingAsImportantAsEverForNewCoders.aspx)
* [Please Learn to Think about Abstractions](https://www.hanselman.com/blog/PleaseLearnToThinkAboutAbstractions.aspx)
* [500lines](https://github.com/muyun/500lines)
* [code complete] 
* [from programmer to architect]  
* [44 engineering management lessons](https://www.defmacro.org/2014/10/03/engman.html?continueFlag=ac31708e6f6b0c4f99bffa25b3a945d8)
*  [Managing people](https://klinger.io/posts/managing-people-%F0%9F%A4%AF)
*  [My Emotions as a CEO](https://ryancaldbeck.co/2021/10/08/my-emotions-as-a-ceo/)
*  [A collection of inspiring resources related to engineering management and tech leadership](https://github.com/charlax/engineering-management)
*  [Heuristics for effective management](https://github.com/ksindi/managers-playbook)
*  [How to mentor software engineers](https://xdg.me/mentor-engineers/)
*  [A Day in the Life of an Engineering Manager](https://www.toptal.com/engineering-management/a-day-in-life-engineering-manager#employ-just-quality-engineers-today?continueFlag=4cd860c7bf88c019e991891b8fd439de)
*  [engineering-manager-role-explained](https://www.toptal.com/engineering-management/engineering-manager-role-explained)
*  [Getting Started with Agility: Essential Reading](https://holub.com/reading/)