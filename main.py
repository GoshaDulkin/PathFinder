import pygame
from queue import PriorityQueue
from queue import Queue
from queue import LifoQueue

# Pygame window formatting
WIDTH = 600
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Pathfinding")

# Defining colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0,0,255)
YELLOW = (255, 255, 0)
PINK = (255, 0, 150)
GREY = (128, 128, 128)


# Making node class
class Node:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.width = width
        self.total_rows = total_rows
        self.color = WHITE
        self.neighbors = []

    def position(self):  # Returns node position
        return self.row, self.col

    # Coloring nodes
    def reset(self):
        self.color = WHITE

    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = BLACK

    def make_start(self):
        self.color = PINK

    # Checking node states
    def make_end(self):
        self.color = YELLOW

    def make_path(self):
        self.color = BLUE

    def is_barrier(self):  # For recognizing if neighbor is a barrier
        return self.color == BLACK

    def draw(self, win):  # Draws node
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():  # DOWN
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():  # UP
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():  # RIGHT
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():  # LEFT
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self, other):
        return False


# Pygame functions
def build_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, gap, rows)
            grid[i].append(node)
    return grid


def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))


def draw(win, grid, rows, width):
    win.fill(WHITE)

    for row in grid:
        for node in row:
            node.draw(win)

    draw_grid(win, rows, width)
    pygame.display.update()


def click_pos(pos, rows, width):
    gap = width // rows
    y, x = pos

    row = y // gap
    col = x // gap
    return row, col


# Function for drawing algorithm path
def make_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()


# DEPTH FIRST ALGORITHM
def dfs(draw, grid, start, end):
    open_set = LifoQueue()  # Initializing open set queue
    open_set.put(start)  # Enqueuing start node
    came_from = {}
    open_set_hash = {start}  # Hash to check if value is in queue

    while not open_set.empty():  # Iterates while there are nodes in the queue
        # Loop for exiting in the middle of running the algorithm
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()

        if current == end:
            make_path(came_from, current, draw)
            end.make_end()
            start.make_start()
            return True

        for neighbor in current.neighbors:
            if neighbor not in open_set_hash:
                came_from[neighbor] = current
                open_set.put(neighbor)
                open_set_hash.add(neighbor)
                neighbor.make_open()
        draw()

        if current != start and current in open_set_hash:
            current.make_closed()

    return False


# BREADTH FIRST ALGORITHM
def bfs(draw, grid, start, end):
    open_set = Queue()  # Initializing open set queue
    open_set.put(start)  # Enqueuing start node
    came_from = {}
    open_set_hash = {start}  # Hash to check if value is in queue

    while not open_set.empty():  # Iterates while there are nodes in the queue
        # Loop for exiting in the middle of running the algorithm
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()

        if current == end:
            make_path(came_from, current, draw)
            end.make_end()
            start.make_start()
            return True

        for neighbor in current.neighbors:
            if neighbor not in open_set_hash:
                came_from[neighbor] = current
                open_set.put(neighbor)
                open_set_hash.add(neighbor)
                neighbor.make_open()
        draw()

        if current != start and current in open_set_hash:
            current.make_closed()

    return False


# ASTAR ALGORITHM
def astar(draw, grid, start, end):  # F(n) = G(n) + H(n)
    count = 0
    open_set = PriorityQueue()  # Initializing open set priority queue
    open_set.put((0, count, start))  # Enqueuing start node, gets smallest element every time
    came_from = {}
    g_score = {node: float("inf") for row in grid for node in row}  # Assigning infinity g_score to each node
    g_score[start] = 0  # Assigning 0 g_score to start node
    f_score = {node: float("inf") for row in grid for node in row}  # Assigning infinity f_score to each node
    f_score[start] = h(start.position(), end.position())  # Approximating f_score of start node

    open_set_hash = {start}

    while not open_set.empty():  # Iterates while there are nodes in the queue
        # Loop for exiting in the middle of running the algorithm
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]  # Gets node value
        open_set_hash.remove(current)  # Removes current node from hash

        if current == end:
            make_path(came_from, end, draw)
            end.make_end()
            start.make_start()
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1  # Possible g_score for every neighbor

            if temp_g_score < g_score[neighbor]:  # If temp g_score is lower than current g_score, update g_score
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = g_score[neighbor] + h(neighbor.position(), end.position())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()
        draw()
        if current != start:
            current.make_closed()

    return False


def h(p1, p2):  # Heuristic distance from two nodes using Manhattan distance
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)


def main(win, width):
    ROWS = 30
    grid = build_grid(ROWS, width)

    start = None
    end = None

    run = True

    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = click_pos(pos, ROWS, width)
                node = grid[row][col]
                if not start and node != end:
                    start = node
                    start.make_start()

                elif not end and node != start:
                    end = node
                    end.make_end()

                elif node != start and node != end:
                    node.make_barrier()

            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = click_pos(pos, ROWS, width)
                node = grid[row][col]
                node.reset()

                if node == start:
                    start = None
                elif node == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1 and start and end:
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)
                    dfs(lambda: draw(win, grid, ROWS, width), grid, start, end)

                if event.key == pygame.K_2 and start and end:
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)
                    bfs(lambda: draw(win, grid, ROWS, width), grid, start, end)

                if event.key == pygame.K_3 and start and end:
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)
                    astar(lambda: draw(win, grid, ROWS, width), grid, start, end)

                if event.key == pygame.K_SPACE:
                    start = None
                    end = None
                    grid = build_grid(ROWS, width)
    pygame.quit()


print("\nLeft click to place down start (pink) and end (yellow) nodes. \n"
      "Also left click to place down barriers (black)\n"
      "Right click removes nodes.\n"
      "To select a pathfinding algorithm press the following:\n"
      "1: Depth-First\n"
      "2: Breadth-First\n"
      "3: AStar\n"
      "Pressing Space clears the screen.")
main(WIN, WIDTH)
