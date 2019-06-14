import random


activation = lambda x: x

class Node:
    def __init__(self):
        self.before = []

    def evaluate(self, inp):
        r = activation(sum(n.evaluate(inp) * w for n, w in self.before))
        return r

    def mutate(self):
        for i in range(len(self.before)):
            if random.random() < 0.005:
                n, w = self.before[i]
                self.before[i] = (n, w + random.uniform(-0.1, 0.1))


class InputNode:
    def __init__(self, ident):
        self.ident = ident

    def evaluate(self, inp):
        return inp[self.ident]

    def mutate(self):
        pass


class Network:
    def __init__(self, layers, input_size):
        self.layers = [[InputNode(i) for i in range(input_size)]]
        for layer in layers:
            for node in layer:
                for last_node in self.layers[-1]:
                    node.before.append((last_node, random.uniform(-0.3, 0.3)))
            self.layers.append(layer)

    def evaluate(self, inp):
        return [n.evaluate(inp) for n in self.layers[-1]]

    def mutate(self):
        for layer in self.layers:
            for node in layer:
                node.mutate()
