import json
import inspect
import time
import logging
import traceback
from functools import wraps
import collections
from logging.handlers import RotatingFileHandler
json.encoder.c_make_encoder = None

_SUPPORTED_KWARGS = ['data', 'context', 'id']
_KEY_ORDER = {'time': 0, 'name': 1, 'level': 2, 'data': 3,
              'exception': 4, 'context': 5, 'id': 6}
raiseExceptions = True

def key_func(k):
    return _KEY_ORDER.get(k, 10)

class StenoFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None):
        super(StenoFormatter, self).__init__(fmt, datefmt)

    def formatException(self, ei):
        """
        Format and return the specified exception information as a string.

        This default implementation just uses
        traceback.print_exception()
        """
        exc_type, exc_value, exc_traceback = ei
        traceback_formated = [lines.strip() for lines in traceback.format_tb(exc_traceback)]
        exc_obj = {
            "exception":{
                "type": exc_type.__name__,
                "message": exc_value.message,
                "traceback": traceback_formated,
                "data": {}
            }}
        return exc_obj

    def format(self, record):
        record.message = record.getMessage()
        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)
        json_log = {
            'name': record.message,
            'level': record.levelname,
            'time': self.formatTime(record, self.datefmt),
            'data': {
                'logger_name': record.name,
            },
            'context': {
                'module': record.__dict__.get('module'),
                'filename': record.__dict__.get('filename'),
                'line': record.lineno
            }}
        # Add supported attribute
        for k, val in record.__dict__.items():
            if k in _SUPPORTED_KWARGS:
                if k == 'id':
                    json_log[k] = val
                else:
                    json_log[k].update(val)

        #print record.__dict__
        # Handle Exception
        if record.exc_info:
            exc_obj = self.formatException(record.exc_info)
            json_log.update(exc_obj)

        # Set log output key order
        ordered_json_log = collections.OrderedDict(
            sorted(json_log.items(), key=lambda t: key_func(t[0])))
        jsons_log = json.dumps(ordered_json_log)
        return jsons_log

class StenoLogger(logging.Logger):
    def __init__(self, name, level=logging.NOTSET, raiseExceptions=raiseExceptions):
        super(StenoLogger, self).__init__(name, level)

    def _parse_extra(self, kwargs):
        extra={k: val for k, val in kwargs.items() if k in _SUPPORTED_KWARGS}
        kwargs={k: val for k, val in kwargs.items() if k not in _SUPPORTED_KWARGS}
        kwargs.update({'extra': extra})
        return kwargs

    def debug(self, msg, *args, **kwargs):
        if self.isEnabledFor(logging.DEBUG):
            self._log(logging.DEBUG, msg, args, **self._parse_extra(kwargs))

    def info(self, msg, *args, **kwargs):
        if self.isEnabledFor(logging.INFO):
            self._log(logging.INFO, msg, args, **self._parse_extra(kwargs))

    def warning(self, msg, *args, **kwargs):
        if self.isEnabledFor(logging.WARNING):
            self._log(logging.WARNING, msg, args, **self._parse_extra(kwargs))

    def error(self, msg, *args, **kwargs):
        if self.isEnabledFor(logging.ERROR):
            self._log(logging.ERROR, msg, args, **self._parse_extra(kwargs))

    def critical(self, msg, *args, **kwargs):
        if self.isEnabledFor(logging.CRITICAL):
            self._log(logging.CRITICAL, msg, args, **self._parse_extra(kwargs))

    def log(self, level, msg, *args, **kwargs):
        if not isinstance(level, int):
            if self.raiseExceptions:
                raise TypeError("level must be an integer")
            else:
                return
        if self.isEnabledFor(level):
            self._log(level, msg, args, **self._parse_extra(kwargs))

def get_logger(name, path=None, console=True):
    logging.setLoggerClass(StenoLogger)
    logger = logging.getLogger(name)
    if console == True:
        shdlr = logging.StreamHandler()
        shdlr.setFormatter(StenoFormatter())
        logger.addHandler(shdlr)
    if path:
        fhdlr = RotatingFileHandler(path)
        fhdlr.setFormatter(StenoFormatter())
        logger.addHandler(fhdlr)
    return logger

def extractParams(f, args, kwargs, matchParam):
    """Find the value of a parameter by name, even if it was passed via *args or is a default value.
    """
    if matchParam in kwargs:
        return kwargs[matchParam]
    else:
        #argspec = inspect.getargspec(f)
        argspec = inspect.getfullargspec(f)
        if matchParam in argspec.args:
            pIndex = argspec.args.index(matchParam)
            if len(args) > pIndex:
                return args[pIndex]
            if argspec.defaults != None:
                dIndex = pIndex - len(argspec.args) + len(argspec.defaults)
                if 0 <= defaults_index < len(argspec.defaults):
                    return argspec.defaults[dIndex]
            raise LoggerBadCallerParametersException(
                "Caller didn't provide a required positional parameter '%s' at index %d", matchParam, pIndex)
        else:
            raise LoggerUnknownParamException("Unknown param %s(%r) on %s", type(matchParam), matchParam, f.__name__)

class LoggerUnknownParamException(Exception):
    pass

class LoggerBadCallerParametersException(Exception):
    pass

def logEventDecorator(evt, evtSev='info', evtSevIssue='critical', logger=None, objIdAttr=None, objIdParam=None):
    """Decorator to send events to the event log
    You must pass in the event name, and may pass in some method of
    obtaining an objectid from the decorated function's parameters or
    return value.
    objIdAttr: The name of an attr on the return value, to be
        extracted via getattr().
    objIdParam: A string, specifies the name of the (kw)arg that
        should be the objectid.
    """
    def wrap(f):
        @wraps(f)
        def decorator(*args, **kwargs):
            evtSevDict = {'info':20, 'critical':50}
            timeStart = time.time()
            try:
                value = f(*args, **kwargs)
            except Exception as e:
                exceptionEvt = "There was an exception in  "
                exceptionEvt += f.__name__
                exceptionEvt += str(e)
                logger.log(evtSevDict[evtSevIssue], exceptionEvt)
                raise
            timeEnd = time.time()
            execTime = timeEnd - timeStart
            evtSevObj = evtSevDict[evtSev]
            if objIdAttr != None:
                evtObjIds = getattr(value, objIdAttr)
            elif objIdParam != None:
                evtObjIds = extractParams(f, args, kwargs, objIdParam)
            else:
                evtObjIds = None
            eventToLog = "event: {evt}, input parameter values: {evtObjIds}, " + \
                         "result values: {value}, exec time: {execTime}s".\
                             format(evt=evt, evtObjIds=evtObjIds, value=value, execTime=execTime)
            logger.log(evtSevObj, eventToLog)
            return value
        return decorator
    return wrap

