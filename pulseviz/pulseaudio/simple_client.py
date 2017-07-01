import ctypes
from enum import Enum


# TODO: Improve Enum type
# TODO: Raise exception when `with client` statement hasn't been executed before trying to read/write data.
# TODO: Add method comments
# TODO: Add underscore to private class members


class SampleSpec(ctypes.Structure):
    _fields_ = [
        # SampleFormat
        ('format', ctypes.c_uint32),
        ('rate', ctypes.c_uint32),
        ('channels', ctypes.c_uint8)
    ]


class ChannelMap(ctypes.Structure):
    pass


class BufferAttributes(ctypes.Structure):
    _fields_ = [
        ('maxlength', ctypes.c_uint32),
        ('tlength', ctypes.c_uint32),
        ('prebuf', ctypes.c_uint32),
        ('minreq', ctypes.c_uint32),
        ('fragsize', ctypes.c_uint32)
    ]


class StreamDirection(Enum):
    PA_STREAM_NODIRECTION = 0
    PA_STREAM_PLAYBACK = 1
    PA_STREAM_RECORD = 2
    PA_STREAM_UPLOAD = 3


class SampleFormat(Enum):
    PA_SAMPLE_U8 = 0
    PA_SAMPLE_S16LE = 3


class SimpleClientErrorException(Exception):
    def __init__(self, error_message, error_code):
        super(SimpleClientErrorException, self).__init__()
        self.error_message = error_message
        self.pulse_error_code = error_code
        self.pulse_error_string = libpulse_simple.pa_strerror(error_code).decode('ascii')

    def __str__(self):
        return '{0} ({1}, Code: {2})'.format(self.error_message,
                                             self.pulse_error_string,
                                             self.pulse_error_code)


class SimpleClient:
    pa_stream_direction = StreamDirection.PA_STREAM_NODIRECTION

    def __init__(self,
                 sample_frequency=44100,
                 sample_format=SampleFormat.PA_SAMPLE_U8,
                 name='pulseviz.py',
                 stream_name='none'):
        self.sink_source_name = None
        self.client = None
        self.name = name.encode('ascii')
        self.stream_name = stream_name.encode('ascii')
        self.sample_frequency = sample_frequency
        self.sample_format = sample_format
        self.sample_spec = SampleSpec(self.sample_format.value, self.sample_frequency, 1)
        self.buffer_attributes = None

    def __enter__(self):
        error = ctypes.c_int(0)
        self.client = libpulse_simple.pa_simple_new(None,
                                                    self.name,
                                                    self.pa_stream_direction.value,
                                                    self.sink_source_name,
                                                    self.stream_name,
                                                    self.sample_spec,
                                                    None,
                                                    self.buffer_attributes,
                                                    error)
        if self.client is None or self.client == 0:
            raise SimpleClientErrorException('Could not create PulseAudio stream.', error.value)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # TODO: Is this really called even when an exception occurs while in __enter__?
        if self.client is not None and self.client != 0:
            libpulse_simple.pa_simple_free(self.client)

    def get_latency(self):
        error = ctypes.c_int(0)
        latency = libpulse_simple.pa_simple_get_latency(self.client, ctypes.byref(error))
        if latency == -1:
            raise SimpleClientErrorException('Could not determine latency.', error.value)
        return latency


class SimpleRecordClient(SimpleClient):
    pa_stream_direction = StreamDirection.PA_STREAM_RECORD

    def __init__(self, source=None, target_latency=100000, **kwargs):
        kwargs['stream_name'] = kwargs.get('stream_name', 'record')
        super(SimpleRecordClient, self).__init__(**kwargs)
        self.sink_source_name = source.encode('ascii') if source is not None else source

        fragsize = libpulse_simple.pa_usec_to_bytes(target_latency, self.sample_spec)
        self.buffer_attributes = BufferAttributes(maxlength=-1,
                                                  tlength=-1,
                                                  prebuf=-1,
                                                  minreq=-1,
                                                  fragsize=fragsize)

    def read(self, size=1024):
        data = (ctypes.c_uint8 * size)()
        error = ctypes.c_int(0)

        result = libpulse_simple.pa_simple_read(self.client, data, size, error)
        if result < 0:
            raise SimpleClientErrorException('Could not read data.', error.value)

        # TODO: I guess, using list is quite slow in this case?
        return list(data)

    def read_samples(self, size=1024):
        """
        Wrapper around the read() function that respects the chosen SampleFormat and automatically
        decodes the chunk data.
        """

        if self.sample_format == SampleFormat.PA_SAMPLE_U8:
            data = self.read(size=size)
            decoded_data = data
            dequantized_data = [x/128.0-1.0 for x in decoded_data]
        else:
            raise Exception('The selected sample format is not supported by read_data().')

        return dequantized_data


class SimplePlaybackClient(SimpleClient):
    pa_stream_direction = StreamDirection.PA_STREAM_PLAYBACK

    def __init__(self, sink=None, **kwargs):
        kwargs['stream_name'] = kwargs.get('stream_name', 'playback')
        super(SimplePlaybackClient, self).__init__(**kwargs)
        self.sink_source_name = sink.encode('ascii') if sink is not None else sink

    def write(self, data):
        size = len(data)
        c_data = (ctypes.c_uint8 * size)(*data)
        error = ctypes.c_int(0)

        result = libpulse_simple.pa_simple_write(self.client, c_data, size, error)
        if result < 0:
            raise SimpleClientErrorException('Could not write data.', error.value)

    def write_samples(self, data):
        # TODO
        raise Exception('Not implemented yet.')

    def drain(self):
        error = ctypes.c_int(0)

        result = libpulse_simple.pa_simple_drain(self.client, error)
        if result < 0:
            raise SimpleClientErrorException('Could not drain data.', error.value)


# Attempt to load libpulse-simple
try:
    libpulse_simple = ctypes.cdll.LoadLibrary('libpulse-simple.so.0')
except OSError as e:
    raise ImportError(str(e))

# pa_strerror()
libpulse_simple.pa_strerror.restype = ctypes.c_char_p

# pa_simple_new()
libpulse_simple.pa_simple_new.argtypes = [
    ctypes.c_char_p,
    ctypes.c_char_p,
    # StreamDirection
    ctypes.c_uint32,
    ctypes.c_char_p,
    ctypes.c_char_p,
    ctypes.POINTER(SampleSpec),
    ctypes.POINTER(ChannelMap),
    ctypes.POINTER(BufferAttributes),
    ctypes.POINTER(ctypes.c_int)
]
libpulse_simple.pa_simple_new.restype = ctypes.c_void_p

# pa_simple_free()
libpulse_simple.pa_simple_free.argtypes = [
    ctypes.c_void_p
]

# pa_simple_get_latency()
libpulse_simple.pa_simple_get_latency.argtypes = [
    ctypes.c_void_p
]
libpulse_simple.pa_simple_get_latency.restype = ctypes.c_uint64 # pa_usec_t

# pa_simple_read()
libpulse_simple.pa_simple_read.argtypes = [
    ctypes.c_void_p, # TODO: pa_simple struct,
    ctypes.POINTER(ctypes.c_uint8),
    ctypes.c_size_t,
    ctypes.POINTER(ctypes.c_int)
]

# pa_simple_write()
libpulse_simple.pa_simple_write.argtypes = [
    ctypes.c_void_p, # TODO: pa_simple struct,
    ctypes.POINTER(ctypes.c_uint8),
    ctypes.c_size_t,
    ctypes.POINTER(ctypes.c_int)
]

# pa_simple_drain()
libpulse_simple.pa_simple_drain.argtypes = [
    ctypes.c_void_p, # TODO: pa_simple struct,
    ctypes.POINTER(ctypes.c_int)
]

# pa_usec_to_bytes()
libpulse_simple.pa_usec_to_bytes.argtypes = [
    ctypes.c_uint64, # pa_usec_t
    ctypes.POINTER(SampleSpec)
]
libpulse_simple.pa_usec_to_bytes.restype = ctypes.c_size_t
