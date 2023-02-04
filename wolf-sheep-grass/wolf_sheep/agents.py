import mesa
from wolf_sheep.random_walk import RandomWalker


class Sheep(RandomWalker):
    """
    A sheep that walks around, reproduces (asexually) and gets eaten.

    The init is the same as the RandomWalker.
    """

    energy = None

    def __init__(self, unique_id, pos, model, moore, energy=None, reproduction = 0.04):
        super().__init__(unique_id, pos, model, moore=moore)
        self.energy = energy
        self.reproduction = reproduction

    def step(self):
        """
        A model step. Reproduce, then move and eat grass. 
        """

        if self.random.random() < self.reproduction:
            # Create a new sheep:
            if self.model.grass:
                self.energy /= 2
            # new_reproduction = self.reproduction + self.random.i
            lamb = Sheep(
                self.model.next_id(), self.pos, self.model, self.moore, self.energy, self.reproduction
            )
            self.model.grid.place_agent(lamb, self.pos)
            self.model.schedule.add(lamb)

        if self.model.grass:
            self.move_to_grass()

    def move_to_grass(self):
        # Pick the next cell from the adjacent cells.
        # next_moves = self.model.grid.get_neighborhood(self.pos, self.moore, True)
        adj_agents = self.model.grid.get_neighbors(self.pos, self.moore, True)
        adj_grass = [obj for obj in adj_agents if isinstance(obj, GrassPatch)]
        adj_grown_grass = [_ for _ in adj_grass if _.fully_grown]

        # Reduce energy
        self.energy -= 1

        if len(adj_grown_grass) > 0:
            # move to food, eat food
            grass_patch = self.random.choice(adj_grown_grass)
            self.model.grid.move_agent(self, grass_patch.pos)
            self.energy += self.model.sheep_gain_from_food
            grass_patch.fully_grown = False

        # if no food around, stay in place

        # check death
        if self.energy < 0:
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)
        
class Wolf(RandomWalker):
    """
    A wolf that walks around, reproduces (asexually) and eats sheep.
    """

    energy = None

    def __init__(self, unique_id, pos, model, moore, energy=None):
        super().__init__(unique_id, pos, model, moore=moore)
        self.energy = energy

    def step(self):
        self.energy -= 1
        self.move_to_sheep()
        
        # Death or reproduction
        if self.energy < 0:
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)
        else:
            if self.random.random() < self.model.wolf_reproduce:
                # Create a new wolf cub
                self.energy /= 2
                cub = Wolf(
                    self.model.next_id(), self.pos, self.model, self.moore, self.energy
                )
                self.model.grid.place_agent(cub, cub.pos)
                self.model.schedule.add(cub)

    def move_to_sheep(self):
        # Pick the next cell from the adjacent cells.
        # next_moves = self.model.grid.get_neighborhood(self.pos, self.moore, True)
        adj_agents = self.model.grid.get_neighbors(self.pos, self.moore, True)
        adj_sheep = [obj for obj in adj_agents if isinstance(obj, Sheep)]

        if len(adj_sheep) > 0:
            # move to food, eat food
            lamb = self.random.choice(adj_sheep)
            self.model.grid.move_agent(self, lamb.pos)
            self.energy += lamb.energy

            # Kill the sheep
            self.model.grid.remove_agent(lamb)
            self.model.schedule.remove(lamb)
        else:
            # if no food around, wander
            self.random_move()



class GrassPatch(mesa.Agent):
    """
    A patch of grass that grows at a fixed rate and it is eaten by sheep
    """

    def __init__(self, unique_id, pos, model, fully_grown, countdown):
        """
        Creates a new patch of grass

        Args:
            grown: (boolean) Whether the patch of grass is fully grown or not
            countdown: Time for the patch of grass to be fully grown again
        """
        super().__init__(unique_id, model)
        self.fully_grown = fully_grown
        self.countdown = countdown
        self.pos = pos

    def step(self):
        if not self.fully_grown:
            if self.countdown <= 0:
                # Set as fully grown
                self.fully_grown = True
                self.countdown = self.model.grass_regrowth_time
            else:
                self.countdown -= 1
