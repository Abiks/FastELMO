import torch
from .unidirectional_lm import UnidirectionalLM


class BidirectionalLM(torch.nn.Module):
    def __init__(self, sru=True, char_embedder_params=None, model_params=None):
        super().__init__()
        self.device = 'cpu'

        self.forward_lm = UnidirectionalLM(
            sru=sru,
            char_embedder_params=char_embedder_params,
            model_params=model_params
        )

        char_embedder = self.forward_lm.char_embedder
        self.backward_lm = UnidirectionalLM(
            char_embedder=char_embedder,
            sru=sru,
            char_embedder_params=char_embedder_params,
            model_params=model_params
        )

    def forward(self, ids, mask, return_embeddings=False, **kwargs):
        forward_out = self.forward_lm(ids, mask)
        
        backward_ids = torch.nn.utils.rnn.pad_sequence(
            [pline[torch.arange(s+1).flip(0)] for s, pline in zip(mask.sum(1), ids)],
            batch_first=True)

        backward_out = self.backward_lm(backward_ids, mask)
        backward_out = torch.nn.utils.rnn.pad_sequence(
            [pline[torch.arange(s+1).flip(0)] for s, pline in zip(mask.sum(1), backward_out)],
            batch_first=True)

        if return_embeddings:
            return torch.cat([forward_out, backward_out], dim=2)
        else:
            return {
                'forward_out': forward_out,
                'backward_out': backward_out
                }

    def to(self, device):
        self = super().to(device)
        self.device = device
        return self
