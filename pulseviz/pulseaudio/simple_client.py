import ctypes
from enum import Enum


_libpulse_simple = None


class _SampleSpec(ctypes.Structure):
    _fields_ = [
        ('format', ctypes.c_uint32),  # SampleFormat
        ('rate', ctypes.c_uint32),
        ('channels', ctypes.c_uint8)
    ]


class _ChannelMap(ctypes.Structure):
    pass


class _BufferAttributes(ctypes.Structure):
    _fields_ = [
        ('maxlength', ctypes.c_uint32),
        ('tlength', ctypes.c_uint32),
        ('prebuf', ctypes.c_uint32),
        ('minreq', ctypes.c_uint32),
        ('fragsize', ctypes.c_uint32)
    ]


class _StreamDirection(Enum):
    PA_STREAM_NODIRECTION = 0
    PA_STREAM_PLAYBACK = 1
    PA_STREAM_RECORD = 2
    PA_STREAM_UPLOAD = 3


class SampleFormat(Enum):
    PA_SAMPLE_U8 = 0
    PA_SAMPLE_S16LE = 3
    PA_SAMPLE_FLOAT32LE = 5


class SimpleClientException(Exception):
    pass


class PulseAudioException(Exception):
    """
    Raised whenever libpulse-simple returns an error.
    """

    def __init__(self, error_message, error_code):
        super().__init__()
        self.error_message = error_message
        self.pulse_error_code = error_code
        self.pulse_error_string = _libpulse_simple.pa_strerror(error_code).decode('ascii')

    def __str__(self):
        return '{0} ({1}, Code: {2})'.format(self.error_message,
                                             self.pulse_error_string,
                                             self.pulse_error_code)


class _SimpleClient:
    _STREAM_DIRECTION = _StreamDirection.PA_STREAM_NODIRECTION

    def __init__(self,
                 sample_frequency, sample_format, channels,
                 name='pulseviz', stream_name='none'):
        if not isinstance(sample_format, SampleFormat):
            raise SimpleClientException('sample_format must be a member of SampleFormat.')

        if channels != 1:
            raise SimpleClientException('Right now only a single audio channel is supported.')

        self._sink_source_name = None
        self._name = name.encode('ascii')
        self._stream_name = stream_name.encode('ascii')
        self._sample_frequency = sample_frequency
        self._channels = channels
        self._sample_format = sample_format
        self._sample_spec = _SampleSpec(self._sample_format.value, self.sample_frequency, self._channels)
        self._buffer_attributes = None
        self._client = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def _fail_if_not_connected(self):
        if not self.is_connected():
            raise SimpleClientException('No connection has been established yet or is already closed.')

    @property
    def sample_frequency(self):
        return self._sample_frequency

    @property
    def sample_format(self):
        return self._sample_format

    def connect(self):
        """Establishes a connection to a PulseAudio server."""

        error = ctypes.c_int(0)

        self._client = _libpulse_simple.pa_simple_new(None,
                                                      self._name,
                                                      self._STREAM_DIRECTION.value,
                                                      self._sink_source_name,
                                                      self._stream_name,
                                                      self._sample_spec,
                                                      None,
                                                      self._buffer_attributes,
                                                      error)
        if self._client is None or self._client == 0:
            self._client = None
            raise PulseAudioException('Could not create PulseAudio stream.', error.value)

    def disconnect(self):
        """Closes and frees the connection to the PulseAudio server."""

        self._fail_if_not_connected()

        if self.is_connected():
            # Do not fail when attempting to flush during disconnect.
            try:
                self.flush()
            except PulseAudioException:
                pass

        if self._client is not None and self._client != 0:
            _libpulse_simple.pa_simple_free(self._client)
            self._client = None

    def is_connected(self):
        """Returns True if the client is connected."""

        return self._client is not None

    def get_latency(self):
        """Returns the latency reported by the PulseAudio server in µs."""

        self._fail_if_not_connected()

        error = ctypes.c_int(0)
        latency = _libpulse_simple.pa_simple_get_latency(self._client, ctypes.byref(error))
        if latency == -1:
            raise PulseAudioException('Could not determine latency.', error.value)
        return latency

    def flush(self):
        """Flushes the playback or record buffer."""

        self._fail_if_not_connected()

        error = ctypes.c_int(0)
        result = _libpulse_simple.pa_simple_flush(self._client, error)
        if result < 0:
            raise PulseAudioException('Could not flush data.', error.value)


class SimpleRecordClient(_SimpleClient):
    """
    Provides a small class that can be used to record audio from a PulseAudio server.
    """

    _STREAM_DIRECTION = _StreamDirection.PA_STREAM_RECORD

    def __init__(self, target_latency, source=None, **kwargs):
        kwargs['stream_name'] = kwargs.get('stream_name', 'record')
        super().__init__(**kwargs)

        self._sink_source_name = source.encode('ascii') if source is not None else source

        fragsize = _libpulse_simple.pa_usec_to_bytes(target_latency, self._sample_spec)
        self._buffer_attributes = _BufferAttributes(maxlength=-1,
                                                    tlength=-1,
                                                    prebuf=-1,
                                                    minreq=-1,
                                                    fragsize=fragsize)

    def read(self, size):
        """Reads `size` samples from the PulseAudio server using the specified SampleSpec format."""

        self._fail_if_not_connected()

        if self._sample_format == SampleFormat.PA_SAMPLE_U8:
            data = (ctypes.c_uint8 * size)()
            size_ = size
        elif self._sample_format == SampleFormat.PA_SAMPLE_S16LE:
            raise Exception('Not implemented yet.')
        elif self._sample_format == SampleFormat.PA_SAMPLE_FLOAT32LE:
            # TODO: There's no guarantee that c_float is in little endian byte order.
            # We should wrap it into a LittleEndianStructure and access it in there.
            data = (ctypes.c_float * size)()
            size_ = size * 4

        error = ctypes.c_int(0)
        result = _libpulse_simple.pa_simple_read(self._client, data, size_, error)
        if result < 0:
            raise PulseAudioException('Could not read data.', error.value)

        return data


class SimplePlaybackClient(_SimpleClient):
    """
    Provides a small class that can be used to play audio to a PulseAudio server.
    """

    _STREAM_DIRECTION = _StreamDirection.PA_STREAM_PLAYBACK

    def __init__(self, sink=None, **kwargs):
        kwargs['stream_name'] = kwargs.get('stream_name', 'playback')
        super().__init__(**kwargs)

        self._sink_source_name = sink.encode('ascii') if sink is not None else sink

    def write(self, data):
        """Writes samples of the given SampleSpec to the PulseAudio server."""

        self._fail_if_not_connected()

        if self._sample_format == SampleFormat.PA_SAMPLE_U8:
            size = len(data)
            c_data = (ctypes.c_uint8 * size)(*data)
        elif self._sample_format == SampleFormat.PA_SAMPLE_S16LE:
            raise Exception('Not implemented yet.')
        elif self._sample_format == SampleFormat.PA_SAMPLE_FLOAT32LE:
            raise Exception('Not implemented yet.')

        error = ctypes.c_int(0)
        result = _libpulse_simple.pa_simple_write(self._client, c_data, size, error)
        if result < 0:
            raise PulseAudioException('Could not write data.', error.value)

    def drain(self):
        """Waits for all remaining data in the samples buffer to be played by the PulseAudio server."""

        self._fail_if_not_connected()

        error = ctypes.c_int(0)
        result = _libpulse_simple.pa_simple_drain(self._client, error)
        if result < 0:
            raise PulseAudioException('Could not drain data.', error.value)


def _load_libpulse_simple():
    global _libpulse_simple

    try:
        _libpulse_simple = ctypes.cdll.LoadLibrary('libpulse-simple.so.0')
    except OSError as e:
        raise ImportError(str(e))

    # pa_strerror()
    _libpulse_simple.pa_strerror.restype = ctypes.c_char_p

    # pa_simple_new()
    _libpulse_simple.pa_simple_new.argtypes = [
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_uint32,  # StreamDirection
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.POINTER(_SampleSpec),
        ctypes.POINTER(_ChannelMap),
        ctypes.POINTER(_BufferAttributes),
        ctypes.POINTER(ctypes.c_int)
    ]
    _libpulse_simple.pa_simple_new.restype = ctypes.c_void_p  # struct pa_simple

    # pa_simple_free()
    _libpulse_simple.pa_simple_free.argtypes = [
        ctypes.c_void_p  # struct pa_simple
    ]

    # pa_simple_get_latency()
    _libpulse_simple.pa_simple_get_latency.argtypes = [
        ctypes.c_void_p
    ]
    _libpulse_simple.pa_simple_get_latency.restype = ctypes.c_uint64  # pa_usec_t

    # pa_simple_read()
    _libpulse_simple.pa_simple_read.argtypes = [
        ctypes.c_void_p,  # struct pa_simple
        ctypes.c_void_p,
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_int)
    ]

    # pa_simple_write()
    _libpulse_simple.pa_simple_write.argtypes = [
        ctypes.c_void_p,  # struct pa_simple
        ctypes.c_void_p,
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_int)
    ]

    # pa_simple_drain()
    _libpulse_simple.pa_simple_drain.argtypes = [
        ctypes.c_void_p,  # struct pa_simple
        ctypes.POINTER(ctypes.c_int)
    ]

    # pa_simple_flush()
    _libpulse_simple.pa_simple_flush.argtypes = [
        ctypes.c_void_p,  # struct pa_simple
        ctypes.POINTER(ctypes.c_int)
    ]

    # pa_usec_to_bytes()
    _libpulse_simple.pa_usec_to_bytes.argtypes = [
        ctypes.c_uint64,  # pa_usec_t
        ctypes.POINTER(_SampleSpec)
    ]
    _libpulse_simple.pa_usec_to_bytes.restype = ctypes.c_size_t


# Attempt to load libpulse-simple
_load_libpulse_simple()
