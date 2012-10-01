---
layout: post
title: "Discovering Python and Oracle with cx_Python"
abstract: "I needed to process records in a table with 14.4 million records the other day. I used cx_Python to make some perf issues disappear."
category: 
tags: [python, oracle]
---
The database is on my laptop so performance on a table that large sucks -- no matter how many indexes you throw at the thing, it’s still all in one data file on one disk and has only 1GB of RAM to work with. My friendly DBA helped me to eliminate the big bottlenecks that I could remove on a laptop, namely to increase the amount of memory assigned to client side SQL manipulation. Other than that it still crawled and then I realized that the Java functions I am calling in the update statements are the slow point, not Oracle itself. See, for each row I am doing a bunch of string manipulation related to turned crummy address data in to nice clean US Postal Service standard addresses, and that takes Java some time; not much time but enough to build up over 14.4 million iterations. And what eventually dawned on me was the JVM itself was getting bogged down and there wasn’t much I could do about it.

Or was there? Again with the help of my DBA, the approach taken was to batch the rows by some arbitrary subset to reduce the load on the JVM and give it a chance to catch up. I chose rip through a ZIP codes’ worth of data for each batch and those ZIPs live in a text file. Could I have written this in PL/SQL? Maybe, but I don’t know it well enough to be productive quickly so instead I reached for my new scripting tool of choice that seems to get this type of job done quickly: Python. I got the [approved Oracle connection bits](http://www.oracle.com/technology/pub/articles/prez-python-queries.html) called [cx_Oracle](http://cx-oracle.sourceforge.net/) and installed them locally. I have a full Oracle install including TNS listener and database server so I didn’t have to mess with Oracle Instant Client, so here is the sum total of my code:

{%highlight python%}
#!/usr/bin/env python
import csv
import time
import cx_Oracle

# Parses USPS addresses from voter addresses
# and inserts them into VR_LOCATION table ready
# for geocoding. Does batches by zipcode
def LoadZips():
    zipcodes = []
    zips = open('OH_ZIP_CODES.txt','r')
    for line in zips:
        zip = line[0:5]
        if zip not in zipcodes:
            zipcodes.append(zip)
    zips.close()
    return zipcodes

def UpdateAddresses(ziplist):
    counter = 1
    total = len(ziplist)
    
    for zipcode in ziplist:
        orcl = cx_Oracle.connect('voter/voter@oracle')
        curs = orcl.cursor()
        countsql = "select count(*) from vr_location where zip_co = '%s'" % zipcode
        concatsql = """update vr_location l set l.usps_address=(
                        select mizar.string_utils.remove_duplicate_whitespace(
                            house_number
                            ||' '||pre_street_direction
                            ||' '||street_name
                            ||' '||street_description
                            ||' '||post_street_direction)
                        from vr_address a where a.address_pk = l.address_pk)
                    where zip_co = '%s'""" % zipcode
        parsesql = """update vr_location set usps_address = mizar.usaddress_utils.parse_address(usps_address)
                    where zip_co = '%s'""" % zipcode
        curs.execute(countsql)
        
        records_affected = curs.fetchone()[0]
        if records_affected == 0:
            print "No records for zipcode %s" % zipcode
            counter += 1 
            continue
        
        print "[%s] %s of %s: %s addresses" % (zipcode, counter, total, records_affected)
        curs.execute(concatsql)
        orcl.commit()
        curs.execute(parsesql)
        orcl.commit()
        curs.close()
        counter += 1 

        # Uncomment this to debug - just steps through X zipcodes      
        #if counter == 3:
        #    print &quot;Cleaning up...&quot;
        #    break
        

if __name__ == "__main__":
    start = time.clock()
    zipcodes = LoadZips()
    print "Processing addresses in %s zip codes" % len(zipcodes)
    UpdateAddresses(zipcodes)
{%endhighlight%}

As you can see from the __main__ method at the bottom, I read in the ZIPs from a text file and eliminate duplicates, then run a couple of update statements using the current ZIP to filter my working set. Look carefully at the update statements and you can see the Java functions being called. Again, I’m sure this could easily be done in PL/SQL if you know how but I’m recording this approach here for posterity. It works. That’s good enough for me.