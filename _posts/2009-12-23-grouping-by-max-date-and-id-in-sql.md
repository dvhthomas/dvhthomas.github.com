---
layout: post
title: "Grouping by MAX date and ID in SQL"
abstract: "Getting the most recent change for a specific row in SQL Server when there are going to be lots of changes for each row. Audit-schmaudit."
category: 
tags: [sql]
---
Another reminder to myself. I have an audit table that is populated by a trigger on a table. I use this table to drive another process and that process involves finding the most recent addition to the table for a specific work order. So basically if a work order has it’s status changed multiple times—which is perfectly valid—I need to know the last change only. Here is what the source data looks like after changing status on a couple of work orders:

<table>
    <tr>
        <th>Id</th><th>WorkorderId</th><th>OldStatus</th><th>NewStatus</th><th>TimeOfUpdate</th>
    </tr>
    <tr>
        <td>F0FE4F81-4CEF-DE11-8442-001C23437026</td><td>10</td><td>null</td><td>CLOSED</td><td>2009-12-22 22:51:14.377</td>
    </tr>
    <tr>
        <td>F1FE4F81-4CEF-DE11-8442-001C23437026</td><td>10</td><td>CLOSED</td><td>OPEN</td><td>2009-12-22 22:51:14.390</td>
    </tr>
    <tr>
        <td>F2FE4F81-4CEF-DE11-8442-001C23437026</td><td>10</td><td>OPEN</td><td>CLOSED</td><td>2009-12-22 22:51:14.390</td>
    </tr>
    <tr>
        <td>F3FE4F81-4CEF-DE11-8442-001C23437026</td><td>9</td><td>null</td><td>CLOSED</td><td>2009-12-22 22:51:14.390</td>
    </tr>
</table>

Because I created these by firing the trigger in a SQL script for testing the times for two of the records for work order 10 are identical. That’s OK; in fact I need to deal with this possibility in my application so I’m glad it happened that way. Anyway, here’s the SQL that I wrote to get the information that I need. Not rocket science but it is just one of those things that had me stumped for a while until it dawned on me that I needed an inner join rather than a subquery.

{%highlight sql%}
select w.Id
 , w.NewStatus
 , w.OldStatus
 , w.TimeOfUpdate
 , w.WorkorderId
from Test.WCS.WorkorderStatusChange w
 -- Inner join on the max date grouped by workorder id
 inner join (select w.WorkorderId as woi, MAX(w.TimeOfUpdate) as tou
   from Test.WCS.WorkorderStatusChange w
   group by w.WorkorderId) as t
  on t.tou = w.TimeOfUpdate
  and t.woi = w.WorkorderId
{%endhighlight%}

And that gives me what I need. Again, notice that the two results for work order 10 are valid because both have the `MAX(TimeOfUpdate)` value:

<table>
    <tr>
        <th>Id</th> <th>NewStatus</th> <th>OldStatus</th> <th>TimeOfUpdate</th> <th>WorkorderId</th>
    </tr>
    <tr>
        <td>F3FE4F81-4CEF-DE11-8442-001C23437026</td> <td>CLOSED</td> <td>null </td><td>2009-12-22 22:51:14.390</td> <td>9</td>
    </tr>
    <tr>
        <td>F1FE4F81-4CEF-DE11-8442-001C23437026</td> <td>OPEN </td><td>CLOSED</td> <td>2009-12-22 22:51:14.390</td> <td>10</td>
    </tr>
    <tr>
        <td>F2FE4F81-4CEF-DE11-8442-001C23437026</td> <td>CLOSED</td> <td>OPEN</td> <td>2009-12-22 22:51:14.390</td> <td>10</td>
    </tr>
</table>

Of course the real question on my mind now is how the heck to do that with HQL or the Criteria API in NHibernate? I’ve wrestled with it for some time now and have basically given up. I am going to grab the whole lot of data from SQL Server and use LINQ to objects to filter out what I need. This is acceptable in this particular case because I delete the rows in the status table once I have read them in; they are only there long enough for the application to add a message to a message queue using the information. Still, it’s bugging me that I cannot figure out the query in NHibernate.