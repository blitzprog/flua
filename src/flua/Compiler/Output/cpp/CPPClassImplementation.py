from flua.Compiler.Output import *
from flua.Compiler.Output.cpp.CPPFunctionImplementation import *

class CPPClassImplementation(BaseClassImplementation):
	
	def __init__(self, classObj, templateValues):
		super().__init__(classObj, templateValues)
		
	def createFunctionImplementation(self, func, paramTypes):
		return CPPFunctionImplementation(self, func, paramTypes)
		
	def getName(self):
		name = self.classObj.name
		if self.templateValues:
			name += "<%s>" % (", ".join(self.templateValues))
		return name
		
	def getTemplateValuesString(self, adjusted = False, clean = False):
		stri = ""
		
		if adjusted:
			if self.templateValues:
				for param in self.templateValues:
					stri += adjustDataTypeCPP(param) + ", "
				
				if clean:
					return ("< " + stri[:-2] + " >").replace(" ", "")
				else:
					return "< " + stri[:-2] + " >"
			else:
				return ""
		else:
			if self.templateValues:
				if clean:
					return "<" + ",".join(self.templateValues) + ">"
				else:
					return "< " + ", ".join(self.templateValues) + " >"
			else:
				return ""
