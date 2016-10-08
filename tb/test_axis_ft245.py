#!/usr/bin/env python
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
import os

import axis_ep
import ft245

module = 'axis_ft245'
testbench = 'test_%s' % module

srcs = []

srcs.append("../rtl/%s.v" % module)
srcs.append("%s.v" % testbench)

src = ' '.join(srcs)

build_cmd = "iverilog -o %s.vvp %s" % (testbench, src)

def bench():

    # Parameters
    WR_SETUP_CYCLES = 3
    WR_PULSE_CYCLES = 7
    RD_PULSE_CYCLES = 8
    RD_WAIT_CYCLES = 5

    # Inputs
    clk = Signal(bool(0))
    rst = Signal(bool(0))
    current_test = Signal(intbv(0)[8:])

    ft245_d_in = Signal(intbv(0)[8:])
    ft245_rxf_n = Signal(bool(1))
    ft245_txe_n = Signal(bool(1))
    input_axis_tdata = Signal(intbv(0)[8:])
    input_axis_tvalid = Signal(bool(0))
    output_axis_tready = Signal(bool(0))

    # Outputs
    ft245_d_out = Signal(intbv(0)[8:])
    ft245_d_oe = Signal(bool(0))
    ft245_rd_n = Signal(bool(1))
    ft245_wr_n = Signal(bool(1))
    ft245_siwu_n = Signal(bool(1))
    input_axis_tready = Signal(bool(0))
    output_axis_tdata = Signal(intbv(0)[8:])
    output_axis_tvalid = Signal(bool(0))

    # sources and sinks
    source_pause = Signal(bool(0))
    sink_pause = Signal(bool(0))

    source = axis_ep.AXIStreamSource()

    source_logic = source.create_logic(
        clk,
        rst,
        tdata=input_axis_tdata,
        tvalid=input_axis_tvalid,
        tready=input_axis_tready,
        pause=source_pause,
        name='source'
    )

    sink = axis_ep.AXIStreamSink()

    sink_logic = sink.create_logic(
        clk,
        rst,
        tdata=output_axis_tdata,
        tvalid=output_axis_tvalid,
        tready=output_axis_tready,
        pause=sink_pause,
        name='sink'
    )

    # FT245
    ft245_inst = ft245.FT245()

    ft245_logic = ft245_inst.create_logic(
        d_in=ft245_d_out,
        d_out=ft245_d_in,
        rd_n=ft245_rd_n,
        wr_n=ft245_wr_n,
        rxf_n=ft245_rxf_n,
        txe_n=ft245_txe_n,
        wr_inactive_to_txe=25,
        txe_inactive_after_wr=80,
        rd_to_data=50,
        rd_inactive_to_rxf=25,
        rxf_inactive_after_rd=80,
        name='ft245'
    )

    # DUT
    if os.system(build_cmd):
        raise Exception("Error running build command")

    dut = Cosimulation(
        "vvp -m myhdl %s.vvp -lxt2" % testbench,
        clk=clk,
        rst=rst,
        current_test=current_test,
        ft245_d_in=ft245_d_in,
        ft245_d_out=ft245_d_out,
        ft245_d_oe=ft245_d_oe,
        ft245_rd_n=ft245_rd_n,
        ft245_wr_n=ft245_wr_n,
        ft245_rxf_n=ft245_rxf_n,
        ft245_txe_n=ft245_txe_n,
        ft245_siwu_n=ft245_siwu_n,
        input_axis_tdata=input_axis_tdata,
        input_axis_tvalid=input_axis_tvalid,
        input_axis_tready=input_axis_tready,
        output_axis_tdata=output_axis_tdata,
        output_axis_tvalid=output_axis_tvalid,
        output_axis_tready=output_axis_tready
    )

    @always(delay(4))
    def clkgen():
        clk.next = not clk

    @instance
    def check():
        yield delay(100)
        yield clk.posedge
        rst.next = 1
        yield clk.posedge
        rst.next = 0
        yield clk.posedge
        yield delay(100)
        yield clk.posedge

        # testbench stimulus

        yield clk.posedge
        print("test 1: write walk")
        current_test.next = 1

        source.write(b'\x00\x01\x02\x04\x08\x10\x20\x40\x80')
        yield clk.posedge

        yield input_axis_tvalid.negedge

        yield delay(100)

        yield clk.posedge

        rx_data = bytearray(ft245_inst.read())
        print(rx_data)
        assert rx_data == b'\x00\x01\x02\x04\x08\x10\x20\x40\x80'

        yield clk.posedge
        print("test 2: write walk 2")
        current_test.next = 2

        source.write(b'\x00\x01\x03\x07\x0F\x1F\x3F\x7F\xFF')
        yield clk.posedge

        yield input_axis_tvalid.negedge

        yield delay(100)

        yield clk.posedge

        rx_data = bytearray(ft245_inst.read())
        print(rx_data)
        assert rx_data == b'\x00\x01\x03\x07\x0F\x1F\x3F\x7F\xFF'

        yield delay(100)

        yield clk.posedge
        print("test 3: read walk")
        current_test.next = 3

        ft245_inst.write(b'\x00\x01\x02\x04\x08\x10\x20\x40\x80')
        yield clk.posedge

        yield delay(2000)

        yield delay(100)

        yield clk.posedge

        rx_data = bytearray(sink.read())
        print(rx_data)
        assert rx_data == b'\x00\x01\x02\x04\x08\x10\x20\x40\x80'

        yield clk.posedge
        print("test 4: read walk 2")
        current_test.next = 4

        ft245_inst.write(b'\x00\x01\x03\x07\x0F\x1F\x3F\x7F\xFF')
        yield clk.posedge

        yield delay(2000)

        yield delay(100)

        yield clk.posedge

        rx_data = bytearray(sink.read())
        print(rx_data)
        assert rx_data == b'\x00\x01\x03\x07\x0F\x1F\x3F\x7F\xFF'

        yield delay(100)

        raise StopSimulation

    return dut, source_logic, sink_logic, ft245_logic, clkgen, check

def test_bench():
    sim = Simulation(bench())
    sim.run()

if __name__ == '__main__':
    print("Running test...")
    test_bench()
