---
layout: post
title: "Parsing XML in a SQL Server stored procedure"
abstract: "I had to send a variable number of columns and values to a stored procedure. So for one query I might need to do the equivalent of an IN query (all values in one search column), but in other cases I might need to do a search on a number of columns and values (WHERE a = 1 AND b = 2 OR…). Here's how I do it."
category: 
tags: [sqlserver]
---
There are all kinds of ways of doing this, but for my application I opted to create a little XML snippet to send the data. Don’t ask me why except that it makes a lot of sense in the context of the code I need to execute. Here’s the C# code where I’m calling my procedure:

{% highlight csharp %}
using (var repository = new RepositoryBase(this._connectionStringName))
{
    IDbCommand command = new SqlCommand(storedProcedure) { CommandType = CommandType.StoredProcedure };
    IDbDataParameter p = command.CreateParameter();
    p.DbType = DbType.Xml;
    p.ParameterName = "?list";
    p.Direction = ParameterDirection.Input;
    p.Value = auditTracking.GenerateCoreEditListAsXml().ToString(SaveOptions.None);
    command.Parameters.Add(p);
    DataSet edits = repository.ExecuteQuery(command, tableNames);
    affectedRecords = this.ParseResultsToAuditRecords(edits);
}
{% endhighlight %}

Where the `GenerateCoreEditListAsXml` function sets the value of the `p.Value` parameter to something like this:

{% highlight xml %}
<PKs>
    <row id="1">
        <pk name="FCA_SURVEY_ID">35255</pk>
    </row>
    <row id="2">
        <pk name="FCA_SURVEY_ID">35254</pk>
    </row>
</PKs>
{% endhighlight %}

In regular SQL calling the procedure looks something like this:

{% highlight sql %}
use [CorridorField]
declare @list xml;
set @list = '<PKs>
 <row id="1">
 <pk name="PATH_ID">10</pk>
 <pk name="ATTRIB_NAME">_Last Visit</pk>
 <pk name="ATTRIB_VALUE">20-Jun-2005</pk>
 </row>
 <row id="2">
 <pk name="PATH_ID">10</pk>
 <pk name="ATTRIB_NAME">05. Service</pk>
 <pk name="ATTRIB_VALUE">Air Force</pk>
 </row>
 <row id="3">
 <pk name="PATH_ID">12</pk>
 <pk name="ATTRIB_NAME">_Playground PA</pk>
 <pk name="ATTRIB_VALUE">Yes</pk>
 </row>
</PKs>'
DECLARE @RC int

EXECUTE @RC = [CorridorField].[FCA].[uspAuditPath_Attrib] 
 @list
{% endhighlight %}

The procedure I’m calling in turn has this inside it. Notice how I’m first transforming the XML parameter in to a temporary table? That is so I can use it as the filter on the WHERE portion of the main query using an IN statement:

{% highlight sql %}
set ANSI_NULLS ON
set QUOTED_IDENTIFIER ON
go

/*
 Get all data associated with a batch of FUS_BLDGS records
*/
ALTER procedure [FCA].[uspAuditPath_Attrib](@list xml)
as
declare @results table(PKRow varchar(30), PKColumn varchar(30), PKValue varchar(30))
 
insert into @results
 select DataSource.keys.value('../@id','varchar(30)') as PKRow
 , DataSource.keys.value('@name','varchar(30)') as PKColumn
 , DataSource.keys.value('.','varchar(30)') as PKValue
 from @list.nodes('/PKs/row/pk') as DataSource(keys)

select * from @results;
-- paths
select distinct(p.path_id) from [path] p
where convert(varchar(30),path_id) in (select distinct(convert(varchar(30),pa.path_id))
 from dbo.path_attrib as pa
 where convert(varchar(30),pa.path_id) in 
 (select PKValue from @results))
{% endhighlight %}

So what do the results look like? Pretty boring actually. The purpose is to pass in multiple rows with multiple discriminating columns and use those to get records from a related table. In this case it’s kind of boring but I couldn’t think of a better or more flexible way of doing it. Maybe I’m just creating a rats nest of maintenance but it’ll work for now.

![Query results using XML as criteria](/images/xml-in-sqlserver.png)