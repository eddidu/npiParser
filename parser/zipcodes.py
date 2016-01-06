from reader import csvReader

class Zipcodes:

    def __init__(self, filePath):
        zipcodes = {}
        for row in csvReader.read(filePath):
            zipcode = row["zip"]
            lat = row["latitude"]
            lng = row["longitude"]
            zipcodes[zipcode] = [float(lat), float(lng)]
        self.dict = zipcodes

    def geocode(self, code):
        return self.dict[code]

    def contains(self, code):
        return code in self.dict