---
layout: post
title: "RegExp in JavaScript"
abstract: "How to manipulate a DOM node the easy way"
category: 
tags: [javascript]
---
I have been writing a little JS library to handle the usual repetitive tasks that are not in the core language, e.g., trim a string, map an array using a function. Of course this has all been done before but it is helping me to get a handle on the language and also on the differences between browser implementations of the DOM. One of the functions I wrote simply removes an existing CSS class from a DOM node. A total no brainer, except I’d never tried to create a RegExp that took a parameter before. A little searching and I found a [helpful answer on Stack Overflow](http://stackoverflow.com/questions/195951/change-an-elements-css-class-with-javascript). I incorporated this pretty much verbatim into my own function:

{% highlight js%}
removeClass: function(node, className) {
  var re = new RegExp('\\b' + className + '\\b', 'g');
  node.className = node.className.replace(re, '').replace(/  /g, ' ');
  return node;
},
{% endhighlight%}

I was missing the fact that the RegExp constructor syntax wants a string, not the inline RegExp definition between forward slashes. That being the case, you also need to escape all of the RegExp special backslashes with a leading backslash. In my case the parameter for a word boundary `\b` became `\\b`. So first, it’s `yadda` not `/yadda/`, and second it’s `\byadda\b` not `\byadda\b`. Took me a few minutes to get there, but now I get it!