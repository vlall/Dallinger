"""Network structures commonly used in simulations of evolution."""

from operator import attrgetter
import random

from .models import Network, Node
from .nodes import Source


class Chain(Network):
    """Source -> Node -> Node -> Node -> ...

    The source is optional, but must be added first.
    """

    __mapper_args__ = {"polymorphic_identity": "chain"}

    def add_node(self, node):
        """Add an agent, connecting it to the previous node."""
        other_nodes = [n for n in self.nodes() if n.id != node.id]

        if isinstance(node, Source) and other_nodes:
            raise(Exception("Chain network already has a nodes, "
                            "can't add a source."))

        if other_nodes:
            parent = max(other_nodes, key=attrgetter('creation_time'))
            parent.connect(whom=node)

class FullyConnected(Network):
    """A fully-connected network (complete graph) with all possible vectors."""

    __mapper_args__ = {"polymorphic_identity": "fully-connected"}

    def add_node(self, node):
        """Add a node, connecting it to everyone and back."""
        other_nodes = [n for n in self.nodes() if n.id != node.id]

        for n in other_nodes:
            if isinstance(n, Source):
                node.connect(direction="from", whom=n)
            else:
                node.connect(direction="both", whom=n)

class Empty(Network):
    """An empty network with no vectors."""

    __mapper_args__ = {"polymorphic_identity": "empty"}

    def add_node(self, node):
        """Do nothing."""
        pass

    def add_source(self, source):
        """Connect the source to all existing other nodes."""
        nodes = [n for n in self.nodes() if not isinstance(n, Source)]
        source.connect(whom=nodes)

class babyNetwork(Network):
    """Just for practice, will be deleted later
        """

    __mapper_args__ = {"polymorphic_identity": "baby_network"}

    def add_node(self, node):
        """Manually connect up a network."""

        # here are all the edges that need to be connected
        all_edges = [(0, 1), (0, 2), (0, 3), (2, 3)]

        # walk through edges
        for edge in all_edges:
            if node.id-2 == max(edge): # wait until you can connect backwards
                connect_to_node = Node.query.filter_by(id=min(edge)+2).one()
                node.connect(direction="from", whom=connect_to_node) # connect backward
                connect_to_node.connect(direction="from", whom=node) # connect forward

    def add_source(self, source):
        """Connect the source to all existing other nodes."""
        nodes = [n for n in self.nodes() if not isinstance(n, Source)]
        source.connect(whom=nodes)


class KarateClub(Network):
    """KarateClub network.

    Data originally from: http://vlado.fmf.uni-lj.si/pub/networks/data/Ucinet/UciData.htm#zachary

    Formatting as described in:
    https://networkx.github.io/documentation/networkx-1.9/examples/graph/karate_club.html

    An undirected, unweighted network showing connections between 34 members
    of Zachary's karate club.

    Reference:
    Zachary W. (1977).
    An information flow model for conflict and fission in small groups.
    Journal of Anthropological Research, 33, 452-473.
    """

    __mapper_args__ = {"polymorphic_identity": "karate_club"}

    def add_node(self, node):
        """Manually connect up a network."""

        # here are all the edges that need to be connected
        all_edges = [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8),
        (0, 10), (0, 11), (0, 12), (0, 13), (0, 17), (0, 19), (0, 21), (0, 31), (1, 17),
        (1, 2), (1, 3), (1, 21), (1, 19), (1, 7), (1, 13), (1, 30), (2, 3), (2, 32),
        (2, 7), (2, 8), (2, 9), (2, 27), (2, 28), (2, 13), (3, 7), (3, 12), (3, 13), (4, 10),
        (4, 6), (5, 16), (5, 10), (5, 6), (6, 16), (8, 32), (8, 30), (8, 33), (9, 33),
        (13, 33), (14, 32), (14, 33), (15, 32), (15, 33), (18, 32), (18, 33), (19, 33),
        (20, 32), (20, 33), (22, 32), (22, 33), (23, 32), (23, 25), (23, 27), (23, 29),
        (23, 33), (24, 25), (24, 27), (24, 31), (25, 31), (26, 33), (26, 29), (27, 33),
        (28, 33), (28, 31), (29, 32), (29, 33), (30, 33), (30, 32), (31, 32), (31, 33),
        (32, 33)]

        # walk through edges
        for edge in all_edges:
            if node.id-2 == max(edge): # wait until you can connect backwards
                connect_to_node = Node.query.filter_by(id=min(edge)+2).one()
                node.connect(direction="from", whom=connect_to_node) # connect backward
                connect_to_node.connect(direction="from", whom=node) # connect forward

    def add_source(self, source):
        """Connect the source to all existing other nodes."""
        nodes = [n for n in self.nodes() if not isinstance(n, Source)]
        source.connect(whom=nodes)


class SmallWorld(Network):
    """Small-world network.
    Manually constructing networks based on getting the edges from
    running python's NetworkX connected_watts_strogatz_graph(n, k, p) function
    """

    __mapper_args__ = {"polymorphic_identity": "small_world"}

    def add_node(self, node):
        """Manually connect up a network."""

        # here are all the edges that need to be connected
        all_edges = [(0, 32), (0, 1), (0, 2), (0, 33), (1, 33), (1, 3), (1, 8),
        (2, 3), (2, 4), (3, 4), (3, 5), (4, 5), (4, 6), (5, 6), (5, 7), (6, 8),
        (6, 7), (7, 8), (7, 9), (8, 9), (8, 26), (9, 23), (9, 10), (9, 11),
        (10, 11), (10, 12), (11, 32), (11, 12), (12, 13), (12, 14), (13, 14),
        (13, 15), (14, 16), (14, 15), (15, 16), (15, 28), (16, 17), (16, 18),
        (17, 18), (17, 19), (18, 19), (18, 20), (19, 20), (19, 33), (20, 21),
        (20, 22), (21, 22), (21, 23), (22, 24), (22, 23), (23, 25), (24, 25),
        (24, 27), (25, 26), (25, 27), (26, 32), (26, 27), (26, 28), (27, 28),
        (27, 29), (28, 29), (28, 30), (29, 30), (29, 31), (30, 32), (30, 31),
        (31, 32), (31, 33)]

        # walk through edges
        for edge in all_edges:
            if node.id-2 == max(edge): # wait until you can connect backwards
                connect_to_node = Node.query.filter_by(id=min(edge)+2).one()
                node.connect(direction="from", whom=connect_to_node) # connect backward
                connect_to_node.connect(direction="from", whom=node) # connect forward

    def add_source(self, source):
        """Connect the source to all existing other nodes."""
        nodes = [n for n in self.nodes() if not isinstance(n, Source)]
        source.connect(whom=nodes)

class Star(Network):
    """A star network.

    A star newtork has a central node with a pair of vectors, incoming and
    outgoing, with all other nodes.
    """

    __mapper_args__ = {"polymorphic_identity": "star"}

    def add_node(self, node):
        """Add a node and connect it to the center."""
        nodes = self.nodes()

        if len(nodes) > 1:
            first_node = min(nodes, key=attrgetter('creation_time'))
            first_node.connect(direction="both", whom=node)


class Burst(Network):
    """A burst network.

    A burst network has a central node with an outgoing connection to each of
    the other nodes.
    """

    __mapper_args__ = {"polymorphic_identity": "burst"}

    def add_node(self, node):
        """Add a node and connect it to the center."""
        nodes = self.nodes()

        if len(nodes) > 1:
            first_node = min(nodes, key=attrgetter('creation_time'))
            first_node.connect(whom=node)


class DiscreteGenerational(Network):
    """A discrete generational network.

    A discrete generational network arranges agents into none-overlapping
    generations. Each agent is connected to all agents in the previous
    generation. If initial_source is true agents in the first generation will
    connect to the oldest source in the network. generation_size dictates how
    many agents are in each generation, generations sets how many generations
    the network involves.

    Note that this network type assumes that agents have a property called
    generation. If you agents do not have this property it will not work.
    """

    __mapper_args__ = {"polymorphic_identity": "discrete-generational"}

    def __init__(self, generations, generation_size, initial_source):
        """Endow the network with some persistent properties."""
        self.property1 = repr(generations)
        self.property2 = repr(generation_size)
        self.property3 = repr(initial_source)
        if self.initial_source:
            self.max_size = repr(generations * generation_size + 1)
        else:
            self.max_size = repr(generations * generation_size)

    @property
    def generations(self):
        """The length of the network: the number of generations."""
        return int(self.property1)

    @property
    def generation_size(self):
        """The width of the network: the size of a single generation."""
        return int(self.property2)

    @property
    def initial_source(self):
        """The source that seeds the first generation."""
        return bool(self.property3)

    def add_node(self, node):
        """Link the agent to a random member of the previous generation."""
        nodes = [n for n in self.nodes() if not isinstance(n, Source)]
        num_agents = len(nodes)
        curr_generation = int((num_agents - 1) / float(self.generation_size))
        node.generation = curr_generation

        if curr_generation == 0:
            if self.initial_source:
                source = min(
                    self.nodes(type=Source),
                    key=attrgetter('creation_time'))
                source.connect(whom=node)
                source.transmit(to_whom=node)
        else:
            prev_agents = type(node).query\
                .filter_by(failed=False,
                           network_id=self.id,
                           generation=(curr_generation - 1))\
                .all()
            prev_fits = [p.fitness for p in prev_agents]
            prev_probs = [(f / (1.0 * sum(prev_fits))) for f in prev_fits]

            rnd = random.random()
            temp = 0.0
            for i, probability in enumerate(prev_probs):
                temp += probability
                if temp > rnd:
                    parent = prev_agents[i]
                    break

            parent.connect(whom=node)
            parent.transmit(to_whom=node)


class ScaleFree(Network):
    """Barabasi-Albert (1999) model of a scale-free network.

    The construction process begins with a fully-connected network with m0
    individuals. After that point, every newcomer makes m connections with
    existing memebers of the network. Critically, new connections are
    chosen using preferential attachment (i.e., you connect with agents
    according to how many connections they already have).
    """

    __mapper_args__ = {"polymorphic_identity": "scale-free"}

    def __init__(self, m0, m):
        """Store m0 in property1 and m in property2."""
        self.property1 = repr(m0)
        self.property2 = repr(m)

    @property
    def m0(self):
        """Number of nodes in the fully-connected core."""
        return int(self.property1)

    @property
    def m(self):
        """Number of connections that a newcomer makes."""
        return int(self.property2)

    def add_node(self, node):
        """Add newcomers one by one, using linear preferential attachment."""
        nodes = self.nodes()

        # Start with a core of m0 fully-connected agents...
        if len(nodes) <= self.m0:
            other_nodes = [n for n in nodes if n.id != node.id]
            for n in other_nodes:
                node.connect(direction="both", whom=n)

        # ...then add newcomers one by one with preferential attachment.
        else:
            for idx_newvector in xrange(self.m):

                these_nodes = [
                    n for n in nodes if (
                        n.id != node.id and
                        not n.is_connected(direction="either", whom=node))]

                outdegrees = [
                    len(n.vectors(direction="outgoing")) for n in these_nodes]

                # Select a member using preferential attachment
                ps = [(d / (1.0 * sum(outdegrees))) for d in outdegrees]
                rnd = random.random() * sum(ps)
                cur = 0.0
                for i, p in enumerate(ps):
                    cur += p
                    if rnd < cur:
                        vector_to = these_nodes[i]

                # Create vector from newcomer to selected member and back
                node.connect(direction="both", whom=vector_to)


class SequentialMicrosociety(Network):
    """A microsociety."""

    __mapper_args__ = {"polymorphic_identity": "microsociety"}

    def __init__(self, n):
        """Store n in property1."""
        self.property1 = repr(n)

    @property
    def n(self):
        """Number of nodes active at once."""
        return int(self.property1)

    def add_node(self, node):
        """Add a node, connecting it to all the active nodes."""
        nodes = sorted(
            self.nodes(),
            key=attrgetter('creation_time'), reverse=True)

        other_nodes = [n for n in nodes if n.id != node.id]

        connecting_nodes = other_nodes[0:(self.n - 1)]

        for n in connecting_nodes:
            n.connect(whom=node)
