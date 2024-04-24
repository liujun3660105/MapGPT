
def get_device() -> str:
    try:
        import torch

        return (
            "cuda"
            if torch.cuda.is_available()
            else "mps"
            if torch.backends.mps.is_available()
            else "cpu"
        )
    except ModuleNotFoundError:
        return "cpu"