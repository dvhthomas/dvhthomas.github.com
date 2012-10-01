---
layout: post
title: "NHibernate HQL Queries I always forget"
abstract: "Hibernate query language (HQL) is very powerful. And I always forget how to do a couple of the simpler queries. So here is a little reminder to myself."
category: 
tags: [nhibernate]
---
## Counting rows

The easy one is the first one---counting rows in a table. Stupid simple but I always forget the `UniqueResult` bit.

{%highlight csharp%}
public long Count()
{
    var woCount = _unitOfWork.CurrentSession
        .CreateQuery("select count(*) from Workorder")
        .UniqueResult<long>();
    return woCount;
}
{%endhighlight%}

## Get by Composite Primary Key

And the not-so-obvious but equally useful way to query an object with a composite primary key. You just pass an anonymous instance of the class with the primary key fields set.


{%highlight csharp%}
public Preference GetDefaultValuePreference(int domain, string name)
{
    if (domain < 0) throw new ArgumentOutOfRangeException(Resources.InvalidDomainMustBeZeroOrGreater);
    if (string.IsNullOrEmpty(name)) throw new ArgumentNullException("name");

    var preference = _unitOfWork.CurrentSession.Get<Preference>(new Preference { DomainId = domain, ElementId = name });
    return preference ?? new Preference { DefaultValue = string.Empty, DomainId = domain, ElementId = name };
}
{%endhighlight%}
