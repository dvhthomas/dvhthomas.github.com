---
layout: post
title: "WiX, XML, and building Windows services"
abstract: "I was tripped up by a couple of WiX things this week while building an installation package for a Windows services project."
category: 
tags: [dotnet, automation]
---
## Windows Services

The first was getting the Windows service to be started correctly. I’ve done this before using [WiX](http://wix.sourceforge.net/) but couldn’t get it to work this time around. Here was my starting point:

{% highlight xml %}
<Directory Id="IMPORTLOCATION" Name="FCA Importer">
<!-- Windows Service that actually imports data from uploaded files to the server db -->
<Component Id="ImportWindowsService" Guid="{87477BBB-E01D-4aa6-8E57-0262F17B40CA}">
  <CreateFolder/>
    <File Id="_7za.exe1" Source="$(var.DoDEA.Sync.ImportService.TargetDir)\7za.exe" />
    <File Id="DoDEA.FCA.Services.dll1" Source="$(var.DoDEA.Sync.ImportService.TargetDir)\DoDEA.FCA.Services.dll" />
    <File Id="DoDEA.Sync.Client.dll1" Source="$(var.DoDEA.Sync.ImportService.TargetDir)\DoDEA.Sync.Client.dll" />
    <File Id="FcaImportService.exe" Source="$(var.DoDEA.Sync.ImportService.TargetPath)" />
</Component>
{% endhighlight %}

I am using a 3rd party compression tool---[7zip](http://www.7-zip.org/)---to manage some aspects of my app so, being alphabetically inclined, I put that first on my list of files to include. The actual service is in the file `FcaImportService.exe`. Then I have my usual service setup and start bits in the same component like this:

{% highlight xml %}
<ServiceInstall Id="ImporterService"
  Name="FcaImport"
  Account="[SERVICEACCOUNT]"
  Password="[SERVICEPASSWORD]"
  DisplayName="DoDEA Importer"
  Type="ownProcess"
  ErrorControl="normal"
  Description="Windows service to reconcile uploaded field edits with the central application database"
  Start="auto"
  Interactive="no"/>
<ServiceControl Id="StopImport" Name="FcaImport" Remove="both" Stop="both"/>
{% endhighlight %}

As I mentioned I’ve used this exact approach before with success. But that darn service kept bombing when it was trying to start! It was a really easy fix though. Simply make sure that the **first** File in the Component is the one that holds the service implementation and WiX will then happily create the service while pointing to the correct executable. Just look in the Service Control Manager to see which file WiX is actually pointing at:

![wix](/images/wix-square-brackets.png)

## XML Hiccup

Really annoying one. It turns out that the Windows installer database that is encapsulated in the *.MSI file treats square brackets as variable delimeters*. So when you use a string that WiX is going to interpret and that string includes square brackets, you need to escape them. Naturally one example is in XPath. Here’s how it should look in WiX:

{% highlight xml%}
<Component Id="ImportDirectory" Guid="{382E974D-69C6-4dc5-B2DD-FC8C8F5D5688}">
  <CreateFolder/>
    <!-- Note the goofy escaping of square brackets in the XPath -->
    <util:XmlFile Id="ModifyImportLocation"
      Action="setValue"
      ElementPath="//configuration/appSettings/add[\[]@key='ImportHoldingArea'[\]]/@value"
      File="[IMPORTLOCATION]\FcaImportService.exe.config"
      Value="[IMPORTHOLDINGAREA]"/>
</Component>
{% endhighlight %}

Hope that saves you a few minutes of head scratching.
