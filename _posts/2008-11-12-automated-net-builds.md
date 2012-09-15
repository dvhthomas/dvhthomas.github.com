---
layout: post
title: "Automated .NET builds"
abstract: "Time to look at automating the painful task of building and testing complex projects."
category: 
tags: [automation]
---
For the past few months I’ve been ramping up on my software building skills. Having cut my teeth on the .NET Framework, my weapon of choice for writing code has long been Visual Studio. Consequently I’ve always considered pushing F5 to be the extent of building software. Of course now I’m a little wiser and know the difference between compiling it and building something useful. In fact, the biggest impetus for me to learn how to run a more elaborate build process was working in a distributed team and needing to keep in sync. Anyway, what do I mean by building anyway?

## Reducing friction

A build process is simply a repeatable way to take a bunch of inputs and finish with a desired set of outputs. Think of a typical web application. It probably has some pages, some resources like images, CSS, JavaScript files, etc. But it also usually has one or more configuration files, 3rd party components, a database or two, and possibly even some management tools. Now imagine having to join a team of developers who are already writing that web site, and being productive immediately. This is where the build process comes in. It should go something like this:

1. Open IDE
1. Connect to version control system and download the trunk (most recent buildable version of the project)
1. Read the Readme.txt file describing the build process.
1. Run the build script
1. Start working

Unfortunately my prior experience has been more along these lines:

1. Open IDE
1. Download the latest code
1. Press F5 and wonder what all the errors are
1. Ask the lead developer what I’m missing, and discover that there are three database I forgot to install, and a dependency for ASP.NET AJAX to XCOPY deploy first.
1. Do what is suggested, still get a bunch of errors. Discover that there are 5 configuration settings that work on Bob’s PC but not on mine so I have to change them.
1. Waste the rest of the day on this crap.
1. Waste most of the next day on similar issues.
1. Sometime towards the end of day three (I kid you not) I can actually start to write code and add value to the project.

Which do you think I prefer?

So the build process implies a couple of things: a _build tool_ that actually does all of the little bits and pieces for me like compiling code, setting up databases, adding users to systems, etc., and also a _build script_ that the build tool uses to do it’s thing. There are numerous build tools out there and they generally seem to be either code based, e.g., Rake uses a Ruby script, bake uses a Boo script, or heavy on the angle brackets, e.g., Ant (Java), Nant (.NET), and MSBuild (.NET) all rely on XML documents to describe the build process. Personally I really like the readability of rake (Ruby) scripts, and theoretically there’s no reason why I could use Rake on my .NET projects. However, I decided to tow the party line and use MSBuild for my first attempts and build scripts simply because is is guaranteed to be installed on every .NET developers machine: one less thing to worry about.

## It doesn't just happen

As I was reading all of the various ALT.NET and agile remonstrations for *not* having a build process, I wondered why on earth everyone didn’t just do this stuff in the first place. Then I tried to create a build script to do the things I need to do and had a very rude awakening. It turns out to be fairly tough to learn MSBuild in the first place. As with anything, the initial frustration level was high enough to make me curse Microsoft up and down, but once I got the hang of it I found it relatively painless (like maybe stubbing your toe badly as opposed to slicing a finger off). In other words, I still find it to be a bit of a chore to keep up with the build script as things evolve, but here’s the lesson:

**Make sure your build script is one of the very first things you do on a fresh project. It’s a lot less painful to make small incremental steps than it is to figure it all out at the end of a project.**

In fact, maintaining a running build has become so central to my last couple of projects for that very reason. Think about this: in order to set up my current project I need to...

1. Install 4 databases from scratch
1. Install one web application
1. Install two web service projects – one is mine, the other is a vendor solution
1. Create web proxies dynamically each time the code in the web services change
1. Update at least 10 config files
1. etc.
1. etc.

Things absolutely go wrong with the build, but the great thing is when I fix something, it always works in the future, and if it breaks again it’s because something has changed that I probably needed to know about in the first place. It’s kind of like test driven development but for your whole project, not just for one tiny piece of it.

## Next time

In my next post I’ll describe what is happening in my latest build script and how it helps the team of 4 developers in 3 time zones and 4 cities to keep tightly in sync.