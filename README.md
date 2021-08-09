# devices-test

## QA stages
* familiarization with the requirements for the device service backend
* test cases implementation (smoke, negative etc.)
* testing/test automation


## Test cases 
1. Check that `GET /devices` method call will return list of devices with its info
2. Check that `PATCH /devices` method call will change specified device parameter
    * duty1
    * duty2
    * freq1
    * freq2
3. Check that `PATCH /devices` method call with invalid/incorrect parameters will cause an exception
    * empty parameters
    * empty values to edit
    * unknown address
    * invalid percentage value
    * invalid percentage parameter type
    * invalid frequencies value
    * invalid frequencies parameter type
4. Check that `GET /report` method call with valid report type for all known devices will return a report text
    * 100
    * 200
    * 300
    * 400
5. Check that `GET /report` method call with invalid/incorrect parameters will cause an exception
    * empty address
    * empty repId
    * unknown address
    * invalid repId value
    * invalid repId type
6. Check that duties and frequencies data could be received via web socket: `/start_monitoring/{address}`
7. Check that proper data could not being received via web socket in invalid parameters specified
   * unknown address
   * invalid address type

## How to run tests:
```bash
docker-compose up --exit-code-from tests
```

## Issues
#### Total issues count: 13
1. Could not monitor Transmission device data (major). 
    * Steps to reproduce:
         1. Call `start_monitoring` method with `129` address specified
         2. Iterate over response to obtain device info
    * Expected result: Device info present in response
    * Actual result: `Not Found` in response

2. Could not obtain report with type `400` for all kind of devices (major).
   * Steps to reproduce:
     1. Call `GET /report` with `repId` specified as `400`
   * Expected result: Response status – 200 OK. Report content present in response
   * Actual result: Response status – 404 Not Found. `Report is not exist` in response
