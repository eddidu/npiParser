from reader import csvReader

class CountryCodes:

    def __init__(self, filePath):
        countryDict = {}
        for row in csvReader.read(filePath):
            code = row["code"].strip()
            countryName = row["country"].strip()
            countryDict[code] = countryName
        self.dict = countryDict

    def getCountryName(self, code):
        return self.dict[code]     
