
# Imports
import sublime, sublime_plugin
import subprocess

# Define base class
class SublimeSQLBase(sublime_plugin.TextCommand):

	database_list = []
	table_list = []

	# **kwargs is the fancy python way of having a variable number of named arguments
	def run(self, edit, **kwargs):

		# Get settings
		settings = sublime.load_settings("SublimeSQL.sublime-settings")

		self.server = self.view.settings().get("server", settings.get("server", "None"))
		self.database = self.view.settings().get("database", settings.get("database", "None"))
		self.select_top_count = self.view.settings().get("select_top_count", settings.get("select_top_count", "50")).lower()
		self.output = self.view.settings().get("output", settings.get("output", "window")).lower()
		self.truncate_output = self.view.settings().get("truncate_output", settings.get("truncate_output", "true"))

		# TODO Implement truncate_output option

		if self.select_top_count.isdigit():
			self.select_top_count = " top " + self.select_top_count + " "
		elif self.select_top_count == "all":
			self.select_top_count = ""

		if not self.output in ["window", "panel"]:
			self.output = "window"

		self.runCommand(edit, **kwargs)

	def check_connection(self):
		
		# Test the server/database combination to ensure information is correct
		# print("check_connection not yet implemented")
		return True

	def execute_query(self, query):

		# Make sure we have a valid connection
		if self.check_connection() == False:
			print("Cannot execute query. Connection is invalid")
			return

		# Execute query
		proc = subprocess.Popen(["sqlcmd", "-S", self.server, "-d", self.database, "-k", "-Y", "30", "-Q", query], stdout = subprocess.PIPE)
		query_results = proc.communicate()[0].decode("utf-8")

		return query_results


	def display_output(self, edit, output, title):

		output = output.replace("\r\n", "\n")

		if self.output == "window":
			# Create a new view in the current window containing the results from the query
			result_view = self.view.window().new_file()
			result_view.insert(edit, 0, output)

			# File settings
			result_view.set_name(title)
			result_view.settings().set("word_wrap", "false")
			result_view.set_scratch(True)

		elif self.output == "panel":
			if int(sublime.version()) < 3000:
				result_view = self.view.window().get_output_panel("query")
			else:
				result_view = self.view.window().create_output_panel("query")

			result_view.run_command("erase_view")
			result_view.insert(edit, 0, output)
			result_view.show(result_view.size())
			self.view.window().run_command("show_panel", {"panel": "output.query"})

	def display_quick_pane(self, output):

		self.view.window().show_quick_panel(output, self.on_done, sublime.MONOSPACE_FONT, 0)

	def get_list_from_query(self, query):
		output_list = []

		query_results = self.execute_query(query)

		#Split string into list
		query_results = query_results.split("\r\n")

		#Insert tables into list
		for result in query_results:
			output_list.append(result.strip())

		output_list = output_list[2:(len(output_list) - 3)]

		return output_list

	def get_database_list(self):
		query = "select name from master..sysdatabases order by name"
		self.database_list = self.get_list_from_query(query)

	def get_table_list(self):
		query = "select table_name from INFORMATION_SCHEMA.TABLES where table_type = 'BASE TABLE' and table_catalog = '" + self.database + "' order by table_name"
		self.table_list = self.get_list_from_query(query)

class run_queryCommand(SublimeSQLBase):
	def runCommand(self, edit):

		selections = self.view.sel()

		# Take care of multiple selections
		if not selections[0].empty():
			queries = []

			for sel in selections:
				queries.append(self.view.substr(sel))

			for query in queries:
				query_results = self.execute_query(query)
				self.display_output(edit, query_results, "Query Results")
		else:
			query = self.view.substr(sublime.Region(0, self.view.size()))
			
			query_results = self.execute_query(query)
			self.display_output(edit, query_results, "Query Results")

class use_databaseCommand(SublimeSQLBase):
	def runCommand(self, edit):

		if len(self.database_list) == 0:
			self.get_database_list()

		self.display_quick_pane(self.database_list)

	def on_done(self, user_input):
		if user_input != -1:
			#We need to take the index returned and store the corresponding database in settings
			print("Database '" + self.database_list[user_input] + "' selected.")
			self.view.settings().set("database", self.database_list[user_input])
		else:
			print("User didn't choose a database")

class select_from_tableCommand(SublimeSQLBase):
	def runCommand(self, edit):

		query = "select table_name from INFORMATION_SCHEMA.TABLES where table_type = 'BASE TABLE' and table_catalog = '" + self.database + "' order by table_name"

		if len(self.table_list) == 0:
			self.get_table_list()

		self.display_quick_pane(self.table_list)

	def on_done(self, user_input):
		query = "select" + self.select_top_count + " * from " + self.table_list[user_input]

		query_results = self.execute_query(query)
		self.view.run_command("display_output_pane", {"output": query_results, "title": self.table_list[user_input]})

class get_table_schemaCommand(SublimeSQLBase):
	def runCommand(self, edit):

		if len(self.table_list) == 0:
			self.get_table_list()

		self.display_quick_pane(self.table_list)

	def on_done(self, user_input):
		query = "select column_name as Field, column_default as [Default], is_nullable as [NULL], case when character_maximum_length = -1 then data_type + '(MAX)' when character_maximum_length is not null then data_type + '(' + cast(CHARACTER_MAXIMUM_LENGTH as nvarchar) + ')' when data_type in ('decimal', 'money') then data_type + '(' + cast(numeric_precision as nvarchar) + ', ' + cast(numeric_scale as nvarchar) + ')' else data_type end as Type from information_schema.columns where table_name = '" + self.table_list[user_input] + "'"

		query_results = self.execute_query(query)
		self.view.run_command("display_output_pane", {"output": query_results, "title": "Schema for " + self.table_list[user_input]})

class display_output_paneCommand(SublimeSQLBase):
	def runCommand(self, edit, output, title):
		self.display_output(edit, output, title)