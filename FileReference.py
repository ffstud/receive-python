class FileReference:
    def __init__(self, file, outputFile):
        self.file = file
        self.outputFile = outputFile

    def getFile(self):
        return self.file

    def getOutput(self):
        return self.outputFile
