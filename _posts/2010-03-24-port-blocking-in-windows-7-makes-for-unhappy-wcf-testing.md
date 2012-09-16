---
layout: post
title: "Port blocking in Windows 7 makes for unhappy WCF testing"
abstract: "Windows 7 locks down HTTP pretty hard. Luckily an netsh one-liner keeps things moving along."
category: 
tags: [windows, dotnet]
---
I typically do something like this when I'm testing a WCF service (using NUnit here):

{% highlight csharp %}
namespace Tests
{
    [TestFixture]
    class When_running_as_hosted_service
    {
        private ServiceHost _host;
        private IWhoKnowsService _client;

        [SetUp]
        public void Before_any_test()
        {
            // 1.
            // Start a WCF service hosted in a generic ServiceHost
            // This is exactly the same as hosting in IIS or a console app
            const string port = "http://localhost:12345/";
            var uri = new Uri(port);
            _host = new ServiceHost(typeof(WebService), uri);
            _host.AddServiceEndpoint(typeof(IWhoKnowsService), new WSHttpBinding(), uri);
            _host.Open();
            
            // 2.
            // Now dynamically build a client to that service.
            // This is the same as 'Add Service Reference' but without all
            // of the code generation
            _client = new ChannelFactory(new WSHttpBinding())
                .CreateChannel(new EndpointAddress(port));
        }

        [TearDown]
        public void After_all_tests()
        {
            // Tear it down so that the TCP port is release correctly
            _host.Close();
        }

        [Test]
        public void Can_get_a_list_of_descripts_for_a_skill_level() 
        {
            var descriptions = _client.DescriptionsByLevel(SkillLevel.Padwan);
            Assert.IsNotNull(descriptions);
            Assert.Greater(descriptions.Length, 0);

            foreach (var item in descriptions)
            {
                Console.WriteLine(item);
            }
        }
    }
}
{% endhighlight %}

I've used this technique many, many times on Windows XP but I just made the switch to Windows 7 for development, having skipped Vista entirely. When trying to run that test I get this error back from the test runner:

{% highlight %}
AddressAccessDeniedException: HTTP could not register URL http://+:12345/<…>.  Your process does not have access rights to this namespace
{% endhighlight %}

That's not good. So I hit the Internet and found an [excellent post](http://blogs.msdn.com/drnick/archive/2006/10/16/configuring-http-for-windows-vista.aspx) by [Nicholas Allen](http://blogs.msdn.com/drnick/default.aspx) that set me straight. Basically Windows 7 really locks down your usage of TCP ports over HTTP. Using the trusty old `netsh` command he shows how to open up the port of choice in one easy step:

    netsh http add urlacl url=http://+:12345/ user=dev2010\Dylan

Problem solved! I reran the test in Visual Studio and got a pass. NOTE: You *must be running your Command Prompt as an administrator* in order for this to work. In other words, right click on Command Prompt in your Start Menu and choose the appropriate option.