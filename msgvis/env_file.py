import os

def read(envFile='.env'):
    result = {}
    try:
        with open(envFile) as f:
            content = f.read()
    except IOError:
        content = ''
        print "Env file %s not found!" % envFile

    import re
    for line in content.splitlines():
        m1 = re.match(r'\A([A-Za-z_0-9]+)=(.*)\Z', line)
        if m1:
            key, val = m1.group(1), m1.group(2)

            m2 = re.match(r"\A'(.*)'\Z", val)
            if m2:
                val = m2.group(1)

            m3 = re.match(r'\A"(.*)"\Z', val)
            if m3:
                val = re.sub(r'\\(.)', r'\1', m3.group(1))

            result[key] = val

    return result

def load(envFile='.env'):

    values = read(envFile)
    for key in values:
        os.environ.setdefault(key, values[key])
