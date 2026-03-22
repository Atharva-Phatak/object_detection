import sys

from counter import config
from counter.helper.logger import setup_logger

logger = setup_logger(__name__)

if __name__ == "__main__":
    img_path = sys.argv[1]
    threshold = float(sys.argv[2])
    with open(img_path, "rb") as img:
        predictions = config.get_count_action().execute(img, threshold)

        logger.info(predictions)
