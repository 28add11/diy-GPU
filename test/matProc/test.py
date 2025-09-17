# Nicholas West, 2025
# Cocotb test file for the whole datapath
# Kinda fixed in its functionality, but we don't want to make a whole emulator

import cocotb
from cocotb.clock import Clock
import cocotb.triggers

from random import randint

def multVecMatrix(matrix, vec):
	"""
	Multiplies a 4x4 matrix by a 3D vector.
	Column major order, with vectors treated as 1x4 matrices (as if they're to the right of the multiplication sign/Post-multiplied)
	Returns a new 4D vector with w coordinate.
	"""

	listResult = [0.0 for i in range(4)]
	listResult[0] = matrix[0][0] * vec[0] + matrix[0][1] * vec[1] + matrix[0][2] * vec[2] + matrix[0][3] * vec[3]
	listResult[1] = matrix[1][0] * vec[0] + matrix[1][1] * vec[1] + matrix[1][2] * vec[2] + matrix[1][3] * vec[3]
	listResult[2] = matrix[2][0] * vec[0] + matrix[2][1] * vec[1] + matrix[2][2] * vec[2] + matrix[2][3] * vec[3]
	listResult[3] = matrix[3][0] * vec[0] + matrix[3][1] * vec[1] + matrix[3][2] * vec[2] + matrix[3][3] * vec[3]

	return listResult

@cocotb.coroutine
async def memoryCorutine(dut):
	matrixData = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
	vectorData = [1, 1, 10, 1]
	
	while True:
		await cocotb.triggers.RisingEdge(dut.clk)
		if (dut.readAddr.value.is_resolvable):
			if (dut.readAddr.value.integer >= 0x8000 and dut.readAddr.value.integer <= 0x803C and dut.readAddr.value.integer & 0x3 == 0):
				dut.dataIn.value = matrixData[(dut.readAddr.value - 0x8000) >> 2]
			elif (dut.readAddr.value.integer >= 0xF000 and dut.readAddr.value.integer <= 0xF02C and dut.readAddr.value.integer & 0x3 == 0):
				dut.dataIn.value = vectorData[(dut.readAddr.value - 0xF000) >> 2]
			else:
				dut.dataIn.value = 0xDEADBEEF
		
		if (dut.writeEn.value.is_resolvable):
			if (dut.writeEn.value == 1):
				if (dut.writeAddr.value.is_resolvable):
					dut.log.info("Write at " + str(dut.writeAddr.value.integer) + " of " + str(dut.writeData.value.integer))
				else:
					dut.log.error("Write requested with bad values")

@cocotb.test()
async def test(dut):
	dut.log.info("Start")

	#cocotb.start_soon(memoryCorutine(dut))

	# Set the clock period to 10 ns (100 MHz)
	clock = Clock(dut.clk, 10, units="ns")
	cocotb.start_soon(clock.start())

	# Reset
	dut.log.info("Reset")
	dut.reset.value = 0
	dut.start.value = 0
	dut.workItemCount.value = 0 # Just means 1 item, should change in later rev
	dut.matrixInAddr.value = 0x8000
	dut.dataInAddr.value = 0xF000
	dut.dataOutAddr.value = 0
	await cocotb.triggers.ClockCycles(dut.clk, 10)
	dut.reset.value = 1

	dut.log.info("Test project behavior")

	await cocotb.triggers.ClockCycles(dut.clk, 10) # matproc should be in idle

	assert dut.mp.controller.state.value.integer == 0

	dut.start.value = 1

	matrixData = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
	tempBatchVectorData = [randint(-23170, 23170) for i in range(16)]
	tempBatchResult = [0 for i in range(16)]
	vectorData = [1, 1, 10, 1]
	result = [0, 0, 0, 0]
	
	# Testing outside loop since batch processing shouldn't need start
	dut.workItemCount.value = 3
	dut.start.value = 1 
	await cocotb.triggers.ClockCycles(dut.clk, 1) # Required for synchronization
	await cocotb.triggers.RisingEdge(dut.mp.controller.load) # Raises on state transition to loadmatrix
	dut.start.value = 0

	for batchVectorTests in range(1):

		testCasesGood = 0
		loopCountFail = 0

		tempBatchResult = tempBatchVectorData

		while testCasesGood < 16  and loopCountFail <= 100:

			if (dut.readAddr.value.is_resolvable):
				if (dut.readAddr.value.integer >= 0x8000 and dut.readAddr.value.integer <= 0x803C and dut.readAddr.value.integer & 0x3 == 0):
					fullIndex = (dut.readAddr.value - 0x8000) >> 2
					dut.dataIn.value = matrixData[(fullIndex & 0xC) >> 2][fullIndex & 0x3]
				elif (dut.readAddr.value.integer >= 0xF000 and dut.readAddr.value.integer <= 0xF03C and dut.readAddr.value.integer & 0x3 == 0):
					dut.dataIn.value = tempBatchVectorData[(dut.readAddr.value - 0xF000) >> 2]
				else:
					dut.dataIn.value = 0xDEADBEEF

			if (dut.writeEn.value.is_resolvable):
				if (dut.writeEn.value == 1):
					if (dut.writeAddr.value.is_resolvable):
						if (dut.writeData.value.signed_integer != tempBatchResult[(dut.writeAddr.value.integer)]):
							dut.log.info("matrix:\t" + str(matrixData) + "\nVector:\t" + str(tempBatchVectorData))
							dut.log.info("Write at " + str(dut.writeAddr.value.integer) + " of " + str(dut.writeData.value.signed_integer))
							dut.log.error("Incorrect return values")
							assert False

						else:
							testCasesGood += 1

					else:
						dut.log.error("Write requested with bad values")
						assert False

			loopCountFail += 1
			await cocotb.triggers.ClockCycles(dut.clk, 1)
	
		if loopCountFail > 100:
			print("Surpassed loop max")
			assert False;
	
	await cocotb.triggers.ClockCycles(dut.clk, 1)


	dut.workItemCount.value = 0

	for randTestCase in range(30):

		testCasesGood = 0
		loopCountFail = 0

		for j in range(4): # Row
			for i in range(4): # Column
				matrixData[j][i] = randint(-23170, 23170)
		
		for i in range(4):
			vectorData[i] = randint(-23170, 23170)

		result = multVecMatrix(matrixData, vectorData)

		dut.start.value = 1 
		await cocotb.triggers.ClockCycles(dut.clk, 1) # Required for synchronization
		await cocotb.triggers.RisingEdge(dut.mp.controller.load) # Raises on state transition to loadmatrix
		dut.start.value = 0

		while testCasesGood != 4 and loopCountFail <= 48:

			if (dut.readAddr.value.is_resolvable):
				if (dut.readAddr.value.integer >= 0x8000 and dut.readAddr.value.integer <= 0x803C and dut.readAddr.value.integer & 0x3 == 0):
					fullIndex = (dut.readAddr.value - 0x8000) >> 2
					dut.dataIn.value = matrixData[(fullIndex & 0xC) >> 2][fullIndex & 0x3]
				elif (dut.readAddr.value.integer >= 0xF000 and dut.readAddr.value.integer <= 0xF02C and dut.readAddr.value.integer & 0x3 == 0):
					dut.dataIn.value = vectorData[(dut.readAddr.value - 0xF000) >> 2]
				else:
					dut.dataIn.value = 0xDEADBEEF

			if (dut.writeEn.value.is_resolvable):
				if (dut.writeEn.value == 1):
					if (dut.writeAddr.value.is_resolvable):
						if (dut.writeData.value.signed_integer != result[dut.writeAddr.value.integer]):
							dut.log.info("matrix:\t" + str(matrixData) + "\nVector:\t" + str(vectorData) + "\nResult:\t" + str(result))
							dut.log.info("Write at " + str(dut.writeAddr.value.integer) + " of " + str(dut.writeData.value.signed_integer))
							dut.log.error("Incorrect return values")
							assert False

						else:
							testCasesGood += 1

					else:
						dut.log.error("Write requested with bad values")
						assert False

			loopCountFail += 1
			await cocotb.triggers.ClockCycles(dut.clk, 1)
	
	await cocotb.triggers.ClockCycles(dut.clk, 1)
	'''
	await cocotb.triggers.ClockCycles(dut.clk, 2)

	assert dut.mp.controller.state.value.integer == 1

	await cocotb.triggers.ClockCycles(dut.clk, 16)

	assert dut.mp.controller.state.value.integer == 2

	await cocotb.triggers.ClockCycles(dut.clk, 128)
	'''
