---
layout: post
title: "Writing documentation using reStructured Text"
abstract: "I’ve been working on some documentation for a web application this week. I’m not a big proponent of doing this in Microsoft Word because the docs need to be in both HTML and PDF formats for the client. Plus Word tends to get pretty squirrely when it comes to precise formatting and doing what I want vs. what it thinks I want."
category: 
tags: [python, tools]
---
## The problem

Where does MS Word fall down on documentation? Think about the need to do code listings: in Word I can define a style that gives it the right font, the right indentation, and all the other stuff to make a code listing just like the examples I use in this blog. In HTML I do something similar but use CSS and the `<pre>` tag, with similar results. Of course the issue is that Word all too frequently mixes up the format of the surrounding paragraph and elements with my style. Just remember for a second how many times you’ve had to mess about with the indentation of the _second_ paragraph of text in a bullet? Too many.

Of course, I also don’t really want to write a boat load of documentation in HTML – I’ve done it quite recently and it’s not fun, even with a [great HTML](http://www.intype.info) editor to lean on. What to do? Well, I looked on the internet tubes for possible answers to my requirements:

* I want to have output in HTML and PDF
* It needs to support version control in a friendly way, so text-based files are a bonus and binary files are a no-no
* Non-technical (non-developer) people should be able to write the help files without needing more than a little bit of training and a text editor.
* It needs to be free - [Adobe's RoboHelp](http://www.adobe.com/products/robohelp/) does this stuff but it costs $999. Obviously not going to work for me no matter how cool it is.

I quickly came across one documentation tool that does what I need: the [Sphinx Python](http://sphinx.pocoo.org/index.html) documentation generator. “Huh?” I hear you say, “Python document generator...how the heck does that fit your list of requirements?” Well, the interesting thing about Sphinx is that it uses a very simple text format called [reStructured Text](http://docutils.sourceforge.net/rst.html) (reST) that lets you write simple markup that mostly looks like simple text without a ton of angle brackets (like `<em>hello</em>`). Sphinx then runs a process using the Python [docutils](http://docutils.sourceforge.net/index.html) utilities that turns the reST in to other formats like HTML and LaTeX. Yes, the whole purpose of Sphinx is to convert reST into exactly the formats I need! From the reST page.

> Docutils is an open-source text processing system for processing plaintext documentation into useful formats, such as HTML or LaTeX. It includes reStructuredText, the easy to read, easy to use, what-you-see-is-what-you-get plaintext markup language.

So it turns out that docutils and Sphinx come from a Python heritage and are implemented using Python, but they are generic tools that can be used to generate any kind of documentation you want using reST. Which sounds like exactly what I’m looking for.

## reStructured Text

Rather than rehash all of the bells and whistles in reST I thought I’d just post an example:

    ============
    Introduction
    ============

    The :abbr:`EMMA (Election Map Maintenance Application)` application enables election officials at multiple levels of government stay on top of changes in electoral boundaries. Specifically it is designed to support changes to precinct boundaries across the entire state of Ohio. Election officials at the county level can propose modifications to precincts that adhere to U.S. Census and |ohsos| rules, and then |ohsos| staff can take those modifications through an electronic approval process. The benefit of EMMA is the easy management of what can quickly become complex changes, and a good historical record of all proposed changes whether or not they eventually are accepted.

    .. warning:: This is a warning.

    .. note:: This is a note.

    .. sidebar:: A sidebar

        with some content

    Before diving in to the detailed workflow guides or specific tool descriptions, take a look at the glossary to make sure you understand the various terms that are used throughout this documentation. While many of them, such as *precinct*, may be familiar to you, others such as :term:`VTD` and :term:`TIGER` may not.


You can see that a couple of simple conventions like indentation and blank lines are used to give the document its structure. Also the main heading just has some lines around it to make it stand out. What else?

* **Directives**---see the `.. warning::` and the `.. sidebar::`? Those are simple tags that represent semantic parts of the document. I don't even really need to describe what they are.
* **Glossary and terms**---See the `:term:VTD`? This is a reference to a definition. Elsewhere in my reST document(s) I have a `.. glossary::` directive which has the description of what `VTD` actually is. reST is smart enough to link the two.

But the really great part is the reST is semantic –- it describes the content and structure of my document in a way that HTML and Word should but often don’t. Way too much time worrying about the colors, the indentations, and all that other guff.

## Generating Output

Yeah, yeah, so semantic content and structure are great concepts, but how does that help me achieve my goal. Well Sphinx has utilities to take the reST and output in a variety of formats. Actually I think the only two widely used formats are HTML and LaTeX. If you haven’t come across LaTeX before then you owe it to yourself to do [a little research](http://www.latex-project.org/). The short version is that it is also a text-based way to describe typeset quality documents (think magazines, journals, documentation) plus tools to take those LaTeX documents and convert them to formats like PDF. Aha! Now you’re getting the point here. In a nutshell:

1. Write reST documents in simple markup
1. Run reST files through Sphinx
1. Sphinx produces HTML or LaTeX
1. For LaTeX, turn the TEX file in to PDF

The “Run reST files through Sphinx” part is straightforward. In fact Sphinx has a handy command to run that even creates a little batch file to help you do it:

    make html
    make latex

As long as Python is installed with the Sphinx and docutils bits, that is all you need to do for HTML. For LaTeX &rarr; PDF conversion you also need to have a LaTeX processor. I am using a distribution called [MiKTeX](http://miktex.org/) that runs very well on Windows and gives me another simple one liner:

    pdflatext SphinxOutput.tex

The result is a very professional looking version of the documentation in PDF. The great part is that the glossary of terms is still all hyperlinked within the document, as are the table of contents and index. Sweet.

![HTML documentation output](images/rst-html.png)

The PDF output for the glossary. In the HTML this is a Definition List.

![PDF documentation output](/images/rst-pdf.png)

Here’s the proof that references and content structure turns in to something useful in the PDF

![PDF documentation TOC](/images/rst-pdf-toc.png)

## A Bit More Detail on Requirements

Because it took a little preparation to get up and running, I’ll share a quick README that I wrote myself so that I can remember how this works. Here you go:


### Setup

Building this documentation requires the following to be installed
on your system:

* Python 2.5.4
    * download from [http://www.python.org/download/](http://www.python.org/download/)
    * Add the `C:\Python25` directory to your Windows PATH
* EasyInstall
    * run `setuptools-0.6c9.win32-py2.5.exe` found in the same directory as this readme file
    * Add `C:\Python25\Scripts` to your Windows PATH
* Sphinx documentation tools
    * Open a command prompt and go to `Project\docs\manual`
    * Type `easy_install Sphinx` from a command prompt, making sure that you have an active Internet connection to download dependencies
* MikTex - LaTeX/PDF document generator
    * Download the Basic MiKTeX 2.7 installer from [http://miktex.org/2.7/setup](http://miktex.org/2.7/setup)

### Building the documentation:

* Open a command prompt and cd to `Project\doc\manual`
* HTML version
    * type `make html`
    * look in `manual\build\html`
* PDF version
    * type `make latex`
    * `cd build\latex`
    * type `pdflatex mydocs.tex` - NOTE: If you are asked to download additional components during the first run then say YES! MiKTeX needs some extra bits to support the features required by the Sphinx PDF documentation style.
    * look for the mydocs.pdf
    * If the Table of Context is not showing up in the PDF simply rerun the pdflatex command. That usually fixes it.

If you need to clean up and start from scratch:

* type `make clean`

## Gotchas

Of course the world is not perfect. Configuring the documentation build happens in a python file called `conf.py`. I have yet to see much of how the LaTeX output can be configured beyond a handful of modifications. This is turn means that the PDF layout is largely beyond my control unless I want to get my hands dirty with the tex file itself. Which I don’t! Also, to change the layout of the HTML beyond the simple cosmetics would mean getting in to the Sphinx templating approach (which is similar to Django templates but not worth it for my current project).
