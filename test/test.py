# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, ReadOnly, NextTimeStep


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
    dut.uio_in.value = 0b00000000
    await ReadOnly();
    assert dut.uo_out.value == "ZZZZZZZZ"
    dut._log.info(">>> High impedance PASS")

    await NextTimeStep()
    dut._log.info("");

    dut._log.info("=== Testing reset ===");
    dut.rst_n.value = 0;
    dut.uio_in.value = 0b00000010
    await ReadOnly()
    assert dut.uo_out.value == 0
    dut._log.info(">>> Reset PASS")

    await NextTimeStep()
    dut._log.info("");

    dut._log.info("=== Testing load ===");
    dut.rst_n.value = 1;
    dut.uio_in.value = 0b00000011
    dut.ui_in.value = 67
    await ClockCycles(dut.clk, 1)
    await ReadOnly()
    assert dut.uo_out.value == 67
    dut._log.info(">>> Load PASS")

    await NextTimeStep()
    dut._log.info("");

    dut._log.info("=== Testing counter from 0-255 ===");
    dut.uio_in.value = 0b00000010
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
        assert dut.uo_out.value == i
        await NextTimeStep()
    dut._log.info(">>> Counter 0-255 PASS")

    await NextTimeStep()
    dut._log.info("");

    dut._log.info("=== Testing counter overflow behaviour ===");
    dut.uio_in.value = 0b00000011
    dut.ui_in.value = 255
    await ClockCycles(dut.clk, 1)
    await ReadOnly()
    assert dut.uo_out.value == 255
    await NextTimeStep()
    dut.uio_in.value = 0b00000010
    await ClockCycles(dut.clk, 1)
    await ReadOnly()
    assert dut.uo_out.value == 0
    dut._log.info(">>> Counter overflow PASS")

    await NextTimeStep()
    dut._log.info("");
