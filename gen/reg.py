REG = {}
def circuit(num, section, title):
    def deco(f):
        REG[num] = dict(num=num, section=section, title=title, fn=f)
        return f
    return deco
