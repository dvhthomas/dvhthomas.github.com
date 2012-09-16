---
layout: post
title: "Running a bunch of SQL scripts in C#"
abstract: "Automating some SQL Server work by hooking into Microsoft's .NET SQL Server SMO namespace."
category: 
tags: [csharp, sqlserver]
---
Here is how I did it. Read in any script called `*.sql` from a directory that does not have the word 'test' somewhere in it, then use the `Microsoft.SqlServer.Management.Common` and `Microsoft.SqlServer.Management.Smo` namespaces for the following:

{%highlight csharp%}
public bool RestoreFieldDatabaseFromBackup(string connectionString)
{
 List scripts = this._sqlDirectory.GetFiles("*.sql", SearchOption.AllDirectories)
  .Where(s => !s.Name.Contains("test"))
  .Select(s => s.FullName).ToList();

 if (scripts.Count() == 0) return false;

 var connection = new SqlConnection(connectionString);

 try
 {
  for (int i = 0; i < scripts.Count; i++)
  {
   using (var reader = new StreamReader(scripts[i]))
   {
    var server = new Server(new ServerConnection(connection));
    var db = new Database(server, connection.Database);
    string scriptText = reader.ReadToEnd();
    Log.For(this).Debug("Running: " + scripts[i]);
    db.ExecuteNonQuery(scriptText);
   }
  }
 }
 catch (Exception ex)
 {
  Log.For(this).Error(ex);
  return false;
 }
 return true;
}
{%endhighlight%}