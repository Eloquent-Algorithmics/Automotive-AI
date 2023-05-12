from j2534_cffi import find_j2534_passthru_dlls

for iface in find_j2534_passthru_dlls():
    print(iface)