from .descriptive import descriptive
from .distance import distance
from .file import file
from .map import map
from .population import population
from .provider import provider

class spm:
    def __init__(self):
        self.descriptive = descriptive(self)
        self.distance = distance(self)
        self.file = file(self)
        self.map = map(self)
        self.provider = provider(self)
        self.population = population(self)
        
        