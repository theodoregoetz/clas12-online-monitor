import os
import jpype

java_started = False

def start_java():
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

    global jvm_started
    jvm_started = True

def shutdown_java():
    jpype.shutdownJVM()

class EvioReader(object):
    def __init__(self,fname=None):
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
        while self.reader.hasEvent():
            yield EvioEvent(self.reader.getNextEvent())

class EvioEvent(object):
    def __init__(self,evt):
        self.event = evt

    def bank(self,bankname):
        if self.event.hasBank(bankname):
            return EvioBank(self.event.getBank(bankname))
        else:
            return None

class EvioBank(object):
    def __init__(self,bnk):
        self.bank = bnk

    def __getitem__(self,key):
        return list(self.bank.getInt(key))


if __name__ == '__main__':

    from matplotlib import pyplot
    import numpy as np

    from clas12monitor import dc

    dcocc = np.zeros((6,6,6,112))

    for evt in EvioReader('exim1690.0001.recon'):
        dchits = evt.bank('HitBasedTrkg::HBHits')
        if dchits is not None:
            hit_data = np.array([
                dchits['sector']    ,
                dchits['superlayer'],
                dchits['layer']     ,
                dchits['wire']      ]) - 1
            for wire_id in zip(*hit_data):
                dcocc[wire_id] += 1

    fig = pyplot.figure()
    ax = fig.add_subplot(1,1,1)
    pt,(cb,cax) = dc.plots.plot_wiremap(ax,dcocc)
    cax.set_ylabel(r'Hits found in Reconstruction')
    pyplot.show()
