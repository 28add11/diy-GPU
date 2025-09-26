# Nicholas West, 2025
# Cocotb test file for the whole datapath
# Kinda fixed in its functionality, but we don't want to make a whole emulator

import cocotb
from cocotb.clock import Clock
import cocotb.triggers

import math

def fourxfourmatmul(mat1, mat2, destMat):
	for row in range(4):
		for column in range(4):
			sum = 0
			for num in range(4):
				sum += mat1[row][num] * mat2[num][column]
			destMat[row][column] = sum // (2**16) # Fixed point scaling factor correction

def multVecMatrix(matrix, vec):
	"""
	Multiplies a 4x4 matrix by a 3D vector.
	Column major order, with vectors treated as 1x4 matrices (as if they're to the right of the multiplication sign/Post-multiplied)
	Returns a new 4D vector with w coordinate.
	"""

	listResult = [0 for i in range(4)]
	listResult[0] = (matrix[0][0] * vec[0] + matrix[0][1] * vec[1] + matrix[0][2] * vec[2] + matrix[0][3] * vec[3]) // (2**16)
	listResult[1] = (matrix[1][0] * vec[0] + matrix[1][1] * vec[1] + matrix[1][2] * vec[2] + matrix[1][3] * vec[3]) // (2**16)
	listResult[2] = (matrix[2][0] * vec[0] + matrix[2][1] * vec[1] + matrix[2][2] * vec[2] + matrix[2][3] * vec[3]) // (2**16)
	listResult[3] = (matrix[3][0] * vec[0] + matrix[3][1] * vec[1] + matrix[3][2] * vec[2] + matrix[3][3] * vec[3]) // (2**16)

	return listResult

def create_perspective_projection_matrix(fov, near_plane, far_plane):
	"""
	Creates a perspective projection matrix.
	fov is the field of view in degrees.
	"""
	right = math.tan(math.radians(fov) / 2) * near_plane
	left = -right
	top = ((right - left) / 1.3333333333) / 2
	bottom = -top
	return [
		[(2 * near_plane) / (right - left), 0, (right + left) / (right - left), 0],
		[0, (2 * near_plane) / (top - bottom), (top + bottom) / (top - bottom), 0],
		[0, 0, -((far_plane + near_plane) / (far_plane - near_plane)), -((2 * far_plane * near_plane) / (far_plane - near_plane))],
		[0, 0, -1, 0]
	]

def normalizeVec(vec):
	"""Normalizes a 4D vector based on the w coordinate.
	AKA divides the x, y, z coordinates by w if w is not 1."""

	finalResult = [0, 0, 0, 1]

	inverse = (1 * (2**32)) // vec[3]

	finalResult[0] = (vec[0] * inverse) // (2**16)
	finalResult[1] = (vec[1] * inverse) // (2**16)
	finalResult[2] = (vec[2] * inverse) // (2**16)
	finalResult[3] = (vec[3] * inverse) // (2**16)
	
	return finalResult

@cocotb.test()
async def test(dut):
	dut.log.info("Start")

	vertices = [[1, 1, -1, 1], [1, -1, -1, 1], [1, 1, 1, 1], 
			[1, -1, 1, 1], [-1, 1, -1, 1], [-1, -1, -1, 1], 
			[-1, 1, 1, 1], [-1, -1, 1, 1]]
	fpVerts = [[(vertices[i][j] * (2**16)) for j in range(4)] for i in range(len(vertices))] # Scale to fixed point
	resultVerts = [[0 for i in range(4)] for i in range(len(vertices))]
	returnedVerts = [[0.0 for i in range(4)] for i in range(len(vertices))]

	worldToCamFloatMat = [[1.0, 0.0, 0.0, 2.4], [0.0, 1.0, 0.0, -1.9], [0.0, 0.0, 1.0, -5.29], [0.0, 0.0, 0.0, 1.0]]
	worldToCamMat = [[int(round(worldToCamFloatMat[i][j] * (2**16))) for j in range(4)] for i in range(len(worldToCamFloatMat))]
	

	projMatFloat = create_perspective_projection_matrix(90, 0.1, 1000)
	projMat = [[int(round(projMatFloat[i][j] * (2**16))) for j in range(4)] for i in range(len(projMatFloat))]
	fourxfourmatmul(projMat, worldToCamMat, projMat)

	for i in range(len(fpVerts)):
		resultVerts[i] = multVecMatrix(projMat, fpVerts[i])

	for i in range(len(fpVerts)):
		resultVerts[i] = normalizeVec(resultVerts[i])

	# Set the clock period to 10 ns (100 MHz)
	clock = Clock(dut.clk, 10, units="ns")
	cocotb.start_soon(clock.start())

	# Reset
	dut.log.info("Reset")
	dut.reset.value = 0
	dut.start.value = 0
	dut.workItemCount.value = len(vertices) - 1 
	dut.matrixInAddr.value = 0x8000
	dut.dataInAddr.value = 0xF000
	dut.dataOutAddr.value = 0
	await cocotb.triggers.ClockCycles(dut.clk, 10)
	dut.reset.value = 1

	dut.log.info("Test project behavior")

	await cocotb.triggers.ClockCycles(dut.clk, 10) # matproc should be in idle

	assert dut.mp.controller.state.value.integer == 0
	
	dut.start.value = 1 
	await cocotb.triggers.ClockCycles(dut.clk, 1) # Required for synchronization
	await cocotb.triggers.RisingEdge(dut.mp.controller.load) # Raises on state transition to loadmatrix
	dut.start.value = 0

	for batchVectorTests in range(1):

		testCasesGood = 0
		loopCountFail = 0

		while testCasesGood < (3 * len(fpVerts))  and loopCountFail <= 5000:

			if (dut.readAddr.value.is_resolvable):

				if (dut.readAddr.value.integer >= 0x8000 and dut.readAddr.value.integer <= 0x803C and dut.readAddr.value.integer & 0x3 == 0):

					fullIndex = (dut.readAddr.value - 0x8000) >> 2
					dut.dataIn.value = projMat[(fullIndex & 0xC) >> 2][fullIndex & 0x3]

				elif (dut.readAddr.value.integer >= 0xF000 and dut.readAddr.value.integer <= (0xF000 + (4 * len(fpVerts) * 4)) and dut.readAddr.value.integer & 0x3 == 0):

					dut.dataIn.value = fpVerts[(dut.readAddr.value.integer - 0xF000) >> 4][((dut.readAddr.value.integer - 0xF000) >> 2) % 4]

				else:
					dut.dataIn.value = 0xDEADBEEF

			if (dut.writeEn.value.is_resolvable):
				if (dut.writeEn.value == 1):
					if (dut.writeAddr.value.is_resolvable):
						# Convert back to float
						returnedVerts[dut.writeAddr.value.integer >> 2][dut.writeAddr.value.integer % 4] = (dut.writeData.value.signed_integer / (2**16))

						if (dut.writeData.value.signed_integer != resultVerts[dut.writeAddr.value.integer >> 2][dut.writeAddr.value.integer % 4]):
							if (dut.writeAddr.value.integer % 4 != 3):
								dut.log.info("matrix:\t" + str(projMat) + "\nVector:\t" + str(resultVerts))
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
	
		if loopCountFail > 5000:
			dut.log.error("Surpassed loop max")
			assert False;

	dut.log.info(returnedVerts)
