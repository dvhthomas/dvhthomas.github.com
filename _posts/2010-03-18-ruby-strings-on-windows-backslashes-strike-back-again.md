---
layout: post
title: "Ruby strings on Windows. Backslashes strike back again"
abstract: "There are all kinds of discussions about how to correctly use single or double quoted strings in Ruby, especially where character escaping is concerned. I was faced with just such an issue today and thought I'd share my experience."
category: 
tags: [ruby, windows]
---
There are all kinds of [discussions](http://stackoverflow.com/questions/648156/backslashes-in-single-quoted-strings-vs-double-quoted-strings-in-ruby) about how to correctly use single or double quoted strings in Ruby, especially where character escaping is concerned. I was faced with just such an issue today and thought I'd share my experience.

Basically I'm building a rake script to automate my .NET project setup. Part of that setup involves doing some search and replace is SQL scripts so that a developer can store some settings in a config file and have that populate variables in files. For example:

* YAML file `config.yml` contains a setting called `production -> db -> backup_location`. The text in the file is `\\\\some\\unc\\path\\name`. You see how the backslashes in the Windows path are doubled up? That's to satisfy Ruby and it is in double quotes.
* The rake script uses this value as a parameter to a method that I wrote that is heavily influenced (copied with simplification!) by the [albacore project](https://github.com/derickbailey/Albacore), which is a set of rake tasks geared towards .NET projects. The important lines of the script are these:

{% highlight ruby %}
replacements.each do |search,replace|
    search_term = "%#{search}%"
    template_data.gsub!search_term, replace
end
{% endhighlight %}

* My SQL script has this in it that should have various paths inserted:

    {% highlight sql %}
    FROM  DISK = N'%backup_file%' WITH  FILE = 1
     , MOVE N'Cityworks_Production' TO N'%db_dir%\Cityworks_WCS.mdf'
     , MOVE N'Cityworks_Production_log' TO N'%db_dir%\Cityworks_WCS_1.ldf'
     , MOVE N'sysft_CityworksFtCat' TO N'%db_dir%\Cityworks_WCS_2.CityworksFtCat'
     , move N'ftrow_CityworksFtCat' to N'%db_dir%\CityworksFtCat.ndf'
    ,  NOUNLOAD,  STATS = 10
    GO
    {% endhighlight %}

Unfortunately when I run the script using a UNC path rather than a typical `C:/something/or/other` path I could never get two backslashes to appear at the start of the path. I tried (literally!) every combination I could think of: doubling up, adding an extra backslash, single quotes, double quotes, you name it. Along the way I wrote a little one liner that converts a string from Ruby path to a Windows path (`winpath = ruby_path.gsub('/','\\')`) but still no joy. Then I searched some more online and finally found an answer: it wasn't my various `File.join` or `File.expand_path` calls that were the issue: it was the gsub call itself that was the problem.

In fact the question was [answered by Matz himself](http://redmine.ruby-lang.org/issues/show/1443) (inventor of the Ruby language). While my string with four backslashes actually did give me the right answer of two escaped backslashes, gsub also assigns special meaning to backslashes. So get this - you need to **quadruple** any backslash in a string if you are going to gsub it. Crazy but true. Here's what my fixed up code looks like now:

{% highlight ruby %}
replacements.each do |search,replace|
    search_term = "%#{search}%"
    template_data.gsub! (search_term) { replace } unless replace.nil?
end
{% endhighlight %}

The trick is to use a block rather than tacking on the replace as a parameter. In this way gsub offloads the whole string interpretation to the block rather than doing its funky thing with interpreting the backslashes inline. Boy, am I glad I got that figured out.