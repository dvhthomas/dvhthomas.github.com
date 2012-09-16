---
layout: post
title: "LINQ to objects: gettting the SQL version into C#"
abstract: "In my last post I described a SQL query that grouped records by an ID (non unique obviously otherwise what is the point of grouping in the first place?), and then selected only the most recently created record from each group. I have been struggling with the LINQ query to do that same thing in C# and finally hit upon an answer."
category: 
tags: [dotnet, csharp]
---
Not **the** answer maybe, but it works so I’ll call in *an* answer

{%highlight csharp%}
void Main()
{
 var list = new WorkorderStatusChangeEvent().Build();
 var ids = from w in list
   group w by w.WorkorderID into g
   let latestDate = g.Max(w => w.TimeOfEvent)
   select g.Where(w => w.TimeOfEvent == latestDate)
    .Select(w => w.Id).First();
 var results = list.Where(x => ids.Contains(x.Id));
 results.Dump();    
}

public class WorkorderStatusChangeEvent
{
 public virtual Guid Id { get; set; }
 public virtual string WorkorderID { get; set; }
 public virtual string OldStatus { get; set; }
 public virtual string NewStatus { get; set; }
 public virtual DateTime TimeOfEvent { get; set; }
 
 public IList Build()
 {
  var earliest = new WorkorderStatusChangeEvent
     {
     Id = Guid.NewGuid(),
     OldStatus = string.Empty,
     NewStatus = "NO",
     TimeOfEvent = DateTime.UtcNow.Subtract(TimeSpan.FromSeconds(120)),
     WorkorderID = "123"
   };
  var earlier = new WorkorderStatusChangeEvent
       {
        Id = Guid.NewGuid(),
        OldStatus = "BLAH",
        NewStatus = "NO",
        TimeOfEvent = DateTime.UtcNow.Subtract(TimeSpan.FromSeconds(60)),
        WorkorderID = "456"
       };
  var latest = new WorkorderStatusChangeEvent
       {
        Id = Guid.NewGuid(),
        OldStatus = "BLAH",
        NewStatus = "YES",
        TimeOfEvent = DateTime.UtcNow,
        WorkorderID = "456"
       };
  var anotherone = new WorkorderStatusChangeEvent
       {
        Id = Guid.NewGuid(),
        OldStatus = "BLAH",
        NewStatus = "NO",
        TimeOfEvent = DateTime.UtcNow.Subtract(TimeSpan.FromSeconds(300)),
        WorkorderID = "456"
       };
  IList list = new List();
  list.Add(earliest);
  list.Add(earlier);
  list.Add(latest);
  list.Add(anotherone);
  
  return list;
 }
}
{%endhighlight%}

Basically there are two parts. First getting the groupings by WorkorderID and extracting the PK of the object (Id) for the most recent record. This uses the let statement. The second part is a simple contains query that does the equivalent of a SQL IN to pull only those records from list whose Id is in the list of grouped/max date matches.

And by the way, I absolutely could not have ever figured this out without the great [LINQPad](http://www.linqpad.net/) tool by Joseph Albahari. It is free and yet absolutely priceless. Here are the results from the query as presented by the Dump extension method that LINQPad provides:

    5IEnumerable<WorkorderStatusChangeEvent> (2 items)

<table>
    <tr>
        <th>Id</th><th>WorkorderID</th><th>OldStatus</th><th>NewStatus</th><th>TimeOfEvent</th>
    </tr>
    <tr>
        <td>8191ab38-e070-4fd0-a8ea-83a7090c16d6</td>
        <td>123</td>
        <td></td>
        <td>NO</td>
        <td>12/24/2009 6:29:51 PM</td>
    </tr>
    <tr>
        <td>a5cee31a-643c-4642-b0f6-3c8f6e54cbfe</td>
        <td>456</td>
        <td>BLAH</td>
        <td>YES</td>
        <td>12/24/2009 6:31:51 PM</td>
    </tr>
</table>

And finally, have a great holiday. I've promised not to do any more techie stuff until the New Year. Well, I'm not going to blog until the New Year anyway!