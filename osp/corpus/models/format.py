

import datetime

from osp.common.models.base import WorkerModel
from peewee import *


class Document_Format(WorkerModel):

    created = DateTimeField(default=datetime.datetime.now)
    document = CharField()
    format = CharField()
