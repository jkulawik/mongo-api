from pymongo import collection


def is_value_unique(_collection: collection, _filter: dict) -> bool:
    return _collection.count_documents(_filter, limit=1) == 0
