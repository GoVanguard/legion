"""
LEGION (https://govanguard.com)
Copyright (c) 2022 GoVanguard

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public
    License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
    version.

    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
    warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
    details.

    You should have received a copy of the GNU General Public License along with this program.
    If not, see <http://www.gnu.org/licenses/>.

Author(s): Dmitriy Dubson (d.dubson@gmail.com)
"""
import os
import logging
from logging import Logger

cachedAppLogger = None
cachedStartupLogger = None
cachedDbLogger = None

cache_path = os.path.expanduser("~/.cache/legion/log")
log_path = os.path.join(cache_path, 'legion.log')
if not os.path.isfile(log_path):
    if not os.path.isdir(cache_path):
        os.makedirs(cache_path)

def getStartupLogger() -> Logger:
    global cachedStartupLogger
    logger = getOrCreateCachedLogger("legion-startup",
            os.path.expanduser("~/.cache/legion/log/legion-startup.log"), True, cachedStartupLogger)
    cachedStartupLogger = logger
    return logger


def getAppLogger() -> Logger:
    global cachedAppLogger
    logger = getOrCreateCachedLogger("legion",
            os.path.expanduser("~/.cache/legion/log/legion.log"), True, cachedAppLogger)
    cachedAppLogger = logger
    return logger


def getDbLogger() -> Logger:
    global cachedDbLogger
    logger = getOrCreateCachedLogger("legion-db",
            os.path.expanduser("~/.cache/legion/log/legion-db.log"), False, cachedDbLogger)
    cachedDbLogger = logger
    return logger


def getOrCreateCachedLogger(logName: str, logPath: str, console: bool, cachedLogger):
    if cachedLogger:
        return cachedLogger

    from utilities.stenoLogging import get_logger
    log = get_logger(logName, path=logPath, console=console)
    log.setLevel(logging.INFO)
    return log
