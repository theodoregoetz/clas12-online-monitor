import os
import jpype
import numpy as np

java_started = False

def start_java():
    global java_started
    java_started = True
    jvm_path = jpype.getDefaultJVMPath()
    curdir = os.path.dirname(os.path.realpath(__file__))
    jars = [os.path.join(curdir,'coat-libs-1.0-SNAPSHOT.jar')]

    def classpath(jars):
        for j in jars:
            if not os.path.isabs(j):
                j = os.curdir+os.sep+j
        return os.pathsep.join(jars)

    jpype.startJVM(jvm_path, '-Djava.class.path='+classpath(jars))
    java = jpype.JPackage('java')
    java.lang.System.setOut(java.io.PrintStream(
        java.io.FileOutputStream('/dev/null')))
    java.lang.System.setErr(java.io.PrintStream(
        java.io.FileOutputStream('/dev/null')))

def shutdown_java():
    jpype.shutdownJVM()

class EvioReader(object):
    def __init__(self,fname=None):
        global java_started
        if not java_started:
            start_java()

        curdir = os.path.dirname(os.path.realpath(__file__))

        EvioFactory = jpype.JClass('org.jlab.evio.clas12.EvioFactory')
        EvioSource = jpype.JClass('org.jlab.evio.clas12.EvioSource')

        EvioFactory.loadDictionary(os.path.join(curdir,'bankdefs'))

        self.reader = EvioSource()
        self.reader.dictionary = EvioFactory.getDictionary()

        if fname is not None:
            self.open(fname)

    def open(self,fname):
        self.reader.open(fname)

    def __iter__(self):
        self.reader.reset()
        return self

    def __next__(self):
        if self.reader.hasEvent():
            return EvioEvent(self.reader.getNextEvent())
        else:
            raise StopIteration

class EvioEvent(object):
    def __init__(self,evt):
        self.event = evt

    def bank(self,bankname):
        if self.event.hasBank(bankname):
            return EvioBank(self.event.getBank(bankname))

    def __getitem__(self,key):
        return self.bank(key)

class EvioBank(object):

    def __init__(self,bnk):
        self.bank = bnk
        self.desc = self.bank.getDescriptor()

    def type(self,key):
        types = {
            1: np.int8   ,
            2: np.int16  ,
            3: np.int32  ,
            4: np.int64  ,
            5: np.float32,
            6: np.float64,
        }
        return types[self.desc.getProperty('type',key)]

    def __getitem__(self,key):
        get = {
            np.int8   : self.bank.getByte  ,
            np.int16  : self.bank.getShort ,
            np.int32  : self.bank.getInt   ,
            np.int64  : self.bank.getInt   , # bug: should be getLong?
            np.float32: self.bank.getFloat ,
            np.float64: self.bank.getDouble,
        }
        tp = self.type(key)
        return np.array(get[tp](key), dtype=tp)

    def __getattr__(self,key):
        return self.__getitem__(key)

if __name__ == '__main__':
    '''
    to run this, issue the following command:

        python3 -m clas12monitor.data.evio
    '''

    from matplotlib import pyplot
    import numpy as np

    from clas12monitor import dc

    dcocc = np.zeros((6,6,6,112))

    for evt in EvioReader('exim1690.0001.recon'):
        dchits = evt['HitBasedTrkg::HBHits']
        if dchits is not None:
            hit_data = np.vstack([
                dchits.sector    ,
                dchits.superlayer,
                dchits.layer     ,
                dchits.wire      ]).T - 1
            for wire_id in hit_data:
                dcocc[tuple(wire_id)] += 1

    def transform_data(data):
        a = data.copy().reshape(6,6*6,112)
        a[3:,:,...] = a[3:,::-1,...]
        a.shape = (2,3,6,6,112)
        a = np.rollaxis(a,2,1)
        a = np.rollaxis(a,3,2)
        a = a.reshape(2*6*6,3*112)
        a = np.roll(a,6*6,axis=0)
        return a

    fig = pyplot.figure()
    ax = fig.add_subplot(1,1,1)

    im = ax.imshow(transform_data(dcocc),
        extent=[0,112*3,-6*6,6*6],
        aspect='auto', origin='lower', interpolation='nearest')
    ax.grid(True)

    _=ax.xaxis.set_ticks([0,112,112*2,112*3])
    _=ax.xaxis.set_ticklabels([1,112,112,112])

    yticks = np.linspace(-36,36,2*6+1,dtype=int)
    ylabels = abs(yticks)
    ylabels[len(ylabels)//2] = 1

    _=ax.yaxis.set_ticks(list(yticks))
    _=ax.yaxis.set_ticklabels([str(x) for x in ylabels])

    for sec in range(6):
        _ = ax.text(0.34*(sec%3) + 0.1, 1.02 if sec<3 else -0.06,
                    'Sector {}'.format(sec+1),
                    transform=ax.transAxes)

    cb = ax.figure.colorbar(im, ax=ax)

    pyplot.show()
