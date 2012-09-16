---
layout: post
title: "Reminder: Parametized LIKE query in C#"
abstract: "Using Oracle.DataAccess in .NET has all sorts of benefits over the Microsoft implementation. But if I have to figure this out yet again for the nth time, I'll get ticked off."
category: 
tags: [oracle, dotnet]
---
So here is how to do a `LIKE` query in C# using an `OracleParameter`:

{% highlight csharp %}
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Oracle.DataAccess;
using Oracle.DataAccess.Client;
using System.Data;

namespace Oracle
{
    class Program
    {
        static void Main(string[] args)
        {
            const string searchTerm = "bd";
            const string cs = @"Data Source=(DESCRIPTION=(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=thehostname)(PORT=1521)))(CONNECT_DATA=(SERVER=DEDICATED)(SERVICE_NAME=the.service.name)));User Id=user;Password=pass.word;";
            const string sql = @"select rm_id, ref_fac_id || ' - ' || rm_num as name
                        from asbestos.rooms
                        where rownum < 51
                          and ref_fac_id is not null
                          and( lower(ref_fac_id) like :q
                            or lower(rm_num) like :q)
                        order by rm_num asc";
            var conn = new OracleConnection(cs);

            var cmd = conn.CreateCommand();
            cmd.CommandText = sql;
            cmd.CommandType = CommandType.Text;
            var param = cmd.CreateParameter();
            param.DbType = DbType.String;
            param.Direction = ParameterDirection.Input;
            param.ParameterName = ":q";
            param.Value = string.Format("{0}{1}{0}", "%", searchTerm.ToLower());
            cmd.Parameters.Add(param);
            conn.Open();

            using (var reader = cmd.ExecuteReader(CommandBehavior.CloseConnection))
            {
                while (reader.Read())
                {
                    Console.WriteLine(reader.GetString(1));
                }
            }

            Console.Read();
        }
    }
}
{% endhighlight %}