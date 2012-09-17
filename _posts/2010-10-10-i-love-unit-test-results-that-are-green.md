---
layout: post
title: "I love unit test results that are green"
abstract: "Green is good when it comes to a visual scan of test results. Especially when the application logic is completely screwy and pulling one end of the coding string causes unlikely things to break. Those Head First authors had it right: you'd better wrap code you didn't write in a boat load of tests, and keep them clean."
category: 
tags: [testing, tools]
---
I've been working on a fairly complex legacy database integration using NHibernate. Several "implied" (a.k.a. missing) relationships, composite keys, magic strings where "B" means projected and empty means...not sure actually. So my unit tests are really a life saver. Every time I add a feature I have the benefit of knowing that I'm getting closer without doing things that are going to bite me later. Yes, my tests could be poorly written in some cases, yes I'm hitting the database way more than I should, but I'll take it as the price for my TDD comfort blanket.

![green unit tests in test runner](/images/green-unit-tests.png)