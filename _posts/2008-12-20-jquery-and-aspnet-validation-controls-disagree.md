---
layout: post
title: "jQuery and ASP.NET validation controls disagree"
abstract: "I spent the better part of a morning struggling to understand how ASP.NET Validation controls interact with non-ASP.NET elements in a page."
category: 
tags: [dotnet, aspnet]
---
<img src="/images/asp-net-calendar.png" />

## The context

I have a number of ASP.NET server pages (aspx) that have one or more TextBox controls on them. Some of those text boxes need to have a popup calendar to allow a user to easily enter a valid date. I am using ASP.NET Validation server controls to inject so JavaScript to perform some simple user input checks like so:

{% highlight html %}
<label for="txtEffectiveDate">Date To Process</label>

<asp:TextBox ID="txtEffectiveDate" runat="server"
    CssClass="inputWide datePick hilite" />
<asp:RequiredFieldValidator ID="valEffDateNotEmpty" runat="server"
    ControlToValidate="txtEffectiveDate"
    ErrorMessage="Date to Process date is required"
    Display="none"
    ValidationGroup="Workflow"
    SetFocusOnError="true" />
<asp:CompareValidator ID="valEffDate" runat="server"
	ControlToValidate="txtEffectiveDate"
	Type="date" Operator="DataTypeCheck" ErrorMessage="Date To Process is not a valid date"
	Display="none" ValidationGroup="Workflow" />
{% endhighlight %}

The popup calendar uses [jQuery’s UI](http://docs.jquery.com/UI/Datepicker) project to provide a nice configurable widget without the overhead of a server control. Why use jQuery? Basically I wanted to simply add a CSS class to any TextBox to add a calendar rather than adding a bunch of server controls, one for each date field. So I have this at the top of the page to import the scripts:

{% highlight html %}
<asp:ScriptManager ID="smMaster" runat="server">
  <Scripts>
    <asp:ScriptReference Path="~/scripts/jquery.js" />
    <asp:ScriptReference Path="~/scripts/jquery-ui.js" />
    <asp:ScriptReference Path="~/scripts/gui.js" />
  </Scripts> 
</asp:ScriptManager>
{% endhighlight %}

The gui.js is my own little script that basically hooks up any TextBox with a class of datePick with the jQuery datepicker widget like so:

{% highlight js %}
$(document).ready(function() {
  $('.datePick').datepicker();
});
{% endhighlight %}

## The Problem

This all works great in Firefox and Chrome, but bombs in IE7 and IE8 every time. Well, it doesn’t bomb unless I choose to debug, but there is definitely a JavaScript error. What I see is the calendar popping up as expected. I can choose a date, but then the calendar stays displayed instead of gracefully closing to leave my new date in the text field. Why?

After doing some Googling I found a great discussion on the jQuery discussion group about ASP.NET validation controls and how they interact with non-ASP.NET JavaScript. Basically the validation script is trying to fire every time the calendar widget calls it’s onSelect function, and because the calendar hasn’t yet put a value in the control the ASP.NET JavaScript errors out (thinks the length of the property array it’s checking is less than zero or just not there).

This means that I can either have a nice jQuery calendar or validation controls. Unless there’s a way around it all…

## The Solution

Thanks entirely to the [supportive jQuery user mt](http://groups.google.com/group/jquery-en/browse_frm/thread/a8902f2774edc05a/7205636697f1c54a?lnk=gst&q=asp.net+calendar+ui#7205636697f1c54a) I got a great workaround. Simply put, you need to subclass (or in jQuery terms, $.extend) the datepicker and override it’s onSelect method by setting it to nothing. Having done that, the calendar popup no longer interferes with what the ASP.NET-generated JavaScript is trying to do. Now I can have the best of both worlds. Here’s the fix in my gui.js:

{% highlight js %}
// Attach calendar functionality to any element
// with a CSS class of datePick. This is safe
// if the page has multiple calendars.
$(document).ready(function() {
  $('.datePick').datepicker($.extend({},
    $.datepicker.regional['en'], {
      onSelect: function() { }
    }));
});

// Create an empty subclass of the datapicker
// so that we can override it's onSelect method
// to accomodate ASP.NET Validation control scripts
jQuery(function($){
  $.datepicker.regional['en'] = {};
  $.datepicker.setDefaults($.datepicker.regional['en']);
});
{% endhighlight %}
