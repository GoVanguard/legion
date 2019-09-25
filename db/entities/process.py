from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from db.database import Base


class process(Base):
    __tablename__ = 'process'
    pid = Column(String)
    id = Column(Integer, primary_key = True)
    display = Column(String)
    name = Column(String)
    tabTitle = Column(String)
    hostIp = Column(String)
    port = Column(String)
    protocol = Column(String)
    command = Column(String)
    startTime = Column(String)
    endTime = Column(String)
    estimatedRemaining = Column(Integer)
    elapsed = Column(Integer)
    outputfile = Column(String)
    output = relationship("process_output")
    status = Column(String)
    closed = Column(String)

    def __init__(self, pid, *args):
        self.display = 'True'
        self.pid = pid
        self.name = args[0]
        self.tabTitle = args[1]
        self.hostIp = args[2]
        self.port = args[3]
        self.protocol = args[4]
        self.command = args[5]
        self.startTime = args[6]
        self.endTime = args[7]
        self.outputfile = args[8]
        self.output = args[10]
        self.status = args[9]
        self.closed = 'False'
        self.estimatedRemaining = args[11]
        self.elapsed = args[12]