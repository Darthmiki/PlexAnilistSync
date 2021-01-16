import logging
import coloredlogs
import simplejson as json

from BatchSyncWorker import BatchSyncWorker

LOGGER = logging.getLogger(__name__)

logging.basicConfig(level=20, format="%(levelname) -10s %(asctime)s %(name) -30s %(funcName) " "-35s %(lineno) -5d: %(message)s")
coloredlogs.install(level='DEBUG')

with open("config.json") as f:
    config = json.load(f)


batch_sync_worker = BatchSyncWorker(config)
batch_sync_worker.run_periodic_sync_jobs()
