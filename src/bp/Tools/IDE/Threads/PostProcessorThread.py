from PyQt4 import QtGui, QtCore, uic
from bp.Compiler import *

class BPPostProcessorThread(QtCore.QThread, Benchmarkable):
	
	def __init__(self, bpIDE):
		super().__init__(bpIDE)
		self.bpIDE = bpIDE
		self.processor = bpIDE.processor
		self.lastException = None
		self.finished.connect(self.bpIDE.postProcessorFinished)
		self.finished.connect(self.bpIDE.msgView.updateViewPostProcessor)
		
	def startWith(self, codeEdit):
		self.codeEdit = codeEdit
		if not self.codeEdit is None:
			self.start()
		
	def run(self):
		try:
			self.startBenchmark("[%s] PostProcessor" % stripDir(self.codeEdit.getFilePath()))
			self.processor.resetDTreesForFile(self.codeEdit.getFilePath())
			self.bpIDE.processorOutFile = self.processor.process(self.codeEdit.root, self.codeEdit.getFilePath())
			#self.bpIDE.processorOutFile = self.processor.processExistingInputFile(self.codeEdit.bpcFile)
			self.endBenchmark()
			self.lastException = None
		except PostProcessorException as e:
			self.lastException = e
