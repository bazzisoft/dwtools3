from collections.abc import Iterable


def int_or_none(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def listify(param):
    """
    Converts the parameter to a list. If it's an iterable, converts it to a list.
    If it's a string, bytes or object, returns a 1-element listing containing it.
    If it's None, returns an empty list.
    """
    if param is None:
        return []
    elif isinstance(param, Iterable) and not isinstance(param, (str, bytes)):
        return list(param)
    else:
        return [param]


def extract_object_id(model_cls, object_or_id, allow_none=False):
    if object_or_id is None and allow_none:
        return None
    elif isinstance(object_or_id, model_cls):
        return object_or_id.id

    try:
        return int(object_or_id)
    except (TypeError, ValueError):
        assert False, '{} is not a numeric ID or {} instance'.format(object_or_id, model_cls.__class__.__name__)


def extract_object(model_cls, object_or_id, allow_none=False, queryset=None):
    """
    Returns a model instance given the instance itself or its ID.

    If ``queryset`` is provided, it is used to retrieve the object.

    :raise ObjectDoesNotExist: if ID is given but doesn't exist.
    """
    if object_or_id is None and allow_none:
        return None
    elif isinstance(object_or_id, model_cls):
        return object_or_id

    try:
        id = int(object_or_id)
    except (TypeError, ValueError):
        assert False, '{} is not a numeric ID or {} instance'.format(object_or_id, model_cls.__class__.__name__)

    if queryset is not None:
        return queryset.get(pk=id)
    else:
        return model_cls.objects.get(pk=id)


def chunk_list(lst, n):
    """
    Split a list into n-sized chunks
    """
    l = list(lst)
    return [l[i:i + n] for i in range(0, len(l), n)]


def chunk_list_into_rows_and_cols(lst, num_rows, num_cols):
    """
    Split a list into ``num_rows * num_cols`` sized chunks, where each
    chunk is a list of ``num_rows`` entries containing ``num_cols`` values.
    """
    return chunk_list(chunk_list(lst, num_cols), num_rows)


def interleave_lists(num, *lsts):
    """
    Interleave two or more lists by picking ``num`` items from 1, then ``num`` from 2,
    etc.
    """
    result = []
    offset = 0
    while offset < len(lsts[0]) - 1:
        for lst in lsts:
            result.extend(lst[offset:offset + num])
        offset += num
    return result
