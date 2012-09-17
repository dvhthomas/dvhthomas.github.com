---
layout: post
title: "Creating WSDLs from .NET assemblies"
abstract: "In a Web services world, WSDLs and XSDs are the lingua franca of communications. I'm primarily building services in .NET so it's easy to forget that not every client is also a .NET client. Here is how to support the Java, Python, and Ruby consumers in one go. And it actually works better for .NET clients too."
category: 
tags: [dotnet, webservices]
---
More of a reminder to myself than anything else, here's a batch file that creates proxy classes that can talk to WCF services. The WCF service interfaces are defined in the Visual Studio project build output. Then it's a simple matter of using the `svcutil` command line utility from the .NET SDK to go through the motions. This turns out to be a great way to automate the creation of WSDLs for non-.NET clients, and a good way to create proxy classes that you have a lot more control over than the “Add Service Reference” approach in Visual Studio.

    set outDir=..\build\wcs-wsdlset /
        wsdlDir=..\lib\wcs-wsdlset /
        svc="C:\Program Files\Microsoft SDKs\Windows\v6.0A\Bin\svcutil.exe"
    set msbuild="C:\WINDOWS\Microsoft.NET\Framework\v3.5\msbuild.exe"
    rmdir /s /q %outDir%mkdir %outDir%%
    msbuild% ..\source\Woolpert.Cityworks.Services\Woolpert.Cityworks.Services.csproj
    %svc% ..\source\Woolpert.Cityworks.Services\bin\Debug\Woolpert.Cityworks.Services.dll
    %svc% *.xsd www.woolpert.com.wis.cityworks.wsdl /language:C# /out:%outDir%\CityworksClient.cs
    %svc% *.xsd www.woolpert.com.wis.security.wsdl /language:C# /out:%outDir%\SecurityClient.cs
    %svc% *.xsd www.woolpert.com.wis.spatial.wsdl /language:C# /out:%outDir%\SpatialClient.cs
    xcopy *.xsd %wsdlDir%\ /I /Y
    xcopy *.wsdl %wsdlDir%\ /I /Y
    xcopy *.config %wsdlDir%\ /I /Y
    del /q *.xsd
    del /q *.wsdl
    del /q *.config

In my other projects that need access to clients I can then run a subset of this script and be all set for consuming the web services:

    set output=MyMiddleware.cs
    del %output%
    set svc="C:\Program Files\Microsoft SDKs\Windows\v6.0A\Bin\svcutil.exe"
    %svc% *.wsdl *.xsd /language:C# /o:%output%
