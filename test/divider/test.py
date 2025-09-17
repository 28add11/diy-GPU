# Nicholas West, 2025
# Cocotb test file for the whole datapath
# Kinda fixed in its functionality, but we don't want to make a whole emulator

import cocotb
from cocotb.clock import Clock
import cocotb.triggers

from random import randint

@cocotb.test()
async def test(dut):
	dut.log.info("Start")

	# Set the clock period to 10 ns (100 MHz)
	clock = Clock(dut.clk, 10, units="ns")
	cocotb.start_soon(clock.start())

	# Reset
	dut.log.info("Reset")
	dut.reset.value = 0
	dut.start.value = 0
	dut.numerator.value = 0
	dut.denominator.value = 0
	await cocotb.triggers.ClockCycles(dut.clk, 10)
	dut.reset.value = 1

	dut.log.info("Test project behavior")

	await cocotb.triggers.ClockCycles(dut.clk, 1)

	numerator = -1
	denominator = 1
	dut.numerator.value = numerator
	dut.denominator.value = denominator

	result = numerator / denominator

	dut.start.value = 1 
	await cocotb.triggers.ClockCycles(dut.clk, 1) # Let start latch
	dut.start.value = 0
	await cocotb.triggers.RisingEdge(dut.finished)
	await cocotb.triggers.ClockCycles(dut.clk, 1)
	
	assert dut.quotient.value.signed_integer == int(result)

	numerator = 1821519698
	denominator = -1536117864
	dut.numerator.value = numerator
	dut.denominator.value = denominator

	result = numerator / denominator

	dut.start.value = 1 
	await cocotb.triggers.ClockCycles(dut.clk, 1)
	dut.start.value = 0
	await cocotb.triggers.RisingEdge(dut.finished)
	await cocotb.triggers.ClockCycles(dut.clk, 1)
	
	assert dut.quotient.value.signed_integer == int(result)
	
	for randTestCase in range(100000):

		numerator = randint(-2**31, 2**31 - 1)
		denominator = randint(-2**31, numerator + 1)
		while (denominator == 0):
			denominator = randint(-2**31, numerator + 1)
		dut.numerator.value = numerator
		dut.denominator.value = denominator

		result = numerator / denominator

		dut.start.value = 1 
		await cocotb.triggers.ClockCycles(dut.clk, 1) # Let start latch
		dut.start.value = 0
		await cocotb.triggers.RisingEdge(dut.finished)
		await cocotb.triggers.ReadOnly() # For reads
		
		assert dut.quotient.value.signed_integer == int(result)

		await cocotb.triggers.NextTimeStep() # Sync up
