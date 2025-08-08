import pygame

class Triangle3d ():
	def __init__(self, p1, p2, p3, color):
		self.p1 = pygame.math.Vector3(p1)
		self.p2 = pygame.math.Vector3(p2)
		self.p3 = pygame.math.Vector3(p3)
		self.color = color

class Triangle2d:
	def __init__(self, p1, p2, p3, color):
		self.p1 = pygame.math.Vector2(p1)
		self.p2 = pygame.math.Vector2(p2)
		self.p3 = pygame.math.Vector2(p3)
		self.color = color


def edgeFunction(p1, p3, dX, dY):
	return dX * (p3.y - p1.y) - dY * (p3.x - p1.x)

def insideTri(point, tri):
	return (edgeFunction(tri.p1, tri.p2, point) > 0 and
			edgeFunction(tri.p2, tri.p3, point) > 0 and
			edgeFunction(tri.p3, tri.p1, point) > 0)
