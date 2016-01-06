from reader import csvReader

class Doctors:

    DOCTOR_CODE = "Allopathic & Osteopathic Physicians"

    def __init__(self, filePath, doctorCode=DOCTOR_CODE):
        group = set()
        specialty = {}
        for row in csvReader.read(filePath):
            if row["Grouping"] != doctorCode:
                continue
            code = row["Code"]
            groupName = row["Classification"]
            specialtyName = row["Specialization"]

            if not specialtyName:
                specialty[code] = (groupName, groupName)
            else:
                specialty[code] = (groupName, specialtyName)

            group.add(groupName)

        self.group = group
        self.specialty = specialty

    def containsCode(self, code):
        return code in self.specialty

    def getGroupName(self, code):
        return self.specialty[code][0]

    def getSpecialtyName(self, code):
        return self.specialty[code][1]

    def toMongoCollection(self):
        l = []
        for name in self.group:
            l.append({"name": name})
        return l