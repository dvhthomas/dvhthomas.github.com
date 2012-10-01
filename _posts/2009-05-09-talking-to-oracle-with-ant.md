---
layout: post
title: "Talking to Oracle with Ant"
abstract: "I’m working on my first Java project this month and wanted to automate some PL/SQL scripts. They do a bunch of setup and teardown on a local Oracle instance to get it ready for work. I’ll soon be adding a simpler task for pushing some disposable test data in to the same database, but for now I’ll keep it simple. Anyway, on .NET projects I like to use msbuild to get my initial post-subversion checkout environment all squared away. Here’s my first Ant build script to handle a little Oracle."
category: 
tags: [oracle]
---
Of course you can see that it’s not exactly rocket science. A little Googling got me on the right path, and I feel immediately more at home with this format than I did when starting MSBuild. I guess maybe I should have tried NAnt!

{%highlight xml%}
<?xml version="1.0" encoding="windows-1252" ?>
<project default="init" basedir="../../">

    <!-- Assumes the existence of a build properties file -->
    <property file="${basedir}/override.properties"/>
    <property file="${basedir}/build.properties"/>
           
    <target name="init"></target>
    
    <!-- Rebuild derived (non-census) data from scratch -->
    <target name="tiger.db.up" depends="tiger.db.down">
        <exec executable="${db.sqlplus}" dir="${project.persistence}/sql/tiger">
            <arg line="${db.sqlplus.sys} @doall.sql"/>
        </exec>
    </target>
    
     <!-- Drop any objects not coming directly from census, i.e., derived data -->
    <target name="tiger.db.down">
        <exec executable="${db.sqlplus}" dir="${project.persistence}/sql/tiger">
            <arg line="${db.sqlplus.sys} @dropall.sql"/>
        </exec>
    </target>
</project>
{%endhighlight%}

The `basedir` property simply points to a directory two levels up. Why? Because I have a few standard properties that developers will need in order for the build to work. The neat part is that they can also create an override.properties file to, well, override (!) any of the defaults that they want to, e.g., the name of the Oracle instance, a username, whatever. Note that the references to the property files in my example above are in a particular order; properties in Ant are immutable so once I’ve defined it in my override file, it cannot then be redefined in the `build.properties` file even if it’s listed there. Nice and simple. Here’s the build.properties and my override.

    #If you need to override any of these properties, create an 
    # override.properties file in the same folder and make sure
    # that it is imported FIRST in any build scripts.

    # Oracle server and connection info
    # Note that the $ is escaped with a leading $, so $$$$ equates to $$
    db.sys.password = pa$$$$w0rd
    db.sqlplus = sqlplus
    db.host = yadda.yadda.whatever.com
    db.sid = yomamma
    db.sqlplus.sys = sys/${db.sys.password} as sysdba@//${db.host}/${db.sid}

    tiger.state.user = tiger2007_39
    tiger.state.password = tiger2007_39

    # Project directories
    # base.dir is defined in each build script and describes
    # the relationship between the build.xml location and
    # the relative location of all of the project
    # directories. For example, if an Ant file is located
    # in SomeCommon\ant\build.xml then the base.dir value
    # defined in that file might read "../../" meaning that
    # the project directories are "two levels up from me"
    some.common = ${basedir}/SomeCommon
    some.persistence = ${basedir}/SomePersistence
    some.security = ${basedir}/SomeSecurity

    # WARNING: Make sure that you leave an EMPTY LINE at the end of this file.

And the override. Notice I just need to override a couple of properties: the rest are left untouched.

    # Any values added here will override values
    # that exist in build.properties. If a value
    # is not present here the value from build.properties
    # will be used by default.
    db.sys.password = secret.word
    db.host = my.pc.com
    db.sid = oracle
