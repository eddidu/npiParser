from parser.taxonomy import Doctors
from parser.zipcodes import Zipcodes
from parser.countryCodes import CountryCodes

from reader import csvReader

import timeit
import pymongo


TAXONOMY_FILEPATH = "./assets/nucc_taxonomy_160.csv"
ZIPCODE_FILEPATH = "./assets/zipcode.csv"
COUNTRY_FILEPATH = "./assets/countryCodes.csv"
NPI_FILEPATH = "./assets/npidata_20050523-20151213.csv"

DB_HOST = "localhost"
DB_PORT = 27017

def process():
    # setup db connection and clean up
    client = pymongo.MongoClient('localhost', 27017)
    specialtyCollection = client.doctorwho.specialtyGroups
    doctorCollection = client.doctorwho.doctors

    specialtyCollection.drop()
    doctorCollection.drop()

    # initialize helpers
    taxonomy = Doctors(TAXONOMY_FILEPATH)
    zipcodes = Zipcodes(ZIPCODE_FILEPATH)
    countryCodes = CountryCodes(COUNTRY_FILEPATH)

    doctors = []

    for row in csvReader.read(NPI_FILEPATH):
        doctor = {}

        if row["Entity Type Code"] == 2:
            continue

        # name
        lastName = row["Provider Last Name (Legal Name)"]
        if not lastName:
            continue 
        firstName = row["Provider First Name"]
        #middleName = row["Provider Middle Name"]
        #prefix = row["Provider Name Prefix Text"]
        #suffix = row["Provider Name Suffix Text"]
        doctor["firstName"] = firstName.capitalize()
        doctor["lastName"] = lastName.capitalize()

        # specialties
        secondaries = set()
        primary = None
        group = None
        for i in xrange(1, 16):
            code = row["Healthcare Provider Taxonomy Code_" + str(i)]
            switch = row["Healthcare Provider Primary Taxonomy Switch_" + str(i)]
            if not code or not taxonomy.containsCode(code):
                continue

            if not group:
                group = taxonomy.getGroupName(code)

            if switch == 'Y':
                primary = taxonomy.getSpecialtyName(code)
            else:
                secondaries.add(taxonomy.getSpecialtyName(code))
        
        # skip non physician
        if not primary and len(secondaries) == 0:
            continue

        specialty = {"group": group, "primary": primary, "secondaries": list(secondaries)}
        doctor["specialty"] = specialty
 
        # npi
        npi = row["NPI"]
        doctor["_id"] = int(npi)

        # business location
        address1 = row["Provider First Line Business Practice Location Address"]
        address2 = row["Provider Second Line Business Practice Location Address"]
        city = row["Provider Business Practice Location Address City Name"]
        state = row["Provider Business Practice Location Address State Name"]
        zipcode = row["Provider Business Practice Location Address Postal Code"]
        countryCode = row["Provider Business Practice Location Address Country Code (If outside U.S.)"]
        phone = row["Provider Business Practice Location Address Telephone Number"]
        zipcode = zipcode[:5]

        location = {
            "address": ' '.join(str(addr) for addr in (address1, address2) if addr),
            "city": city.capitalize(),
            "state": state,
            "zipcode": zipcode,
            "country": countryCodes.getCountryName(countryCode),
            "phone": phone
        }

        if zipcodes.contains(zipcode):
            location["geopoint"] = zipcodes.geocode(zipcode)
        else:
            for i in xrange(100):
                candid = zipcode[:3] + str(i).zfill(2)
                if zipcodes.contains(zipcode):
                    location["geopoint"] = zipcodes.geocode(zipcode)
                    break

        doctor["location"] = location

        doctors.append(doctor)
        if len(doctors) == 10000:
            # insert doctors
            doctorCollection.insert_many(doctors)
            # empty the list
            doctors[:] = []

    doctorCollection.insert_many(doctors)
    # insert specialties
    specialtyCollection.insert_many(taxonomy.toMongoCollection())

    client.close()

if __name__ == "__main__":
    t = timeit.Timer(lambda: process())
    print t.timeit(number=1)