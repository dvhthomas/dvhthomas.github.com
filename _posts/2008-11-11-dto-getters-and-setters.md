---
layout: post
title: "DTO getters and setters"
abstract: "If this was Java I wouldn't forget getters and setters. But it ain't!"
category: 
tags: [csharp]
---
I just burned about 30 minutes trying to figure out why my data transfer object (DTO) didn’t work. I have a C# Web Service (asmx) that accepts a simple class. There are two properties I care about:

1. A unique ID which is an integer
1. An array of another simple class with a few simple properties

No matter how hard I tried I could not get the array property to show up. I know I’ve done this a million times before, but my proxy class (created by the `wsdl` command line tool in the .NET SDK) just wouldn’t generate the damn thing.

Simple answer: I forgot to add a setter to the property, so while I could get the array, the serializer that .NET uses to XML-serialize the array could not be called. Rather than notify me of this, the wsdl command simply ignored the type when generating the proxy classes. So there you have it. Make sure your DTOs have:

1. A parameterless constructor
1. Getters and setters on properties you need to use on the client