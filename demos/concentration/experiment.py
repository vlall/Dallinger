"""The game Snake."""

import dallinger

config = dallinger.config.get_config()


def extra_parameters():
    config.register('num_participants', int)


class ConcentrationGame(dallinger.experiments.Experiment):
    """Define the structure of the experiment."""

    def __init__(self, session):
        """Initialize the experiment."""
        super(ConcentrationGame, self).__init__(session)
        self.experiment_repeats = 1
        self.initial_recruitment_size = config["num_participants"]
        self.setup()
