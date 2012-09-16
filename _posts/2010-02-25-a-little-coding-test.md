---
layout: post
title: "A little coding test"
abstract: "Someone recently asked me about some questions to give someone during an interview. The fun part is having the interviewee do the problem on a white board without an IDE to help them."
category: 
tags: [general, programming]
---
As a long time Visual Studio user it's amazing to realize how heavily you lean on the IDE for little things like IntelliSense.

## Do this without compiling...

Here is one such problem. It’s not very complicated but it does force the interviewee to think about assumptions being made. And I tried it!

> Given a certain amount of money that you need, and a set of coin denominations, tell me the minimum number of coins of each denomination I need to have that amount of money.

Having heard the problem statement I tried the whiteboard version. Then I opened up Visual Studio and typed out the following. I waited until I typed the whole thing before trying to build or run tests, just to keep myself honest about assumptions I was making.

**STOP**! Try to do this yourself without reading my approach. Not that I'm right, fast, wrong, or anything else, but see how you do first.

{% highlight csharp %}
public class CoinCounter
{
  /// <summary>
  /// Assumptions made:
  /// 1. There's always a denomination of 1 unit
  /// 2. There are no fractional units like the 1/2 pence in England
  /// 3. The denominations are always in the same units (cents, not cents and dollars)
  /// </summary>
  public static Dictionary GetMinimumCoinsNeeded(int[] denominations, int targetValue)
  {
    var result = new Dictionary();
    
    // Sort in descending order so we get the biggest denomination first
    Array.Sort(denominations);
    Array.Reverse(denominations);
    int remaining = targetValue;
    
    foreach (int denomination in denominations)
    {
      // Turns out there's a Math.DivRem function that gets both the
      // coins and remaining value in one go.
      int coins = remaining / denomination;
      
      // Forgot to add this first time through - don't need to
      // do the rest if there aren't any coins
      if (coins == 0) 
        continue;
      
      // Got this backwards first time - denomination % targetValue
      remaining = targetValue % denomination;
      result.Add(denomination, coins);
      Console.WriteLine("Adding {0} coins of denomination {1} leaving {2} to work with...",
            coins, denomination, remaining);
      
      if (remaining == 0)
        break;
    }
    
    return result;
  }
}
{% endhighlight %}

## And see if it works when you finally build it

When I saw this problem I ended up with a solution that resembles the one above. I did make some goofy mistakes that involved some wiping out and re-"coding" on the whiteboard. For example, I'd just been using Excel to do some modulus work and actually wrote in the Excel Mod function rather than the C# modulus (`%`) built in function. Embarassing! The other things I found when I actually tried to compile then run the code are listed in C# comments. For example, I got the order of the two parameters in the `%` call backwards. Here is the final part where I report the number of different coins to use:

{%highlight csharp%}
var result = CoinCounter.GetMinimumCoinsNeeded(new[] { 2, 1, 100, 500, 10, 25 }, 2341);

foreach (var item in result)
{
 Console.WriteLine("Denomination: {0}, Coins: {1}", item.Key, item.Value);
}
{%endhighlight%}

Which returns this output:

    Denomination: 500, Coins: 4
    Denomination: 100, Coins: 3
    Denomination: 25, Coins: 1
    Denomination: 10, Coins: 1
    Denomination: 1, Coins: 1

Try it yourself. It’s a good test of your logic ability and knowledge of your core language and platform.