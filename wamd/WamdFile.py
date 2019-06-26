# Simpler WAMD equivalent of GuanoFile - read only
# Largely taken from on https://github.com/riggsd/guano-py/blob/master/bin/wamd2guano.py
# Note: the licence of this file is MIT, independent of the overall licence of the project, due to its source
import chunk
import re
import struct
from datetime import datetime

from guano import tzoffset


class WamdFile:
    # binary WAMD field identifiers
    WAMD_IDS = {
        0x00: 'version',
        0x01: 'model',
        0x02: 'serial',
        0x03: 'firmware',
        0x04: 'prefix',
        0x05: 'timestamp',
        0x06: 'gpsfirst',
        0x07: 'gpstrack',
        0x08: 'software',
        0x09: 'license',
        0x0A: 'notes',
        0x0B: 'auto_id',
        0x0C: 'manual_id',
        0x0D: 'voicenotes',
        0x0E: 'auto_id_stats',
        0x0F: 'time_expansion',
        0x10: 'program',
        0x11: 'runstate',
        0x12: 'microphone',
        0x13: 'sensitivity',
    }

    # fields that we exclude from our in-memory representation
    WAMD_DROP_IDS = (
        0x0D,  # voice note embedded .WAV
        0x10,  # program binary
        0x11,  # runstate giant binary blob
        0xFFFF,  # used for 16-bit alignment
    )

    # rules to coerce values from binary string to native types (default is `str`)
    WAMD_COERCE = {
        'version': lambda x: struct.unpack('<H', x)[0],
        'timestamp': lambda x: WamdFile._parse_wamd_timestamp(x),
        'gpsfirst': lambda x: WamdFile._parse_wamd_gps(x),
        'time_expansion': lambda x: struct.unpack('<H', x)[0],
    }

    @staticmethod
    def _parse_text(value: bytes):
        """Default coercion function which assumes text is UTF-8 encoded"""
        return value.decode('utf-8')

    @staticmethod
    def _parse_wamd_timestamp(timestamp):
        """WAMD timestamps are one of these known formats:
        2014-04-02 22:59:14-05:00
        2014-04-02 22:59:14.000
        2014-04-02 22:59:14
        Produces a `datetime.datetime`.
        """
        if isinstance(timestamp, bytes):
            timestamp = timestamp.decode('utf-8')
        if len(timestamp) == 25:
            dt, offset = timestamp[:-6], timestamp[19:]
            try:
                tz = tzoffset(offset)
            except ValueError as e:
                # WA have an issue with timezones… https://github.com/riggsd/guano-py/issues/17
                no_colon_match = re.match(r'([+-]?)(\d{2})(\d{2})', offset)
                if no_colon_match:
                    sign, hours, minutes = no_colon_match.groups()
                    tz = tzoffset(float(sign + hours) + float(sign + minutes) / 60)
                else:
                    raise e

            return datetime.strptime(dt, '%Y-%m-%d %H:%M:%S').replace(tzinfo=tz)
        elif len(timestamp) == 23:
            return datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
        elif len(timestamp) == 19:
            return datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        else:
            return None

    @staticmethod
    def _parse_wamd_gps(gpsfirst):
        """WAMD "GPS First" waypoints are in one of these two formats:
        SM3, SM4, (the correct format):
            WGS..., LAT, N|S, LON, E|W [, alt...]
        EMTouch:
            WGS..., [-]LAT, [-]LON[,alt...]
        Produces (lat, lon, altitude) float tuple.
        """
        if not gpsfirst:
            return None
        if isinstance(gpsfirst, bytes):
            gpsfirst = gpsfirst.decode('utf-8')
        vals = tuple(val.strip() for val in gpsfirst.split(','))
        _, vals = vals[0], vals[1:]
        if vals[1] in ('N', 'S'):
            # Standard format
            lat, lon = float(vals[0]), float(vals[2])
            if vals[1] == 'S':
                lat *= -1
            if vals[3] == 'W':
                lon += -1
            alt = int(round(float(vals[4]))) if len(vals) > 4 else None
        else:
            # EMTouch format
            lat, lon = float(vals[0]), float(vals[1])
            alt = float(vals[2]) if len(vals) > 2 and vals[2] != '(null)' else None
        return lat, lon, alt

    def __init__(self, filename: str):
        self.initialised = False
        self.filename = filename
        self.metadata = {}

    def __getitem__(self, item):
        if not self.initialised:
            self.process_file()
        return self.metadata.get(item, None)

    def __contains__(self, item):
        if not self.initialised:
            self.process_file()
        return item in self.metadata

    def items(self):
        if not self.initialised:
            self.process_file()
        for k, v in self.metadata.items():
            yield k, v

    def process_file(self):
        """Extract WAMD metadata from a .WAV file as a dict"""
        fname = self.filename
        with open(fname, 'rb') as f:
            ch = chunk.Chunk(f, bigendian=False)
            if ch.getname() != b'RIFF':
                raise Exception('%s is not a RIFF file!' % fname)
            if ch.read(4) != b'WAVE':
                raise Exception('%s is not a WAVE file!' % fname)

            wamd_chunk = None
            while True:
                try:
                    subch = chunk.Chunk(ch, bigendian=False)
                except EOFError:
                    break
                if subch.getname() == b'wamd':
                    wamd_chunk = subch
                    break
                else:
                    subch.skip()
            if not wamd_chunk:
                raise ValueError('No wamd data chunk found')

            metadata = {}
            offset = 0
            size = wamd_chunk.getsize()
            buf = wamd_chunk.read(size)
            while offset < size:
                id = struct.unpack_from('< H', buf, offset)[0]
                len = struct.unpack_from('< I', buf, offset + 2)[0]
                val = struct.unpack_from('< %ds' % len, buf, offset + 6)[0]
                if id not in WamdFile.WAMD_DROP_IDS:
                    name = WamdFile.WAMD_IDS.get(id, id)
                    val = WamdFile.WAMD_COERCE.get(name, WamdFile._parse_text)(val)
                    metadata[name] = val
                offset += 6 + len
            self.metadata = metadata

        self.initialised = True
