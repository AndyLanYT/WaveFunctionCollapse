import math
import random


N = 2
OUTPUT_SIZE = (50, 50)

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
UP_LEFT = (-1, -1)
UP_RIGHT = (1, -1)
DOWN_LEFT = (-1, 1)
DOWN_RIGHT = (1, 1)

dirs = [UP, DOWN, LEFT, RIGHT, UP_LEFT, UP_RIGHT, DOWN_LEFT, DOWN_RIGHT]


def rotate(lst2D):
    return [[lst2D[j][i] for j in range(len(lst2D))] for i in range(len(lst2D[0])-1, -1, -1)]

def slice(lst2D, i, j, n):
    return list(map(lambda x: x[i:i+n], lst2D[j:j+n]))


class Pattern:
    def __init__(self, pixels):
        self.pixels = pixels
    
    def offsetTiles(self, direction):
        if direction == ( 0,  0):
            return self.pixels
        elif direction == (-1, -1):
            return self.pixels[0][0]
        elif direction == (-1,  0):
            return list(map(lambda x: x[0], self.pixels))
        elif direction == (-1,  1):
            return self.pixels[-1][0]
        elif direction == ( 0,  1):
            return self.pixels[-1]
        elif direction == ( 1,  1):
            return self.pixels[-1][-1]
        elif direction == ( 1,  0):
            return list(map(lambda x: x[-1], self.pixels))
        elif direction == ( 1, -1):
            return self.pixels[0][-1]
        elif direction == ( 0, -1):
            return self.pixels[0]
    
    def __eq__(self, other):
        return self.pixels == other.pixels
    
    def __hash__(self):
        return hash(tuple(map(lambda x: tuple(x), self.pixels)))

    def __repr__(self):
        return str(self.pixels)


class Index:
    def __init__(self, patterns):
        self.rules = {}
        for basePattern in patterns:
            self.rules[basePattern] = {}
            for d in dirs:
                self.rules[basePattern][d] = []
                for pattern in patterns:
                    if basePattern.offsetTiles(d) == pattern.offsetTiles((-d[0], -d[1])):
                        self.rules[basePattern][d].append(pattern)

    def check(self, basePattern, adjacentPattern, direction):
        return adjacentPattern in self.rules[basePattern][direction]

    def __repr__(self):
        string = ''
        for pattern in self.rules:
            string += f'{pattern}\n'
            for d in dirs:
                string += f'\t{d}\n'
                string += f'\t\t{self.rules[pattern][d]}\n'
            string += '\n'
        
        return string


class WaveFunction:
    def __init__(self, pixels, outputSize=OUTPUT_SIZE, n=N):
        self.inputSize = (len(pixels[0]), len(pixels))
        self.outputSize = outputSize
        
        patterns = []
        for i in range(self.inputSize[0]-n+1):
            for j in range(self.inputSize[1]-n+1):
                pattern = slice(pixels, i, j, n)                
                patterns.append(Pattern(pattern))
                patterns.append(Pattern(rotate(pattern)))
                patterns.append(Pattern(rotate(rotate(pattern))))
                patterns.append(Pattern(rotate(rotate(rotate(pattern)))))

                # mirror = list(map(lambda x: list(reversed(x)), pattern))
                # patterns.append(Pattern(mirror))
                # patterns.append(Pattern(rotate(mirror)))
                # patterns.append(Pattern(rotate(rotate(mirror))))
                # patterns.append(Pattern(rotate(rotate(rotate(mirror)))))
        
        self.patterns = list(set(patterns))
        self.weights = {p: patterns.count(p) for p in patterns}
        self.probabilities = {p: patterns.count(p) / len(patterns) for p in patterns}
        self.index = Index(self.patterns)
        self.coeffs = [[self.patterns for _ in range(outputSize[0])] for _ in range(outputSize[1])]
    
    def entropy(self, pos):
        x, y = pos

        if len(self.coeffs[y][x]) == 1:
            return 0
        
        return -sum([self.probabilities[p] * math.log(self.probabilities[p], 2) for p in self.coeffs[y][x]])
    
    def minEntropyPos(self):
        minEntropy = None
        pos = None

        for i in range(len(self.coeffs)):
            for j in range(len(self.coeffs[i])):
                entropy = self.entropy((j, i))

                if entropy != 0 and (minEntropy is None or minEntropy > entropy):
                    minEntropy = entropy
                    pos = j, i
        
        return pos
    
    def validDirs(self, pos):
        x, y = pos

        dirs = []
        if x == 0:
            dirs += [RIGHT]

            if y == 0:
                dirs += [DOWN, DOWN_RIGHT]
            elif y == self.outputSize[1] - 1:
                dirs += [UP, UP_RIGHT]
            else:
                dirs += [DOWN, DOWN_RIGHT, UP, UP_RIGHT]
        elif x == self.outputSize[0] - 1:
            dirs += [LEFT]

            if y == 0:
                dirs += [DOWN, DOWN_LEFT]
            elif y == self.outputSize[1] - 1:
                dirs += [UP, UP_LEFT]
            else:
                dirs += [DOWN, DOWN_LEFT, UP, UP_LEFT]
        else:
            dirs += [LEFT, RIGHT]

            if y == 0:
                dirs += [DOWN, DOWN_LEFT, DOWN_RIGHT]
            elif y == self.outputSize[1] - 1:
                dirs += [UP, UP_LEFT, UP_RIGHT]
            else:
                dirs += [DOWN, DOWN_LEFT, DOWN_RIGHT, UP, UP_LEFT, UP_RIGHT]

        return dirs
    
    def isCollapsed(self):
        for row in self.coeffs:
            for patterns in row:
                if len(patterns) > 1:
                    return False
        
        return True
    
    def patternsAtPos(self, pos):
        return self.coeffs[pos[1]][pos[0]]

    def observe(self):
        pos = self.minEntropyPos()

        if pos is None:
            return
        
        patterns = self.patternsAtPos(pos)
        
        # maxProbability = max([self.probabilities[p] for p in patterns])
        # self.coeffs[pos[1]][pos[0]] = [random.choice([p for p in patterns if self.probabilities[p] >= maxProbability-0.01])]
        # self.coeffs[pos[1]][pos[0]] = [random.choice(patterns)]
        self.coeffs[pos[1]][pos[0]] = random.choices(patterns, [self.probabilities[p] for p in patterns])
        
        return pos
    
    def propagate(self, pos):
        stack = [pos]

        counter = 0
        while len(stack) > 0:
            print(counter)
            counter += 1
            pos = stack.pop()
            patterns = self.patternsAtPos(pos)    # it can be a list with only a single Pattern
            
            for d in self.validDirs(pos):
                adjacentPos = (pos[0]+d[0], pos[1]+d[1])
                adjacentPatterns = self.patternsAtPos(adjacentPos)

                availablePatterns = []
                for p in adjacentPatterns:
                    if any([self.index.check(basePattern, p, d) for basePattern in patterns]):
                        availablePatterns.append(p)
                
                if len(availablePatterns) > 0:
                    self.coeffs[adjacentPos[1]][adjacentPos[0]] = availablePatterns
                
                if len(availablePatterns) != len(adjacentPatterns):
                    stack.append(adjacentPos)
            # ...
    
    def collapse(self):
        while not self.isCollapsed():
            pos = self.observe()
            self.propagate(pos)
        
        self.coeffs = [[patterns[0] for patterns in row] for row in self.coeffs]

    def imageFirsts(self):
        pixels = []
        for row in self.coeffs:
            r = []
            for pattern in row:
                r.append(pattern.pixels[0][0])
            pixels.append(r)
        
        return pixels
         
    def imagePatterns(self):
        pixels = []
        for row in self.coeffs:
            r = []
            for idx in range(N):
                level = []
                for pattern in row:
                    level += pattern.pixels[idx]
                r.append(level)
            pixels += r
        
        return pixels
