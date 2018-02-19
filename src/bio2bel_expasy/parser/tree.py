# -*- coding: utf-8 -*-

import logging
import os
from urllib.request import urlretrieve

import networkx as nx

from ..constants import EXPASY_TREE_DATA_PATH, EXPASY_TREE_URL
from ..utils import normalize_expasy_id

__all__ = [
    'normalize_expasy_id',
    'give_edge',
    'edge_description',
    'get_tree',
]

log = logging.getLogger(__name__)


def download_expasy_tree(force_download=False):
    """Download the expasy tree file

    :param Optional[str] path: The destination of the download
    :param Optional[bool] force_download: True to force download
    """
    if os.path.exists(EXPASY_TREE_DATA_PATH) and not force_download:
        log.info('using cached data at %s', EXPASY_TREE_DATA_PATH)
    else:
        log.info('downloading %s to %s', EXPASY_TREE_URL, EXPASY_TREE_DATA_PATH)
        urlretrieve(EXPASY_TREE_URL, EXPASY_TREE_DATA_PATH)

    return EXPASY_TREE_DATA_PATH


def give_edge(head_str):
    """Returns (parent, child) tuple for given id

    :param str head_str:
    :rtype: tuple
    """
    head_str = normalize_expasy_id(head_str)
    nums = head_str.split('.')
    for i, obj in enumerate(nums):
        nums[i] = obj.strip()

    while '-' in nums:
        nums.remove('-')

    l_nums = len(nums)

    if l_nums == 1:
        return None, "{}.-.-.-".format(nums[0])

    if l_nums == 2:
        return (normalize_expasy_id("{}. -. -.-".format(nums[0])),
                normalize_expasy_id("{}.{:>2}. -.-".format(nums[0], nums[1])))

    if l_nums == 3:
        return (normalize_expasy_id("{}.{:>2}. -.-".format(nums[0], nums[1])),
                normalize_expasy_id("{}.{:>2}.{:>2}.-".format(nums[0], nums[1], nums[2])))

    if l_nums == 4:
        return (normalize_expasy_id("{}.{:>2}.{:>2}.-".format(nums[0], nums[1], nums[2])),
                normalize_expasy_id("{}.{:>2}.{:>2}.{}".format(nums[0], nums[1], nums[2], nums[3])))


def get_tree(path=None, force_download=False):
    """Populates graph from a given specific file.

    :param Optional[str] path: The destination of the download
    :param Optional[bool] force_download: True to force download
    :rtype: networkx.DiGraph
    """
    if path is None:
        download_expasy_tree(force_download=force_download)

    graph = nx.DiGraph()

    with open(path or EXPASY_TREE_DATA_PATH, 'r') as file:
        for line in file:
            line.rstrip('\n')
            if not line[0].isnumeric():
                continue
            head = line[:10]
            parent, child = give_edge(head)
            name = line[11:]
            name = name.strip().strip('.')
            graph.add_node(child, description=name)
            if parent is not None:
                graph.add_edge(parent, child)

    return graph
