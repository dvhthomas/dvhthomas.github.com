---
layout: post
title: "Blogging like you'd write code with Jekyll"
abstract: "This is a recursive post, in which I describe how I wrote this post using my new blogging setup."
category: 
tags: [general]
---
## A history of blogging frustration

I've had a personal blog for a long time. Photos of kids, and before that, stories of heroic 100+ mile bike rides across continental divides and Tuscan fields. And for that I was happy using the blogging tools *du jour*. But when I started throwing my technical musings online back in 2009 I was always disatisfied with the process of blogging about coding and technology in general. Here I was, living life in a text editor or IDE, running commands on remote systems via SSH, and generally bending systems to my will for money. And yet I couldn't ever get my code to paste properly into [Blogger](http://dylandoesdigits.blogspot.com). And stuff never seemed to line up right in WordPress (defunct now). And although [Posterous](http://dylandoesdigits.posterous.com) let me write in Markdown and submit via email, I just lacked the absolute power that propellor-headed geeks crave so desperately. You know, to have it *just so*.

Frustrated by that, and by having my previous efforts littering the Internet, I [Googled](https://www.google.com/search?q=blogging+platform+for+developers) "blogging platforms for developers". A little digging and I reached what I believe to be geek-blogging-Nirvana: [Jekyll](https://github.com/mojombo/jekyll).

## Blogging for developers...on Jekyll

I'm not going to repeat the [myriad](http://jekyllbootstrap.com/) [ways](http://orgmode.org/worg/org-tutorials/org-jekyll.html) [that](http://www.ksornberger.com/blog/blogging-with-jekyll-and-github/) [others](http://brianscaturro.com/2012/06/12/blog-with-jekyll-and-github.html) have both explained and sung the praises of Jekyll, except to say that it is a Ruby library that takes a bunch of Markdown files in a simple directory structure, reads a little configuration information from a YAML file, then spits out static HTML that can be FTP'd, SSH'd, rsync'd, or otherwise deployed to your web server of choice.

OK, I'll add one other thing: if you choose to store your content files for your site on Github, the nice people at Github will automatically run Jekyll for you, and host the resulting site for you. All you have to do is (a) use Git to manage your code, and (b) name your Github-hosted repository as `your-user-name.github.com`. Something like [`dvhthomas.github.com`](http://www.github.com/dvhthomas/dvhthomas.github.com) in fact. How nice!

So the initial setup is pretty easy then.

* Install Ruby.
* Install the Jekyll gem: `gem install jekyll`
* Create a Git repo on Github with the naming convention `your-github-username.github.com`
* Navigate to the parent directory where you want to keep your blog to work on locally. I typically do this in my home directory: `cd` or `cd ~/` takes care of that.
* Get the git repo on you local machine: `git clone https://your-github-username.github.com .`
* Create a file called `_config.yml`, a file called `index.html`, a directory called `_layouts`, and a directory called `_posts`.
* Visit the source for my blog and copy whatever you want out of there to stick in the two files and the `_layouts` directory.
* A just because we're lazy programmers, create a file called `Rakefile` and stick the contents of [my `Rakefile`](https://github.com/dvhthomas/dvhthomas.github.com/blob/master/Rakefile) in there. Of course I 'borrowed' this from other sources and promptly forget from whom exactly...kind of bad manners.
* Make sure it's working: `jekyll` at the directory root level, then open `http://localhost:4000` in your browser to render the contents (hopefully!) of the index.html file.
* `touch .gitignore`
* `vim .gitignore` and add `_site/` to make sure the generated content is always ignored and always fresh.
* `git add .`
* `git commit -m "My awesome blog is alive!"`
* `git push origin` to send it to Github
* Wait 10 seconds
* Visit `http://your-github-username.github.com` and see your blog online for free.

If that doesn't work, read the official docs on the [Jekyll](https://github.com/mojombo/jekyll) wiki: they're really pretty simple and easy to follow.

## Writing this post

With that all out of the way, here is the part that I absolutely love. Again, remember my frustrations with the usual consumer blogging platforms? Well read this and weep tears of geeky joy:

* Have an idea for an amazing blog post. Open a terminal.
* `cd ~/dvhthomas.github.com`
* `rake post title="Blogging like you'd write code with Jekyll" date="2012-09-18"`
* `vim _posts/2012-09-19-blogging-like-youd-write-code-with-jekyll.md`
* Use your vim skills to write some markdown
* `wq` in vim to save your new post
* `git add .`
* `git commit -m "yet another amazing blog post about the process of blogging"`
* `git push origin`
* Go tell all your buddies that you just posted something online.

## Extras

So it really is that easy. I've been moving my old posts over from other services. There are automated import tasks as part of Jekyll, but I don't have a ton of backlog, and I wrote some crap posts too, so I've been handpicking what I want to migrate and doing a bit of cleanup as I go.

That said, I do also use `rake preview` to fire up the Jekyll server with some options to preview my work locally before actually committing. A couple of times I've been scratching my head when this does not render correctly; I learned that running `jekyll --no-auto` can help in these cases, because every time it's been a error in my markdown syntax, and Jekyll tells you exactly what you've done wrong.

I have also followed the Jekyll author's guidelines and put a `CNAME` file at the root level containing one line: the domain name I want to serve my blog from. Obviously I also bought the domain and set up the DNS `A`-level entry. With that done, any attempt to load [http://dvhthomas.github.com](http://dvhthomas.github.com) is automatically redirected to the real domain.

## Summary

Jekyll is really a dream come true for me. I can blog inside of my favorite text editor. I have the comfort of version control. I have absolutely every pixel of the rendered content at my command (even when I choose odd fonts and weird colors, and blatantly ignore anyone using an older browser!).

There are several meta-Jekyll projects that attempt to make paging, tagging, categories, Atom feeds, commenting systems, and all that jazz much easier. But until I'm comfortable with the basic package, I'll hold off on bells and whistles. And for now, that's just fine by me.