---
layout: post
title: "Scripting my way out of a long afternoon of text editing using Ruby"
abstract: "I'm submitted the mother of all system configuration requests to the Ops team. They need an insanely detailed list of IP addresses, servers, configs, you name it. So I broke out my newfound Ruby skills, and scripted the config details. Beats hours of copy and paste."
category: 
tags: [ruby, scripting]
---
I want to post this more for my own reference than anything else, but I'm pretty pleased with this little Ruby script.

## Background

I have to submit a lengthy request to my operations team to open up some specific ports on virtual IPs between two sets of remote servers. Cross referencing all of the various IPs, server names, and masks was pretty daunting until I decided to create the work request programmatically.

## Solution

### ERB

First up I knew I needed to create a text file that I could cut'n'paste into the online work order form, and that the form has to be in a very specfic format. So what in Ruby-land lets you create such a template and pass some variable data to it? ERB of course. Defining the string for the template is simple. Just use Ruby's multi-line encapsulation (`<<PLACEHOLDER The text you want goes in here PLACEHOLDER`). Here I'm using the word `ERB` as my delimeter:

{%highlight ruby%} 
#!ruby
require 'erb'

template = <<ERB (mask <%= @ip_mask %>)
* Source port: 23, 135, 6798, 7001-7025,1083, 8200
* Source Environment (PROD/PPE/INT/N/A): PROD
* Source Domain (PHX/CEZ/DEN/RNO/N/A): PHX
* Destination address (NOT HOSTNAME): <%= @be_ip %>
* Destination port: 23, 135, 6798, 7001-7025,1083, 8200
* Destination Environment (PROD/PPE/INT/N/A): PROD
* Destination Domain (PHX/CEZ/DEN/RNO/N/A): PHX
* Protocol: TCP
* VIP/DIP VIP
* Established: Yes

ERB
{%endhighlight%}

In fact, I'm only interested in Vlans that have a vlanId like `vlanId####` and where the range begins with `10.`. The [Nokogiri](http://nokogiri.org/) XML/HTML reader and parse is tailor made for this type of work. It's a Ruby C extension that uses the ultra fast libxml package, and has great XPath support. So to zero in on the handful of nodes I need in the 7MB file takes a fraction of a second using a query like this:

{%highlight ruby%}
#!ruby
doc = Nokogiri::XML(File.open('/some/file/name.xml'))
@vlans = doc.xpath("//Vlan[contains(@vlanId,'vlanid')]")

# then a bit later we query each vlan like so:
if vlan['vlanId'] =~ /\Avlanid\d{4}\b/i and vlan['range'] =~ /\A10\b/i
    # do something
end
{%endhighlight%}

You can see how I'm plucking all Vlan elements (a NodeList, in Nokogiri parlance) and simultaneously using a 'string contains' query on the contents of the vlandId attribute. Pretty neat way to get an array-like NodeList to work with.

### Yaml

The other set of server information--for the ones that are *not* in the XML files, I created a simple [YAML](http://yaml.org) file to hold what I need:

{%highlight yaml%}
bl2:
  name: blah
  ap: blah blah.xml
  servers:
  - server1: 10.#####
  - server2: 10.####
db3:
  name: another-name
  ap: blah blah.xml
  servers:
  ...
{%endhighlight%}

### Putting it all together

Here's the final script. For each entry in the YAML file we figure out which XML file is related. Then we find the nodes in the XML file that are needed, and finally write out a long list of entries in our form template. Really a small amount for code that saved me hours and hours and tedious text editing. Thank you, scripting :-)

{%highlight ruby%}
#!ruby
require 'yaml'
require 'nokogiri'
require 'erb'

template = < (mask <%= @ip_mask %>)
* Source port: ########, #####
* Source Environment (PROD/PPE/INT/N/A): PROD
* Source Domain (PHX/CEZ/DEN/RNO/N/A): PHX
* Destination address (NOT HOSTNAME): <%= @be_ip %>
* Destination port: #####< #####
* Destination Environment (PROD/PPE/INT/N/A): PROD
* Destination Domain (PHX/CEZ/DEN/RNO/N/A): PHX
* Protocol: TCP
* VIP/DIP VIP
* Established: Yes

* Business justification:
  Open up communication between <%= @ap_cluster %> with 
  vlan '<%= @vlan_id %>' and <%= @dc_name %> hosting

ERB

@entry = ERB.new(template)
@ip_range = ''
@ip_mask = ''
@vlan_id = ''
@be_ip = ''
@dc_name = ''
@ap_cluster = ''

datacenters = YAML::load(File.open('dc.yml'))
output = 'network-access-ticket.txt'
File.delete(output) if File::exists?(output)

File.open(output, 'w') do |file|

    datacenters.each do |k,v|
        @dc_name = v['name']
        xml = v['ap']
        @ap_cluster = xml.split('.')[0].upcase
        puts xml
        puts "Reading #{xml}..."
        doc = Nokogiri::XML(File.open(xml))
        @vlans = doc.xpath("//Vlan[contains(@vlanId,'vlanid')]")
        
        v['servers'].each do |server|
            @be_ip = server.values[0]

            @vlans.each do |vlan|
                # vlan must have name like 'vlan####' and ip beginning with '10'
                if vlan['vlanId'] =~ /\Avlanid\d{4}\b/i and vlan['range'] =~ /\A10\b/i
                    @vlan_id = vlan['vlanId']
                    @ip_range = vlan['range']
                    @ip_mask = vlan['mask']
                    #puts "Vlan: #{vlan['vlanId']}\tRange: #{vlan['range']}"
                    file.puts @entry.result
                end
            end
        end
    end

end
{%endhighlight%}