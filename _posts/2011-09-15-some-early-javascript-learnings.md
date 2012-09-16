---
layout: post
title: "Some early JavaScript learnings"
abstract: "I’ve been spending some time trying to learn how to put together a JavaScript library that is not just a throwaway script. My impetus is to avoid the usual steaming pile of globals and functions that I end up with in any web site that has more than a trivial amount to client side code."
category: 
tags: [javascript]
---
Having committed to do 'the right thing', I bought a copy of [JavaScript: The Good Parts](http://www.amazon.com/dp/0596517742/). I devoured the entire thing in one sitting and if much of it was lost on the first pass, I remembered enough to look up critical sections (closures, anyone?). It was great to learn about functional style object hierarchies, prototypal inheritance in a way that made sense, and mostly what to avoid.

I took a stab at some basic functions to see how I can tinker with them in a page and [put the results on Github](https://github.com/dvhthomas/noskijs). Just load up the test.html file in Chrome or Firefox and crack open the console (native or Firebug). The autocomplete comes in handy to explore the ‘classes’ and to see what data is hidden in closures and what is not. A really good learning experience for me. And just is case you’re wondering, 'noski' is Russian for 'socks'.

Here's an example showing a closure (`deshashify`) that is still available privately to the set of functions returned by calling `noski.util`:

{%highlight js%}
/**
 * Depends on noski.core
 */
var noski;

if (!noski) noski = {};
else if (typeof noski != 'object') {
    throw new Error('noski already exists and is not an object');
}

if (!noski.util) noski.util = {};
else if (typeof noski.util != 'object') {
    throw new Error('noski.util already exists and is not an object');
}

noski.util = function() {

    var cache = {};
    var count = [];

    /**
     * Removes the leading '#' from a string, typically a hex color.
     * @param {string} hexColor Color string with or without leading '#'.
     * @return {string} String minus a single leading '#' character.
     */
    function dehashify(hexColor) {
        var hash = hexColor.charAt(0) === '#';
        return hash ? hexColor.substring(1, 7) : hexColor;
    }

    return {
        /**
         * Turns a hex color string into an object with rgb properties
         * @param {color} Hex color either with or without leading '#', e.g., "#43f3c9".
         * @return {Object} Color object with three integer properties r, g, and b.
         */
        hex2rgb: function(color) {
            if (arguments.length !== 1) {
                throw new Error('hexColor requires a single argument in the form ' +
                        '"#ddcc33" or "ddcc33"');
            }

            if (typeof color !== 'string') {
                throw new Error(color + ' is not a hex number in the ' +
                        'form #43ffa3 ("#" is optional).');
            }

            var color_in = dehashify(color).toLowerCase();

            if (color_in in cache) {
                return cache[color];
            }

            var value = parseInt(color_in, 16);

            var rgb = {
                    r: (value & 0xff0000) >> 16,
                    g: (value & 0xff00) >> 8,
                    b: value & 0xff
                };

            cache[color_in] = rgb;
            count.push(color_in);

            if (count.length > 1000) {
                delete cache[count.shift()];
            }

            return rgb;
        },

        /**
         * Accessing a specific named cookie.
         * Leans heavily on this article:
         * http://leaverou.me/2009/12/reading-cookies-the-regular-expression-way/
         * @param {string} cookie_name Name of the cookie you want to load.
         * @this {Cookie}
         */
        Cookie: function(cookie_name) {
            // Escape regexp special characters
            this.$name = cookie_name.replace(/([.*+?^=!:${}()|[\]\/\\])/g, '\\$1');
            var allcookies = document.cookie;

            if (allcookies === '') return;

            var cookies = allcookies.split(';');
            var cookie = null;
            var r = new RegExp('(?:^|;)\\s?' + this.$name + '=(.*?)(?:;|$)', 'i');
            cookie = document.cookie.match(r);

            if (cookie === null) return;

            var cookie_eval = cookie; //cookie.substring(this.$name.length + 1);
            var a = cookie[1].split('&');

            // Split each cookie name/value pair into an array
            for (var j = a.length - 1; j >= 0; j--) {
                a[j] = a[j].split(':');
            }

            for (var k = a.length - 1; k >= 0; k--) {
                this[a[k][0]] = decodeURIComponent(a[k][1]);
            }
        } // End Cookie
    }; // End return
}();

/**
 * @param {integer} daysToLive Count of days before expiration.
 *      Failing to set this will cause the cookie storing process
 *      to silently fail.
 * @param {string} path Path at and below which the cookie
 *      is accessible, e.g., '/' or '/public'.
 * @param {string} domain Domain for which the cookie is valid, e.g.,
 *      'test.com', 'site1.test.com'.
 * @param {bool} secure Whether to secure the cookie. Default is false.
 * @this {Cookie}
 */
noski.util.Cookie.prototype.store = function(daysToLive, path, domain, secure) {
    var cookieeval = '';
    for (var prop in this) {
        // Ignore props that start with $ so that
        // our special $name property isn't included
        // Same goes for functions - that's a no-no!
        if ((prop.charAt(0) == '$') || (typeof this[prop] == 'function')) {
            continue;
        }
       if (cookieeval !== '') cookieeval += '&';
       cookieeval += prop + ':' + encodeURIComponent(this[prop]);
    }

    var cookie = this.$name + '=' + cookieeval;
    if (daysToLive || daysToLive === 0) {
        cookie += '; max-age=' + (daysToLive * 24 * 60 * 60);
    }

    if (path) cookie += '; path=' + path;
    if (domain) cookie += '; domain=' + domain;
    if (secure) cookie += '; secure';
    document.cookie = cookie;
};

/**
 * Removes a cookie. The arguments are all optional
 * but must the the same as the ones used to
 * store the cookie in the first place.
 * @param {string} path Path at and below which the cookie
 *      is accessible, e.g., '/' or '/public'.
 * @param {string} domain Domain for which the cookie is valid, e.g.,
 *      'test.com', 'site1.test.com'.
 * @param {bool} secure Whether to secure the cookie. Default is false.
 * @this {Cookie}
 */
noski.util.Cookie.prototype.remove = function(path, domain, secure) {
    for (var prop in this) {
        if (prop.charAt(0) !== '$' && typeof this[prop] !== 'function') {
            delete this[prop];
        }
    }

    this.store(0, path, domain, secure);
};

/**
 * Static method (no prototype chain) to see whether cookies are
 * enabled in the browser.
 * @return {boolean} True if cookies are enabled, otherwise false.
 */
noski.util.Cookie.enabled = function() {
    if (navigator.cookieEnabled !== undefined) {
        return navigator.cookieEnabled;
    }

    if (Cookie.enabled.cache !== undefined) {
        return Cookie.enabled.cache;
    }

    document.cookie = 'testcookie=test; max-age=10000';

    var cookies = document.cookie;
    if (cookies.indexOf('testcookie=test') === -1) {
        return Cookie.enabled.cache = false;
    }
    else {
        document.cookie = 'testcookie=test; max-age=0'; // delete cookie
        return Cookie.enabled.cache = true;
    }
};

noski.util.Cookie.all = function() {
    var results = [];
    var all_cookies = document.cookie;
    if (all_cookies === '') return results;

    var parts = all_cookies.split(';');
    var j = parts.length;
    while (j--) {
        var data = parts[j].split('=');
        var name = noski.core.trim(data[0]);
        var cookie = new noski.util.Cookie(name);
        results.push(cookie);
    }
    return results;
};
{%endhighlight%}