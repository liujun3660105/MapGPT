from dataclasses import asdict, dataclass, field
from typing import Optional,Dict,Any

# @PublicAPI(stability="beta")
@dataclass
class ModelOutput:
    """A class to represent the output of a LLM.""" ""

    text: str
    """The generated text."""
    error_code: int
    """The error code of the model inference. If the model inference is successful,
    the error code is 0."""
    model_context: Optional[Dict] = None
    finish_reason: Optional[str] = None
    usage: Optional[Dict[str, Any]] = None
    # metrics: Optional[ModelInferenceMetrics] = None
    """Some metrics for model inference"""

    def to_dict(self) -> Dict:
        """Convert the model output to dict."""
        return asdict(self)