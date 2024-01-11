import crcmod
def compute_crc(file_path):
    crc_value = 0
    crc_func = crcmod.mkCrcFun(0x142F0E1EBA9EA3693, initCrc=0, xorOut=0xffffffffffffffff, rev=True)

    with open(file_path, 'rb') as file:
        data = file.read(1024)

        while data:
            crc_value = crc_func(data, crc_value)
            data = file.read(1024)

    return crc_value

file_path = 'happy.exe'
crc = compute_crc(file_path)
print('文件的CRC校验码为:', crc)