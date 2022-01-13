import socket
import struct
import time


__all__ = ['TracertError', 'Pytracert']


class TracertError(Exception):
    def __init__(self, msg):
        self.msg = msg


class Pytracert:
    # https://www.ibm.com/docs/en/power8?topic=commands-traceroute-command
    PORT = 33434
    TRIES = 3

    def __init__(self, destination: str, hops: int = 30):
        self.dest = destination
        self.hops = hops
        self.__icmp = self.__configure_receiver()
        self.__udp = self.__configure_sender()

    @staticmethod
    def __configure_receiver():
        icmp_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        try:
            icmp_socket.bind(('', Pytracert.PORT))
        except socket.error as e:
            raise TracertError(f"Couldn't bind receiver socket: {e}")

        timeout = struct.pack("ll", 3, 0)
        icmp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, timeout)

        return icmp_socket

    @staticmethod
    def __configure_sender():
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        return udp_socket

    def __send(self, sender, ttl):
        sender.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
        sender.sendto(b'', (self.dest, Pytracert.PORT))

    @staticmethod
    def __receive_address(receiver):
        try:
            return receiver.recvfrom(1024)[1]
        except socket.error:
            return None

    @staticmethod
    def __format_output(address, evaluation_time):
        if not address:
            print("*", end=' ')
            return
        try:
            address_name = socket.gethostbyaddr(address[0])[0]
        except socket.error:
            address_name = address[0]
        print(address_name, f"({address[0]})", evaluation_time, 'ms', end=' ')

    def run(self):
        try:
            dest_address = socket.gethostbyname(self.dest)
        except socket.error:
            raise TracertError(f"{self.dest}: Name or service not known")

        print(f'traceroute to {dest_address} ({self.dest}), {self.hops} hops max')

        for ttl in range(1, self.hops + 1):
            receiver = self.__icmp
            sender = self.__udp
            print(f'{ttl:<3}', end=' ')

            for _ in range(Pytracert.TRIES):
                time_start = time.perf_counter_ns()
                self.__send(sender=sender, ttl=ttl)
                address = self.__receive_address(receiver)
                time_end = time.perf_counter_ns()
                self.__format_output(address, (time_end - time_start) // 1e6)
                if address and address[0] == dest_address:
                    return 0

            print()

        print(f'Could not reach {dest_address} ({self.dest})\nTry to increase number of hops')
        return 0
