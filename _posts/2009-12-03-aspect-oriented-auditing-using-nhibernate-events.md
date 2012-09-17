---
layout: post
title: "Aspect oriented auditing using NHibernate Events"
abstract: "I have a legacy database with a wonky auditing feature. So wonky in fact that I cannot use the current set of vendor sprocs built for auditing. I use NHibernate Events to ensure that every time I change a domain object, I track the change in my own audit trail."
category: 
tags: [nhibernate]
---
## The Issue, in which Dylan gets bit in the ass by a legacy database

I'm building some message-oriented-middleware (MOM?) for a 3rd party vendor product. The database has evolved over many years and has all of the quirks that you might expect of such a system: primary keys that are implied but not made explicit with constraints, relationships that are implied but not explicit, columns that are not nullable in the business logic but are nullable in the tables, etc. I’m not knocking the vendor: I am keenly aware that keeping a multipurpose database absolutely clean of cruft is a tough challenge indeed. But it does make for some really tough integration points. My major challenge over the past week has been auditing. The vendor system makes very heavy use of sprocs and embeds the creation of the audit trail in those sprocs rather than using what, to my mind, is the more obvious approach of triggers.

Walking through an example, let’s say that my MOM or some other end user creates a new workorder record. The steps go like this:

1. Call the sproc to add the workorder—This itself calls a number of other sprocs with all kinds of logic in there based upon magic strings. Hairs standing up on the back of my neck!
1. Call the sproc to do the auditing
    1. Get the name of the table you’re adding a record to. In this case it might be something like WORKORDERS.
    1. Query a table that has a listing of specific columns in tables to keep an audit trail on. So the query might look something like this: `select a.auditcolumn from auditable a where a.tablename = 'WORKORDERS'`. The list of resulting `auditcolumns` tells us what values from our workorder records we have to add in to the `audittrail` table.
    1. For each `auditcolumn`, get the before value and after value from the inserted or updated record and store them in the `audittrail` table.

The ugly part is that I have to explicitly call the sproc to do the auditing rather than leverage a trigger to do the work for me. And the *really* ugly part is that I need to avoid user the vendor’s sprocs and replicate the business logic in C# code in the MOM. There are some historical reasons for this that are not relevant to this discussion, but the point remains: because I have to avoid the vendor sprocs “business logic interface” and because the auditing is not handled by triggers, I’m faced with figuring out the auditing with my tool of choice, NHibernate. The selection of NHibernate was driven primarily by the need for my MOM to have transparent support for both Oracle and SQL Server. SubSonic appears to have some holes related to Oracle that my co-workers have found, and Entity Framework is too new for me to be building a cross platfrom product core on top of. I am concerned that some of the wackier edge cases like auditing and composite keys will trip me up.

In summary, I have a legacy database with a wonky auditing feature, I cannot use the current set of vendor sprocs, and I need to be absolutely sure that when my MOM is creating and updating records that I create the audit trail.

## NHibernate Events and Aspect Oriented Programming

Of course this sounds like a perfect place to use some [AOP](http://en.wikipedia.org/wiki/Aspect-oriented_programming) jujitsu because the auditing function is cross cutting in nature, just like logging or security authorization. In other words, the act of creating a workorder or updating an employee record are tasks that a developer would need to understand and account for. But the auditing itself is orthogonal to the main task at hand and thus should be handled elsewhere in the code. Frameworks like Spring in the Java world and [PostSharp](http://www.postsharp.org/aop-net/overview) for the .NET crowd handle all of the plumbing to enable AOP. But luckily, so does the container that NHibernate uses---[the Castle project’s Windsor Container](http://castleproject.org/container/index.html).

Here’s the basic idea of AOP then. I should be able to create a class or implement and interface or listen for an event in my application code and tell the AOP framework to catch that event and do something with it. One of the canonical examples for AOP is logging; rather than litter my code with `Log.Debug("some message")` or `Log.Fatal("boom!")` I would rather tell the AOP framework to listen for any method call and write a debug statement, or listen for any unhandled exception and send an email to the system administrator. The Windsor Container (I’ll just call it Windsor from here on out) can do exactly that for me, and the NHibernate developers have built extensibility points in to the persistence lifecycle to help me. Enter NHibernate events.

These NH events were added at v2.0 and are a set of interfaces that I can implement to do things like, oh, I don't know...auditing! For example, there is an interface called `IPostInsertEventListener` that I can implement. If I then tell NH that I want to use my implementation of `IPostInsertEventListener` by adding it during the configuration stage of NH startup, then my code in the `OnPostInsert` method will run every single time a record is inserted or updated in the database. As you might imagine, when I realized the consequences of having this capability at my fingertips, I got a little giddy! After all this turned out to be the magic bullet I was looking for to solve my crazy auditing problem. Seems like I should be able to run through the steps I described above in that `OnPostInsert` method and add my audit records using the before and after values. Now, I'm more of a look-at-someone-elses-implementation-and-modify-it kind of guy, so I trolled around on the Internet and found a couple of great resources beyond the standard [NHibernate docs](http://www.nhforge.net/).

* Ayende has [a great blog](http://ayende.com/Blog/archive/2009/04/29/nhibernate-ipreupdateeventlistener-amp-ipreinserteventlistener.aspx) post describing almost precisely what I need to do. He’s one of the committers on NH as well so I felt like his advice was pretty sound.
* Rob Reynolds also read Ayende’s post and applied it specifically to an auditing event listener so I read [his approach](http://ferventcoder.com/archive/2009/11/18/nhibernate-event-listener-registration-with-fluent-nhibernate.aspx) with great interest as well.

## The pieces are all there. How to actually do it

Having done all of the research I was able to whip up my cross-cutting auditing event handler in pretty short order. Here’s the complete code, with some of the vendor specific stuff ellided and obfuscated for non-disclosure reasons:

{%highlight csharp%}
using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using NHibernate.Event;
using StructureMap;

namespace *****.Core.Persistence
{
    /// <summary>
    /// Adds auditing to classes that implement <see cref="IAuditable"/>
    /// </summary>
    /// <remarks>This is an NHibernate interceptor and will get called
    /// automatically whenever a transient entity is persisted
    /// (INSERTed) for the first time. It will examine the transient
    /// class for any <see cref="AuditedFieldAttribute"/>s on properties
    /// to get underlying column names that ***** might need to
    /// keep track of in the audit table (<see cref="*****Metadata"/>).</remarks>
    public class AuditEventListener : IPostInsertEventListener
    {
        public const string *****AuditUser = "*****Services";

        #region IPostInsertEventListener Members

        public void OnPostInsert(PostInsertEvent insertEvent)
        {
            // Make sure it's auditable first
            var audit = insertEvent.Entity as IAuditable;
            if (audit == null)
                return;

            // Then go in to specific implementations, starting with Workorders
            var workorder = audit as Workorder;

            if (workorder == null)
                return;

            if (workorder.DomainId.HasValue)
            {
                CreateAuditTrail(workorder, ObjectNames.TableWorkorder);
            }
        }

        #endregion

        /// <summary>
        /// Create audit trails for any fields that ***** needs to track. We do this
        /// by examining the class for fields with the <see cref="AuditedFieldAttribute"/>
        /// on them and then checking which of those fields ***** is interested
        /// in tracking.
        /// </summary>
        private static void CreateAuditTrail<T>(T auditThis, string tablename) where T : IAuditable
        {
            IList<*****Metadata> audits = new List<*****Metadata>();

            var ar = ObjectFactory.GetInstance<IAuditRepository>();
            IEnumerable<AuditedItem> auditableFields = ar.AuditableFields((int) auditThis.DomainId, tablename);
            if (auditableFields == null || auditableFields.Count() == 0) return;

            Type auditableType = typeof (T);

            foreach (PropertyInfo propertyInfo in auditableType.GetProperties())
            {
                // We're only interested in properties
                // that are auditable
                object[] customAttributes = propertyInfo.GetCustomAttributes(typeof (AuditedFieldAttribute), false);

                foreach (object o in customAttributes)
                {
                    var auditedAttribute = o as AuditedFieldAttribute;
                    object newValue = propertyInfo.GetValue(auditThis, null);
                    if (auditedAttribute != null)
                    {
                        AuditedItem matchingRecord =
                            auditableFields.FirstOrDefault(af => af.Field == auditedAttribute.DatabaseColumn);

                        // Looks like we've got an attribute that ***** wants
                        // to keep track of. Add it to the list...
                        if (matchingRecord != null)
                        {
                            var meta = new *****Metadata
                                           {
                                               ChangedByUser = *****AuditUser,
                                               ModifiedAt = DateTime.UtcNow,
                                               OldValue = null,
                                               NewValue = newValue == null ? null : newValue.ToString(),
                                               SourceField = auditedAttribute.DatabaseColumn,
                                               SourceId = auditThis.UniqueId,
                                               SourceTable = tablename
                                           };

                            audits.Add(meta);
                        }
                    }
                }
            }

            ar.CreateAuditTrail(audits);
        }
    }
}
{%endhighlight%}

As you can see I capture every single insert or update event in my system and then look for the `IAuditable` marker interface that I created for that purpose. If I actually have an `IAuditable` class then I proceed to handle the specific cases. Right now I just need to do workorders but expanding this is trivially easy. You can see where I then use some attributes to map between the properties/fields in my class and the column names in the database. I did try to mine the NHibernate metadata to avoid this (you can [read about my frustrations on Stack Overflow](http://stackoverflow.com/questions/1800930/getting-class-field-names-and-table-column-names-from-nhibernate-metadata)) but ultimately went with a bit of duplication of metadata to avoid a much bigger headache in the long run. This is, after all, a consulting gig and I can only futz around for so long before I just have to get the darn thing working.

How to configure NHibernate to use this? Well I’m using [Fluent NHibernate](http://fluentnhibernate.org/) for this project and luckily for me [Rob Reynolds had again beat me to it](http://ferventcoder.com/archive/2009/11/18/nhibernate-event-listener-registration-with-fluent-nhibernate.aspx). I essentially copied his code and arrived at this to hook it all together. Yep, just one extra line of code in my config setup:

{%highlight csharp%}
Configuration cfg = GetDbConnectionConfiguration(Resources.CityworksDatasource);
Fluently.Configure(cfg)
    .ExposeConfiguration(c =>
        c.EventListeners.PostInsertEventListeners = new IPostInsertEventListener[] { new AuditEventListener() })
        .Mappings(m => m.FluentMappings
            .Add()    ... // Lots more mappings
            .Add()
            .BuildConfiguration();
return cfg;
{%endhighlight%}

So there you have it, a very clean way to leverage the Windsor/NHibernate AOP extensibility point to make a messy auditing story a lot easier to swallow.