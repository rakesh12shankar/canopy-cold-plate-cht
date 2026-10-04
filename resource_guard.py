"""Wait for other Fluent compute processes without stopping other tasks."""
import ctypes
import time
import psutil

class MemoryStatus(ctypes.Structure):
    _fields_ = [('length', ctypes.c_ulong), ('load', ctypes.c_ulong),
                ('physical_total', ctypes.c_ulonglong), ('physical_free', ctypes.c_ulonglong),
                ('pagefile_total', ctypes.c_ulonglong), ('pagefile_free', ctypes.c_ulonglong),
                ('virtual_total', ctypes.c_ulonglong), ('virtual_free', ctypes.c_ulonglong),
                ('extended_free', ctypes.c_ulonglong)]

def wait_for_resources(min_commit_gb=10):
    announced=False
    while True:
        workers=[]
        for p in psutil.process_iter(['pid','name','cmdline']):
            if (p.info['name'] or '').lower().startswith('fl_mpi'):
                workers.append(p.info['pid'])
            elif any('microchannel-heat-sink-benchmark' in arg and 'run_fluent.py' in arg for arg in (p.info['cmdline'] or [])):
                workers.append(p.info['pid'])
        status=MemoryStatus();status.length=ctypes.sizeof(status)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            raise OSError('Cannot read Windows memory status')
        if not workers and status.pagefile_free/1024**3 >= min_commit_gb:
            print('RESOURCE_GUARD_READY', round(status.pagefile_free/1024**3,2), 'GB commit available', flush=True)
            return
        if not announced:
            print('RESOURCE_GUARD_WAITING: another Fluent worker or insufficient commit capacity; no processes will be stopped.', flush=True)
            announced=True
        if (ROOT/'cancel_wait').exists():
            raise RuntimeError('Resource wait canceled by local marker')
        time.sleep(10)
