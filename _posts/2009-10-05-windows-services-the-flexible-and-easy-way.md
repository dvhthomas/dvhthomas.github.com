---
layout: post
title: "Windows services the flexible and easy way"
abstract: "For a long time now I’ve been a big fan of creating Windows service projects in .NET using console applications rather than the canned Visual Studio Service Project template. My primary reason initially was to make sure I could debug the service application easily by setting a command line switch rather than monkeying around with attempting to debug a live Windows service."
category: 
tags: [dotnet]
---
## Business as usual

By using a console, my typical code would look something like this:

{%highlight csharp%}
internal class Program
{
    private static void Main(string[] args)
    {
        ILogFactory factory = new NLogFactory();
        Log.InitializeLogFactory(factory);
        ContainerBootstrapper.BootstrapStructureMap();

        if (Environment.CommandLine.ToLower().Contains("-console"))
        {
            Console.WriteLine("Starting service in console mode...");
            using (var hostService = new GeneratorHost())
            {
                hostService.StartMeUp();

                Console.WriteLine("{0} is running with the following WCF endpoints..." + Environment.NewLine,
                                  hostService.Host.Description.ServiceType.Name);

                Console.WriteLine("Endpoints");
                Console.WriteLine("*********");

                foreach (var se in hostService.Host.Description.Endpoints)
                {
                    Console.WriteLine("Endpoint:");
                    Console.WriteLine("name: {0}", se.Name);
                    Console.WriteLine("address: {0}", se.Address);
                    Console.WriteLine("binding: {0}", se.Binding.Name);
                    Console.WriteLine("contract: {0}\n", se.Contract.Name);
                }

                Console.WriteLine("Service started. Press 'Enter' to Exit");
                Console.ReadLine();
                hostService.ShutMeDown();
            }
        }
        else
        {
            var servicesToRun = new ServiceBase[] {new GeneratorHost()};
            ServiceBase.Run(servicesToRun);
        }
    }
}
{%endhighlight%}

Notice how the first check is to see whether the command line contains a switch called `–console`? That is something I set up in the DEBUG properties of the Visual Studio project. So whenever I launch the executable during development it acts just like a console app, and I can in fact use that in production as well for testing purposes (`-CONSOLE` spits out a lot more logging information). If the `–console` switch isn’t present then the service class—--GeneratorHost in this case—--starts as a service as usual.

## TopShelf

But I’ve been looking at [TopShelf](http://topshelf-project.com) recently and prefer what I see here as a cleaner approach for testable code. It came from the [MassTransit](http://masstransit-project.com) open source .NET service bus project as a way to quickly create service hosts for the large number publishers and subscribers involved in a typical MassTransit implementation, and was then refactored out in to its own project that has, interestingly enough, been coopted by [Udi Dahan](http://www.udidahan.com) in his own [NServiceBus](http://nservicebus.com) project.

I came across TopShelf mostly because I’ve been pleased with how the MassTransit and nServiceBus approach to distributed systems is shaping up on my current project. I’m using a hand-rolled message queue with a database backend (NHibernate for Oracle, SQL Server, and SQLite support) and making all of my information exchanges be self contained messages that are simply added to the message queue for further processing. The WCF services for web service endpoints and other backend processing code are all hosted as Windows services for ease of deployment and configuration (app.config rather than messing with IIS 6.0). And the nice thing about TopShelf is that it support the IoC container that I’m using these days—StructureMap—and makes debugging and installation/deinstallation a piece of cake. Not to mention XML config of the user account for the service to run under which is a bonus when dealing with [ArcGIS Server](http://resources.esri.com/help/9.3/arcgisserver/apis/arcobjects/ao_start.htm) direct connections, which is how I'm using TopShelf in the first place.

So what does it look like? Simply put, there is a fluent configuration API that talks to StructureMap and dynamically builds a Windows service for you without tinkering with ServiceInstaller classes and the like. Here’s an example from my current project where the main purpose of the Windows service is simply to serve as a host to a WCF HTTP service that in turn runs some ArcObjects bits:

{%highlight csharp%}
using System;
using StructureMap;
using Topshelf;
using Topshelf.Configuration;

namespace GisQueryDirectHost
{
    internal class Program
    {
        private static void Main(string[] args)
        {
        // Set up logging and other application services using StructureMap
            ContainerBootstrapper.BootstrapStructureMap();

            try
            {
                IRunConfiguration cfg = RunnerConfigurator.New(x =>
                {
                    x.AfterStoppingTheHost(h => Console.WriteLine("All services are stopping since the host is closing down."));
                    x.ConfigureService<QueryHost>("qh", s =>
                    {
            // Here comes StructureMap behind the Microsoft ServiceLocator facade
                        s.CreateServiceLocator(() =>
                        {
                            ObjectFactory.Initialize(i =>
                            {
                                i.ForConcreteType<QueryHost>().Configure.WithName("qh");
                                i.ForConcreteType<ServiceConsole>();
                            });

                            return new StructureMapServiceLocator();
                        });
                        
            // I have two methods in my QueryHost class...Start and Stop. They simply
            // start and stop a WCF service host process
                        s.WhenStarted(qh => qh.Start());
                        s.WhenStopped(qh => qh.Stop());
                    });

                    x.SetDescription("Supports generation of basic spatial data for clients through an ArcGIS Server query");
                    x.SetDisplayName("WCS GIS Query");
                    x.SetServiceName("wcsgisquery");
                    
            // You can also specify username/password, or point to app.config in one line of code
                    x.RunAsLocalSystem();
                });

                Runner.Host(cfg, args);
            }

            catch (Exception e)
            {
                Console.WriteLine(e);
            }
        }
    }
}
{%endhighlight%}

I got a bit turned around with the StructureMap / Microsoft.Practices.ServiceLocation facade but the TopShelf source code has a good example of how to implement this. In fact, it was a cut’n’paste job:

{%highlight csharp%}
using System;
using System.Collections.Generic;
using Microsoft.Practices.ServiceLocation;
using StructureMap;

namespace GisQueryDirectHost
{
    public class StructureMapServiceLocator : IServiceLocator
    {
        #region IServiceLocator Members

        public object GetService(Type serviceType)
        {
            return ObjectFactory.GetInstance(serviceType);
        }

        public object GetInstance(Type serviceType)
        {
            return ObjectFactory.GetInstance(serviceType);
        }

        public object GetInstance(Type serviceType, string key)
        {
            return ObjectFactory.GetNamedInstance(serviceType, key);
        }

        public IEnumerable<object> GetAllInstances(Type serviceType)
        {
            foreach (object instance in ObjectFactory.GetAllInstances(serviceType))
            {
                yield return instance;
            }
        }

        public TService GetInstance<TService>()
        {
            return ObjectFactory.GetInstance<TService>();
        }

        public TService GetInstance<TService>(string key)
        {
            return ObjectFactory.GetNamedInstance<TService>(key);
        }

        public IEnumerable<TService> GetAllInstances<TService>()
        {
            return ObjectFactory.GetAllInstances<TService>();
        }

        #endregion
    }
}
{%endhighlight%}

## Debug, install, uninstall

The truly great thing about TopShelf, though, is using it in production. Putting the configuration in a console application means that by default running the EXE such as `GisDirectQueryHost.exe` runs the “service” without having a Windows service. Running `GisDirectQueryHost.exe /install` installs the service and (you saw this one coming) `/uninstall` removes it. But in a real hat-tip to flexibility you can install multiple separate instances of the service by adding `/install – instance InstanceName`. Now that’s just plain cool. Thank you [Kevin Miller](http://www.dovetailsoftware.com/blogs/kmiller/archive/2009/09/24/running-multiple-instances-of-a-windows-service-using-topshelf) for pointing this out.

