---
layout: post
title: "WCF Experimentation"
abstract: "I’ve been working on a Windows Communication Foundation (WCF) service at work this past week or so, and it’s taught me a few things about structuring projects correctly, and supporting unit tests."
category: 
tags: [dotnet]
---
First, you can get the code from [Google Code](http://code.google.com/p/dylansknowledgebase/source/browse/#svn/trunk/WcfReferenceProject) using your favorite Subversion client

## Key points

* Do not try to create a WCF service using the New Project wizard in Visual Studio and expect to have something flexible or testable! That’s probably the biggest lesson of the week. I learned this through my struggles with the out-of-the-box arrangement that Microsoft provides, and got all of the right answers from an excellent Dot Net Rocks TV episode by [Miguel Castro](http://www.dnrtv.com/default.aspx?showNum=122).
* Do not use any automated tools or cut’n’paste too much when working with the app.config or web.config for your services. I have a much better understanding of what the heck is going on by slowly and methodically adding my own settings and seeing what works and what doesn’t. It’s pretty painful at first but it pays off when you can quickly diagnose a problem that seems to be coming from nowhere, only to discover a simple fix in the system.serviceModel section of the file.
* Don’t use a Add Service Reference option in Visual Studio to automatically create your client proxy to the WCF service. Instead use `ClientBase<T>` to create a strongly type proxy very easily in code. It’s less work, and let’s you know _immediately_ if it no longer matches the server implementation. Plus, you can override the logic in your own client if you need to, e.g., adding user verification before uploading a large file. Look in `ClientTests\HelloClient.cs` for an example of this in action.

That’s it: pretty simple stuff, but it had a profound and positive impact on the way that I’m pursuing WCF.