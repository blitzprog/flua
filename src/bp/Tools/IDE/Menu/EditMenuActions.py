from bp.Tools.IDE.Startup import *
from bp.Compiler import *

class EditMenuActions:
	
	def showPreferences(self):
		self.preferences.setStyleSheet(self.config.dialogStyleSheet)
		self.preferences.exec()
	
	def showRegexSearch(self):
		self.showSearch(regex = True)
	
	def showSearch(self, regex = False):
		self.searchForm, existed = self.getUIFromCache("search")
		
		if not existed:
			self.searchForm.setStyleSheet(self.config.dialogStyleSheet)
			
			flags = self.searchForm.windowFlags()
			flags |= QtCore.Qt.WindowStaysOnTopHint
			#flags |= QtCore.Qt.Popup
			#flags |= QtCore.Qt.FramelessWindowHint
			
			self.searchForm.setWindowFlags(flags)
			
			#self.searchForm.layout().addWidget(self.searchEdit)
		
		#self.searchForm.show()
		
		#self.searchEdit.selectAll()
		if regex:
			self.searchEdit.focusRegex()
		else:
			self.searchEdit.focusNormal()
	
	def undoLastAction(self):
		if self.codeEdit:
			self.codeEdit.undo()
		
	def redoLastAction(self):
		if self.codeEdit:
			self.codeEdit.redo()
	
	# Copy console log
	def copy(self):
		if self.console.log:
			self.console.log.copy()
		elif self.codeEdit:
			self.codeEdit.copy()
		
	# Cut console log
	def cut(self):
		if self.console.log:
			self.console.log.copy() # Don't cut!
		elif self.codeEdit:
			self.codeEdit.cut()
		
	# Paste into console - forbidden, the police will hunt you if you dare.
	def paste(self):
		# Don't do anything
		pass