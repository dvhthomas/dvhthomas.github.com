---
layout: post
title: "Idiot's guide to UML class diagrams"
abstract: "I put this together and figured I'd share it. I always draw the wrong little diamond for aggregation vs. composition so maybe this will help me to use the right pen for the job next time!"
category: 
tags: [uml, practices]
---
## Introduction

Unified Modeling Language (UML) is a graphical notation covering a wide variety of steps in software and system design. One of the core uses of UML is to design object oriented systems using classes, interfaces, relationships, and other simple graphical elements. The purpose of this document is to describe the most common elements of UML diagrams geared towards class design.
All diagrams were created using the [yUML](http://yuml.me) website.

## The Elements

### Class

* Just the class - no properties or other information

![Simple class](/images/uml-class.png)

* A class with details. The name is at the top. The public fields (or properties) come next. They have a plus sign if they are public and a minus sign if they are private. Finally come the methods, again marked public or private with signs.

![Class with details](/images/uml-class-props.png)

### Interface

* Just the name - no details

![Interface](/images/uml-interface.png)

* With some details

![Interface](/images/uml-interface-details.png)

## Relationships

There are a few different kinds of relationships and deciding which one to use can be a bit confusing at first because it depends upon the intent of the relationship. *Simple associations* kind of ignore the two main types of associations and can be used for higher level UML diagrams. But being more specific is important as the design evolves and so understanding the difference between aggregation and composition is key. It really comes down to ownership and object lifecycle.

* **Aggregation** -- This is known as a has a relationship because the containing object has a member object. But here is the critical part: The member object can survive or exist without the enclosing or containing class, so it can have a meaning beyond the lifetime of the enclosing object. *Example: A room has a table and the table can exist without the room.*

* **Composition** -- This is known as a is a part of or is a relationship because the member object is part of the containing class and cannot existing or survive outside the context of the containing class. This also means that the lifetime of the member object ends with the lifetime of the enclosing object. *Example: The IT Department is part of the Company. The IT Department cannot exist without the Company and has no meaning after the lifetime of the Company.*

That said, let's have a look at the ways to show various kinds of relationship and the characteristics of those relationships.

### Simple association

Customers *have a* billing address

![simple association](/images/uml-have-a.png)

The relationship between a Customer and their Orders is described by the action orders. So it reads *a Customer __orders__ an Order*.

![simple association](/images/uml-relationship.png)

### Cardinality

A Customer can have zero or more Addresses. An Address must have exactly one Customer. Notice how the numbers are positioned on the line: the customer fact (zero or more) is written next to the Address class.

![cardinality](/images/uml-cardinality.png)

### Directionality

An Order has an Address called `billing` and an Address called `shipping`. This does not say anything about the Address-to-Order relationship.

![directionality](/images/uml-directionality.png)

### Aggregation

A Company has exactly one Location. A Location has a Point.

![aggregation](/images/uml-aggregation.png)

### Composition

The Company has exactly one Location. The Location does not exist outside of the context of the Company.

![composition](/images/uml-composition.png)

## Other dependencies

### Inheritance

Both the Contract and Salaried classes inherit from the Wages class.

![inheritance](/images/uml-inheritence.png)

The NightlyBillingTask class inherits (implements) the ITask interface

![inheritance](/images/uml-implements.png)

### Depends On

The HttpContext class is dependent upon the Response class. The relationship reads as *"the HttpContext class **uses** the Response class"*. There is no *has a* or *is part of* a Response implied here. It is just plain usage.

![depends on](/images/uml-depends-on.png)

## Complete Example

Here it all comes together with some extra annotations in the form of notes.

![complete uml class diagram](/images/uml-example.png)
