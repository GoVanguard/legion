import asyncio, aioredis, aiohttp, aiomonitor
from six.moves.urllib.parse import quote
from datetime import datetime
import hashlib, json
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from utilities.stenoLogging import *
import configparser
from utilities import DictToObject, DictObject
from sanic import Sanic, response
from sanic.views import HTTPMethodView
from sanic.response import text
from sanic_swagger import doc, openapi_blueprint, swagger_blueprint

app = Sanic(__name__)
app.blueprint(openapi_blueprint)
app.blueprint(swagger_blueprint)

config = configparser.ConfigParser()
config.read('./azureCveQuery.conf')

redisHost = str(config.get('redis', 'host'))
redisPort = int(config.get('redis', 'port'))
redisCacheTtl = int(config.get('redis', 'cacheTtl'))
bindHost = str(config.get('general', 'host'))
cliPort = int(config.get('cli', 'port'))
apiServerPort = int(config.get('api', 'port'))
azureMlsWebServiceUrl = str(config.get('azure', 'webServiceUrl'))
azureMlsWebServiceKey = str(config.get('azure', 'webServiceKey'))
serviceCycleTime = int(config.get('azureCveQuery', 'serviceCycleTime'))
metricLimit = int(config.get('metrics', 'metricLimit'))
metricAverageLimit = int(config.get('metrics', 'averageLimit'))
logFile = str(config.get('logging', 'logFilename'))
debug = bool(config.get('general', 'debug'))
heartbeatInterval = int(config.get('general', 'heartbeatInterval'))

log = get_logger('azureCveQueryLogger', path=logFile)
log.setLevel(logging.INFO)

azureMlsQuery = {
    'since': '',
    'until': '',
    'date_range': '',
    'statuses[]': ['triggered'],
    'incident_key': '',
    'service_ids[]': [],
    'team_ids[]': [],
    'user_ids[]': [],
    'urgencies[]': [],
    'time_zone': 'UTC',
    'sort_by[]': [],
    'include[]': []
}

azureMlsNote = {
    'note': {
        'content': ''
    }
}

azureMlsHeaders = {'Accept': 'application/vnd.json;version=2',
           'Authorization': 'Token token={0}'.format(azureMlsWebServiceKey)}

metrics = {}

from functools import wraps
from time import time

def timing(f):
    @wraps(f)
    async def wrap(*args, **kw):
        ts = time()
        result = await f(*args, **kw)
        te = time()
        tr = te-ts
        log.debug('Function:%r args:[%r, %r] took: %2.4f sec' % (f.__name__, args, kw, tr))
        try:
             testGet = metrics[f.__name__]
        except:
             metrics[f.__name__] = {}
             metrics[f.__name__]['count'] = 0
             metrics[f.__name__]['execution_time'] = []
        metrics[f.__name__]['execution_time'].append(tr)
        metricLen = len(metrics[f.__name__]['execution_time'])
        if metricLen > metricLimit:
            del metrics[f.__name__]['execution_time'][0]
        else:
            metrics[f.__name__]['count'] = metrics[f.__name__]['count'] + 1
        if metricLen > metricAverageLimit:
            metrics[f.__name__]['avg_execution_time'] = sum(metrics[f.__name__]['execution_time']) / metrics[f.__name__]['count']
        return result
    return wrap

# Drop heartbeat
@timing
async def heartbeat(pub):
    timeNow = str(datetime.now())
    log.info('Tick tock! The time is: {timeNow}'.format(timeNow=timeNow))
    await publishToRedis(pub, 'heartbeats', {'azureCveQuery':timeNow})

# Enque aquisition of PagerDuty Incidents and publiush them
@timing
@doc.summary("Enque aquisition of PagerDuty Incidents and publiush them")
async def checkPagerDutyIncidents(pub):
    async with aiohttp.ClientSession(loop=loop) as session:
        data = await fetchFromPagerDuty(azureMlsServiceUrl, azureMlsHeaders, azureMlsQuery, session)
        if 'incidents' in data:
            incidentDictionaries = DictToObject(data['incidents'])
            for incidentDictionary in incidentDictionaries.outputStructure:
                log.info("Incident: {id}".format(id=str(incidentDictionary.id)))
                fields = {}
                fields['id'] = incidentDictionary.id
                fields['description'] = incidentDictionary.description
                fields['service'] = incidentDictionary.impacted_services[0].id
                fields['status'] = incidentDictionary.status
                if len(incidentDictionary.teams) > 0:
                    fields['teams'] = incidentDictionary.teams[0].id
                fields['url'] = incidentDictionary.html_url
                await publishToRedis(pub, 'incoming-incidents', json.dumps(fields))

# Create Note on Incident
@timing
@doc.summary("Create Note on Incident")
async def postNoteToPagerDutyNote(incId, Note):
    async with aiohttp.ClientSession(loop=loop) as session:
        url = "{serviceUrl}/{incId}/notes".format(serviceUrl=azureMlsServiceUrl, incId=incId)
        data = azureMlsNote
        await postToPagerDuty(url, azureMlsHeaders, data, session)

# Receive from Redis
@timing
async def redisMessageReceived(channelObj, pub):
    while (await channelObj.wait_message()):
        channelName = channelObj.name.decode()
        log.info("Message recieved on {channelName}".format(channelName=channelName))
        if channelName == 'outgoing-incidents':
            messageJson = await channelObj.get_json()
            try:
                messageDict = eval(messageJson)
            except:
                messageDict = messageJson
            incId = messageDict['inc_id']
            incMessage = messageDict['catagorical_noise']
            log.info("INC {0} recieved on outgoing-incidents.".format(incId))
            ## postBackToPagerDuty(incId, incMessage)
            await deleteFromRedis(pub, messageJson)

# Execute post to create note on PagerDuty Incident
@timing
async def postToPagerDuty(url: str, headers: dict, data: dict, session):
    log.debug('Post {url}'.format(url=url))
    data = quote(str(data))
    async with session.request('POST', url, headers=headers, data=data) as resp:
        data = await resp.json()
        return data

# Execute aquisition of PagerDuty Incidents
@timing
async def fetchFromPagerDuty(url: str, headers: dict, params: dict, session) -> dict:
    log.debug('Query {url}'.format(url=url))
    params = quote(str(params))
    async with session.request('GET', url, headers=headers, params=params) as resp:
        data = await resp.json()
        return data

# Delete from Redis and remove cache items
@timing
async def deleteFromRedis(pub, message):
    try:
        await setOrUpdateRedisCache(pub, message, delete = True)
        pub.delete(str(message))
    except:
        raise "Error frlrting from Redis."

# Publish to Redis Channel
@timing
async def publishToRedis(pub, channel: str, message):
    try:
        cache = await setOrUpdateRedisCache(pub, message)
        if not cache:
            log.info("Published to {channel}.".format(channel=channel))
            await pub.publish_json(channel, message)
        else:
            log.info("Already exists, Not published to {channel}.".format(channel=channel))
    except:
        raise "Publish failure to {channel}.".format(channel=channel)

# Check Redis Cache
@timing
async def setOrUpdateRedisCache(pub, data: dict, delete = False) -> bool:
    try:
        hash = hashlib.sha256(json.dumps(data).encode()).hexdigest()
        compoundName = "cache:" + hash
        cacheValue = await pub.exists(compoundName)
        if not cacheValue and not delete:
            await pub.set(compoundName, "True")
            await pub.expire(compoundName, redisCacheTtl)
            return False
        if delete:
            await pub.delete(compoundName)
        return True
    except:
        raise "Issue setting cache in Redis for item: {compoundName}.".format(compoundName)


@app.route("/")
@timing
async def getRoot(request):
    return await getMetrics(request)

@app.route("/metrics")
@timing
async def getMetrics(request):
    return response.json(metrics)

@app.route("/config")
@timing
async def getConfig(request):
    return response.json(config._sections)

# Primary event loop
async def mainloop(loop):

    # Setup Redis
    pub = await aioredis.create_redis('redis://{redisHost}:{redisPort}'.format(redisHost=redisHost, redisPort=redisPort))
    sub = await aioredis.create_redis('redis://{redisHost}:{redisPort}'.format(redisHost=redisHost, redisPort=redisPort))
    outgoingIncidentsSub = await sub.subscribe('outgoing-incidents')
    outgoingIncidentsChannel = outgoingIncidentsSub[0]
    incomingIncidentsSub = await sub.subscribe('incoming-incidents')
    incomingIncidentsChannel = incomingIncidentsSub[0]

    # Setup Scheduler
    scheduler = AsyncIOScheduler()
    scheduler.add_job(heartbeat, args=(pub,), trigger='interval', seconds=heartbeatInterval)
    scheduler.add_job(checkPagerDutyIncidents, args=(pub,), trigger='interval', seconds=serviceCycleTime)
    scheduler.start()

    # Monitor Outgoing Channel
    await asyncio.ensure_future(redisMessageReceived(outgoingIncidentsChannel, pub))

    # Shutdown
    sub.close()
    pub.close()


if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()
        webSvr = app.create_server(host=bindHost, port=apiServerPort)

        with aiomonitor.start_monitor(loop=loop, host=bindHost, port=cliPort, console_enabled=False):
            webSvrTask = asyncio.ensure_future(webSvr)
            loop.run_until_complete(mainloop(loop=loop))
            loop.close()
    except (KeyboardInterrupt, SystemExit):
        pass
