---
layout: post
title: "SQL Server and firewalls"
abstract: "I keep forgetting to open up port 1433 to access SQL Server 2008 on the network."
category: 
tags: [sqlserver]
---
Did a little searching and found [this post](http://www.robkerr.com/2008/07/windows-firewall-and-sql-server-2008.html) that shows how to use the netsh command to do it all in a script. For example:

    netsh firewall set portopening TCP 1433 "SQLServer"

Much better than going through the Windows Firewall user interface because you can set a bunch of exceptions in one script.