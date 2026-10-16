class ClassificationPostprocess:
    def __call__(self, logits):
        if logits.ndim != 2 or logits.shape[1] < 2:
            raise ValueError("Expected logits with shape [batch, classes], classes >= 2")
        return {
            "logits": logits,
            "probabilities": logits.softmax(dim=1),
            "labels": logits.argmax(dim=1),
        }
