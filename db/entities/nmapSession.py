from sqlalchemy import String, Column

from db.database import Base


class nmapSessionObj(Base):
    __tablename__ = 'nmapSessionObj'
    filename = Column(String, primary_key=True)
    startTime = Column(String)
    finish_time = Column(String)
    nmapVersion = Column(String)
    scanArgs = Column(String)
    totalHosts = Column(String)
    upHosts = Column(String)
    downHosts = Column(String)

    def __init__(self, filename, *args, **kwargs):
        self.filename = filename
        self.startTime = args[0]
        self.finish_time = args[1]
        self.nmapVersion = kwargs.get('nmapVersion') or 'unknown'
        self.scanArgs = kwargs.get('scanArgs') or ''
        self.totalHosts = kwargs.get('total_host') or '0'
        self.upHosts = kwargs.get('upHosts') or '0'
        self.downHosts = kwargs.get('downHosts') or '0'
