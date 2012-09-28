---
layout: post
title: "Circuit breaker of the non electrical variety"
abstract: "You all know about circuit breakers. They protect electrical networks and devices from surges by opening up when the bad stuff happens. Basically they are a binary toggle: a circuit breaker that is closed ensures that electricity can flow unimpeded through a medium like good old copper wires. A circuit breaker that is open...well...doesn't. It protects our expensive gadgets like computers and toasters from spikes in the supply. I may work for an engineering company, but that just exhausted my knowledge of what an actual, physical circuit breaker does."
category: 
tags: [patterns, dotnet]
---
You all know about circuit breakers. They protect electrical networks and devices from surges by opening up when the bad stuff happens. Basically they are a binary toggle: a circuit breaker that is closed ensures that electricity can flow unimpeded through a medium like good old copper wires. A circuit breaker that is open...well...doesn't. It protects our expensive gadgets like computers and toasters from spikes in the supply. I may work for an engineering company, but that just exhausted my knowledge of what an actual, physical circuit breaker does.

But what about protecting software from volatile resources in their own systems? I can't remember how many times I've assumed that a website was running when attempting to call it, or how many #\*(#%$#@! WCF services I've depended on in a "loosely coupled" system for critical things like, oh I don't know...security! I guess my loosely coupled systems are still prone to massive failures when some innocuous part decides to puke. I'm sure you've had this happen before: a database that didn't work, an file transfer that was just too slow. Enter the Circuit Breaker.

## Release It!

In most excellent book [Release It!](http://www.pragprog.com/titles/mnee/release-it) Michael T. Nygard presents many approaches to deploy fault tolerant software into the wild. We all know how easy it is to build software. We all know that it can bring a business to it's knees when said software doesn't work right. Personally I'm thinking about an embarrassing tool I wrote that crashed and burned when access to an FTP site wasn't there. Totally missed it during coding, got bit in the ass when a deployed system failed spectacularly. No details necessary. Suffice it say that shame caused me to seek out ways to make my deliverable more tolerant of the daily hiccups we all identify with. But Nygard's book is a real revelation me and many others in the pragmatic advice he gives to protect systems against just such failures. And of course, one "pattern" he advocates is the use of Circuit Breakers (big C and B).

It goes something like this:

1. Software calls an unreliable service like "Bob's automated electronic knife sharpening service". For some unfathomable reason this works the first time around. All good.
1. The next time we call the service it times out. Oh no! Disaster! Except we handle the error nicely and increment our "screw up" counter by one.
1. We try again (darn user just keeps clicking the "sharpen my knife on the internet button") and the thing fails again. No problem - we again catch the error and tell the use "Whoops!" and increment the "screw up" counter again. We now have two service failures. We have also configured our system to stop the madness if a service fails three times in a row.
1. Of course, the user clicks the button again immediately, thus ignoring all of our strongly worded advice that "it ain't going to work". Our "screw up" counter hits three and guess what? The circuit trips. Somewhere in our calling code we decide that enough is enough and we should just open the circuit and stop these requests to the unreliable service for a while. We hope beyond hope that just waiting a while, like maybe 30 seconds in a web application, will give Bob's Knife Sharpening Service time to recover.
1. Wouldn't you know it...the user still presses the darn button. But this time we stop the madness and immediately and instantly report back that the circuit is open and request cannot go through. Or a popup saying "Knife sharpening is busy...try again in a minute or two". Or we disable the offending button. Whatever we present to the user, the important part is that a timer is fired up when the circuit trips open and no amount of button clicking will induce our cleverly protected system to call the unstable service until the timeout period has expired.

Do you get the idea? We are essentially trying to stop a bad situation from getting worse. We all know that when a remote service is down, the last thing we should do is to just keep right on calling it. We should give it a chance to catch it's breath. That's what the Circuit Breaker gives us.

## C# Circuit Breaker, Anyone?

I've been burned enough time that I wanted to implement CB on my current project. Hey, who am I to ignore 100 years of sound electrical advice, let alone 5 year old software engineering wisdom? I found some really excellent implementations that all approach the problem from slight different angles. In particular the canonical (or first, at least) version came from [Tim Ross](http://timross.wordpress.com/2008/02/10/implementing-the-circuit-breaker-pattern-in-c/). This was followed up earlier in 2009 by the prolific [Davy Brion](http://davybrion.com/blog/) in a great [blog post](http://davybrion.com/blog/2009/07/protecting-your-application-from-remote-problems/) that laid it all out there. Davy uses the Castle Windsor inversion of control container to do some fancy aspect oriented stuff using interceptors (and if you understand that sentence they I think we would enjoy drinking a beer together). For my current project that is all a bit too much, plus I'm using [StructureMap](http://docs.structuremap.net), so I made a couple of very minor tweaks to his code to get up and running. Here's the implementation. Notice how the CB used a state pattern and failure counter but is really all about invoking an Action.

{% highlight csharp %}
using System;
using System.Timers;

namespace CityIQ.HealthMonitor
{
    /// <summary>
    /// Intercepts calls to brittle or problematic resources
    /// and maintains state of the resource using a circuit breaker
    /// analogy. A closed circuit is good, and open circuit is bad because
    /// it means that the resource being called is not responding within
    /// the allotted time span.
    /// </summary>
    /// <remarks>Apart from removing Castle Windsor Interceptor dependencies
    /// and going with an Action instead, this is verbatim from an excellent
    /// implementation by Davy Brion: http://davybrion.com/blog/2009/07/protecting-your-application-from-remote-problems/</remarks>
    public class CircuitBreaker : ICircuitBreaker
    {
        private readonly object _monitor = new object();

        private int _failures;
        private CircuitBreakerState _state;
        private TimeSpan _timeout;
        private readonly int _threshold;

        public CircuitBreaker(int threshold, TimeSpan timeout)
        {
            _threshold = threshold;
            _timeout = timeout;
            MoveToClosedState();
        }

        public int Failures
        {
            get { return _failures; }
        }

        #region IInterceptor Members

        public void ExecuteCall<T>(T invoker,Action<T> action)
        {
            using (TimedLock.Lock(_monitor))
            {
                _state.ProtectedCodeIsAboutToBeCalled();
            }

            try
            {
                action.Invoke(invoker);
            }
            catch (Exception e)
            {
                using (TimedLock.Lock(_monitor))
                {
                    _failures = Failures + 1;
                    _state.ActUponException(e);
                }

                throw;
            }

            using (TimedLock.Lock(_monitor))
            {
                _state.ProtectedCodeHasBeenCalled();
            }
        }

        #endregion

        private void MoveToClosedState()
        {
            _state = new ClosedState(this);
        }


        private void MoveToOpenState()
        {
            _state = new OpenState(this);
        }


        private void MoveToHalfOpenState()
        {
            _state = new HalfOpenState(this);
        }


        private void ResetFailureCount()
        {
            _failures = 0;
        }


        private bool ThresholdReached()
        {
            return Failures >= _threshold;
        }

        #region Nested type: CircuitBreakerState

        private abstract class CircuitBreakerState
        {
            protected readonly CircuitBreaker CircuitBreaker;

            protected CircuitBreakerState(CircuitBreaker circuitBreaker)
            {
                CircuitBreaker = circuitBreaker;
            }

            public virtual void ProtectedCodeIsAboutToBeCalled()
            {
            }

            public virtual void ProtectedCodeHasBeenCalled()
            {
            }

            public virtual void ActUponException(Exception e)
            {
            }
        }

        #endregion

        #region Nested type: ClosedState

        private class ClosedState : CircuitBreakerState
        {
            public ClosedState(CircuitBreaker circuitBreaker)
                : base(circuitBreaker)
            {
                circuitBreaker.ResetFailureCount();
            }

            public override void ActUponException(Exception e)
            {
                if (CircuitBreaker.ThresholdReached()) CircuitBreaker.MoveToOpenState();
            }
        }

        #endregion

        #region Nested type: HalfOpenState

        private class HalfOpenState : CircuitBreakerState
        {
            public HalfOpenState(CircuitBreaker circuitBreaker)
                : base(circuitBreaker)
            {
            }

            public override void ActUponException(Exception e)
            {
                CircuitBreaker.MoveToOpenState();
            }

            public override void ProtectedCodeHasBeenCalled()
            {
                CircuitBreaker.MoveToClosedState();
            }
        }

        #endregion

        #region Nested type: OpenState

        private class OpenState : CircuitBreakerState
        {
            private readonly Timer _timer;

            public OpenState(CircuitBreaker circuitBreaker)
                : base(circuitBreaker)
            {
                _timer = new Timer(circuitBreaker._timeout.TotalMilliseconds);
                _timer.Elapsed += TimeoutHasBeenReached;
                _timer.AutoReset = false;
                _timer.Start();
            }

            private void TimeoutHasBeenReached(object sender, ElapsedEventArgs e)
            {
                CircuitBreaker.MoveToHalfOpenState();
            }

            public override void ProtectedCodeIsAboutToBeCalled()
            {
                throw new OpenCircuitException();
            }
        }

        #endregion
    }
}
{% endhighlight %}

In my heartbeat service (health monitor for a web site) I do something very, very simple and test resources. The crux of the whole thing is to wrap that call to the potentially unreliable remote resource inside the circuit breaker:

{% highlight csharp %}
using System;
using System.Collections.Generic;
using CityIQ.HealthMonitor.Notifiers;
using CityIQ.HealthMonitor.Testers;

namespace CityIQ.HealthMonitor
{
    /// <summary>
    /// Implementation that can make requests of services and optionally notify
    /// interested parties of the results.
    /// </summary>
    public class HeartbeatMonitor : IHeartbeatMonitor
    {
        private readonly IEnumerable<INotifier> _notifiers;

        public HeartbeatMonitor()
        {
            _notifiers = new List<INotifier>();
        }

        /// <summary>
        /// Ctor that can take some notification providers
        /// </summary>
        /// <param name="notifiers"></param>
        public HeartbeatMonitor(IEnumerable<INotifier> notifiers)
        {
            _notifiers = notifiers;
        }

        #region IHeartbeatMonitor Members

        public void CheckResource(IResourceTester resource, ICircuitBreaker circuitBreaker)
        {
            try
            {
                circuitBreaker.ExecuteCall(resource, r => r.IsAlive());
                bool alive = resource.IsAlive();

                if (!alive)
                {
                    Notify(Importance.Minor, resource.Name, string.Format("Failed to call the resource {0}", resource.Name));
                }
            }
            catch (OpenCircuitException oce)
            {
                // This indicates that the service has been repeatedly unavailable
                // and we should let someone know about it. Until the timeout period
                // has passed we'll keep throwing these until the circuit is reset to half open
                Notify(Importance.Critical, resource.Name, oce.ToString());
            }
            catch (Exception e)
            {
                // The operation failed but not didn't happen enough to trip the circuit breaker.
                // So this is the exception that caused the problem.
                Notify(Importance.Important, resource.Name, e.ToString());
            }
        }

        #endregion

        private void Notify(Importance severity, string resourceName, string message)
        {
            foreach (INotifier notifier in _notifiers)
            {
                notifier.Notify(severity, resourceName, message);
            }
        }
    }
}
{% endhighlight %}

I've included a couple of unit tests so that you can see how it all ties together.

{% highlight csharp%}
using System;
using CityIQ.HealthMonitor;
using CityIQ.HealthMonitor.Testers;
using NUnit.Framework;
using StructureMap;

namespace CityIQ.MonitorTests
{
    [TestFixture]
    public class When_testing_web_sites
    {
        [SetUp]
        public void Before_any_test()
        {
            IoC.Bootstrap();
        }

        [Test]
        public void Valid_website_causes_no_failures()
        {
            var tester = new WebSite("Google","http://www.google.com",TimeSpan.FromSeconds(5d));
            var hb = new HeartbeatMonitor();
            var cb = ObjectFactory.GetInstance<ICircuitBreaker>();
            Assert.AreEqual(cb.Failures, 0);
            hb.CheckResource(tester, cb);
            Assert.AreEqual(cb.Failures, 0);
        }

        [Test]
        public void Inaccessible_website_causes_1_failure()
        {
            var tester = new WebSite("Boom", "http://www.google.com/c", TimeSpan.FromSeconds(5));
            var hb = new HeartbeatMonitor();
            var cb = ObjectFactory.GetInstance<ICircuitBreaker>();
            Assert.AreEqual(cb.Failures, 0);
            hb.CheckResource(tester, cb);
            Assert.AreEqual(cb.Failures, 1);
        }
    }
}
{%endhighlight%}

## Summary

The circuit breaker protects a system from potentially unreliable dependencies. It does not bury the errors but actually let's the calling application still be fully aware of the exceptions. But it does draw a line in the sand by way of a failure threshold and stops an excessive number of calls to the bad resource. That is the essence of controlled failure. Let the thing break, but don't let the break cause a cascading meltdown to your carefully crafted calling system. Handle the unpredictability by opening the circuit.