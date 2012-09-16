---
layout: post
title: "Poor man's spatial query against ArcSDE"
abstract: "Avoiding expensive APIs and dropping into SQL for a fast alternative to COM."
category: 
tags: [esri, sql]
---
I pretty much forget this every single time that I need to do a quick minimum bounding extent (MBE) or 'bounding box' query in ArcSDE. The ArcObjects alternative is just too painful to deal with when you simply need the extent of a feature, and SQL does the trick.

{%highlight sql%}
use sde_database
go
declare @meter nvarchar(20)
set @meter='MN13'

select layer_id from sde.SDE_layers where [owner] = 'GIS'
  and table_name='WMETER'

-- Answer is 155, and this is the table name for the next query
-- Notice the f155 here...

select b.OBJECTID, f.eminx,f.eminy from gis.f155 f
inner join gis.WMETER b
 on f.fid=b.Shape
where b.SerialNumber = @meter;
{%endhighlight%}

Like I said, stupid simple but I still have to [look it up](http://webhelp.esri.com/arcgisdesktop/9.3/index.cfm?TopicName=Feature_classes_in_a_geodatabase_in_SQL_Server) every darn time.