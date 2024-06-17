import time
import pytest
from mock import Mock
from devo.sender.data import SenderBufferFlusher


def test_initialize_timestamp():
    flusher = SenderBufferFlusher()
    now = time.time()
    timestamp = flusher.initialize_timestamp()
    assert isinstance(timestamp, float)
    assert timestamp - now <= SenderBufferFlusher.DEFAULT_INTERNAL_WAIT_VALUE


def test_wait():
    flusher = SenderBufferFlusher()
    flusher.wait()
    assert flusher._SenderBufferFlusher__loop_wait is None
    assert flusher._SenderBufferFlusher__first_data_timestamp is None


def test_run_and_stop():
    flusher = SenderBufferFlusher()
    flusher.buffer_timeout = 1.0
    flusher.flush_buffer_func = lambda: None
    flusher.start()
    time.sleep(2)
    flusher.stop()
    assert not flusher._SenderBufferFlusher__running_flag


def test_start_invalid_buffer_timeout():
    flusher = SenderBufferFlusher()
    flusher.buffer_timeout = 0.0
    flusher.flush_buffer_func = lambda: None
    with pytest.raises(Exception):
        flusher.start()


def test_start_invalid_flush_buffer_func():
    flusher = SenderBufferFlusher()
    flusher.buffer_timeout = 10.0
    with pytest.raises(Exception):
        flusher.start()


def test_flush_after_buffer_timeout():

    """
    This test will check if the flush_buffer_func is called after the
    buffer_timeout mock_time_stamp_value is used to mock the time.time()
    function with a fixed value old enough to trigger the flush.
    """

    mock_time_stamp_value = 1718288971.7541466

    flusher = SenderBufferFlusher()
    flusher.buffer_timeout = 1.0
    time_mock = Mock()
    time_mock.time = Mock(return_value=mock_time_stamp_value)
    flusher._SenderBufferFlusher__first_data_timestamp = mock_time_stamp_value
    flusher.flush_buffer_func = Mock(name="flush_buffer_func")
    flusher.start()
    time.sleep(2)
    flusher.stop()
    assert flusher.flush_buffer_func.called
    assert not flusher._SenderBufferFlusher__running_flag


if __name__ == "__main__":
    pytest.main()
