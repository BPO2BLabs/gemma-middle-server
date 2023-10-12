class Transcript():

  def __init__ (self, filename, fileId, agent, transcript, correction, transcriptText, filesize) -> None:
    self.filename = filename
    self.fileId = fileId
    self.agent = agent
    self.transcript = transcript
    self.correction = correction
    self.transcriptText = transcriptText
    self.filesize = filesize
