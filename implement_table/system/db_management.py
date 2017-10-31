import os

import ujson
from django.conf import settings
from mongoengine.connection import get_db
from pydash.strings import kebab_case
from implement_table. table.models import Table, TableColumns, TableClasses, TableConfig
from implement_table.shared.config.models import BillingConfig

db = get_db()
counters_collection = db["mongoengine.counters"]

json_path = os.path.join(settings.PARENT_FOLDER, "others", "json")


def reset_collection(collection):
    counters_collection.remove({"_id": collection + ".id"})
    db[collection].drop()


def init_general_config(path=json_path):
    with open(os.path.join(path, "billing-config.json"), encoding='utf-8') as data_file:
        data = ujson.load(data_file)

    for item in data:
        BillingConfig(**item).save()


def insert_tables_config(name, path=json_path):
    with open(os.path.join(path, '{}-columns.json'.format(kebab_case(name))), encoding='utf-8') as data_file:
        data = ujson.load(data_file)

    table = Table(columns=list(), classes=list())

    columns = data.get('columns', [])
    classes = data.get('classes', [])

    for item in columns:
        config = TableColumns(**item)
        table.columns.append(config)

    for item in classes:
        config = TableClasses(**item)
        table.classes.append(config)

        table.filtered_by_owner = data.get('filtered_by_owner', False)

    table_config = TableConfig.get_by_key(name, create=True)
    table_config.value = table

    table_config.save()