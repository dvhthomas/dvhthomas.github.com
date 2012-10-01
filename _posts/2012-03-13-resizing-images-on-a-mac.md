---
layout: post
title: "Resizing images on a Mac"
abstract: "How to automate a really boring manual process"
category: 
tags: [tools]
---
OK, this is so old hat that it's almost silly. But I want to record this somewhere before I have to figure it out again. So here's how to resize an image quickly on a Mac:

1. Install ImageMagick

    `brew install imagemagick`

1. Run a command like this, which does a resize and adds a little gray border at the same time:

    `convert ~/Downloads/photo.jpg -mattecolor lightgray -frame 20 -resize 300 ~/Downloads/framed.jpg`

Done :-)