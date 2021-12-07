"""This specially named module makes the package runnable."""

from projects.pj02 import constants
from projects.pj02.model import Model
from projects.pj02.ViewController import ViewController
from projects.pj02.work import work_unit
import concurrent.futures

def main() -> None:
    """Entrypoint of simulation."""
    with concurrent.futures.ProcessPoolExecutor(max_workers=128) as executor:
        future_to_tick = {
            executor.submit(work_unit): \
                _ for _ in range(0,1)
        }
        for future in concurrent.futures.as_completed(future_to_tick):
            res = future.result()

if __name__ == "__main__":
    main()
