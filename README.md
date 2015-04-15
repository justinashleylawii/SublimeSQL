# SublimeSQL
Sublime Text 2/3 Plugin for Running SQL Server queries from within Sublime Text using Windows authentication and sqlcmd.

##Setup
Git clone the repository to your Packages folder. Then set up your server and default database in the SublimeSQL settings file.  You can set these settings at the package level, or put it into your project-specific settings (Project -> Edit Project) for more fine-grained control. Currently there are only a handful of settings supported:

* _server_ - This is the server you're trying to connect to. This should be the same value you use when you're connecting to the database within SSMS or SQL Server Express.
* _database_ - This is the default database in which your queries will run. If you leave this out, you need to select the database using the **Use Database** command (explained below).
* _select_top_count_ - (Optional - _default=50_) The number of records to return when using the **Select from Table** command.

##Commands

###Execute Query

There are several ways to execute a query. The easiest way is to open a file containing a query, and hitting F5 (default keybinding). You could also run the command from the command palette ``SublimeSQL: Execute Query``. Using either of these methods will execute the entire file currently opened as a query. If you'd like to execute just a subset of the currently opened view, select the query with your mouse and run the Execute Query command in any of the ways mentioned.

Since Sublime has support for multiple simultaneous selections, it would make sense to be able to run multiple queries occuring in multiple selections. SublimeSQL will open the result set of each query in a separate view.

###Use Database

If you didn't set a default database, or you'd like to temporarily use a different database, you can accomplish this with the ``SublimeSQL: Use Database`` command from the command palette. The command will return a list of all of the databases for the current server. When you pick one, the default database _for the current view_ will be _temporarily_ set to the selection. Alternatively, you can just add a "use database" command to your query, but note that a database needs to be set regardless. This may be fixed at some point.

###Select from Table

The ``SublimeSQL: Select from Table`` command provides a list of tables in the quick panel. When you select one, it will query the database like this:

``
  select top 50
    *
  from
    table_name
``

where table_name is the name of the table you selected. As mentioned above, the number 50 can be set to any other number using the _select_top_count_ option.

###Get Table Schema

The ``SublimeSQL: Get Table Schema`` command provides a list of tables in the quick panel. When you select one, it will get the schema for that table in a manner similar to the mysql "describe table" command. It shows the names of the fields, their default values, data types, and whether they're allowed to be null.

##Completions

When you're in a SQL file, and you activate the completion menu using _ctrl+space_, SublimeSQL will go get the list of tables from the current database to populate the list. This would be way cooler if it could be smart and suggest valid stuff like SSMS does, but that would require some sort of SQL interpreter, and I think that's outside the scope of this plugin.

##Notes

There's probably a lot of cool things that could be added to this plugin. If you think of anything, or if you run into issues (as you probably will), please open up an issue so I can take a look. Feel free to try to work on it yourself if you want, but I'll warn you: the code needs some love.  (read:refactoring)

Happy Coding =]

