import uuid
from twisted.python import log
from scrapyd.launcher import Launcher as ScrapydLauncher
from scrapyd.interfaces import ISpiderScheduler
from scrapyd.utils import get_spider_list
from scrapyd.config import Config
from apscheduler.schedulers.twisted import TwistedScheduler
from apscheduler.triggers.cron import CronTrigger
from scrapyduler import __version__


def str_to_dict(s):
    return dict(x.split('=', 1) for x in s.split())


def convert_interval(d):
    return {k: int(v) if v.isdigit() else v for k, v in d.items()}


class Launcher(ScrapydLauncher):

    name = 'launcher'

    def __init__(self, config: Config, app):
        super().__init__(config, app)
        self.scrapyd_scheduler = self.app.getComponent(ISpiderScheduler)

        self.schedulers = []
        for section in config.cp.sections():
            if 'scheduler.' in section:
                self.schedulers.append(dict(config.items(section, ())))

    def startService(self):
        super().startService()
        scheduler = TwistedScheduler()
        for item in self.schedulers:
            cron = item.get('cron', None)
            if cron is not None:
                cron = CronTrigger.from_crontab(cron)

            interval = item.get('interval', None)
            if interval is not None:
                interval = convert_interval(str_to_dict(interval))

            if cron is None and interval is None:
                raise ValueError("Required parameter 'cron' or 'interval' not set")
            elif cron is not None and interval is not None:
                raise ValueError("Only one parameter 'cron' or 'interval' must be set")
            elif cron:
                scheduler.add_job(self.schedule_spider, cron, kwargs=item)
            elif interval:
                scheduler.add_job(self.schedule_spider, 'interval', **interval, kwargs=item)
        scheduler.start()
        log.msg(format='Scrapyduler launcher %(version)s started', version=__version__, system='Launcher')

    def schedule_spider(self, **kwargs):
        project = kwargs.get('project')
        spider = kwargs.get('spider')
        version = kwargs.get('_version', '')

        spiders = get_spider_list(project, version=version)
        if spider not in spiders:
            log.msg(format='spider %(spider)r not found', spider=spider, system='Scrapyduler')
            return

        priority = float(kwargs.get('priority', 0))
        settings = kwargs.get('settings', [])
        settings = str_to_dict(settings)
        args = kwargs.get('args', {})
        args = str_to_dict(args)
        args['settings'] = settings
        jobid = kwargs.get('jobid', uuid.uuid1().hex)
        args['_job'] = jobid

        self.scrapyd_scheduler.schedule(project, spider, priority=priority, **args)
