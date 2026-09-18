# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, ReadOnly, NextTimeStep

async def load(dut, value, *, output_en = 1):
    for i in range(0, 8):
        dut.ui_in.value = 0b00000010 | (output_en << 3) | (((1 << i) & value) >> i)
        await ClockCycles(dut.clk, 1)
    dut.ui_in.value = 0b00000100 | (output_en << 3)
    await ClockCycles(dut.clk, 1)
    dut.ui_in.value = 0b00000000 | (output_en << 3)


@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    dut._log.info("Test project behavior")

    await NextTimeStep()
    dut._log.info("");

    dut._log.info("===== Testing high impedance =====")
    dut.ui_in.value = 0b00000000
    await ClockCycles(dut.clk, 1)
    await ReadOnly();
    # assert all(bit == 'z' for bit in dut.uo_out.value.binstr.lower())
    assert dut.uio_pad.value == "ZZZZZZZZ"
    dut._log.info(">>> High impedance PASS")

    await NextTimeStep()
    dut._log.info("");

    dut._log.info("=== Testing reset ===");
    dut.ui_in.value = 0b00001000
    await ClockCycles(dut.clk, 1)
    await ReadOnly();
    assert dut.uio_pad.value != 0
    await NextTimeStep()
    dut.rst_n.value = 0;
    await ReadOnly()
    assert dut.uio_pad.value == 0
    dut._log.info(">>> Reset PASS")

    await NextTimeStep()
    dut._log.info("");

    dut._log.info("=== Testing load ===");
    dut.rst_n.value = 1;
    await load(dut, 67)
    await ReadOnly();
    assert dut.uio_pad.value == 67
    dut._log.info(">>> Load PASS")

    await NextTimeStep()
    dut._log.info("");

    dut._log.info("=== Testing counter from 0-255 ===");
    dut.ui_in.value = 0b00001000
    for i in range(0, 256):
        if i == 0:
            dut.rst_n.value = 0;
            await ClockCycles(dut.clk, 1)
            await NextTimeStep()
        if i == 0:
            dut.rst_n.value = 1;
        else:
            await ClockCycles(dut.clk, 1)
            await ReadOnly()
        assert dut.uio_pad.value == i
        await NextTimeStep()
    dut._log.info(">>> Counter 0-255 PASS")

    await NextTimeStep()
    dut._log.info("");

    dut._log.info("=== Testing counter overflow behaviour ===");
    await load(dut, 255)
    await ReadOnly()
    assert dut.uio_pad.value == 255
    await NextTimeStep()
    await ClockCycles(dut.clk, 1)
    await ReadOnly()
    assert dut.uio_pad.value == 0
    dut._log.info(">>> Counter overflow PASS")

    # await NextTimeStep()
    # dut._log.info("");
