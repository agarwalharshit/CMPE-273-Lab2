import operator
#from collections import OrderedDict

import requests
from spyne import Application, Unicode, Integer, Float
from spyne import ServiceBase
from spyne import rpc, Iterable
from spyne.protocol.http import HttpRpc
from spyne.protocol.json import JsonDocument
from spyne.server.wsgi import WsgiApplication


class CrimeReportService(ServiceBase):
    @rpc(Unicode, Unicode,Unicode, _returns=Unicode)
    def checkcrime(ctx, lat, lon, radius):
        json1 = requests.get(
            'https://api.spotcrime.com/crimes.json?lat=' + lat + '&lon=' + lon + '&radius=' + radius + '&key=.')
        json1 = json1.json()
        json2 = json1["crimes"]
        listCrimes=[]
        dictCrimesCount = {}
        for row in json2:
            address = row['address']
            addressList = address.split('&')
            for row1 in addressList:
                row1=row1.strip()
                if (row1.find("OF") > -1):
                    r = row1.split("OF")
                    rowz = r[-1].strip()
                elif (row1.find("BLOCK") > -1):
                    r = row1.split("BLOCK")
                    rowz = r[-1].strip()
                else:
                    rowz = row1
                street = rowz
                if dictCrimesCount.get(street):
                    count = dictCrimesCount[street]
                    count = count + 1
                    del dictCrimesCount[street]
                    dictCrimesCount.update({street: count})
                else:
                    dictCrimesCount.update({street: 1})

            crimeType = row["type"]
            crimeDate = row["date"]
            hour = crimeDate[9:11]
            hour=int(hour)
            second= crimeDate[12:14]
            second=int(second)
            AmPm = crimeDate[15:17]
            crimeTimeSlot = 0
            if (AmPm == "AM" and ((hour == 12 and second>0) or hour == 1 or hour == 2 or (hour==3 and second==0))):
                crimeTimeSlot = 1
            elif (AmPm == "AM" and (hour == 3 or hour == 4 or hour == 5 or (hour==6 and second==0))):
                crimeTimeSlot = 2
            elif (AmPm == "AM" and (hour == 6 or hour == 7 or hour == 8 or (hour == 9 and second==0))):
                crimeTimeSlot = 3
            elif (AmPm == "AM" and (hour == 9 or hour == 10 or hour == 11 )):
                crimeTimeSlot = 4
            elif (AmPm == "PM" and (hour == 12  and second==0 )):
                crimeTimeSlot = 4
            elif (AmPm == "PM" and ((hour == 12 and second>0) or hour == 1 or hour == 2 or (hour==3 and second==0))):
                crimeTimeSlot = 5
            elif (AmPm == "PM" and (hour == 3 or hour == 4 or hour == 5 or (hour==6 and second==0))):
                crimeTimeSlot = 6
            elif (AmPm == "PM" and (hour == 6 or hour == 7 or hour == 8 or (hour==9 and second==0))):
                crimeTimeSlot = 7
            elif (AmPm == "PM" and (hour == 9 or hour == 10 or hour == 11)):
                crimeTimeSlot = 8
            elif (AmPm == "AM" and (hour == 12 and second==0)):
                crimeTimeSlot = 8
            data = [crimeType, crimeTimeSlot]
            listCrimes.append(data)


        SortedDictCrimesCount = sorted(dictCrimesCount.items(), key=operator.itemgetter(1), reverse=True)
        the_most_dangerous_streets = []
        total_crime = 0
        differentCrimes={}
        Time1 = 0
        Time2 = 0
        Time3 = 0
        Time4 = 0
        Time5 = 0
        Time6 = 0
        Time7 = 0
        Time8 = 0

        for i in SortedDictCrimesCount[0:3]:
            the_most_dangerous_streets.append(i[0])
        for j in listCrimes:
            if differentCrimes.get(j[0]):
                count = differentCrimes[j[0]]
                count = count + 1
                del differentCrimes[j[0]]
                differentCrimes.update({j[0]: count})
                total_crime += 1
            else:
                differentCrimes.update({j[0]: 1})
                total_crime+=1

            if (j[1] == 1):
                Time1 += 1
            elif (j[1] == 2):
                Time2 += 1
            elif (j[1] == 3):
                Time3 += 1
            elif (j[1] == 4):
                Time4 += 1
            elif (j[1] == 5):
                Time5 += 1
            elif (j[1] == 6):
                Time6 += 1
            elif (j[1] == 7):
                Time7 += 1
            elif (j[1] == 8):
                Time8 += 1


        jsonString ={
            "total_crime": total_crime,
            "the_most_dangerous_streets": the_most_dangerous_streets,
            "crime_type_count":
                differentCrimes
            ,
            "event_time_count": {
                "12:01am-3am": Time1,
                "3:01am-6am": Time2,
                "6:01am-9am": Time3,
                "9:01am-12noon": Time4,
                "12:01pm-3pm": Time5,
                "3:01pm-6pm": Time6,
                "6:01pm-9pm": Time7,
                "9:01pm-12midnight": Time8
            }
        }

        yield jsonString




application = Application([CrimeReportService],
    tns='spyne.examples.hello',
    in_protocol=HttpRpc(validator='soft'),
    out_protocol=JsonDocument()
)

if __name__ == '__main__':
    # You can use any Wsgi server. Here, we chose
    # Python's built-in wsgi server but you're not
    # supposed to use it in production.
    from wsgiref.simple_server import make_server
    wsgi_app = WsgiApplication(application)
    server = make_server('0.0.0.0', 8000, wsgi_app)
    server.serve_forever()
