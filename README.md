# Verilog FT245 Readme

For more information and updates: http://alexforencich.com/wiki/en/verilog/ft245/start

GitHub repository: https://github.com/alexforencich/verilog-ft245

## Introduction

This is a basic FTDI FT245 USB FIFO to AXI Stream IP core, written in Verilog
with MyHDL testbenches.

## Documentation

The main code for the core exists in the rtl subdirectory.  axis_ft245.v
contains the entire implementation.  

### Source Files

    axis_ft245.v           : FTDI FT245 to AXI stream bridge

### AXI Stream Interface Example

two byte transfer with sink pause after each byte

              __    __    __    __    __    __    __    __    __
    clk    __/  \__/  \__/  \__/  \__/  \__/  \__/  \__/  \__/  \__
                    _____ _________________
    tdata  XXXXXXXXX_D0__X_D1______________XXXXXXXXXXXXXXXXXXXXXXXX
                    _______________________
    tvalid ________/                       \_______________________
           ______________             _____             ___________
    tready               \___________/     \___________/


## Testing

Running the included testbenches requires MyHDL and Icarus Verilog.  Make sure
that myhdl.vpi is installed properly for cosimulation to work correctly.  The
testbenches can be run with a Python test runner like nose or py.test, or the
individual test scripts can be run with python directly.

### Testbench Files

    tb/axis_ep.py        : MyHDL AXI Stream endpoints
    tb/ft245.py          : MyHDL FT245 model
