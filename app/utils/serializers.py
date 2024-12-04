def serialize_individu(individu):
    individu["_id"] = str(individu["_id"])
    return individu

def serialize_pointage(pointage):
    pointage["_id"] = str(pointage["_id"])
    return pointage
