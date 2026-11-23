"""fastcoref on transformers 5: FCorefModel gets the post_init() that transformers 5 needs.

fastcoref 2.1.6 (unmaintained since 2023) ends FCorefModel.__init__ with the old self.init_weights(). transformers 5
sets all_tied_weights_keys in post_init(), and from_pretrained reads it, so FCoref() stopped with
"'FCorefModel' object has no attribute 'all_tied_weights_keys'" (1.6.47, Python 3.11). The patch calls post_init()
when that attribute is missing, and does nothing on transformers 4.
"""

import coreference_neural_util


class _Model:
    """Stands in for FCorefModel: __init__ runs the model's own setup, post_init sets the transformers 5 attribute."""

    def __init__(self, config, sets_attribute=False):
        self.config = config
        self.post_init_calls = 0
        if sets_attribute:  # as on transformers 4 code paths that already set it
            self.all_tied_weights_keys = {}

    def post_init(self):
        self.post_init_calls += 1
        self.all_tied_weights_keys = {}


def _fresh_class():
    return type("FCorefModel", (_Model,), {})


def test_post_init_runs_when_the_attribute_is_missing():
    cls = _fresh_class()
    coreference_neural_util.patch_fastcoref_post_init(cls)
    model = cls("config")
    assert model.config == "config"
    assert model.post_init_calls == 1
    assert model.all_tied_weights_keys == {}


def test_post_init_not_run_again_when_the_attribute_is_set():
    cls = _fresh_class()
    coreference_neural_util.patch_fastcoref_post_init(cls)
    model = cls("config", sets_attribute=True)
    assert model.post_init_calls == 0


def test_patching_twice_wraps_once():
    cls = _fresh_class()
    coreference_neural_util.patch_fastcoref_post_init(cls)
    coreference_neural_util.patch_fastcoref_post_init(cls)
    assert cls("config").post_init_calls == 1
