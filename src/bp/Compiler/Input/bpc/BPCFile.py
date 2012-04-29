####################################################################
# Header
####################################################################
# Syntax:   Blitzprog Code
# Author:   Eduard Urbach

####################################################################
# License
####################################################################
# (C) 2008  Eduard Urbach
# 
# This file is part of Blitzprog.
# 
# Blitzprog is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Blitzprog is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Blitzprog.  If not, see <http://www.gnu.org/licenses/>.

####################################################################
# Imports
####################################################################
from bp.Compiler.Utils import *
from bp.Compiler.Config import *
from bp.Compiler.Input.bpc.BPCUtils import *
import codecs

####################################################################
# Variables
####################################################################
# XML tags which can follow another tag
# Used by BPC -> XML compiler

# 2 levels
blocks = {
	"if-block" : ["else-if", "else"],
	"try-block" : ["catch"]
}

# 1 level
simpleBlocks = {
	"class" : [],
	"function" : [],
	"while" : [],
	"for" : [],
	"in" : [],
	"switch" : [],
	"case" : [],
	"target" : [],
	"extern" : [],
	"compiler-flags" : [],
	"template" : [],
	"get" : [],
	"set" : [],
	"cast-definition" : [],
	"getter" : [],
	"setter" : [],
	"operators" : [],
	"operator" : [],
	"casts" : []
}

####################################################################
# Classes
####################################################################
class BPCFile(ScopeController):
	
	def __init__(self, compiler, fileIn, isMainFile):
		ScopeController.__init__(self)
		
		self.compiler = compiler
		self.file = fileIn
		self.dir = os.path.dirname(fileIn) + "/"
		self.stringCount = 0
		self.importedFiles = []
		self.nextLineIndented = False
		self.savedNextNode = 0
		self.inClass = 0
		self.inSwitch = 0
		self.inCase = 0
		self.inExtern = 0
		self.inTemplate = 0
		self.inGetter = 0
		self.inSetter = 0
		self.inCasts = 0
		self.inOperators = 0
		self.inRequire = 0
		self.inEnsure = 0
		self.inMaybe = 0
		self.inTest = 0
		self.inCompilerFlags = 0
		self.parser = self.compiler.parser
		self.isMainFile = isMainFile
		self.doc = parseString("<module><header><title/><dependencies/><strings/></header><code></code></module>".encode( "utf-8" ))
		self.root = self.doc.documentElement
		self.header = getElementByTagName(self.root, "header")
		self.dependencies = getElementByTagName(self.header, "dependencies")
		self.strings = getElementByTagName(self.header, "strings")
		self.lastLine = ""
		self.lastLineCount = 0 
		
		# This is used for xml tags which have a "code" node
		self.nextNode = 0
		
		# parseExpr
		self.parseExpr = self.parser.buildXMLTree
		
	def getRoot(self):
		return self.root
		
	def getFilePath(self):
		return self.file
	
	def getFileName(self):
		return self.file[len(self.dir):]
	
	def getDirectory(self):
		return self.dir
		
	def getLastLine(self):
		return self.lastLine
	
	def getLastLineCount(self):
		return self.lastLineCount
		
	def compile(self, codeText = ""):
		#print("Compiling: " + self.file)
		
		currentLine = None
		self.currentNode = getElementByTagName(self.root, "code")
		self.lastNode = None
		
		# Read
		if not codeText:
			with codecs.open(self.file, "r", "utf-8") as inStream:
				codeText = inStream.read()
			
			# TODO: Remove all BOMs
			if len(codeText) and codeText[0] == '\ufeff': #codecs.BOM_UTF8:
				codeText = codeText[1:]
		
		self.lastLineCount = -1	# -1 because of "import bp.Core"
		lines = ["import bp.Core"] + codeText.split('\n') + [""]
		
		#if "unicode" in self.file:
		#	print(lines)
		tabCount = 0
		prevTabCount = 0
		
		# Go through every line -> build the structure
		for lineIndex in range(0, len(lines)):
			line = lines[lineIndex].rstrip()
			tabCount = self.countTabs(line)
			line = line.lstrip()
			
			# Set last line for exception handling
			self.lastLine = line
			self.lastLineCount += 1
			
			# Remove strings, comments and check brackets
			line = self.prepareLine(line)
			
			if line == "":
				continue
			
			# TODO: Enable all unicode characters
			line = line.replace("π", "pi")
			
			self.nextLineIndented = False
			if lineIndex < len(lines) - 1:
				tabCountNextLine = self.countTabs(lines[lineIndex + 1])
				if tabCountNextLine == tabCount + 1: #and lines[lineIndex + 1].strip() != "":
					self.nextLineIndented = True
			
			# Remove whitespaces
			line = line.replace("\t", " ")
			while line.find("  ") != -1:
				line = line.replace("  ", " ")
			
			if tabCount < prevTabCount:
				savedCurrentNode = self.currentNode
				self.tabBack(currentLine, prevTabCount, tabCount, True)
				self.currentNode = savedCurrentNode
			
			currentLine = self.processLine(line)
			
			# Save the connection for debugging purposes
			nodeToOriginalLine[currentLine] = line
			
			# Tab level hierarchy
			if tabCount > prevTabCount:
				if self.savedNextNode:
					self.currentNode = self.savedNextNode
					self.savedNextNode = 0
				else:
					self.currentNode = self.lastNode
			elif tabCount < prevTabCount:
				self.tabBack(currentLine, prevTabCount, tabCount, False)
			
			self.savedNextNode = self.nextNode
			
			if currentLine:
				if not isTextNode(currentLine) and currentLine.tagName == "assign":
					variableNode = currentLine.childNodes[0].childNodes[0]
					if isTextNode(variableNode):
						variable = variableNode.nodeValue
						if not variable in self.getCurrentScope().variables:
							self.getCurrentScope().variables[variable] = currentLine
				
				self.lastNode = self.currentNode.appendChild(currentLine)
			prevTabCount = tabCount
		
	def tabBack(self, currentLine, prevTabCount, tabCount, countIns):
		atTab = prevTabCount
		while atTab > tabCount:
			if countIns:
				nodeName = self.currentNode.tagName
				if nodeName == "switch":
					self.inSwitch -= 1
				elif nodeName == "class":
					self.inClass -= 1
				elif nodeName == "extern":
					self.inExtern -= 1
				elif nodeName == "template":
					self.inTemplate -= 1
				elif nodeName == "get":
					self.inGetter -= 1
				elif nodeName == "set":
					self.inSetter -= 1
				elif nodeName == "casts":
					self.inCasts = 0
				elif nodeName == "operators":
					self.inOperators -= 1
				elif nodeName == "require":
					self.inRequire -= 1
				elif nodeName == "ensure":
					self.inEnsure -= 1
				elif nodeName == "maybe":
					self.inMaybe -= 1
				elif nodeName == "test":
					self.inTest -= 1
				elif nodeName == "compiler-flags":
					self.inCompilerFlags -= 1
			
			self.currentNode = self.currentNode.parentNode
			
			if countIns:
				if self.currentNode.tagName == "case":
					self.inCase -= 1
			
			# XML elements with "code" tags need special treatment
			if self.currentNode.parentNode.tagName in blocks:
				tagsAllowed = blocks[self.currentNode.parentNode.tagName]
				if atTab != tabCount + 1 or isTextNode(currentLine) or (not currentLine.tagName in tagsAllowed):
					self.currentNode = self.currentNode.parentNode.parentNode
				else:
					self.currentNode = self.currentNode.parentNode
			elif self.currentNode.tagName in simpleBlocks:
				if len(self.currentNode.childNodes) == 0:
					raise CompilerException("A '%s' block needs at least one operation (e.g. '...')" % (nodeName))
				tagsAllowed = simpleBlocks[self.currentNode.tagName]
				if atTab != tabCount + 1 or isTextNode(currentLine) or (not currentLine.tagName in tagsAllowed):
					self.currentNode = self.currentNode.parentNode
			atTab -= 1
		
	def processLine(self, line):
		if startsWith(line, "import"):
			return self.handleImport(line)
		elif startsWith(line, "while"):
			return self.handleWhile(line)
		elif startsWith(line, "for"):
			return self.handleFor(line)
		elif startsWith(line, "try"):
			return self.handleTry(line)
		elif startsWith(line, "catch"):
			return self.handleCatch(line)
		elif startsWith(line, "if"):
			return self.handleIf(line)
		elif startsWith(line, "elif"):
			return self.handleElif(line)
		elif startsWith(line, "else"):
			return self.handleElse(line)
		elif startsWith(line, "throw"):
			return self.handleThrow(line)
		elif startsWith(line, "return"):
			return self.handleReturn(line)
		elif startsWith(line, "const"):
			return self.handleConst(line)
		elif startsWith(line, "break"):
			return self.handleBreak(line)
		elif startsWith(line, "continue"):
			return self.handleContinue(line)
		elif startsWith(line, "private"):
			return self.handlePrivate(line)
		elif startsWith(line, "in"):
			return self.handleIn(line)
		elif startsWith(line, "switch"):
			return self.handleSwitch(line)
		elif startsWith(line, "extern"):
			return self.handleExtern(line)
		elif startsWith(line, "include"):
			return self.handleInclude(line)
		elif startsWith(line, "template"):
			return self.handleTemplate(line)
		elif startsWith(line, "get"):
			return self.handleGet(line)
		elif startsWith(line, "set"):
			return self.handleSet(line)
		elif startsWith(line, "to"):
			return self.handleCasts(line)
		elif startsWith(line, "operator"):
			return self.handleOperatorBlock(line)
		elif startsWith(line, "require"):
			return self.handleRequire(line)
		elif startsWith(line, "ensure"):
			return self.handleEnsure(line)
		elif startsWith(line, "maybe"):
			return self.handleMaybe(line)
		elif startsWith(line, "test"):
			return self.handleTest(line)
		elif startsWith(line, "target"):
			return self.handleTarget(line)
		elif startsWith(line, "compilerflags"):
			return self.handleCompilerFlags(line)
		elif line == "...":
			return self.handleNOOP(line)
		elif self.nextLineIndented:
			if self.inSwitch > 0:
				return self.handleCase(line)
			elif self.inOperators or self.inCasts or line[0].islower():
				return self.handleFunction(line)
			else:
				return self.handleClass(line)
		else:
			if self.inTemplate:
				return self.handleTemplateParameter(line)
			elif self.inCompilerFlags:
				return self.handleCompilerFlag(line)
			
			if self.inExtern and not self.inClass:
				return self.handleExternLine(line)
			
			line = self.addBrackets(line)
			line = self.addGenerics(line)
			node = self.parseExpr(line)
			
			return node
	
	def addGenerics(self, line):
		bracketCounter = 0
		char = ''
		startGeneric = -1
		#oldLine = line
		
		for i in range(len(line)):
			char = line[i]
			
			if char == '<':
				bracketCounter += 1
				if bracketCounter == 1:
					startGeneric = i
			elif char == '>':
				bracketCounter -= 1
				
				# End of template parameter
				if bracketCounter == 0:
					templateParam = self.addGenerics(line[startGeneric+1:i])
					line = line[:startGeneric] + "§(" + templateParam + ")" + line[i+1:]
					
			elif bracketCounter > 0 and char != '~' and char != ',' and (not char.isspace()) and ((not isVarChar(char)) or char == '.'):
				break
		
#		if oldLine != line:
#			print("Start: " + oldLine)
#			print("End: " + line)
		return line
		
	def addBrackets(self, line):
		bracketCounter = 0
		char = ''
		
		for i in range(len(line)):
			char = line[i]
			
			if char == '(' or char == '[':
				bracketCounter += 1
			elif char == ')' or char == ']':
				bracketCounter -= 1
			elif (not isVarChar(char)) and char != '.' and bracketCounter == 0:
				break
		
		identifier = line[:i]
		if char == '.':
			if identifier:
				raise CompilerException("You need to specify a function or property of '%s'" % (identifier))
			else:
				raise CompilerException("Invalid instruction: '%s'" % line)
		
		rightOperand = line[i+1:]
		if isDefinitelyOperatorSign(char):
			if (not identifier or not rightOperand):
				print(line, "|", identifier, "|", rightOperand)
				raise CompilerException("Invalid instruction: '%s'" % line)
		
		if i < len(line) - 1:
			nextChar = rightOperand[0]
			
			if char.isspace() and (isVarChar(nextChar) or nextChar == '('):
				line = "%s(%s)" % (line[:i], rightOperand)
		elif line[-1] != ')':
			line += "()"
		
		return line
		
	def handleCase(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("case", line)
		
		node = self.doc.createElement("case")
		values = self.compiler.parser.getParametersNode(self.parseExpr(line))
		code = self.doc.createElement("code")
		
		values.tagName = "values"
		for value in values.childNodes:
			value.tagName = "value"
	
		node.appendChild(values)
		node.appendChild(code)
		
		self.inCase += 1
		self.nextNode = code
		return node
		
	def handleSwitch(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("switch", line)
		
		node = self.doc.createElement("switch")
		value = self.doc.createElement("value")
		value.appendChild(self.parseExpr(line[len("switch")+1:]))
		
		node.appendChild(value)
		
		self.inSwitch += 1
		self.nextNode = node
		return node
		
	def handleCasts(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("casts", line)
		
		node = self.doc.createElement("casts")
		
		self.inCasts = 1
		self.nextNode = node
		return node
		
	def handleGet(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("get", line)
		
		node = self.doc.createElement("get")
		
		self.inGetter = 1
		self.nextNode = node
		return node
	
	def handleSet(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("set", line)
		
		node = self.doc.createElement("set")
		
		self.inSetter = 1
		self.nextNode = node
		return node
	
	def handleOperatorBlock(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("operator", line)
		
		node = self.doc.createElement("operators")
		
		self.inOperators = 1
		self.nextNode = node
		return node
		
	def handleTemplate(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("template", line)
		
		node = self.doc.createElement("template")
		
		self.inTemplate = 1
		self.nextNode = node
		return node
		
	def handleTemplateParameter(self, line):
		paramNode = self.parseExpr(line)
		
		if isElemNode(paramNode) and paramNode.tagName == "assign":
			paramNode.tagName = "parameter"
			paramNode.childNodes[0].tagName = "name"
			paramNode.childNodes[1].tagName = "default-value"
			return paramNode
		else:
			node = self.doc.createElement("parameter")
			node.appendChild(paramNode)
			return node
		
	def handleIn(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("in", line)
		
		node = self.doc.createElement("in")
		expr = self.doc.createElement("expression")
		code = self.doc.createElement("code")
		expr.appendChild(self.parseExpr(line[len("in")+1:]))
		
		node.appendChild(expr)
		node.appendChild(code)
		
		self.nextNode = code
		return node
		
	def handleFor(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("for", line)
		
		node = self.doc.createElement("for")
		
		line += " "
		pos = line.find(" to ")
		posUntil = line.find(" until ")
		if pos == -1 and posUntil == -1:
			pos = line.find(" in ")
			if pos == -1:
				raise CompilerException("Missing iterator definition in 'for' expression")
			else:
				node.tagName = "foreach"
				# TODO: Foreach
				#return None
				raise CompilerException("'for' as 'foreach' not implemented yet")
		else:
			toUsed = True
			if pos == -1:
				pos = posUntil
				toUsed = False
			
			initCode = line[len("for")+1:pos]
			if initCode.find('=') == -1:
				# TODO: Allow nameless iterators
				raise CompilerException("Missing iterator assignment: %s" % (initCode))
			initExpr = self.parseExpr(initCode)
			
			#if not toParam:
			#	keyword = ["until", "to"][toUsed]
			#	raise CompilerException("Missing expression after '%s'" % (keyword))
			
			if toUsed:
				toParam = line[pos+len(" to "):]
				toExpr = self.parseExpr(toParam)
			else:
				toParam = line[pos+len(" until "):]
				toExpr = self.parseExpr(toParam)
			
			iterNode = self.doc.createElement("iterator")
			iterNode.appendChild(initExpr.childNodes[0].childNodes[0])
			
			fromNode = self.doc.createElement("from")
			fromNode.appendChild(initExpr.childNodes[1].childNodes[0])
			
			if toUsed:
				toNode = self.doc.createElement("to")
			else:
				toNode = self.doc.createElement("until")
			toNode.appendChild(toExpr)
			
			codeNode = self.doc.createElement("code")
			
			node.appendChild(iterNode)
			node.appendChild(fromNode)
			node.appendChild(toNode)
			node.appendChild(codeNode)
			
			self.nextNode = codeNode
		
		return node
		
	def handlePrivate(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("private", line)
		
		node = self.doc.createElement("private")
		self.nextNode = node
		return node
		
	def handleRequire(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("require", line)
		
		node = self.doc.createElement("require")
		self.inRequire += 1
		
		self.nextNode = node
		return node
	
	def handleEnsure(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("ensure", line)
		
		node = self.doc.createElement("ensure")
		self.inEnsure += 1
		
		self.nextNode = node
		return node
	
	def handleMaybe(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("maybe", line)
		
		node = self.doc.createElement("maybe")
		self.inMaybe += 1
		
		self.nextNode = node
		return node
	
	def handleTest(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("test", line)
		
		node = self.doc.createElement("test")
		self.inTest += 1
		
		self.nextNode = node
		return node
		
	def handleNOOP(self, line):
		return self.doc.createElement("noop")
		
	def handleWhile(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("while", line)
		
		node = self.doc.createElement("while")
		condition = self.doc.createElement("condition")
		code = self.doc.createElement("code")
		condition.appendChild(self.parseExpr(line[len("while")+1:]))
		
		node.appendChild(condition)
		node.appendChild(code)
		
		self.nextNode = code
		return node
	
	def handleTarget(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("target", line)
		
		node = self.doc.createElement("target")
		condition = self.doc.createElement("name")
		code = self.doc.createElement("code")
		condition.appendChild(self.doc.createTextNode(line[len("target")+1:]))
		
		node.appendChild(condition)
		node.appendChild(code)
		
		self.nextNode = code
		return node
	
	def handleCompilerFlags(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("compilerflags", line)
		
		node = self.doc.createElement("compiler-flags")
		self.inCompilerFlags += 1
		
		self.nextNode = node
		return node
	
	def handleCompilerFlag(self, line):
		node = self.doc.createElement("compiler-flag")
		node.appendChild(self.doc.createTextNode(line))
		
		return node
	
	def handleExtern(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("extern", line)
		
		node = self.doc.createElement("extern")
		self.inExtern += 1
		
		self.nextNode = node
		return node
	
	def handleExternLine(self, line):
		node = self.doc.createElement("extern-function")
		name = self.doc.createElement("name")
		node.appendChild(name)
		
		pos = line.find(":")
		
		if pos == -1:
			name.appendChild(self.doc.createTextNode(line))
		else:
			funcName = line[:pos].rstrip()
			funcType = line[pos+1:].lstrip()
			
			type = self.doc.createElement("type")
			node.appendChild(type)
			
			name.appendChild(self.doc.createTextNode(funcName))
			type.appendChild(self.doc.createTextNode(funcType))
		
		return node
		
	def handleContinue(self, line):
		return self.doc.createElement("continue")
		
	def handleBreak(self, line):
		return self.doc.createElement("break")
		
	def handleConst(self, line):
		node = self.doc.createElement("const")
		param = self.parseExpr(line[len("const")+1:])
		if param.hasChildNodes() and param.tagName == "assign":
			node.appendChild(param)
		else:
			raise CompilerException("#const keyword expects a variable assignment")
		return node
		
	def handleReturn(self, line):
		node = self.doc.createElement("return")
		param = self.parseExpr(line[len("return")+1:])
		if param.nodeValue or param.hasChildNodes():
			node.appendChild(param)
		return node
	
	def handleThrow(self, line):
		node = self.doc.createElement("throw")
		param = self.parseExpr(line[len("throw")+1:])
		if param.nodeValue or param.hasChildNodes():
			node.appendChild(param)
		else:
			raise CompilerException("#throw keyword expects a parameter (e.g. an exception object)")
		return node
	
	def handleInclude(self, line):
		node = self.doc.createElement("include")
		param = self.doc.createTextNode(line[len("include")+1:])
		if param.nodeValue:
			node.appendChild(param)
		else:
			raise CompilerException("#include keyword expects a file name")
		return node
		
	def handleFunction(self, line):
		# Check for function
		funcName = ""
		pos = 0
		lineLen = len(line)
		while pos < lineLen and isVarChar(line[pos]):
			pos += 1
		
		if pos is len(line):
			funcName = line
		elif line[pos] == ' ':
			funcName = line[:pos]
		else:
			whiteSpace = line.find(' ')
			if whiteSpace is not -1:
				funcName = line[:whiteSpace]
			else:
				funcName = line
			
			if (not self.inOperators) and (not self.inCasts):
				raise CompilerException("Invalid function name '" + funcName + "' for function definition")
		
		#print(" belongs to " + self.currentNode.tagName)
		nameNode = self.doc.createElement("name")
		
		if self.inSetter:
			node = self.doc.createElement("setter")
		elif self.inGetter:
			node = self.doc.createElement("getter")
		elif self.inOperators:
			node = self.doc.createElement("operator")
		elif self.inCasts:
			node = self.doc.createElement("cast-definition")
			nameNode.tagName = "to"
			nameNode.appendChild(self.parseExpr(self.addGenerics(funcName)))
		else:
			node = self.doc.createElement("function")
		
		if not self.inCasts:
			nameNode.appendChild(self.doc.createTextNode(funcName))
		
		expr = self.addGenerics(line[len(funcName)+1:])
		if expr:
			params = self.parseExpr(expr)
			paramsNode = self.parser.getParametersNode(params)
			node.appendChild(paramsNode)
		
		codeNode = self.doc.createElement("code")
		
		node.appendChild(nameNode)
		node.appendChild(codeNode)
		
		#self.inFunction = True
		self.nextNode = codeNode
		return node
		
	def handleClass(self, line):
		self.inClass += 1
		
		className = line
		
		node = self.doc.createElement("class")
		
		nameNode = self.doc.createElement("name")
		nameNode.appendChild(self.doc.createTextNode(className))
		#publicNode = self.doc.createElement("public")
		#privateNode = self.doc.createElement("private")
		code = self.doc.createElement("code")
		
		node.appendChild(nameNode)
		#node.appendChild(publicNode)
		#node.appendChild(privateNode)
		node.appendChild(code)
		
		self.nextNode = code
		return node
		
	def handleTry(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("try", line)
		
		node = self.doc.createElement("try-block")
		
		tryNode = self.doc.createElement("try")
		code = self.doc.createElement("code")
		
		tryNode.appendChild(code)
		
		node.appendChild(tryNode)
		self.nextNode = code
		return node
	
	def handleCatch(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("catch", line)
		
		node = self.doc.createElement("catch")
		exceptionType = self.doc.createElement("variable")
		code = self.doc.createElement("code")
		
		varExpr = line[len("catch")+1:]
		if varExpr:
			varNode = self.parseExpr(varExpr)
			if nodeIsValid(varNode):
				exceptionType.appendChild(varNode)
		
		node.appendChild(exceptionType)
		node.appendChild(code)
		self.nextNode = code
		return node
		
	def raiseBlockException(self, keyword, line):
		raise CompilerException("It is required to have an indented %s block after '%s'" % (keyword, line))
		
	def handleIf(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("if", line)
		
		node = self.doc.createElement("if-block")
		
		ifNode = self.doc.createElement("if")
		condition = self.doc.createElement("condition")
		code = self.doc.createElement("code")
		
		conditionText = line[len("if")+1:]
		if conditionText == "":
			raise CompilerException("You need to specify an if condition")
		
		condition.appendChild(self.parseExpr(conditionText))
		
		ifNode.appendChild(condition)
		ifNode.appendChild(code)
		
		node.appendChild(ifNode)
		
		self.nextNode = code
		return node
	
	def handleElif(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("elif", line)
		
		node = self.doc.createElement("else-if")
		condition = self.doc.createElement("condition")
		code = self.doc.createElement("code")
		
		condition.appendChild(self.parseExpr(line[len("elif")+1:]))
		
		node.appendChild(condition)
		node.appendChild(code)
		
		self.nextNode = code
		return node
		
	def handleElse(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("else", line)
		
		node = self.doc.createElement("else")
		code = self.doc.createElement("code")
		
		node.appendChild(code)
		self.nextNode = code
		return node
		
	def handleImport(self, line):
		if self.nextLineIndented:
			raise CompilerException("import can not be used as a block (yet)")
		
		importedModule = line[len("import"):].strip()
		modulePath = getModulePath(importedModule, self.dir, self.compiler.projectDir, ".bpc")
		
		if modulePath:
			self.importedFiles.append(modulePath)
		elif importedModule == "":
			raise CompilerException("You need to specify which module you want to import")
		else:
			raise CompilerException("Module not found: " + importedModule)
		
		element = self.doc.createElement("import")
		element.appendChild(self.doc.createTextNode(importedModule))
		self.dependencies.appendChild(element)
		
		return None
	
	def countTabs(self, line):
		tabCount = 0
		while tabCount < len(line) and line[tabCount] == '\t':
			tabCount += 1
		
		return tabCount
	
	def prepareLine(self, line):
		i = 0
		roundBracketsBalance = 0 # ()
		curlyBracketsBalance = 0 # {}
		squareBracketsBalance = 0 # []
		#chevronsBalance = 0 # <>
		
		while i < len(line):
			# Remove comments
			if line[i] == '#':
				return line[:i].rstrip()
			# Number of brackets check
			elif line[i] == '(':
				roundBracketsBalance += 1
			elif line[i] == ')':
				roundBracketsBalance -= 1
			elif line[i] == '[':
				squareBracketsBalance += 1
			elif line[i] == ']':
				squareBracketsBalance -= 1
			elif line[i] == '{':
				curlyBracketsBalance += 1
			elif line[i] == '}':
				curlyBracketsBalance -= 1
			#elif line[i] == '<':
			#	chevronsBalance += 1
			#elif line[i] == '>':
			#	chevronsBalance -= 1
			
			# Remove strings
			elif line[i] == '"':
				lineLen = len(line)
				
				h = i + 1
				while h < lineLen and line[h] != '"':
					h += 1
					
				if h == lineLen:
					raise CompilerException("You forgot to close the string: '\"' missing")
				
				if h + 1 < lineLen and mustNotBeNextToExpr(line[h + 1]):
					raise CompilerException("Operator missing: %s ↓ %s" % (line[i:h+1].strip(), line[h+1:].strip()))
				if i > 1 and mustNotBeNextToExpr(line[i - 1]):
					raise CompilerException("Operator missing: %s ↓ %s" % (line[:i].strip(), line[i:h+1].strip()))
				
				# TODO: Add string to string list
				identifier = "bp_string_" + str(self.stringCount) #.zfill(9)
				
				# Create XML node
				stringNode = self.doc.createElement("string")
				stringNode.setAttribute("id", identifier)
				stringNode.appendChild(self.doc.createTextNode(line[i+1:h]))
				self.strings.appendChild(stringNode)
				
				line = line[:i] + identifier + line[h+1:]
				self.stringCount += 1
				i += len(identifier) - 1
			i += 1
		
		# ()
		if roundBracketsBalance > 0:
			raise CompilerException("You forgot to close the round bracket: ')' missing%s" % ([" %d times" % (abs(roundBracketsBalance)), ""][abs(roundBracketsBalance) == 1]))
		elif roundBracketsBalance < 0:
			raise CompilerException("You forgot to open the round bracket: '(' missing%s" % ([" %d times" % (abs(roundBracketsBalance)), ""][abs(roundBracketsBalance) == 1]))
		
		# []
		if squareBracketsBalance > 0:
			raise CompilerException("You forgot to close the square bracket: ']' missing%s" % ([" %d times" % (abs(squareBracketsBalance)), ""][abs(squareBracketsBalance) == 1]))
		elif squareBracketsBalance < 0:
			raise CompilerException("You forgot to open the square bracket: '[' missing%s" % ([" %d times" % (abs(squareBracketsBalance)), ""][abs(squareBracketsBalance) == 1]))
		
		# <>
		#if chevronsBalance > 0:
		#	raise CompilerException("You forgot to close the chevron: '>' missing%s" % ([" %d times" % (chevronsBalance), ""][abs(chevronsBalance) == 1]))
		#elif chevronsBalance < 0:
		#	raise CompilerException("You forgot to open the chevron: '<' missing%s" % ([" %d times" % (chevronsBalance), ""][abs(chevronsBalance) == 1]))
		
		return line