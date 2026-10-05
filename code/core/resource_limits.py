"""Windows resource limits and outward rational decimal formatting."""
import ctypes
from fractions import Fraction as F
JOB=None

class IO(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint64) for name in ('ro','wo','oo','rt','wt','ot')]

class BASIC(ctypes.Structure):
    _fields_ = [('pu',ctypes.c_int64),('ju',ctypes.c_int64),('flags',ctypes.c_uint32),
                ('minws',ctypes.c_size_t),('maxws',ctypes.c_size_t),('active',ctypes.c_uint32),
                ('affinity',ctypes.c_size_t),('priority',ctypes.c_uint32),('scheduling',ctypes.c_uint32)]

class LIMIT(ctypes.Structure):
    _fields_ = [('basic',BASIC),('io',IO),('process_memory',ctypes.c_size_t),
                ('job_memory',ctypes.c_size_t),('peak_process',ctypes.c_size_t),('peak_job',ctypes.c_size_t)]

class MEMORY(ctypes.Structure):
    _fields_ = [('length',ctypes.c_uint32),('load',ctypes.c_uint32)] + [
        (name,ctypes.c_uint64) for name in ('total_physical','available_physical','total_commit',
        'available_commit','total_virtual','available_virtual','available_extended_virtual')]

def hard_job():
    global JOB
    k=ctypes.windll.kernel32
    k.CreateJobObjectW.restype=ctypes.c_void_p
    k.GetCurrentProcess.restype=ctypes.c_void_p
    k.SetInformationJobObject.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_void_p,ctypes.c_uint32]
    k.AssignProcessToJobObject.argtypes=[ctypes.c_void_p,ctypes.c_void_p]
    JOB=k.CreateJobObjectW(None,None)
    info=LIMIT(); info.basic.flags=0x2000|0x200; info.job_memory=256<<20
    assert JOB and k.SetInformationJobObject(JOB,9,ctypes.byref(info),ctypes.sizeof(info))
    assert k.AssignProcessToJobObject(JOB,k.GetCurrentProcess())

def decimal_enclosure(low, high, digits=24):
    scale=10**digits
    def fmt(value):
        return ('-' if value<0 else '')+str(abs(value)//scale)+'.'+str(abs(value)%scale).zfill(digits)
    low=F(low); high=F(high)
    a=low.numerator*scale//low.denominator
    b=-((-high.numerator*scale)//high.denominator)
    return [fmt(a),fmt(b)]
