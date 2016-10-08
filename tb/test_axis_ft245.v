/*

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

*/

// Language: Verilog 2001

`timescale 1ns / 1ps

/*
 * Testbench for axis_ft245
 */
module test_axis_ft245;

// Parameters
parameter WR_SETUP_CYCLES = 3;
parameter WR_PULSE_CYCLES = 7;
parameter RD_PULSE_CYCLES = 8;
parameter RD_WAIT_CYCLES = 5;

// Inputs
reg clk = 0;
reg rst = 0;
reg [7:0] current_test = 0;

reg [7:0] ft245_d_in = 0;
reg ft245_rxf_n = 0;
reg ft245_txe_n = 0;
reg [7:0] input_axis_tdata = 0;
reg input_axis_tvalid = 0;
reg output_axis_tready = 0;

// Outputs
wire [7:0] ft245_d_out;
wire ft245_d_oe;
wire ft245_rd_n;
wire ft245_wr_n;
wire ft245_siwu_n;
wire input_axis_tready;
wire [7:0] output_axis_tdata;
wire output_axis_tvalid;

initial begin
    // myhdl integration
    $from_myhdl(
        clk,
        rst,
        current_test,
        ft245_d_in,
        ft245_rxf_n,
        ft245_txe_n,
        input_axis_tdata,
        input_axis_tvalid,
        output_axis_tready
    );
    $to_myhdl(
        ft245_d_out,
        ft245_d_oe,
        ft245_rd_n,
        ft245_wr_n,
        ft245_siwu_n,
        input_axis_tready,
        output_axis_tdata,
        output_axis_tvalid
    );

    // dump file
    $dumpfile("test_axis_ft245.lxt");
    $dumpvars(0, test_axis_ft245);
end

axis_ft245 #(
    .WR_SETUP_CYCLES(WR_SETUP_CYCLES),
    .WR_PULSE_CYCLES(WR_PULSE_CYCLES),
    .RD_PULSE_CYCLES(RD_PULSE_CYCLES),
    .RD_WAIT_CYCLES(RD_WAIT_CYCLES)
)
UUT (
    .clk(clk),
    .rst(rst),
    .ft245_d_in(ft245_d_in),
    .ft245_d_out(ft245_d_out),
    .ft245_d_oe(ft245_d_oe),
    .ft245_rd_n(ft245_rd_n),
    .ft245_wr_n(ft245_wr_n),
    .ft245_rxf_n(ft245_rxf_n),
    .ft245_txe_n(ft245_txe_n),
    .ft245_siwu_n(ft245_siwu_n),
    .input_axis_tdata(input_axis_tdata),
    .input_axis_tvalid(input_axis_tvalid),
    .input_axis_tready(input_axis_tready),
    .output_axis_tdata(output_axis_tdata),
    .output_axis_tvalid(output_axis_tvalid),
    .output_axis_tready(output_axis_tready)
);

endmodule
