import pygame
import math
import triangle
import gpu


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
		[(2 * near_plane) / (right - left), 0, 0, 0],
		[0, (2 * near_plane) / (top - bottom), 0, 0],
		[(right + left) / (right - left), (top + bottom) / (top - bottom), -((far_plane + near_plane) / (far_plane - near_plane)), -1],
		[0, 0, -((2 * far_plane * near_plane) / (far_plane - near_plane)), 0]
	]

pygame.init()
screen = pygame.display.set_mode((640, 480))
clock = pygame.time.Clock()
running = True

tri2d = triangle.Triangle2d(pygame.math.Vector2(100, 100), pygame.math.Vector2(200, 200), pygame.math.Vector2(100, 200), (255, 255, 255))
tri = triangle.Triangle3d(pygame.math.Vector3(), pygame.math.Vector3(), pygame.math.Vector3(), (255, 255, 255))
tri3d = triangle.Triangle3d(pygame.math.Vector3(0.25, 0.25, -1), pygame.math.Vector3(0.5, 0.5, -1), pygame.math.Vector3(0.25, 0.5, -1), (255, 255, 255))

vertices = [pygame.math.Vector3(1.000000, 1.000000, -1.000000), pygame.math.Vector3(1.000000, -1.000000, -1.000000), pygame.math.Vector3(1.000000, 1.000000, 1.000000), 
			pygame.math.Vector3(1.000000, -1.000000, 1.000000), pygame.math.Vector3(-1.000000, 1.000000, -1.000000), pygame.math.Vector3(-1.000000, -1.000000, -1.000000), 
			pygame.math.Vector3(-1.000000, 1.000000, 1.000000), pygame.math.Vector3(-1.000000, -1.000000, 1.000000)]
indices = [[5, 3, 1],
			[3, 8, 4],
			[7, 6, 8],
			[2, 8, 6],
			[1, 4, 2],
			[5, 2, 6],
			[5, 7, 3],
			[3, 7, 8],
			[7, 5, 6],
			[2, 4, 8],
			[1, 3, 4],
			[5, 1, 2]]



transformedVerts = [[0 for i in range(4)] for i in range(len(vertices))] # Nested list comprehensions are pretty... this is to accomadate the w coord before normalization
normalizedVerts = [0 for i in range(len(vertices))]

worldToCamMat = [
	[1.0, 0.0, 0.0, 0.0],
	[0.0, 1.0, 0.0, 0.0],
	[0.0, 0.0, 1.0, 0.0],
	[0.0, 0.0, 0.0, 1.0]]

while running:

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
	
	keys = pygame.key.get_pressed()
	if keys[pygame.K_w]:
		worldToCamMat[3][2] += 0.1
	if keys[pygame.K_s]:
		worldToCamMat[3][2] -= 0.1
	if keys[pygame.K_a]:
		worldToCamMat[3][0] += 0.1
	if keys[pygame.K_d]:
		worldToCamMat[3][0] -= 0.1
	if keys[pygame.K_q]:
		worldToCamMat[3][1] += 0.1
	if keys[pygame.K_e]:
		worldToCamMat[3][1] -= 0.1

	screen.fill((0, 0, 0))

	projMat = create_perspective_projection_matrix(90, 0.1, 1000)
	gpu.fourxfourmatmul(worldToCamMat, projMat, projMat)

	gpu.projectVertices(vertices, transformedVerts, projMat)


	culledIndices = [[0 for i in range(3)] for j in range(len(indices) + 20)] # Extra buffer in case we generate more triangles during culling

	gpu.displayTriangles(screen, transformedVerts, indices, len(indices))

	#culledTriCount = gpu.cullTriangles(transformedVerts, indices, culledIndices, len(indices))

	#for i in range(len(transformedVerts)):
	#	normalizedVerts[i] = gpu.normalizeVec(transformedVerts[i])
	#	normalizedVerts[i].x = (normalizedVerts[i].x + 1) * (640 / 2) # To raster space
	#	normalizedVerts[i].y = (normalizedVerts[i].y + 1) * (480 / 2)

	# MOVE LOOP TO GPU (keep as seperate call for GPGPU???)

	#for i in range(culledTriCount):
	#	gpu.rasterTriangle(screen, triangle.Triangle3d(normalizedVerts[culledIndices[i][0] - 1], normalizedVerts[culledIndices[i][1] - 1], normalizedVerts[culledIndices[i][2] - 1], ((i * 43) % 255, (i * 37) % 255, 255)))


	pygame.display.flip()

	clock.tick(60)
