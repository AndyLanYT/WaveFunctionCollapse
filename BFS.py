UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

WAYS = [UP, DOWN, LEFT, RIGHT]


class Queue:   # FIFO
    def __init__(self, q):
        self.queue = q
    
    def get(self):
        return self.queue.pop(0)
    
    def put(self, element):
        self.queue.append(element)
    
    def clear(self):
        self.queue = []

    def __repr__(self):
        return str(self.queue)


class BFS:
    def __init__(self, maze):
        self.maze = maze

    def adjacentNodes(self, pos):
        x, y = pos
        valid = [255]

        nodes = []
        for dx, dy in WAYS:
            if 0 <= x+dx < len(self.maze[0]) and 0 <= y+dy < len(self.maze) and self.maze[y+dy][x+dx] in valid:
                nodes.append((x+dx, y+dy))
        
        return nodes
    
    def createGraph(self, start, finish):
        queue = Queue([start])
        
        graph = {start: None}

        while finish not in graph:
            pos = queue.get()

            for p in self.adjacentNodes(pos):
                if p not in graph:
                    graph[p] = pos
                    queue.put(p)
            
        return graph

    def path(self, start, finish):
        graph = self.createGraph(start, finish)

        currentPos = finish
        path = [finish]
        while currentPos != start:
            currentPos = graph[currentPos]
            path.insert(0, currentPos)
        path.insert(0, start)

        return path
    
    def run(self, start, finish):
        path = self.path(start, finish)
        
        mazed = []
        for i in range(len(self.maze)):
            row = []
            for j in range(len(self.maze[i])):
                if (j, i) in path:
                    row.append(137)
                else:
                    row.append(self.maze[i][j])
            mazed.append(row)
            
        return mazed
