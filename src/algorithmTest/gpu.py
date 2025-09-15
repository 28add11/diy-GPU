import pygame
import triangle

# matricies are defined [row][column] (row major order in memory)

def fourxfourmatmul(mat1, mat2, destMat):
	for row in range(4):
		for column in range(4):
			sum = 0.0
			for num in range(4):
				sum += mat1[row][num] * mat2[num][column]
			destMat[row][column] = sum

def multVecMatrix(matrix : list[list[float]], vec : pygame.math.Vector3) -> list[float]:
	"""
	Multiplies a 4x4 matrix by a 3D vector (w coord is set to 1 implicitly).
	Column major order, with vectors treated as 1x4 matrices (as if they're to the right of the multiplication sign/Post-multiplied)
	Returns a new 4D vector with w coordinate.
	"""

	listResult = [0.0 for i in range(4)]
	listResult[0] = matrix[0][0] * vec.x + matrix[0][1] * vec.y + matrix[0][2] * vec.z + matrix[0][3]
	listResult[1] = matrix[1][0] * vec.x + matrix[1][1] * vec.y + matrix[1][2] * vec.z + matrix[1][3]
	listResult[2] = matrix[2][0] * vec.x + matrix[2][1] * vec.y + matrix[2][2] * vec.z + matrix[2][3]
	listResult[3] = matrix[3][0] * vec.x + matrix[3][1] * vec.y + matrix[3][2] * vec.z + matrix[3][3]

	return listResult

def normalizeVec(vec : list[float]) -> pygame.math.Vector3:
	"""Normalizes a 4D vector based on the w coordinate.
	AKA divides the x, y, z coordinates by w if w is not 1."""

	finalResult = pygame.math.Vector3(0, 0, 0)
	if vec[3] != 1:
		finalResult.x = vec[0] / vec[3]
		finalResult.y = vec[1] / vec[3]
		finalResult.z = vec[2] / vec[3]
	else:
		finalResult.x = vec[0]
		finalResult.y = vec[1]
		finalResult.z = vec[2]

	return finalResult

def singleVertClipInterpolate(verts, deltas, insideInd):
	insideDelta = deltas[insideInd]
	insideVert =  verts[insideInd]

	currentInd = insideInd 
	nextIndList = [1, 2, 0]
	for i in range(2):
		currentInd = nextIndList[currentInd] # Better pattern for hardware, effectively LUT

		outsideDelta = deltas[currentInd]
		outsideVert = verts[currentInd]

		a = insideDelta / (insideDelta - outsideDelta)
		insidePointxA = [j * (1 - a) for j in insideVert] # All of these list comps are just element-wise ops
		outsidePointxA = [j * a for j in outsideVert]
		verts[currentInd] = [insidePointxA[j] + outsidePointxA[j] for j in range(4)] # Replace original vert

def twoVertClipInterpolate(verts, extraTriBuffer, extraTriBufferInd, deltas, outsideInd):
	outsideDelta = deltas[outsideInd]
	outsideVert = verts[outsideInd]
	generatedVertBuffer = [[0 for i in range(4)] for j in range(2)]

	currentInd = outsideInd
	nextIndList = [1, 2, 0]
	for i in range(2): # Vertex gen loop
		currentInd = nextIndList[currentInd] # Better pattern for hardware, effectively LUT

		insideDelta = deltas[currentInd]
		insideVert = verts[currentInd]

		a = insideDelta / (insideDelta - outsideDelta)
		insidePointxA = [j * (1 - a) for j in insideVert] # All of these list comps are just element-wise ops
		outsidePointxA = [j * a for j in outsideVert]
		for j in range(4):
			newPoint = insidePointxA[j] + outsidePointxA[j]
			newPoint = round(newPoint, 10)
			generatedVertBuffer[i][j] = newPoint # We want to use i here since its a generated buffer thing

	currentInd = nextIndList[outsideInd]
	
	# currentInd is vertex B (per https://www.gabrielgambetta.com/computer-graphics-from-scratch/11-clipping.html)
	extraTriBuffer[extraTriBufferInd] = [generatedVertBuffer[0], verts[currentInd], generatedVertBuffer[1]] # Tri A`BB`
	verts[outsideInd] = generatedVertBuffer[1] # Tri ABA` (we will render this tri fully first)


def displayTriangles(screen, vecArray, indexArrayIn, triCount):

	# De-index tris first and push them in this buffer
	# 9 is the max number of generated verts in a worst case senario clipping (+ 3 for og tri) but RTL for indexing into these would be horribly innefficient
	triBuffer = [[[0 for i in range(4)] for j in range(3)] for k in range(8)] # 7 tris at most (+ 1 og tri again)
	triBufferCount = 0

	for i in range(triCount):

		deindexedTri = [vecArray[j - 1] for j in indexArrayIn[i]] # For every item in the index array, get the corresponding vector

		triBuffer[0] = deindexedTri # Item 0 since we loop over the buffer
		triBufferCount = 1

		while triBufferCount > 0: # In hardware is just ORs (UNSIGNED)

			##### Clipping #####
			goodToRender = True
			vertices = triBuffer[triBufferCount - 1] # Get the current triangle vertices
			triBufferCount -= 1


			for plane in range(6): 
				clippedVertices = 0
				#vertexCoords = vecArray[j - 1]
				#x, y, z, w = vertexCoords[0], vertexCoords[1], vertexCoords[2], vertexCoords[3]

				if (plane & 0x01) == 1: # Odd
					planeCoords = [-vertices[0][plane >> 1], -vertices[1][plane >> 1], -vertices[2][plane >> 1]]
				else:
					planeCoords = [vertices[0][plane >> 1], vertices[1][plane >> 1], vertices[2][plane >> 1]]

				v0delta = vertices[0][3] + planeCoords[0]
				if v0delta < 0:
					clippedVertices += 1

				v1delta = vertices[1][3] + planeCoords[1]
				if v1delta < 0:
					clippedVertices += 1

				v2delta = vertices[2][3] + planeCoords[2]
				if v2delta < 0:
					clippedVertices += 1

				if clippedVertices == 3: # All vertices are clipped, skip this triangle
					goodToRender = False
					break # State machine transition to next tri

				elif clippedVertices == 2: # Simple new tri with verts at intersections
					if v0delta > 0:
						singleVertClipInterpolate(vertices, [v0delta, v1delta, v2delta], 0)
					elif v1delta > 0:
						singleVertClipInterpolate(vertices, [v0delta, v1delta, v2delta], 1)
					elif v2delta > 0:
						singleVertClipInterpolate(vertices, [v0delta, v1delta, v2delta], 2)

				elif clippedVertices == 1: # Hard two new tris
					if v0delta < 0:
						twoVertClipInterpolate(vertices, triBuffer, triBufferCount, [v0delta, v1delta, v2delta], 0)
						triBufferCount += 1
					elif v1delta < 0:
						twoVertClipInterpolate(vertices, triBuffer, triBufferCount, [v0delta, v1delta, v2delta], 1)
						triBufferCount += 1
					elif v2delta < 0:
						twoVertClipInterpolate(vertices, triBuffer, triBufferCount, [v0delta, v1delta, v2delta], 2)
						triBufferCount += 1

			##### Rasterization and edge function #####

			if goodToRender:
				vec1 = normalizeVec(vertices[0])
				vec1.x = (vec1.x + 1) * (640 / 2) # To raster space
				vec1.y = (vec1.y + 1) * (480 / 2)
				vec2 = normalizeVec(vertices[1])
				vec2.x = (vec2.x + 1) * (640 / 2)# To raster space
				vec2.y = (vec2.y + 1) * (480 / 2)
				vec3 = normalizeVec(vertices[2])
				vec3.x = (vec3.x + 1) * (640 / 2)# To raster space
				vec3.y = (vec3.y + 1) * (480 / 2)
				tri = triangle.Triangle3d(vec1,
										  vec2,
										  vec3,
										  ((i * 43) % 255, (i * 37) % 255, 255))

				# For sub pixel accuracy in real hardware 4 extra bits at least should be used (PLAY AROUND WITH THIS)
				edge0 = tri.p2 - tri.p1
				edge1 = tri.p3 - tri.p2
				edge2 = tri.p1 - tri.p3

				area = triangle.edgeFunction(tri.p1, tri.p3, edge0.x, edge0.y)

				if area <= 0: # Simple and stupid back face culling
					continue

				p1 = pygame.math.Vector2(min(tri.p1.x, tri.p2.x, tri.p3.x),
										min(tri.p1.y, tri.p2.y, tri.p3.y))
				p2 = pygame.math.Vector2(max(tri.p1.x, tri.p2.x, tri.p3.x),
										max(tri.p1.y, tri.p2.y, tri.p3.y))

				p1.x = max(0, p1.x)
				p1.y = max(0, p1.y)
				p2.x = min(screen.get_width(), p2.x)
				p2.y = min(screen.get_height(), p2.y)

				deltaXw0 = edge0.x
				deltaYw0 = edge0.y

				deltaXw1 = edge1.x
				deltaYw1 = edge1.y

				deltaXw2 = edge2.x
				deltaYw2 = edge2.y

				w0Row = triangle.edgeFunction(tri.p1, pygame.math.Vector2(p1.x, p1.y), deltaXw0, deltaYw0)
				w1Row = triangle.edgeFunction(tri.p2, pygame.math.Vector2(p1.x, p1.y), deltaXw1, deltaYw1)
				w2Row = triangle.edgeFunction(tri.p3, pygame.math.Vector2(p1.x, p1.y), deltaXw2, deltaYw2)


				for y in range(int(p1.y), int(p2.y)):

					w0 = w0Row
					w1 = w1Row
					w2 = w2Row

					for x in range(int(p1.x), int(p2.x)):

						overlap = (((w0 > 0), ((edge0.y == 0 and edge0.x < 0) or edge0.y < 0))[w0 == 0] and
							((w1 > 0), ((edge1.y == 0 and edge1.x < 0) or edge1.y < 0))[w1 == 0] and
							((w2 > 0), ((edge2.y == 0 and edge2.x < 0) or edge2.y < 0))[w2 == 0]
							)

						if overlap:
							screen.set_at((x, screen.get_height() - y), tri.color)

						w0 -= deltaYw0
						w1 -= deltaYw1
						w2 -= deltaYw2

					w0Row += deltaXw0
					w1Row += deltaXw1
					w2Row += deltaXw2


def projectVertices(inVert, outVert, projMat):
	for i in range(len(inVert)):
		outVert[i] = multVecMatrix(projMat, inVert[i])
