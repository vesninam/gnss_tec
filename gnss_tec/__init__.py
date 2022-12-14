# coding=utf-8
"""TEC === Tools to calculate total electron content value in the ionosphere
using data derived from global navigation satellite systems."""

# Shortcut
from .glo import collect_freq_nums
from .gnss import BAND_PRIORITY
from .rinex import ObsFileV2
from .rinex import ObsFileV3
from .rinex import ObsFileV4

# General information
__version__ = '1.1.1'
__author__ = __maintainer__ = 'Ilya Zhivetiev'
__email__ = 'i.zhivetiev@gnss-lab.org'


def rnx(file, **kwargs):
    """Return a reader object which will iterate over observation records in
    the given file. Each iteration will return Tec object. The file can be any
    object which supports iterator protocol.

    Parameters
    ----------
    file : file-like object
    timestep : int
    band_priority : dict
    glo_freq_nums : dict

    Returns
    -------
    reader : iterator
        Yields Tec object for each satellite of the epoch.
    """
    timestep = kwargs.get('timestep', 30)
    glo_freq_nums = kwargs.get('glo_freq_nums')
    band_priority = kwargs.get('band_priority', BAND_PRIORITY)

    if glo_freq_nums is None:
        glo_freq_nums = {}

    try:
        row = next(file)
        rinex_version = float(row[:9])
        rinex_type = row[20]
        # rinex_sat_system = row[40]
    except StopIteration:
        raise ValueError("rnx: Empty input file")
    except ValueError:
        raise ValueError("rnx: Unknown file type")

    if rinex_type.upper() != 'O':
        raise Exception('rnx: Not an observation file')

    rinex_reader = {
        (2.0, 2.1, 2.11, 2.12): ObsFileV2,
        (3.0, 3.01, 3.02, 3.03, 3.04, 3.05): ObsFileV3,
        (4.0,): ObsFileV4
    }

    reader = None
    for ver in rinex_reader:
        if rinex_version in ver:
            reader = rinex_reader[ver]

    if reader is None:
        raise Exception('Unknown RINEX version: {}'.format(rinex_version))

    reader_kwargs = dict(
        version=rinex_version,
        band_priority=band_priority,
        glo_freq_nums=glo_freq_nums,
    )
    if rinex_version >= 3: reader_kwargs.update(timestep=timestep)

    return reader(file, **reader_kwargs)