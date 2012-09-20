---
layout: post
title: "Markdown to HTML the easy way"
abstract: "Hooking up Pandoc to Sublime Text 2 build systems."
category: 
tags: [tools]
---
I've been using [Sublime Text](http://www.sublimetext.com/2) as my main text editor for a couple of weeks. I still use Vim a lot, but I like the cross platform GUI that ST2 provides. I've also been using [Markdown](http://daringfireball.net/projects/markdown/) to write a lot of my notes and documents. ST2 lets you define custom build providers so I whipped up a simple one that uses [Pandoc](http://johnmacfarlane.net/pandoc/) to transform the Markdown text into HTML by pressing F7. Kind of nice.

## Build Provider

Build providers are simple JSON-style files in Sublime Text 2. Here's what mine looks like:

{%highlight js%}
{
    "cmd": ["pandoc.exe", "--to=html", "--output=$file.html", "$file"],
    "selector": "source.md"
}
{%endhighlight%}

## Using the build provider

* Install [Pandoc](http://johnmacfarlane.net/pandoc/) on your system. I'm assuming that you have the `pandoc.exe` on your PATH on Windows.
* In Sublime Text 2 choose *Tools &rarr; Build System &rarr; New Build System* and paste in the definition for the Pandoc-based system (see above).
* Save the Markdown.sublime-build file to your ST2 Packages folder. On my Windows 7 system this is:

  `C:\Users\USERNAME\AppData\Roaming\Sublime Text 2\Packages\Markdown`

* Open a Markdown file (with \*.md file extension) and hit F7.