from wipeos_bottle.bottle import route, run, request
from datetime import datetime, timedelta
from parsers.dmidecode import DmiParser
from parsers.battery_parser import battery_parser
from parsers.battery_parser import battery_parser2
from parsers.lshw_parser import LshwNetworkParser
from parsers.lshw_parser import LshwCPUParser
from parsers.lshw_parser import LshwMemoryParser
from parsers.lshw_parser import LshwSystemParser
from parsers.lshw_parser import LshwDiskParser
from parsers.lshw_parser import LshwPowerParser
from parsers.lshw_parser import LshwBusParser
from parsers.lshw_parser import LshwDisplayParser
import json

dmidecode=""

@route('/dmidecode', method='POST')
def dmidecode_parse():
    try:
        data = request.json
        dmidecode = data.get('data')
        d = DmiParser(dmidecode).human()
        
        return {"status_code":200,"text":json.dumps(d, indent=4)}
    
    except Exception as e:
        return {'error': 'An error occurred: {}'.format(e)}

@route('/battery', method='POST')
def battery_parse():
    try:
        data = request.json
        battery = data.get('data')
        d = battery_parser(battery).parse()

        return {"status_code":200,"text":json.dumps(d, indent=4)}
    
    except Exception as e:
        return {'error': 'An error occurred: {}'.format(e)}

@route('/battery2', method='POST')
def battery2_parse():
    try:
        data = request.json
        battery = data.get('data')
        d = battery_parser2(battery).parse()

        return {"status_code":200,"text":json.dumps(d, indent=4)}
    
    except Exception as e:
        return {'error': 'An error occurred: {}'.format(e)}

@route('/lshw', method='POST')
def lshw_parse():
    try:
        data = request.json
        lshw = data.get('data')
        option = data.get('option')
        print(lshw)
        print(option)
        if option == "network":
            d = LshwNetworkParser(lshw).parse()
        elif option == "cpu":
            d = LshwCPUParser(lshw).parse()
        elif option == "memory":
            d = LshwMemoryParser(lshw).parse()
        elif option == "system":
            d = LshwSystemParser(lshw).parse()
        elif option == "disk":
            d = LshwDiskParser(lshw).parse()
        elif option == "power":
            d = LshwPowerParser(lshw).parse()
        elif option == "bus":
            d = LshwBusParser(lshw).parse()
        elif option == "display":
            d = LshwDisplayParser(lshw).parse()
        else:
            raise ValueError("Invalid option provided")
        print(d)

        return {"status_code":200,"text":json.dumps(d, indent=4)}
    
    except Exception as e:
        return {'error': 'An error occurred: {}'.format(e)}

@route('/hwinfo', method='POST')
def hwinfo_parse():
    try:
        data = request.json
        hwinfo = data.get('data')
        option = data.get('option')
        print(hwinfo)
        print(option)
        if option == "network":
            d = LshwNetworkParser(lshw).parse()
        elif option == "cpu":
            d = LshwCPUParser(lshw).parse()
        elif option == "memory":
            d = LshwMemoryParser(lshw).parse()
        elif option == "system":
            d = LshwSystemParser(lshw).parse()
        elif option == "disk":
            d = LshwDiskParser(lshw).parse()
        elif option == "power":
            d = LshwPowerParser(lshw).parse()
        elif option == "bus":
            d = LshwBusParser(lshw).parse()
        elif option == "display":
            d = LshwDisplayParser(lshw).parse()
        else:
            raise ValueError("Invalid option provided")
        print(d)

        return {"status_code":200,"text":json.dumps(d, indent=4)}
    
    except Exception as e:
        return {'error': 'An error occurred: {}'.format(e)}

if __name__ == '__main__':
    run(host='0.0.0.0', port=8089, debug=True, quiet=False)
