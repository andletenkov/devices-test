import random
import pytest

from utils import random_percent, random_hz

parametrize = pytest.mark.parametrize
p = pytest.param


def test_get_devices_info(device_client):
    r = device_client.get_devices()
    assert r.ok, f'Expected status code 200, but was {r.status_code}'
    assert isinstance(r.json(), list), 'Expected list of devices'
    for device in r.json():
        assert device.get('address'), 'Device has no address filed'
        assert device.get('name'), 'Device has no name field'
        assert device.get('pin_1_pwm_d'), 'Device has no pin1 duty field'
        assert device.get('pin_1_pwm_f'), 'Device has no pin1 frequency field'
        assert device.get('pin_2_pwm_d'), 'Device has no pin2 duty field'
        assert device.get('pin_2_pwm_f'), 'Device has no pin2 frequency field'
        assert device.get('type'), 'Device has no type field'


@parametrize('param, value, device_field', [
    ('duty1', random_percent(), 'pin_1_pwm_d'),
    ('duty2', random_percent(), 'pin_2_pwm_d'),
    ('freq1', random_hz(), 'pin_1_pwm_f'),
    ('freq2', random_hz(), 'pin_2_pwm_f'),
])
def test_edit_device(device_client, param, value, device_field):
    devices_before = device_client.get_devices().json()
    device_index = random.choice(range(len(devices_before)))
    address = devices_before[device_index]['address']

    r = device_client.edit_device(address=address, **{param: value})
    assert r.ok, f'Expected status code 200, but was {r.status_code}'

    devices_after = device_client.get_devices().json()
    assert devices_after[device_index][device_field] == value


@parametrize('params, expected_status, expected_error', [
    p(dict(), 400, "Please specify 'address' value", id='Empty params'),
    p({'address': '4A'}, 400, "Please specify one of values: 'duty1', 'freq1', 'duty2', 'freq2'",
      id='Empty values to edit'),
    p({'address': 'test', 'duty1': 10}, 404, 'Not Found', id='Unknown address'),
    p({'address': '4A', 'duty1': 101}, 400, "Invalid value of 'duty1' value. Valid diapason is 0 - 100 (%)",
      id='Invalid % value'),
    p({'address': '4A', 'duty2': 'test'}, 400, "Invalid type of 'duty2' value", id='Invalid % param type'),
    p({'address': '4A', 'freq1': 150}, 400,
      "Invalid value of 'freq1' value. Valid values (Hz) are 1, 2, 5, 10, 20, 50, 100, 200, 500",
      id='Invalid Hz value'),
    p({'address': '4A', 'freq2': 'test'}, 400, "Invalid type of 'freq2' value", id='Invalid Hz param type'),
])
def test_edit_device_invalid_params(device_client, params, expected_status, expected_error):
    r = device_client.edit_device(**params)
    assert r.status_code == expected_status, f'Expected status code {expected_status}, but was {r.status_code}'
    assert expected_error in r.text, 'Invalid error message'


@parametrize('address', [
    '4A',
    '65',
    '80',
    '3F'
])
@parametrize('rep_id', [
    100,
    200,
    300,
    400
])
def test_get_report(device_client, address, rep_id):
    r = device_client.get_report(address=address, rep_id=rep_id)
    assert r.ok, f'Expected status code 200, but was {r.status_code}'


@parametrize('params, expected_status, expected_error', [
    p({'rep_id': 100}, 400, "Please specify 'address' value", id='Empty address'),
    p({'address': '4A'}, 400, "Please specify 'repId' value", id='Empty repId'),
    p({'address': 'test', 'rep_id': 100}, 404, "Report is not exist", id='Unknown address'),
    p({'address': '4A', 'rep_id': 99}, 404, "Report is not exist", id='Invalid repId'),
    p({'address': '4A', 'rep_id': 'test'}, 400, "Invalid type of 'repId' value", id='Invalid repId type'),
])
def test_get_report_invalid_params(device_client, params, expected_status, expected_error):
    r = device_client.get_report(**params)
    assert r.status_code == expected_status, f'Expected status code {expected_status}, but was {r.status_code}'
    assert expected_error in r.text, 'Invalid error message'


@parametrize('address, web_address, duty1, duty2, freq1, freq2', [
    ('4A', '74', random_percent(), random_percent(), random_hz(), random_hz()),
    ('65', '101', random_percent(), random_percent(), random_hz(), random_hz()),
    ('80', '129', random_percent(), random_percent(), random_hz(), random_hz()),
    ('3F', '63', random_percent(), random_percent(), random_hz(), random_hz()),
])
def test_device_monitoring(device_client, address, web_address, duty1, duty2, freq1, freq2):
    device_client.edit_device(address=address, duty1=duty1, freq1=freq1)
    device_client.edit_device(address=address, duty2=duty2, freq2=freq2)

    monitor = device_client.start_monitoring(web_address)

    chunk = next(monitor)
    assert 'freqs' in chunk, 'Invalid data received'

    pin_1_freq, pin_2_freq, *_ = chunk['freqs']

    chunk = next(monitor)
    assert 'duties' in chunk, 'Invalid data received'

    pin_1_duty, pin_2_duty, *_ = chunk['duties']

    assert int(pin_1_duty) == duty1, 'Invalid Pin 1 % value'
    assert int(pin_2_duty) == duty2, 'Invalid Pin 2 % value'
    assert int(pin_1_freq) == freq1, 'Invalid Pin 1 Hz value'
    assert int(pin_2_freq) == freq2, 'Invalid Pin 2 Hz value'


@parametrize('address', [
    p(1, id='Unknown address'),
    p('test', id='Invalid address type')
])
def test_device_monitoring_invalid_address(device_client, address):
    monitor = device_client.start_monitoring(address)
    chunk = next(monitor)
    assert 'Not found' in chunk, f'Unexpected or empty data received: {chunk}'
