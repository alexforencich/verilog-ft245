"""

Copyright (c) 2016 Alex Forencich

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""

from myhdl import *

class FT245(object):
    def __init__(self):
        self.tx_queue = bytearray()
        self.rx_queue = bytearray()
        self.flag = Signal(bool(False))

    def write(self, data):
        self.tx_queue.extend(data)
        self.flag.next = not self.flag

    def read(self, count=-1):
        ret = None
        if count < 0:
            count = len(self.rx_queue)
        if len(self.rx_queue) > 0:
            ret = self.rx_queue[:count]
            del self.rx_queue[:count]
            self.flag.next = not self.flag
        return ret

    # FT245/FT2232D timings:
    # wr_inactive_to_txe=25
    # txe_inactive_after_wr=80
    # rd_to_data=50
    # rd_inactive_to_rxf=25
    # rxf_inactive_after_rd=80
    #
    # FT2232H timings:
    # wr_inactive_to_txe=14
    # txe_inactive_after_wr=49
    # rd_to_data=14
    # rd_inactive_to_rxf=14
    # rxf_inactive_after_rd=49

    def create_logic(self,
            d_in=None,
            d_out=None,
            d_oe=Signal(bool(False)),
            rd_n=Signal(bool(True)),
            wr_n=Signal(bool(True)),
            rxf_n=Signal(bool(True)),
            txe_n=Signal(bool(False)),
            wr_inactive_to_txe=25,
            txe_inactive_after_wr=80,
            rd_to_data=50,
            rd_inactive_to_rxf=25,
            rxf_inactive_after_rd=80,
            name=None):

        @instance
        def read_logic():
            while True:
                rxf_n.next = 1

                if len(self.tx_queue) == 0:
                    yield self.flag
                else:
                    yield delay(rxf_inactive_after_rd)
                    rxf_n.next = 0
                    yield rd_n.negedge
                    yield delay(rd_to_data)
                    d = self.tx_queue.pop(0)
                    if name is not None:
                        print("[%s] Sending data byte %d" % (name, d))
                    d_out.next = d
                    d_oe.next = 1
                    yield rd_n.posedge
                    d_oe.next = 0
                    yield delay(rd_inactive_to_rxf)

        @instance
        def write_logic():
            while True:
                txe_n.next = 1

                if len(self.rx_queue) >= 128:
                    yield self.flag
                else:
                    yield delay(txe_inactive_after_wr)
                    txe_n.next = 0
                    yield wr_n.negedge
                    if name is not None:
                        print("[%s] Got data byte %d" % (name, int(d_in)))
                    self.rx_queue.append(int(d_in))
                    yield delay(wr_inactive_to_txe)

        return read_logic, write_logic

