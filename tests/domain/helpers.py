from counter.domain.models import Box, Prediction


def generate_prediction(class_name, score=1.0):
    return Prediction(
        class_name=class_name, score=score, box=Box(xmin=0, ymin=0, xmax=0, ymax=0)
    )
