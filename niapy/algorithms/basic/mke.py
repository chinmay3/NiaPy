# encoding=utf8
import logging
from math import ceil

import numpy as np

from niapy.algorithms.algorithm import Algorithm, Individual, default_individual_init, default_numpy_init

logging.basicConfig()
logger = logging.getLogger('niapy.algorithms.basic')
logger.setLevel('INFO')

__all__ = ['MonkeyKingEvolutionV1', 'MonkeyKingEvolutionV2', 'MonkeyKingEvolutionV3']


class MkeSolution(Individual):
    r"""Implementation of Monkey King Evolution individual.

    Data:
        2018

    Authors:
        Klemen Berkovič

    License:
        MIT

    Attributes:
        x_pb (array of (float or int)): Personal best position of Monkey particle.
        f_pb (float): Personal best fitness/function value.
        MonkeyKing (bool): Boolean value indicating if particle is Monkey King particle.

    See Also:
        * :class:`niapy.algorithms.Individual`

    """

    def __init__(self, **kwargs):
        r"""Initialize Monkey particle.

        Args:
            **kwargs: Additional arguments

        See Also:
            * :class:`niapy.algorithms.Individual.__init__`

        """
        super().__init__(**kwargs)
        self.f_pb, self.x_pb = self.f, self.x
        self.monkey_king = False

    def update_personal_best(self):
        r"""Update personal best position of particle."""
        if self.f < self.f_pb:
            self.x_pb, self.f_pb = self.x, self.f


class MonkeyKingEvolutionV1(Algorithm):
    r"""Implementation of monkey king evolution algorithm version 1.

    Algorithm:
        Monkey King Evolution version 1

    Date:
        2018

    Authors:
        Klemen Berkovič

    License:
        MIT

    Reference URL:
        https://www.sciencedirect.com/science/article/pii/S0950705116000198

    Reference paper:
        Zhenyu Meng, Jeng-Shyang Pan, Monkey King Evolution: A new memetic evolutionary algorithm and its application in vehicle fuel consumption optimization, Knowledge-Based Systems, Volume 97, 2016, Pages 144-157, ISSN 0950-7051, https://doi.org/10.1016/j.knosys.2016.01.009.

    Attributes:
        Name (List[str]): List of strings representing algorithm names.
        fluctuation_coeff (float): Scale factor for normal particles.
        population_rate (float): Percent value of now many new particle Monkey King particle creates.
        c (int): Number of new particles generated by Monkey King particle.
        fc (float): Scale factor for Monkey King particles.

    See Also:
        * :class:`niapy.algorithms.algorithm.Algorithm`

    """

    Name = ['MonkeyKingEvolutionV1', 'MKEv1']

    @staticmethod
    def info():
        r"""Get basic information of algorithm.

        Returns:
            str: Basic information.

        See Also:
            * :func:`niapy.algorithms.Algorithm.info`

        """
        return r"""Zhenyu Meng, Jeng-Shyang Pan, Monkey King Evolution: A new memetic evolutionary algorithm and its application in vehicle fuel consumption optimization, Knowledge-Based Systems, Volume 97, 2016, Pages 144-157, ISSN 0950-7051, https://doi.org/10.1016/j.knosys.2016.01.009."""

    def __init__(self, population_size=40, fluctuation_coeff=0.7, population_rate=0.3, c=3, fc=0.5, *args, **kwargs):
        """Initialize MonkeyKingEvolutionV1.

        Args:
            population_size (int): Population size.
            fluctuation_coeff (float): Scale factor for normal particle.
            population_rate (float): Percent value of now many new particle Monkey King particle creates. Value in rage [0, 1].
            c (int): Number of new particles generated by Monkey King particle.
            fc (float): Scale factor for Monkey King particles.

        See Also:
            * :func:`niapy.algorithms.algorithm.Algorithm.__init__`

        """
        super().__init__(population_size,
                         individual_type=kwargs.pop('individual_type', MkeSolution),
                         initialization_function=kwargs.pop('initialization_function', default_individual_init),
                         *args, **kwargs)
        self.fluctuation_coeff = fluctuation_coeff
        self.population_rate = population_rate
        self.c = c
        self.fc = fc

    def set_parameters(self, population_size=40, fluctuation_coeff=0.7, population_rate=0.3, c=3, fc=0.5, **kwargs):
        r"""Set Monkey King Evolution v1 algorithms static parameters.

        Args:
            population_size (int): Population size.
            fluctuation_coeff (float): Scale factor for normal particle.
            population_rate (float): Percent value of now many new particle Monkey King particle creates. Value in rage [0, 1].
            c (int): Number of new particles generated by Monkey King particle.
            fc (float): Scale factor for Monkey King particles.

        See Also:
            * :func:`niapy.algorithms.algorithm.Algorithm.set_parameters`

        """
        super().set_parameters(population_size=population_size,
                               individual_type=kwargs.pop('individual_type', MkeSolution),
                               initialization_function=kwargs.pop('initialization_function', default_individual_init),
                               **kwargs)
        self.fluctuation_coeff = fluctuation_coeff
        self.population_rate = population_rate
        self.c = c
        self.fc = fc

    def get_parameters(self):
        r"""Get algorithms parameters values.

        Returns:
            Dict[str, Any]

        See Also:
            * :func:`niapy.algorithms.Algorithm.get_parameters`

        """
        d = Algorithm.get_parameters(self)
        d.update({
            'fluctuation_coeff': self.fluctuation_coeff,
            'population_rate': self.population_rate,
            'c': self.c,
            'fc': self.fc
        })
        return d

    def move_p(self, x, x_pb, x_b, task):
        r"""Move normal particle in search space.

        For moving particles algorithm uses next formula:
        :math:`\mathbf{x_{pb} - \mathit{differential_weight} \odot \mathbf{r} \odot (\mathbf{x_b} - \mathbf{x})`
        where
        :math:`\mathbf{r}` is one dimension array with `D` components. Components in this vector are in range [0, 1].

        Args:
            x (numpy.ndarray): Particle position.
            x_pb (numpy.ndarray): Particle best position.
            x_b (numpy.ndarray): Best particle position.
            task (Task): Optimization task.

        Returns:
            numpy.ndarray: Particle new position.

        """
        return x_pb + self.fluctuation_coeff * self.random(task.dimension) * (x_b - x)

    def move_mk(self, x, task):
        r"""Move Monkey King particle.

        For moving Monkey King particles algorithm uses next formula:
        :math:`\mathbf{x} + \mathit{fc} \odot \mathbf{population_rate} \odot \mathbf{x}`
        where
        :math:`\mathbf{population_rate}` is two dimensional array with shape `{c * D, D}`. Components of this array are in range [0, 1]

        Args:
            x (numpy.ndarray): Monkey King patricle position.
            task (Task): Optimization task.

        Returns:
            numpy.ndarray: New particles generated by Monkey King particle.

        """
        return x + self.fc * self.random((int(self.c * task.dimension), task.dimension)) * x

    def move_particle(self, p, p_b, task):
        r"""Move particles.

        Args:
            p (MkeSolution): Monkey particle.
            p_b (numpy.ndarray): Population best particle.
            task (Task): Optimization task.

        """
        p.x = self.move_p(p.x, p.x_pb, p_b, task)
        p.evaluate(task, rng=self.rng)

    def move_monkey_king_particle(self, p, task):
        r"""Move Monkey King Particles.

        Args:
            p (MkeSolution): Monkey King particle to apply this function on.
            task (Task): Optimization task.

        """
        p.monkey_king = False
        a = np.apply_along_axis(task.repair, 1, self.move_mk(p.x, task), self.rng)
        a_f = np.apply_along_axis(task.eval, 1, a)
        ib = np.argmin(a_f)
        p.x, p.f = a[ib], a_f[ib]

    def move_population(self, pop, xb, task):
        r"""Move population.

        Args:
            pop (numpy.ndarray[MkeSolution]): Current population.
            xb (numpy.ndarray): Current best solution.
            task (Task): Optimization task.

        Returns:
            numpy.ndarray[MkeSolution]: New particles.

        """
        for p in pop:
            if p.monkey_king:
                self.move_monkey_king_particle(p, task)
            else:
                self.move_particle(p, xb, task)
            p.update_personal_best()
        return pop

    def init_population(self, task):
        r"""Init population.

        Args:
            task (Task): Optimization task

        Returns:
            Tuple(numpy.ndarray[MkeSolution], numpy.ndarray[float], Dict[str, Any]]:
                1. Initialized solutions
                2. Fitness/function values of solution
                3. Additional arguments

        """
        pop, fpop, _ = Algorithm.init_population(self, task)
        for i in self.rng.choice(self.population_size, int(self.population_rate * len(pop)), replace=False):
            pop[i].monkey_king = True
        return pop, fpop, {}

    def run_iteration(self, task, population, population_fitness, best_x, best_fitness, **params):
        r"""Core function of Monkey King Evolution v1 algorithm.

        Args:
            task (Task): Optimization task.
            population (numpy.ndarray[MkeSolution]): Current population.
            population_fitness (numpy.ndarray[float]): Current population fitness/function values.
            best_x (numpy.ndarray): Current best solution.
            best_fitness (float): Current best solutions function/fitness value.
            **params (Dict[str, Any]): Additional arguments.

        Returns:
            Tuple(numpy.ndarray[MkeSolution], numpy.ndarray[float], Dict[str, Any]]:
                1. Initialized solutions.
                2. Fitness/function values of solution.
                3. Additional arguments.

        """
        population = self.move_population(population, best_x, task)
        for i in self.rng.choice(self.population_size, int(self.population_rate * len(population)), replace=False):
            population[i].monkey_king = True
        population_fitness = np.asarray([m.f for m in population])
        best_x, best_fitness = self.get_best(population, population_fitness, best_x, best_fitness)
        return population, population_fitness, best_x, best_fitness, {}


class MonkeyKingEvolutionV2(MonkeyKingEvolutionV1):
    r"""Implementation of monkey king evolution algorithm version 2.

    Algorithm:
        Monkey King Evolution version 2

    Date:
        2018

    Authors:
        Klemen Berkovič

    License:
        MIT

    Reference URL:
        https://www.sciencedirect.com/science/article/pii/S0950705116000198

    Reference paper:
        Zhenyu Meng, Jeng-Shyang Pan, Monkey King Evolution: A new memetic evolutionary algorithm and its application in vehicle fuel consumption optimization, Knowledge-Based Systems, Volume 97, 2016, Pages 144-157, ISSN 0950-7051, https://doi.org/10.1016/j.knosys.2016.01.009.

    Attributes:
        Name (List[str]): List of strings representing algorithm names.

    See Also:
        * :class:`niapy.algorithms.basic.mke.MonkeyKingEvolutionV1`

    """

    Name = ['MonkeyKingEvolutionV2', 'MKEv2']

    @staticmethod
    def info():
        r"""Get basic information of algorithm.

        Returns:
            str: Basic information.

        See Also:
            * :func:`niapy.algorithms.Algorithm.info`

        """
        return r"""Zhenyu Meng, Jeng-Shyang Pan, Monkey King Evolution: A new memetic evolutionary algorithm and its application in vehicle fuel consumption optimization, Knowledge-Based Systems, Volume 97, 2016, Pages 144-157, ISSN 0950-7051, https://doi.org/10.1016/j.knosys.2016.01.009."""

    def move_mk(self, x, task, dx=None):
        r"""Move Monkey King particle.

        For movement of particles algorithm uses next formula:
        :math:`\mathbf{x} - \mathit{fc} \odot \mathbf{dx}`

        Args:
            x (numpy.ndarray): Particle to apply movement on.
            task (Task): Optimization task.
            dx (numpy.ndarray): Difference between to random particles in population.

        Returns:
            numpy.ndarray: Moved particles.

        """
        return x - self.fc * dx

    def move_monkey_king_particle(self, p, task, pop=None):
        r"""Move Monkey King particles.

        Args:
            p (MkeSolution): Monkey King particle to move.
            task (Task): Optimization task.
            pop (numpy.ndarray[MkeSolution]): Current population.

        """
        p.monkey_king = False
        p_b, p_f = p.x, p.f
        for _i in range(int(self.c * self.population_size)):
            r = self.rng.choice(self.population_size, 2, replace=False)
            a = task.repair(self.move_mk(p.x, task, pop[r[0]].x - pop[r[1]].x), self.rng)
            a_f = task.eval(a)
            if a_f < p_f:
                p_b, p_f = a, a_f
        p.x, p.f = p_b, p_f

    def move_population(self, pop, xb, task):
        r"""Move population.

        Args:
            pop (numpy.ndarray[MkeSolution]): Current population.
            xb (numpy.ndarray): Current best solution.
            task (Task): Optimization task.

        Returns:
            numpy.ndarray[MkeSolution]: Moved population.

        """
        for p in pop:
            if p.monkey_king:
                self.move_monkey_king_particle(p, task, pop)
            else:
                self.move_particle(p, xb, task)
            p.update_personal_best()
        return pop


class MonkeyKingEvolutionV3(MonkeyKingEvolutionV1):
    r"""Implementation of monkey king evolution algorithm version 3.

    Algorithm:
        Monkey King Evolution version 3

    Date:
        2018

    Authors:
        Klemen Berkovič

    License:
        MIT

    Reference URL:
        https://www.sciencedirect.com/science/article/pii/S0950705116000198

    Reference paper:
        Zhenyu Meng, Jeng-Shyang Pan, Monkey King Evolution: A new memetic evolutionary algorithm and its application in vehicle fuel consumption optimization, Knowledge-Based Systems, Volume 97, 2016, Pages 144-157, ISSN 0950-7051, https://doi.org/10.1016/j.knosys.2016.01.009.

    Attributes:
        Name (List[str]): List of strings that represent algorithm names.

    See Also:
        * :class:`niapy.algorithms.basic.mke.MonkeyKingEvolutionV1`

    """

    Name = ['MonkeyKingEvolutionV3', 'MKEv3']

    @staticmethod
    def info():
        r"""Get basic information of algorithm.

        Returns:
            str: Basic information.

        See Also:
            * :func:`niapy.algorithms.Algorithm.info`

        """
        return r"""Zhenyu Meng, Jeng-Shyang Pan, Monkey King Evolution: A new memetic evolutionary algorithm and its application in vehicle fuel consumption optimization, Knowledge-Based Systems, Volume 97, 2016, Pages 144-157, ISSN 0950-7051, https://doi.org/10.1016/j.knosys.2016.01.009."""

    def __init__(self, *args, **kwargs):
        """Initialize MonkeyKingEvolutionV3."""
        super().__init__(individual_type=kwargs.pop('individual_type', None),
                         initialization_function=kwargs.pop('initialization_function', default_numpy_init),
                         *args, **kwargs)

    def set_parameters(self, **kwargs):
        r"""Set core parameters of MonkeyKingEvolutionV3 algorithm.

        See Also:
            * :func:`niapy.algorithms.basic.MonkeyKingEvolutionV1.set_parameters`

        """
        super().set_parameters(individual_type=kwargs.pop('individual_type', None),
                               initialization_function=kwargs.pop('initialization_function', default_numpy_init),
                               **kwargs)

    @staticmethod
    def neg(x):
        r"""Transform function.

        Args:
            x (Union[int, float]): Should be 0 or 1.

        Returns:
            float: If 0 then 1 else 0.

        """
        return 0.0 if x == 1.0 else 1.0

    def init_population(self, task):
        r"""Initialize the population.

        Args:
            task (Task): Optimization task.

        Returns:
            Tuple[numpy.ndarray, numpy.ndarray[float], Dict[str, Any]]:
                1. Initialized population.
                2. Initialized population function/fitness values.
                3. Additional arguments:
                    * k (int): Starting number of rows to include from lower triangular matrix.
                    * c (int): Constant.

        See Also:
            * :func:`niapy.algorithms.algorithm.Algorithm.init_population`

        """
        population, fitness, d = Algorithm.init_population(self, task)
        k, c = int(ceil(self.population_size / task.dimension)), int(ceil(self.c * task.dimension))
        d.update({'k': k, 'c': c})
        return population, fitness, d

    def run_iteration(self, task, population, population_fitness, best_x, best_fitness, **params):
        r"""Core function of Monkey King Evolution v3 algorithm.

        Args:
            task (Task): Optimization task.
            population (numpy.ndarray): Current population.
            population_fitness (numpy.ndarray[float]): Current population fitness/function values.
            best_x (numpy.ndarray): Current best individual.
            best_fitness (float): Current best individual function/fitness value.
            **params: Additional arguments

        Returns:
            Tuple[numpy.ndarray, numpy.ndarray[float], Dict[str, Any]]:
                1. Initialized population.
                2. Initialized population function/fitness values.
                3. Additional arguments:
                    * k (int): Starting number of rows to include from lower triangular matrix.
                    * c (int): Constant.

        """
        k = params.pop('k')
        c = params.pop('c')

        x_gb = np.apply_along_axis(task.repair, 1,
                                   best_x + self.fc * population[self.rng.choice(len(population), c)] - population[self.rng.choice(len(population), c)],
                                   self.rng)
        x_gb_f = np.apply_along_axis(task.eval, 1, x_gb)
        best_x, best_fitness = self.get_best(x_gb, x_gb_f, best_x, best_fitness)
        m = np.ones((self.population_size, task.dimension))
        for i in range(k):
            m[i * task.dimension:(i + 1) * task.dimension] = np.tril(m[i * task.dimension:(i + 1) * task.dimension])
        for i in range(self.population_size):
            self.rng.shuffle(m[i])
        population = np.apply_along_axis(task.repair, 1, m * population + np.vectorize(self.neg)(m) * best_x, self.rng)
        population_fitness = np.apply_along_axis(task.eval, 1, population)
        best_x, best_fitness = self.get_best(population, population_fitness, best_x, best_fitness)
        iw, ib_gb = np.argmax(population_fitness), np.argmin(x_gb_f)
        if x_gb_f[ib_gb] <= population_fitness[iw]:
            population[iw], population_fitness[iw] = x_gb[ib_gb], x_gb_f[ib_gb]
        return population, population_fitness, best_x, best_fitness, {'k': k, 'c': c}


