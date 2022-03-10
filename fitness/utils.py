import uuid



def generateRefCode():
    code = str(uuid.uuid4()).replace('_','')[:12]
    return code

