from projects.pj02 import constants
from projects.pj02.model import Model
from projects.pj02.ViewController import ViewController

def work_unit():
    model = Model(constants.CELL_COUNT, constants.CELL_SPEED)
    vc = ViewController(model)
    vc.start_simulation()