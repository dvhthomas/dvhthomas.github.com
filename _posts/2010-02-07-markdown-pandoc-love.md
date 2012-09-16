---
layout: post
title: "Markdown, Pandoc, Love"
abstract: "I realized that writing software requirement specs in Word is a massive pain in the behind, and at the same time thought that have simple text files under version control is the way to go. You know, like you might with code?"
category: 
tags: [tools, practices]
---
I'm in the middle of writing a lengthy software requirements spec this week. It's actually been fun to go through the process again on a fresh project with a clean slate. The requirements gathering meetings were great: business leader, sales people, and developers all in one room and surprisingly united in their goals. I used the usual tools of the trade---like FreeMind and Unable (a clone of a great little note taking application called Notable)---and was able to get a lot of the requirements and user story details knocked out on site.

Then I was sitting back at the office wondering how to keep all of my SRS edits in version control and hit upon the idea of using HTML rather than Word. No good reason other than wanting to keep my change sets small. I'm very comfortable with HTML and can whip out a mean CSS/HTML combo in no time flat. The beauty of it all, of course, is that I can just write what I want without fussing over headers, page numbers, indenting bullets the right amount, and all that guff. I like a good looking document as much as the next guy but frankly I just needed to focus on getting the requirements done, not worrying about the font color of my headings.

## Enter Markdown

Being no stranger to sites like Stack Overflow I know that people can write pretty complex stuff using HTML. But also that it's a total drag when again, all I really need is the write text with some minimal markup. So if I want to highlight something I might type `this is *important* stuff` and I might want to create a bulleted list like so:

    * item one
    * item two
    * and something else

This is pretty much how I write notes anyway, and it turns out it's very, very close to how a simple 'HTML lite' syntax called [Markdown](http://daringfireball.net/projects/markdown/) does things. Essentially is a dead simple format that can be transformed into HTML by any number of tools. So I did a little test. I started to write my SRS in Markdown format using a text editor rather than Word, all the while committing my changes to Subversion. It was actually pretty nice and I did indeed focus on writing instead of formatting. But then what? I've got a text file in some goofy format that only a programmer could love (ahem! guilty as charged!!!). I needed to deliver something usable to my client like a web page. Here's what a typical section looks like:

    #### Trademarks
    All brand names and product names are trademarks or registered trademarks of their respective companies

    Software Requirements Purpose and Process
    -----------------------------------------

    A Software Requirement Specification--hereafter called an SRS--is an initial attempt to describe the functionality of a custom software product or custom system. It can be likened to the blueprint for building a new house (or perhaps remodeling an existing house). Just as an architect guides a homeowner through their needs for the new house, so Woolpert technical staff guide clients though the requirements process. This implies two very important points that the client project management team and stakeholders should remember through the software requirements process:

    * *Continuous client involvement* is crucial to success. A homeowner generally does not sign off on architectural plans early on and then just hope that the architect understood perfectly your meaning. Woolpert technical staff are highly skilled, but they cannot possibly know all the needs or business processes of the clients as well as they do.
    * *Requirements are a moving target*, not a set of mandates that are set in stone. To be sure, some requirements are so central to the project that they are unlikely to change. However, changing requirements...

Ignore the actual content for a second, and focus on the simple rules that Markdown uses. If I want a heading I underline the text. If I want bullets I put an asterisk as the first character and leave some white space around the 'list'. If I want a highlight (`<em>` in HTML) I put a couple of asterisks around the text. Simple. To be sure there are complicated parts but at that point I just drop in the HTML, e.g., a div is just a div.

## Enter Pandoc

In the 'Holy Cow! How did he do that?' category I found a wonderful little program called [Pandoc](http://johnmacfarlane.net/pandoc/) written in Haskell by an associate professor of philosophy from the University of California at Berkeley (!!!!???!?!). Not exactly a normal, run of the mill combination there, but Pandoc is a beautiful little program. It essentially does one thing, and does it exceptionally well: it takes one or more Markdown text files and spits out HTML or PDF (or DocBook and a few other formats). So in order to turn my `srs.markdown` text file and various screenshots in to an HTML page complete this those hyperlink-thingies, I just double-click the batch file I wrote and in less than a second I've got an excellent SRS document in HTML format that my client can open on any computer, share with anyone on the team, and click around in. From my script you can see that I'm including some CSS stylesheets, I'm asking for HTML out, and I've overridden a default HTML template because I needed to add some autogenerated stuff to the HTML HEAD section. Oh, and I also wanted it to generate a hyperlink table of contents for me based upon my H tags. Short and sweet.

    pandoc -o srs.html
      -c "assets/css/blueprint/print.css"
      -c "assets/css/blueprint/screen.css"
      -c "assets/css/woolpert.css"
      -w html srs.markdown
      --template html.template
      --toc

I wish I could show you some of the output but I'm under a non-disclosure agreement. But I promise, it's really...neat. Not to mention, when I've made changes, my client simply gets the latest from my employer's public svn repository, double-clicks the same batch file, and gets the very latest docs.

Smile.