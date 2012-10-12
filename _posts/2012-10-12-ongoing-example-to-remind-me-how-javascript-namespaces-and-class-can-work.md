---
layout: post
title: "Ongoing example to remind me how JavaScript namespaces and class can work"
abstract: "In spite of my best efforts I always, always forget how to do the simplest data hiding and code organizing in JavaScript. I'm getting better, but here is an ongoing, ever-updating reminder to myself of some of the basics."
category: 
tags: [javascript]
---
Of course, this is wrapped a web page so that you can pop open your `Command-Option-J` magic in Chrome to play with the code. For example, try constructing a `Goodbye` like so: `var g = new ns.stuff.Goodbye({ one: 'fare thee', two: 'well!'});` then do `g.toString()`.

{%highlight html%}
<html>
<head>
    <script type="text/javascript">
        var ns = ns || {};

        ns.Hello = function(data) {
          this.a = data.one;
          this.b = data.two;
        };

        ns.Hello.prototype.to_link = function() {
          console.log(this.a + ", " + this.b);
        };
        
        ns.Hello.staticMethodDate = function () {
            console.log(new Date());
        }

        ns.testing = {zip: 'hi', zap: 'there'};

        ns.stuff = function () {
            return {
                Goodbye: function(data) {
                    this.j = data.one;
                    this.k = data.two;
                }
            };
        }();

        ns.stuff.Goodbye.prototype.toString = function() {
            console.log(this.j + ", " + this.k);
        };
    </script>
</head>
<body>
    <h1>How the heck does namespacing and class instantiation work in JS?</h1>
    <p>Command-Option-J to work with the code.</p>
</body>
</html>
{%endhighlight%}