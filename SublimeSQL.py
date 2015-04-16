import sublime, sublime_plugin
import subprocess

class run_queryCommand(sublime_plugin.WindowCommand):
	def run(self):
		settings = sublime.load_settings("SublimeSQL.sublime-settings")
		server = sublime.active_window().active_view().settings().get("server", settings.get("server", "None"))
		database = sublime.active_window().active_view().settings().get("database", settings.get("database", "None"))

		if server == "None" or database == "None":
			sublime.message_dialog("Cannot execute query. No server or database specified.")
			return

		selections = sublime.active_window().active_view().sel()

		if not selections[0].empty():
			queries = []

			for sel in selections:
				queries.append(sublime.active_window().active_view().substr(sel))

			for query in queries:
				proc = subprocess.Popen(["sqlcmd", "-S", server, "-d", database, "-k", "-Y", "30", "-Q", query], stdout=subprocess.PIPE)
				query_results = proc.communicate()[0].decode("utf-8").replace("\r\n", "\n")

				# Create a new view in the current window containing the results from the query
				result_view = self.window.new_file()
				result_view.set_name("Query Results")
				result_view.run_command("output_results", {"results":query_results})
				result_view.settings().set("word_wrap", "false")
				result_view.set_scratch(True)
		else:
			query = self.window.active_view().substr(sublime.Region(0, self.window.active_view().size()))
			
			proc = subprocess.Popen(["sqlcmd", "-S", server, "-d", database, "-k", "-Y", "30", "-Q", query], stdout=subprocess.PIPE)
			query_results = proc.communicate()[0].decode("utf-8").replace("\r\n", "\n")

			#Create a new view in the current window containing the results from the query
			result_view = self.window.new_file()
			result_view.set_name("Query Results")
			result_view.run_command("output_results", {"results":query_results})
			result_view.settings().set("word_wrap", "false")
			result_view.set_scratch(True)

class output_resultsCommand(sublime_plugin.TextCommand):
	def run(self, edit, results):

		self.view.insert(edit, 0, results)

class use_databaseCommand(sublime_plugin.WindowCommand):
	databases = []
	def run(self):

		self.databases = []
		
		settings = sublime.load_settings("SublimeSQL.sublime-settings")
		server = self.window.active_view().settings().get("server", settings.get("server", "None"))

		if len(self.databases) == 0:
			proc = subprocess.Popen(["sqlcmd", "-S", server, "-Q", "select name from master..sysdatabases order by name"], stdout=subprocess.PIPE)
			database_list = proc.communicate()[0].decode("utf-8")

			#Split string into list
			database_list = database_list.split("\r\n")

			#Insert databases into list
			for db in database_list:
				self.databases.append(db.strip())

			# Remove extra rows from result set
			self.databases = self.databases[2:(len(self.databases) - 3)]

		# Display database list in quick panel
		self.window.show_quick_panel(self.databases, self.on_done, sublime.MONOSPACE_FONT, 0)

	def on_done(self, user_input):
		if user_input != -1:
			#We need to take the index returned and store the corresponding database in settings
			print("Database '" + self.databases[user_input] + "' selected.")
			sublime.active_window().active_view().settings().set("database", self.databases[user_input])
		else:
			print("User didn't choose a database")

class select_from_tableCommand(sublime_plugin.WindowCommand):
	tables = []
	def run(self):
		
		self.tables = []
		
		if len(self.tables) == 0:
			view = self.window.active_view()

			# Get settings
			settings = sublime.load_settings("SublimeSQL.sublime-settings")
			server = sublime.active_window().active_view().settings().get("server", settings.get("server", "None"))
			database = sublime.active_window().active_view().settings().get("database", settings.get("database", "None"))

			if server == "None" or database == "None":
				sublime.message_dialog("Cannot execute query. No server or database specified.")
				return

			proc = subprocess.Popen(["sqlcmd", "-S", server, "-d", database, "-Q", "select table_name from INFORMATION_SCHEMA.TABLES where table_type = 'BASE TABLE' and table_catalog = '" + database + "' order by table_name"], stdout=subprocess.PIPE)
			table_list = proc.communicate()[0].decode("utf-8")

			#Split string into list
			table_list = table_list.split("\r\n")

			#Insert tables into list
			for table in table_list:
				self.tables.append(table.strip())

			self.tables = self.tables[2:(len(self.tables) - 3)]

		self.window.show_quick_panel(self.tables, self.on_done, sublime.MONOSPACE_FONT, 0)

	def on_done(self, user_input):
		if user_input != -1:
			settings = sublime.load_settings("SublimeSQL.sublime-settings")
			server = sublime.active_window().active_view().settings().get("server", settings.get("server", "None"))
			database = sublime.active_window().active_view().settings().get("database", settings.get("database", "None"))
			select_top_count = sublime.active_window().active_view().settings().get("select_top_count", settings.get("select_top_count", "50"))

			proc = subprocess.Popen(["sqlcmd", "-S", server, "-d", database, "-k", "-Y", "30", "-Q", "select top " + select_top_count + " * from " + self.tables[user_input]], stdout=subprocess.PIPE)
			query_results = proc.communicate()[0].decode("utf-8").replace("\r\n", "\n")

			#Create a new view in the current window containing the results from the query
			result_view = self.window.new_file()
			result_view.set_name("Query Table " + self.tables[user_input])
			result_view.run_command("output_results", {"results":query_results})
			result_view.settings().set("word_wrap", "false")
			result_view.set_scratch(True)
		else:
			print("User didn't choose a table")
	
class get_table_schemaCommand(sublime_plugin.WindowCommand):
	tables = []
	def run(self):
		
		self.tables = []

		if len(self.tables) == 0:
			view = self.window.active_view()

			# Get settings
			settings = sublime.load_settings("SublimeSQL.sublime-settings")
			server = sublime.active_window().active_view().settings().get("server", settings.get("server", "None"))
			database = sublime.active_window().active_view().settings().get("database", settings.get("database", "None"))

			if server == "None" or database == "None":
				sublime.message_dialog("Cannot execute query. No server or database specified.")
				return

			#Run query and convert byte string into regular string
			proc = subprocess.Popen(["sqlcmd", "-S", server, "-d", database, "-Q", "select table_name from INFORMATION_SCHEMA.TABLES where table_type = 'BASE TABLE' and table_catalog = '" + database + "' order by table_name"], stdout=subprocess.PIPE)
			table_list = proc.communicate()[0].decode("utf-8")

			#Split string into list
			table_list = table_list.split("\r\n")

			#Insert tables into list
			for table in table_list:
				self.tables.append(table.strip())

			self.tables = self.tables[2:(len(self.tables) - 3)]

		self.window.show_quick_panel(self.tables, self.on_done, sublime.MONOSPACE_FONT, 0)

	def on_done(self, user_input):
		if user_input != -1:
			settings = sublime.load_settings("SublimeSQL.sublime-settings")
			server = sublime.active_window().active_view().settings().get("server", settings.get("server", "None"))
			database = sublime.active_window().active_view().settings().get("database", settings.get("database", "None"))

			# It's messy, but this query will get us what we want
			query = "select column_name as Field, column_default as [Default], is_nullable as [NULL], case when character_maximum_length = -1 then data_type + '(MAX)' when character_maximum_length is not null then data_type + '(' + cast(CHARACTER_MAXIMUM_LENGTH as nvarchar) + ')' when data_type in ('decimal', 'money') then data_type + '(' + cast(numeric_precision as nvarchar) + ', ' + cast(numeric_scale as nvarchar) + ')' else data_type end as Type from information_schema.columns where table_name = '" + self.tables[user_input] + "'"

			# query_results = subprocess.check_output(["sqlcmd", "-S", server, "-d", database, "-k", "-Y", "30", "-Q", query]).decode("utf-8").replace("\r\n", "\n")
			
			proc = subprocess.Popen(["sqlcmd", "-S", server, "-d", database, "-k", "-Y", "30", "-Q", query], stdout=subprocess.PIPE)
			query_results = proc.communicate()[0].decode("utf-8").replace("\r\n", "\n")

			#Create a new view in the current window containing the results from the query
			result_view = self.window.new_file()
			result_view.set_name("Query Table Schema for " + self.tables[user_input])
			result_view.run_command("output_results", {"results":query_results})
			result_view.settings().set("word_wrap", "false")
			result_view.set_scratch(True)
		else:
			print("User didn't choose a table")

class table_autocomplete(sublime_plugin.EventListener):
	tables = []
	def on_query_completions(self, view, prefix, locations):

		#Temporary fix for lists not updating properly when switching databases/servers
		self.tables = []

		complete = False

		for loc in locations:
			if view.match_selector(loc, "source.sql"):
				complete = True

		if complete:
			if len(self.tables) == 0:
				self.get_tables()

			return self.tables
		else:
			return

	def get_tables(self):
		view = sublime.active_window().active_view()

		# Get settings
		settings = sublime.load_settings("SublimeSQL.sublime-settings")
		server = view.settings().get("server", settings.get("server", "None"))
		database = view.settings().get("database", settings.get("database", "None"))

		if server == "None" or database == "None":
			sublime.message_dialog("Cannot execute query. No server or database specified.")
			return

		#Run query and convert byte string into regular string
		proc = subprocess.Popen(["sqlcmd", "-S", server, "-d", database, "-Q", "select table_name from INFORMATION_SCHEMA.TABLES where table_type = 'BASE TABLE' and table_catalog = '" + database + "' order by table_name"], stdout=subprocess.PIPE)
		table_list = proc.communicate()[0].decode("utf-8")

		#Split string into list
		table_list = table_list.split("\r\n")

		#Insert tables into list
		for table in table_list:
			temp_list = []
			temp_list.append(table.strip() + "\t(Table)")
			temp_list.append(table.strip())
			self.tables.append(temp_list)

		self.tables = self.tables[2:(len(self.tables) - 3)]
