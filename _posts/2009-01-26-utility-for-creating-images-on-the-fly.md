---
layout: post
title: "Utility for creating images on the fly"
abstract: "Sometimes you need to create an image with specific size parameters for testing on the fly. Here's how I do it."
category:
tags: [dotnet, utility]
---
File this under "stupid, simple", but I keep this handy for created files on the fly, especially when I’m testing system boundaries for files of various sizes. For example, in my current project I limited the size of an upload to 5MB. So I create a whopping big image on the fly then try to send it.

{% highlight csharp %}
public static MemoryStream CreateTempImage(int width, int height)
{
  using (var image = new Bitmap(width, height, PixelFormat.Format32bppArgb))
  {
    string text = String.Format("{0:s}", DateTime.Now);
    Graphics graphics = Graphics.FromImage(image);
    var brush = new SolidBrush(Color.Red);
    graphics.FillRectangle(brush, 0, 0, image.Width, image.Height);
    var font = new Font("Arial", 18, FontStyle.Bold);
    var textBrush = new SolidBrush(Color.White);
    var format = new StringFormat { Alignment = StringAlignment.Center };
    graphics.DrawString(text, font, textBrush, width / 2, height / 2, format);
    var stream = new MemoryStream();
    image.Save(stream, ImageFormat.Bmp);
    stream.Position = 0;
    return stream;
  }
}
{% endhighlight %}

Including the time is just a way to make sure that your visual test is using the image you think it's using.Ï