# Nicholas West, 2025
# Cocotb test file for the whole datapath
# Kinda fixed in its functionality, but we don't want to make a whole emulator

import cocotb
from cocotb.clock import Clock
import cocotb.triggers

async def memoryCorutine(dut):
	matrixData = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
	vectorData = [1, 1, 10, 1, 2, 2, 10, 1, 0, 0, 10, 1]
	
	while True:
		try:
			await cocotb.triggers.RisingEdge(dut.clk)
			if (dut.readAddr.value.integer >= 0x8000 and dut.readAddr.value.integer <= 0x803C and dut.readAddr.value.integer & 0x3 == 0):
				dut.dataIn.value = matrixData[(dut.readAddr.value - 0x8000) >> 2]
			elif (dut.readAddr.value.integer >= 0xF000 and dut.readAddr.value.integer <= 0xF02C and dut.readAddr.value.integer & 0x3 == 0):
				dut.dataIn.value = vectorData[(dut.readAddr.value - 0xF000) >> 2]
			else:
				dut.dataIn.value = 0xDEADBEEF
		except IndexError:
			raise IndexError
		except:
			continue

@cocotb.test()
async def test(dut):
	dut._log.info("Start")

	cocotb.start_soon(memoryCorutine(dut))

	# Set the clock period to 10 ns (100 MHz)
	clock = Clock(dut.clk, 10, units="ns")
	cocotb.start_soon(clock.start())

	# Reset
	dut._log.info("Reset")
	dut.reset.value = 0
	dut.start.value = 0
	dut.workItemCount.value = 2
	dut.matrixInAddr.value = 0x8000
	dut.dataInAddr.value = 0xF000
	dut.dataOutAddr.value = 0
	await cocotb.triggers.ClockCycles(dut.clk, 10)
	dut.reset.value = 1

	dut._log.info("Test project behavior")

	await cocotb.triggers.ClockCycles(dut.clk, 10) # matproc should be in idle

	assert dut.mp.controller.state.value.integer == 0

	dut.start.value = 1
	
	await cocotb.triggers.ClockCycles(dut.clk, 2)

	assert dut.mp.controller.state.value.integer == 1

	await cocotb.triggers.ClockCycles(dut.clk, 16)

	assert dut.mp.controller.state.value.integer == 2

	await cocotb.triggers.ClockCycles(dut.clk, 10)
