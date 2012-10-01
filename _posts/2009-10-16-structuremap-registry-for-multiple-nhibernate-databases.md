---
layout: post
title: "StructureMap registry for multiple NHibernate Databases"
abstract: "How to clean up your code base by centralized object initialization using an Inversion of Control container."
category: 
tags: [dotnet, nhibernate, ioc]
---
This is more for my information but feel free to look. I have centralized all object dependencies in my current project and have settled on the [StructureMap](http://docs.structuremap.net) IoC container as the coordinator. It took me a while to figure this out because I have two databases configured with NHibernate and depending on which repository I'm using I need to point to different NHibernate ISessionFactory instances. This was getting complicated so I created a simple unit of work class to manage the details, and was left with a much cleaner config. Admittedly this may look complicated to the uninitiated, but it's a lot easier that spreading all this stuff throughout my entire code base.

{%highlight csharp%}
/// <summary>
/// All of the dependencies for the core Cityworks processing
/// </summary>
public class CityworksCoreRegistry : Registry
{
    public CityworksCoreRegistry()
    {
        ForRequestedType<ILogFactory>().TheDefaultIsConcreteType<NLogFactory>();

        ISessionFactory cityworks = NHibernateHelper.SessionFactory(Resources.CityworksDatasource);
        ISessionFactory wcs = NHibernateHelper.SessionFactory(Resources.WCSDatasource);

        ForRequestedType<ISessionFactory>()
            .AddInstances(x =>
                              {
                                  x.IsThis(cityworks).WithName(Resources.CityworksDatasource);
                                  x.IsThis(wcs).WithName(Resources.WCSDatasource);
                              })
            .TheDefault.Is.TheInstanceNamed(Resources.CityworksDatasource);

        ForRequestedType<IUnitOfWork>()
            .AddInstances(x =>
                              {
                                  x.OfConcreteType<UnitOfWork>()
                                      .CtorDependency<ISessionFactory>("sessionFactory")
                                      .Is(z => z.TheInstanceNamed(Resources.CityworksDatasource))
                                      .WithName(Resources.CityworksDatasource);
                                  x.OfConcreteType<UnitOfWork>()
                                      .CtorDependency<ISessionFactory>("sessionFactory")
                                      .Is(z => z.TheInstanceNamed(Resources.WCSDatasource))
                                      .WithName(Resources.WCSDatasource);
                              })
            .TheDefault.Is.TheInstanceNamed(Resources.CityworksDatasource);

        ForRequestedType<ISpatialQuery>()
            .TheDefaultIsConcreteType<ClientPlugin>();
        ForRequestedType<IMessageProcessor>()
            .TheDefaultIsConcreteType<CoreMessageProcessor>();
        ForRequestedType<SystemConfiguration>()
            .TheDefaultIsConcreteType<SystemConfiguration>();
        ForRequestedType<IUserRoleRepository>()
            .TheDefaultIsConcreteType<UserRoleRepository>();

        ForRequestedType<ISettingRepository>()
            .TheDefault.Is.OfConcreteType<ApplicationSettingRepository>()
            .CtorDependency<IUnitOfWork>("unitOfWork")
            .Is(u => u.TheInstanceNamed(Resources.WCSDatasource));

        InstanceOf<IWorkorderRepository>().Is.OfConcreteType<WorkorderRepository>()
            .CtorDependency<IUnitOfWork>("unitOfWork")
            .Is(x => x.TheInstanceNamed(Resources.CityworksDatasource));
        InstanceOf<IMessageRepository>().Is.OfConcreteType<MessageRepository>()
            .CtorDependency<IUnitOfWork>("unitOfWork")
            .Is(x => x.TheInstanceNamed(Resources.WCSDatasource));
        InstanceOf<ISettingRepository>().Is.OfConcreteType<ApplicationSettingRepository>()
            .CtorDependency<IUnitOfWork>("unitOfWork")
            .Is(x => x.TheInstanceNamed(Resources.WCSDatasource));
        InstanceOf<ICityworksRepository>().Is.OfConcreteType<CityworksMSSQL>()
            .CtorDependency<IUnitOfWork>("unitOfWork")
            .Is(x => x.TheInstanceNamed(Resources.CityworksDatasource));
    }
}
{%endhighlight%}