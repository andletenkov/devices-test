import json
import logging
from typing import Iterator, Any, Union

import requests
import websocket
from requests import Session


class DeviceTestClient:

    def __init__(self, host: str, port: int) -> None:
        self._http_url = f'http://{host}:{port}'
        self._ws_url = f'ws://{host}:{port}'
        self._session = Session()

    def _call(self, method: str, endpoint: str, **kwargs: Any) -> requests.Response:
        url = self._http_url + endpoint
        logging.info(f'Request – {method.upper()} {url} {kwargs if kwargs else ""}')
        resp = self._session.request(method, self._http_url + endpoint, **kwargs)
        logging.info(
            f'Response – <{resp.status_code} {resp.reason}> {resp.text} ({resp.elapsed.microseconds / 10 ** 6} sec)'
        )
        return resp

    def start_monitoring(self, address: str) -> Iterator[Union[dict, str]]:
        url = f'{self._ws_url}/start_monitoring/{address}'
        ws = websocket.create_connection(url)
        logging.info(f'Connected to {url}')

        try:
            while True:
                raw_data = ws.recv()
                try:
                    data = json.loads(raw_data)
                except json.JSONDecodeError:
                    data = raw_data

                logging.info(f'Received from {url} – {data}')
                yield data
        finally:
            ws.close()
            logging.info(f'Disconnected from {url}')

    def get_devices(self) -> requests.Response:
        return self._call('GET', '/devices')

    def edit_device(
            self,
            address: Any = None,
            duty1: Any = None,
            duty2: Any = None,
            freq1: Any = None,
            freq2: Any = None
    ) -> requests.Response:
        params = {
            'address': address,
            'duty1': duty1,
            'duty2': duty2,
            'freq1': freq1,
            'freq2': freq2
        }
        return self._call('PATCH', '/devices', params=params)

    def get_report(self, address: Any = None, rep_id: int = None) -> requests.Response:
        return self._call('GET', '/report', params={
            'address': address,
            'repId': rep_id
        })

    def close(self) -> None:
        if self._session:
            self._session.close()


if __name__ == '__main__':
    dc = DeviceTestClient('localhost', 5585)
    try:
        for c in dc.start_monitoring('65'):
            print(c)
    except KeyboardInterrupt:
        dc.close()
