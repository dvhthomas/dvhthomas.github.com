---
layout: post
title: "When you expect an exception using NUnit 2.5"
abstract: "I have a piece of code that I know throws an exception during testing, but I need to then do some work after the exception has been thrown to make sure that my system is in a consistent state."
category: 
tags: [testing, dotnet]
---
I keep forgetting this and it's a hassle to find an example. Here's how I'm running some code to do the setup and throwing the actual exception. And then there's the part that does my second round of checking. Obviously in this case I don't want to see data in the database if an exception happening before my transaction was committed.

{%highlight csharp%}
[Test]
public void Throwing_an_exception_prevents_anything_from_being_saved()
{
    Assert.Throws<Exception>(() =>
                                 {
                                     using (ISession session = NHibernateHelper.OpenSession())
                                     {
                                         Person person = ObjectMother.ValidPerson();
                                         Person person2 = ObjectMother.ValidPersonTwo();

                                         using (ITransaction transaction = session.BeginTransaction())
                                         {
                                             var ps = new PersonService(session);
                                             ps.SaveChanges(person);
                                             ps.SaveChanges(person2);
                                             throw new Exception();
                                             transaction.Commit();
                                         }
                                     }
                                 });

    using (ISession session = NHibernateHelper.OpenSession())
    {
        var ps = new PersonService(session);
        long count = ps.Count();
        Assert.AreEqual(0, count);
    }
}
{%endhighlight%}
