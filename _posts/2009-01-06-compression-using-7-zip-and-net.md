---
layout: post
title: "Compression using 7 zip and .NET"
abstract: "Hooking up an open source compression library in executable form for a .NET project"
category: 
tags: [dotnet]
---
## Alternatives

I needed to compress some data across the wire on a project. Basically sending very large files that, when compressed, get really small so choosing the right compression algorithm is important. I ran tests with [SharpZipLib](http://sharpziplib.com) and the native .NET zip compression handlers with decent results. But I also use the [7-zip](http://www.7-zip.org/) desktop application for my day to day usage instead of WinZip so I tried compressing the data files using that as well. Glad I did: the 7-zip compressed an additional 20% on top of what ZIP did. Well worth the effort to incorporate in to my WCF application.

I basically took the code wholesale from [this post by Rob Reynolds](http://geekswithblogs.net/robz/archive/2008/09/23/sharpziplib-versus-7-zip-for-large-file-sets.aspx) and sprinkled in a little of my own meager magic. The solution revolves around a generic `IZip` interface and `IZipFileUtility`. Lots of comments:

## Code Time

First the interface for any zipping utility

{% highlight csharp %}
using System;
using System.IO;

namespace Woolpert.Compression
{
    /// <summary>
    /// Zips files up
    /// </summary>
    public interface IFileZipUtility
    {
        /// <summary>
        /// Zips files from a directory and subdirectories
        /// </summary>
        /// <param name="zipFilePath">The name of the zipped file</param>
        /// <param name="directory">directory to zip files up in</param>
        void GenerateZipFile(string zipFilePath, string directory);

        /// <summary>
        /// Zips files from a directory and subdirectories if recursive is true
        /// </summary>
        /// <param name="zipFilePath">The name of the zipped file</param>
        /// <param name="directory">directory to zip files up in</param>
        /// <param name="recursive">Would you like to zip up subdirectories as well?</param>
        void GenerateZipFile(string zipFilePath, string directory, bool recursive);


        /// <summary>
        /// Zips a single file in to a compressed archive
        /// </summary>
        /// <param name="zipFilePath">The full name of the zip file that
        /// will be created, e.g., "C:\Temp\MyArchive.7z". Make 
        /// sure that the file extension is appropriate to the 
        /// archive format that you are creating, e.g., zip or 7z.
        /// 
        /// If the archive already exists then the file will be added
        /// to that archive. Delete any existing files first if you
        /// want a fresh archive.</param>
        /// <param name="file">The file that you want to compress</param>
        void GenerateZipFile(string zipFilePath, FileInfo file);

        /// <summary>
        /// Unzips all of the contents of a compressed archive
        /// to a single directory
        /// </summary>
        /// <param name="zipFilePath">The full name of the zip file
        /// that you want to uncompress, e.g., "C:\Temp\MyArchive.7z"</param>
        /// <param name="outputDirectory">An existing directory
        /// to which all the contents of the <paramref name="zipFilePath"/>
        /// will be extracted.</param>
        void Unzip(string zipFilePath, string outputDirectory);
    }
}
{% endhighlight %}

Then the interface for handling files and folders _en masse_.

{% highlight csharp %}
using System.IO;

namespace Woolpert.Compression
{
    /// <summary>
    /// Zips up files and folders
    /// </summary>
    public interface IZip
    {
        /// <summary>
        /// Generates zip files
        /// </summary>
        /// <param name="zipFilePath">Path of zip file to create</param>
        /// <param name="directoryToZip">The top level directory to zip up</param>
        /// <param name="recursive">Would you like to zip up subdirectories as well?</param>
        void GenerateZipFile(string zipFilePath, string directoryToZip, bool recursive);

        /// <summary>
        /// Extracts files from a zip archive
        /// </summary>
        /// <param name="zipFile">Path of the zip file to create or overwrite</param>
        /// <param name="directoryToUnzipTo">The existing directory to put unzipped files into</param>
        void UnzipZipFile(string zipFile, string directoryToUnzipTo);

        /// <summary>
        /// Compress a single file
        /// </summary>
        /// <param name="zipFilePath">The archive file to create or overwrite</param>
        /// <param name="fileToCompress">The single file to compress</param>
        void GenerateZipFile(string zipFilePath, FileInfo fileToCompress);
    }
}
{% endhighlight %}

Now we implement the `IZip` interface: the SevenZip implementation essentially calls the command line version of the 7-zip utility (`7za.exe`) with the appropriate parameters:

{% highlight csharp %}
using System;
using System.ComponentModel;
using System.IO;
using Woolpert.Common;
using Woolpert.Logging;

namespace Woolpert.Compression
{
    /// <summary>
    /// Zips up files and folders using 7-Zip, a command line tool with speed
    /// </summary>
    /// <remarks>Note that any directory paths supplied are interpreted
    /// by 7z from it's executing location. So generally it's better to avoid
    /// relative paths and just stick to fully qualified paths otherwise
    /// you may be surprised at the eventual location of your outputs.</remarks>
    public sealed class SevenZip : IZip
    {
        #region Private Fields

        private readonly string _outputFormat;
        private readonly string _sevenZipExecutablePath = ".\\7Zip\\7za.exe";

        #endregion

        #region Constructors

        /// <summary>
        /// Creates a new 7-Zip ready to zip files
        /// </summary>
        /// <remarks>By default it tries to find the 7z executable
        /// alongside the assembly location. The default output format is
        /// <see cref="SevenZipOutputFormat.SevenZip"/>.</remarks>
        public SevenZip()
            : this(".\\7za.exe")
        {
        }

        /// <summary>
        /// Creates a new compression utility with the default <see cref="SevenZipOutputFormat.SevenZip"/>
        /// output format.
        /// </summary>
        /// <param name="sevenZipExecutablePath">Path to the 7-Zip stand alone file</param>
        public SevenZip(string sevenZipExecutablePath) :
            this(sevenZipExecutablePath, SevenZipOutputFormat.SevenZip)
        {
        }

        /// <summary>
        /// Creates a new compress file
        /// </summary>
        /// <param name="sevenZipExecutablePath"></param>
        /// <param name="outputFormat"></param>
        public SevenZip(string sevenZipExecutablePath, SevenZipOutputFormat outputFormat)
        {
            Log.For(this).Debug(string.Format("Initializing {0} with {1} format", GetType().Name,
                                              Enum.GetValues(typeof(SevenZipOutputFormat)), outputFormat));
            this._sevenZipExecutablePath = sevenZipExecutablePath;
            this._outputFormat = Enumerations.Get(outputFormat);
        }

        #endregion

        #region Public Methods

        /// <summary>
        /// Generates zip files using the 7-Zip on the command line. Blindingly fast
        /// </summary>
        /// <param name="zipFilePath">Path of zip file to create</param>
        /// <param name="directoryToZip">The top level directory to zip up</param>
        /// <param name="recursive">Would you like to zip up subdirectories as well?</param>
        public void GenerateZipFile(string zipFilePath, string directoryToZip, bool recursive)
        {
            if (string.IsNullOrEmpty(zipFilePath) || string.IsNullOrEmpty(directoryToZip))
            {
                Log.For(this).Warn(
                    "Either you have left out a path to zip files to or the directory that you want to zip up. " +
                    string.Format("You specified {0} and {1} respectively. No files will be zipped.",
                                  zipFilePath ?? "",
                                  directoryToZip ?? ""
                        ));
                return;
            }

            if (Directory.Exists(directoryToZip))
            {
                Log.For(this).Info(string.Format("Using 7-Zip to zip up directory {0}.", directoryToZip));

                string externalAppArgs = string.Format("a -t{0} \"{1}\" \"{2}\\*.*\" -r", _outputFormat, zipFilePath, directoryToZip);

                if (!recursive)
                {
                    externalAppArgs = string.Format("a -t{0} \"{1}\" \"{2}\\*.*\"", _outputFormat, zipFilePath, directoryToZip);
                }

                this.RunSevenZipCommand(externalAppArgs);
            }
        }

        /// <summary>
        /// Compress a single file
        /// </summary>
        /// <param name="zipFilePath">The archive file to create or overwrite</param>
        /// <param name="fileToCompress">The single file to compress</param>
        public void GenerateZipFile(string zipFilePath, FileInfo fileToCompress)
        {
            if (fileToCompress == null) throw new ArgumentNullException("fileToCompress");

            if (string.IsNullOrEmpty(zipFilePath) || !fileToCompress.Exists)
            {
                Log.For(this).Error("Either the zip file target name is empty or " +
                                    "the file to be compressed does not exist. Please check your input values.");
                return;
            }

            DirectoryInfo zipFileLocation = new DirectoryInfo(zipFilePath);
            DirectoryInfo parent = zipFileLocation.Parent;

            if (parent != null) if (!parent.Exists) return;

            // -m is an option argument, and x=9 means ultra compression.
            var externalAppArgs = string.Format("a -t{0} \"{1}\" \"{2}\" -mx=9",
                this._outputFormat,
                zipFilePath,
                fileToCompress.FullName);
            this.RunSevenZipCommand(externalAppArgs);
        }

        /// <summary>
        /// Extracts files from a zip archive
        /// </summary>
        /// <param name="zipFile">Path of the zip file to create or overwrite</param>
        /// <param name="directoryToUnzipTo">The existing directory to put unzipped files into</param>
        /// <remarks>The files extracted from the archive will be flattened; this means that
        /// any directory structure within the archive will be lost. Also, any existing
        /// files will the same name will be overwritten without asking.</remarks>
        public void UnzipZipFile(string zipFile, string directoryToUnzipTo)
        {
            if (string.IsNullOrEmpty(zipFile) || string.IsNullOrEmpty(directoryToUnzipTo))
            {
                Log.For(this).Error("Either the zip file name is empty or " +
                                    "the output directory name is empty. Please check your input values.");
                return;
            }

            if (!File.Exists(zipFile))
            {
                Log.For(this).Info(string.Format("The zip file {0} does not exist", zipFile));
                return;
            }

            var externalAppArgs = string.Format("e \"{0}\" -o\"{1}\" -aoa -y", zipFile, directoryToUnzipTo);
            this.RunSevenZipCommand(externalAppArgs);
        }

        #endregion

        #region Private/Protected Methods

        /// <summary>
        /// Executes the SevenZip command line with the parameters
        /// created by one of the public methods.
        /// </summary>
        /// <param name="externalAppArgs"></param>
        private void RunSevenZipCommand(string externalAppArgs)
        {
            Log.For(this).Info(string.Format("Calling external process {0} with arguments {1}.",
                                             this._sevenZipExecutablePath,
                                             externalAppArgs));
            var exitCode = (SevenZipExitCodeType)ExternalApplication.RunCommandLine(
                                                      this._sevenZipExecutablePath
                                                      , externalAppArgs
                                                      , true
                                                      , true
                                                      );

            if (exitCode != SevenZipExitCodeType.Success)
            {
                string error =
                    string.Format("7-Zip Utility had an error zipping up files. The reported error was {0}.",
                                  Enum.GetName(typeof(SevenZipExitCodeType), exitCode));
                Log.For(this).Error(error);
                throw new ApplicationException(error);
            }
        }

        #endregion
    }

    public enum SevenZipExitCodeType
    {
        Success = 0,
        Warning = 1,
        FatalError = 2,
        CommandLineError = 7,
        NotEnoughMemoryError = 8,
        UserStoppedProcessingError = 255
    }

    public enum SevenZipOutputFormat
    {
        [Description("7z")]
        SevenZip,
        [Description("zip")]
        Zip,
    }
}
{% endhighlight %}

And of course the concrete implementation of the `IFileZipUtility` actually pulls it all together. The idea is that this could have a WinZip implementation as well if necessary so that there would be no non-Base Class Library dependencies. You can see this [in the Subversion repository](http://dylansknowledgebase.googlecode.com/svn/Compression/source/Woolpert.Compression/FileZipUtility.cs).

Here’s how it looks in a test case:

{% highlight csharp %}
[Test]
public void Compressing_file_in_non_working_directory_zips_the_right_files()
{
    const string zipFile = "archive.7z";
    const string fileToCompress = "sample.jpg";
    DirectoryInfo directoryInfo = new DirectoryInfo(@"..\..\..\..\");
    Console.Write(directoryInfo.FullName);
    Assert.IsTrue(directoryInfo.Exists);
    FileInfo zipTarget = new FileInfo(Path.Combine(directoryInfo.FullName, zipFile));

    IFileZipUtility zipper = new FileZipUtility(new SevenZip());
    zipper.GenerateZipFile(zipTarget.FullName, new FileInfo(Path.Combine(directoryInfo.FullName, fileToCompress)));
    var exists = zipTarget.Exists;
    Assert.IsTrue(exists);
    zipTarget.Delete();
}

/// <summary>
/// Setup that happens before any test run in this fixture
/// </summary>
[TestFixtureSetUp]
public void SetupFixture()
{
    ILogFactory logFactory = new Logging.NLog.NLogFactory();
    Log.InitializeLogFactory(logFactory);
    this._utility = new FileZipUtility(new SevenZip(_sevenZipPath));
}
{% endhighlight %}

You can grab all of the source code from [Google Code](http://code.google.com/p/dylansknowledgebase/source/browse/Compression/).