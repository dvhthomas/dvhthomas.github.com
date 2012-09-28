---
layout: post
title: "Rake for .NET Projects"
abstract: "I'm working on a .NET project right now that involves 3 (or is it 4?) developers on two different teams in 3 different locations. The usual dance is being played with different dev settings for each person, like 'use this GIS server for these layers' and 'use this Oracle TNS for that database, but SQL Server for the other one'. Not to mention the need to update a bunch of JSON configuration files depending on who is building the project. So I thought I'd take a look at the Rake build system that is written in Ruby."
category: 
tags: [dotnet, ruby]
---
Actually, because I know there would be a revolution if the developers had to install Ruby just to update some files, I went with IronRuby instead. This is the version of Ruby that is being built to run on the .NET Framework. The beauty of it (apart from a slow startup time) is the speed of execution, and an xcopy deployment for any machine that already has .NET installed. Which is every Windows PC out there.

## Setup

So how does this work? Well, I first [downloaded IronRuby](http://www.ironruby.net/Download) (get the ZIP file not the MSI installer) and unzipped it into the `trunk\tools` directory of my project. I followed the excellent advice of [Evan Closson](http://www.evanclosson.com/devlog/ironrakeironrubyakagoodbyenant) and created a little batch file that sets up my Ruby environment such that commands like `iirb` and `irake` actually cause the expected thing to happen. Ignore the stuff about 7-zip for now. I added that later and will explain.

    @ECHO OFF
    cd tools
    if not exist ironruby\nul 7zip\7za.exe x -y ironruby.7z
    cd ..
    set PATH=%PATH%;C:\Windows\Microsoft.NET\Framework\v3.5;%CD%\tools\ironruby\bin
    set GEM_PATH=%CD%\tools\ironruby\lib\ruby\gems\1.8
    set GEM_HOME=%CD%\tools\ironruby\lib\ruby\gems\1.8

After getting what amounts to a zero-installer, xcopy deployment of the entire Ruby language running in 3 minutes, we then need to get Rake. Ruby has a wonderful package management system called Gems. By typing `igem install rake` (don't miss the "i" there...that's IronRuby you're running!), Rake is downloaded and installed in to my `trunk\tools\ironruby\lib\ruby\gems\1.8\gems\rake-0.8.7` directory. I had unzipped my IronRuby download in to the ironruby directory, and the rest was done for me. Test thinks out by typing `irake`. It'll barf at you because it's got nothing to do, but at least you now have the environment all squared away.

Next I compressed my IronRuby directory, complete with Rake, into a [7-zip](http://7-zip.org/) file called `ironruby.7z` and then deleted my ironruby directory. The resulting file is about 2MB is size and suitable to put in subversion. Large files need not apply! I also have the 7-zip executable in my `trunk\tools` directory so that my init.bat file can uncompress it on demand when a new developer downloads the code for the first time. (note: if you're not using 7-zip yet then drop everything, go and install it, then carry on reading).

That leaves us with this directory structure (omitted the irrelevant parts). You can see how the JSON resources that I want to update per user are in the resource directory of my websites, and that the ConnectionStrings.config.template is at the top of the source directory. I link to this file from every project in the solution that needs access to databases so that the Web.config or App.config simply has in it and updating the one file automatically squares away any other application.

![Rake directory structure](/images/rake-ironruby.png)

## Rake

Big deal. I have Ruby and rake. So what? Again following Evan's advice I created a few files. Rake expects a file called `rakefile.rb` or just plain `rakefile` to live in the directory from which it is executed. In my case this means in my trunk directory. But I don't want to clutter things up so I also created a `trunk\source\tasks` directory to hold the two build scripts that really do the work: `build.rb` and `rakefile.rb`. First comes the rakefile:

{%highlight ruby%}
$LOAD_PATH << './source/Tasks/'

# Command configuration items - if this changes it should change
# for all users
APP_SETTINGS = YAML.load_file('common.yml')

# Create user settings if not present
setting_template = "config.yml.template"
if !File.exist?(setting_template.ext(''))
    p setting_template.ext('')
    cp setting_template, setting_template.ext('')
end

# Load up the desired deployment target or default to development
# This is set at the irake command line using DEPLOY=production
DEPLOYMENT= (ENV['DEPLOY'] or 'development')
USER_SETTINGS = YAML.load_file('config.yml')[DEPLOYMENT]
require 'build.rb'
{%endhighlight%}

As you might be able to tell, this is reading in some settings in the YAML (YAML ain't another markup language, I think) format. The yaml format is essentially the de facto Ruby serialization format, so by using yaml I get free conversion from a text file to a ruby object simply by calling YAML.load_file. Exactly the same as if I were to read a JSON file in to JavaScript - implicit understanding of the content. Here's a yaml file:

{%highlight yaml%}
development:
    database:
        city: 'Data Source=DWHS;User ID=yahooozi;Password=look-the-other-way;'
        eventservices: you-get-the-idea
        security: this-is-where-setting-values-go
    servers:
        gisserver: someservername
        webserver: yepanothername
production:
    database:
        city: zapperoo 
        eventservices: some-other-string 
        security: some-other-string 
    servers:
        gisserver: servername 
        webserver: servername 
{%endhighlight%}

The structure is very simple and can be created in a text editor. Assuming the user starts the build process with `irake DEPLOY=production` then the production values are used. If they enter `irake DEPLOY=development` or just `irake` without a parameter then the dev settings are used. Amazing! Astounding! Just so much better than msbuild that I've struggled with.

> I'm not just spouting off here. I've written a few fairly ambitious and complex build scripts using msbuild. It works, it's powerful, and it's a bugger to use and learn. This rake business, on the other hand, is the first time I've ever touched Ruby and I'm not looking back. So there.

OK, we've got our configs. Now what do we do with them? My use case is simple: I need to update a boat load of JSON files and a single web.config file with some fresh server names, connection strings, and the like. Here's what build.rb looks like:

{%highlight ruby%}
require 'rexml/document'

@json_files
@xml_files

# This set of tasks assumes that some settings have been already
# been loaded in to globals called APP_SETTINGS and USER_SETTINGS.
# Pretty much everything will fail until that has been done, usually
# in a calling rakefile
desc "Default build task"
task :default => ['user_config','db:update_connection_strings'] do
end

task :clean => ['creator:clean']
task :clobber => ['creator:clean']

desc 'Update configuration files specific to a user'
task :user_config => ['creator:create_user_files'] do
    puts "Updating JSON configuration files"
    search_terms = USER_SETTINGS['servers']
    
    APP_SETTINGS['json_templates'].each do |name|
        target = name.ext('') # strip file extension
        cp name, target, :verbose => false
        text = File.read(target)
        
        search_terms.each do |s,r|
            text = text.gsub(s.upcase,r)
        end

        f = File.open(target, 'w')
        f.write(text)
    end
end

def load_file_lists
    @json_files = Array.new
    @json_files.concat(APP_SETTINGS['json_templates'])
    @xml_files = Array.new
    @xml_files.concat(APP_SETTINGS['xml_templates'])
end

namespace :creator do


    # This is kind of wacky - Rake can create a task-per-file. In this
    # case we first build a list of all of the files we want and THEN
    # build a task that collects all of the file copy activities
    # together. Sort of backwards to my way of thinking but it works.
    
    # What's really cool is that Rake keeps track of which files it's
    # already created, so you can call this multiple times and it'll
    # only copy files that don't yet exist. Of course, if you've changed
    # a file then you need to run the creator:clean task first to get
    # back to square one
    load_file_lists()

    FileList[@json_files, @xml_files].each do | source |
        target = source.ext('')
        file target => source do
            cp source, target, :verbose => false
        end
        desc 'Creates all of the user specific files from templates'
        task :create_user_files  => target

    end
    
    desc 'Remove user specific config files'
    task :clean do
        load_file_lists()
        delete_these = @json_files.map {|x| x.ext('') }
        delete_these.concat(@xml_files.map {|x| x.ext('') })
        puts "Deleting existing user configurations"
        rm_f FileList[delete_these], :verbose => false
    end

end

# Database specific stuff
namespace :db do

    desc 'Updates *.config files with valid database connection strings'
    task :update_connection_strings => ['creator:create_user_files'] do
        puts "Updating connection strings"
        @xml_files.each do | xml |
            doc = REXML::Document::new(File.open(xml.ext('')))
            doc.elements.each('connectionStrings/add') do | element |
                element.attributes["connectionString"] = USER_SETTINGS['database'][element.attributes['name'].to_s.downcase]
            end
            
            f = File.open(xml.ext(''), 'w')
            f.write(doc)
        
        end
    end

end
{%endhighlight%}

Rake is geared towards completing tasks. It is a build system, after all. First thing to notice is the default task. Just like every other system out there like make, ant, nant, msbuild, bake, psake, etc., it can have dependencies. So when I run `irake` it looks for a rakefile, then looks for a task called default. Finding that it then runs `update_user_configs` which in turn runs `create_user_files` which... It's obviously turtles all the way down from there - just keep following the dependency trail.

You can, dear programmer, probably figure out the rest of what is happening because Ruby is pretty expressive and clear (mostly!). For example, notice the 'require rexml/document'. REXML is the core Ruby XML processing library and I use that in the update_connection_strings task on line 84. If you've written any .NET applications you can tell that I'm opening up app.config or web.config files in the solution and doing a search and replace for a series of database connection strings. Look back at the YAML to refresh your memory. It's simple and I can literally cut'n'paste this task in to any one of my other .NET projects that need to have developer-specific connection strings in them.

## Summary

I'm getting tired of typing here so I'll summarize briefly. IronRuby is a version of Ruby that is written in C# and runs on the CLR. It can use standard Ruby plugins or Gems such as Rake. Rake is a build system that uses regular Ruby code and files instead of XML to make writing build scripts less painful. I'm sure I've missed some key details in describing my setup. Let me know if you're confused by any steps and I'll do my best to update this post.