---
layout: post
title: "Summary about Probability and Statistics"
date: 2017-06-04
comments: true
categories: [home,algorithms]
abstract: "[updating] Summary about Probability and Statistics"
---

> [updating] A Summary about Probability and Statistics 

#### Bayesians   
TODO 


#### Statistical Inference
* 总体和样本
    - 总体分布是一个概率分布族(因为参数未知)
    - 非参数总体(假定总体有一定的概率分布而并不明确知其道数学形式) 
    - 从总体中抽出的**独立随机**的样本  
     
    <br/>

* 由样本推断总体：为解决具体问题而抽样，**样本分布族规定了问题的统计模型(概率分布)**，样本的具体数值推断样本分布中的未知参数。比如 依据样本 X_1, ..., X_n 对分布 $N(μ, σ^2)$中的参数μ作推断，这个推断的具体内容依据样本X_1, ..., X_n算出一个数作为μ估计值。  
  
    <br/>
    
* Frequentist - 极大似然估计方法 (Maximum likelihood estimation) (要求假设的分布函数有参数形式) 是用来估计一个概率模型的参数的一种方法。 

    <br/>

    假设总体有分布  f(X;θ_1,...,θ_k), X_1,...X_n  为抽出的样本; 當有了結果X（样本）时，即在所有由原因θ而产生的可能性中，寻找一个值使这个X（样本）的“可能性”最大(即似然程度最大)。  

    <br/>

    则有似然函数    
    $$L(θ|X_1,...,X_n) = f(X_1|θ)f(X_2|θ)...f(X_1|θ) = \prod_{i=1}^n f (x_i|θ)  

    $$\log(L(θ|X_1,...,X_n)) = \sum_{i=1}^n {\log(f(X_i|θ))}  
     
    我们要似然程度最大, 即“极大似然估计”:    
    $$\hat{θ}_{MLE}=\operatorname*{arg\,max}_\theta \sum_{i=1}^n {\log(f(X_i|θ)}  
    
    <br/><br/>   
    
#### Nonparametric statistics
One of the biggest problems with tests like the chi-squared test is that they make a lot 
of assumptions about how your data was generated. Often we could figure out that this is 
without having to make a bunch of assumptions .  
 



#### TODO
    
    
#### reference 
* [Statistical Rethinking: A Bayesian Course with Examples in R and Stan](https://github.com/rmcelreath/statrethinking_winter2019) 
* [Some good "Statistics for programmers" resources](https://jvns.ca/blog/2017/04/17/statistics-for-programmers/)
* [统计学浅谈](http://episte.math.ntu.edu.tw/articles/mm/mm_03_3_07/index.html)
*  陈希孺的《概率论与数理统计》
