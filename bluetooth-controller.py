import bluetooth
import struct
import time
from datetime import datetime


device_address = '00:E0:4C:B3:D0:E3'  #MAC-address
port = 1
# UUID для SPP-сервісу
spp_uuid = "00001101-0000-1000-8000-00805f9b34fb"


class DataPacket:
    def __init__(self, command):
        self.prefix = bytes.fromhex("01fe")
        self.key = struct.pack('>i', 21384)  # '>' means big-endian
        self.arg1 = struct.pack('>i', 0)
        self.arg2 = struct.pack('>i', 0)
        self.command = bytes(command)

    def getByteArray(self):
        command_length = struct.pack('>h', len(self.command))
        byte_array = self.prefix + self.key + self.arg1 + self.arg2 + command_length + self.command
        current_length = len(byte_array) + 1  
        padding_needed = (4 - (current_length % 4)) % 4
        byte_array += bytes([0] * padding_needed)
        total_length = struct.pack('b', 1 + len(byte_array))
        byte_array = self.prefix + self.key + total_length + self.arg1 + self.arg2 + command_length + self.command + bytes([0] * padding_needed)

        return byte_array


class Device:
    def __init__(self, device_address):
        self.sock = connectToDevice(device_address, port)

    def sendCommand(self, command_bytes):
        data_packet = DataPacket(command_bytes)
        byte_array = data_packet.getByteArray()
        self.sock.send(byte_array)
        hex_combined_data = byte_array.hex()
        print("Надіслано:", hex_combined_data)

    def sendCustomCommand(self, custom_command_bytes):
        self.sock.send(custom_command_bytes)
        hex_combined_data = custom_command_bytes.hex()
        print("Надіслано:", hex_combined_data)

    def recieveResponse(self):
        response = self.sock.recv(1024)
        return response

    def disconnect(self):
        self.sock.close()




def connectToDevice(device_address, port):
    try:
        sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        sock.connect((device_address, port))
        return sock

    except bluetooth.btcommon.BluetoothError as e:
        print(f"Помилка підключення до Bluetooth-пристрою: {e}")
        exit()


class CalendarUtil:
    def encodeDateTime(current_time):
        # Визначення компонентів дати та часу
        year = current_time.year
        month = current_time.month
        day = current_time.day
        hour = current_time.hour
        minute = current_time.minute
        second = current_time.second

        # Врахування Little Endian формату для року
        year_part = format(year % 256, '02x') + format(year // 256, '02x')

        month_part = format(month - 1, '02x')

        # Форматування дня, години, хвилин і секунд
        day_part = format(day, '02x')
        hour_part = format(hour, '02x')
        minute_part = format(minute, '02x')
        second_part = format(second, '02x')

        # З'єднання всіх частин в один шістнадцятковий рядок
        hex_string = year_part + month_part + day_part + hour_part + minute_part + second_part
        return hex_string


    def decodeDateTime(hex_string):
        year_part = hex_string[0:4]
        month_part = hex_string[4:6]
        day_part = hex_string[6:8]
        hour_part = hex_string[8:10]
        minute_part = hex_string[10:12]
        second_part = hex_string[12:14]

        year = int(year_part[2:4], 16) * 256 + int(year_part[0:2], 16)
        month = int(month_part, 16)
        day = int(day_part, 16)
        hour = int(hour_part, 16)
        minute = int(minute_part, 16)
        second = int(second_part, 16)

        return year, month, day, hour, minute, second


if __name__ == "__main__":
    my_device = Device(device_address)
    my_device.sendCustomCommand(b'01234567') #sending test bytes array
    my_device.sendCustomCommand(bytes.fromhex('01fe0000510210000000008000000080')) #if protocol supported
    response = my_device.recieveResponse()
    print(response.hex())
    my_device.sendCustomCommand(bytes.fromhex('01fe0000530018000000000000000080' + CalendarUtil.encodeDateTime(datetime.now())) + bytes([0])) #send current datetime
    #my_device.sendCommand(bytes([81, 33, 129, 0])) # 0 < warm < 128 < cold < 255
    #my_device.sendCommand(bytes([81, 33, 139, 65])) # 0 < dim < 128 < bright < 255
    #my_device.sendCommand(bytes([81, 33, 129, 255, 255, 255])) # office light
    #my_device.sendCommand(bytes([81, 33, 130, 112])) # red pulse
    #my_device.sendCommand(bytes([81, 33, 130, 33])) # rgb switching
    #my_device.sendCommand(bytes([81, 33, 130, 32])) # smooth transition
    #my_device.sendCommand(bytes([81, 33, 130, 65])) # rgb switching on-off
    #my_device.sendCommand(bytes([81, 33, 128, 44, 120, 100])) #rgb
    # time.sleep(4)
    #my_device.sendCommand(bytes([81, 33, 128, 0, 0, 0])) #rgb
    # time.sleep(4)
    #my_device.sendCommand(bytes([81, 33, 128, 12, 77, 110])) #rgb
    # time.sleep(4)
    #my_device.sendCommand(bytes([81, 33, 120]))
    # time.sleep(4)
    #my_device.sendCommand(bytes([81, 33, 121]))
    my_device.disconnect()
