---
layout: post
title: "Batch download of Facebook images using Ruby"
abstract: "Scripting, scripting. Doing repetitive things is so much easier with a quick script. Of course the first thing you need a scripting language that you're really comfortable with. Ruby is becoming my language of choice for these little tasks on Windows."
category: 
tags: [ruby, scripting]
---
OK, so Ruby isn't just a scripting language. It is a full fledged dynamically typed object-oriented language. But I'll be darned if it just doens't make some thing easier to get done that my trusty old C#. For instance, I need to run a batch job that will get the latest fan count from a bunch of Facebook fan pages. Using the built-in libraries it's a cinch:

{%highlight ruby%}
#!ruby
require 'rubygems'
require 'yaml'
require 'net/http'
require 'json'
require 'csv'

config = YAML.load_file('config/config.yml')['facebook']['sources']
sources = {}

config.each do |group|
    group[1].each do |source|
        sources[source[0]] = source[1]
    end
end

sources.sort

# download ids
CSV.open('./fan_counts.csv', 'wb') do |output|
    output << ["fb_id","name","fans"]
    sources.each do |key,value|
        json = Net::HTTP.get('graph.facebook.com', "/#{value}")
        result = JSON.parse(json)
        fan_count = result['fan_count']
        name = result['name']
        puts "#{name} has #{fan_count} fans"
        output << [value, "#{name}", fan_count]
    end
end
{%endhighlight%}

The YAML file looks like this:

{%highlight yaml%}
#!yaml
facebook:
  sources:
      news:
        barack_obama: 6815841748
        cnn: 5550296508
        republican_national_committee: 123192635089
        huffington_post: 18468761129
        msnbc: 23294612872
        new_york_times: 5281959998
      entertainment:
        e_online: 89033370735
        us_weekly: 9034820804
        perez_hilton: 116397088405021
{%endhighlight%}

You can see the full context of this little snippet in [my first
attempt at Sinatra](https://github.com/dvhthomas/socks).