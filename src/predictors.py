import torch
import torch.nn.functional as F
import dgl.function as fn
import sympy
import scipy
import dgl.nn.pytorch.conv as dglnn
import dgl
from torch import nn
from scipy.special import comb
import math
import copy
import numpy as np
from collections import OrderedDict

import itertools
from functools import reduce
import utils

EPS = 1e-5

def apply_edges_distance(edges):
    # L2 norm
    h_edge = torch.linalg.norm(edges.src['h_tmp'] - edges.dst['h_tmp'], dim=1, ord=2)
    return {'h_edge': h_edge}

def SubgraphPooling(h, sg):
    with sg.local_scope():
        sg.ndata['h_tmp'] = h
        sg.update_all(fn.u_mul_e('h_tmp', 'pw', 'm'), fn.sum('m', 'h_tmp'))
        h = sg.ndata['h_tmp'] + h

        return h

class MLP(nn.Module):
    def __init__(self, in_feats, h_feats=32, num_classes=2, num_layers=2, dropout_rate=0, activation='ReLU', **kwargs):
        super(MLP, self).__init__()
        self.layers = nn.ModuleList()
        self.act = getattr(nn, activation)()
        if num_layers == 0:
            return
        if num_layers == 1:
            self.layers.append(nn.Linear(in_feats, num_classes))
        else:
            self.layers.append(nn.Linear(in_feats, h_feats))
            for i in range(1, num_layers-1):
                self.layers.append(nn.Linear(h_feats, h_feats))
            self.layers.append(nn.Linear(h_feats, num_classes))
        self.dropout = nn.Dropout(dropout_rate) if dropout_rate > 0 else nn.Identity()

    def forward(self, h, is_graph=True):
        if is_graph:
            h = h.ndata['feature']
        for i, layer in enumerate(self.layers):
            if i != 0:
                h = self.dropout(h)
            h = layer(h)
            if i != len(self.layers)-1:
                h = self.act(h)
        return h

class UNIMLP(nn.Module):
    def __init__(self, in_feats, h_feats=32, num_classes=2, num_layers=3, mlp_layers=2, dropout_rate=0, activation='ReLU', graph_batch_num=1, **kwargs):
        super().__init__()
        # batch size
        self.graph_batch_num = graph_batch_num
        self.num_classes = num_classes
        self.mlp = MLP(h_feats, h_feats, num_classes, mlp_layers, dropout_rate)

    def forward(self, g, h):
        with g.local_scope():
            num_nodes = h.shape[0]
            g.ndata['h'] = h
            hg = dgl.mean_nodes(g, 'h')
            h_hg = torch.cat([h, hg], 0)
            out = self.mlp(h_hg)
            node_logits, graph_logits = torch.split(out, num_nodes, dim=0)
            return node_logits, graph_logits

class UNIMLP_E2E(nn.Module):
    def __init__(self, in_feats, embed_dims=32, num_classes=2, stitch_mlp_layers=1, final_mlp_layers=2, dropout_rate=0, khop=0, activation='ReLU', graph_batch_num=1, pretrain_model=None, output_route='n', input_route='n', **kwargs):
        super().__init__()
        # batch size
        self.graph_batch_num = graph_batch_num
        self.num_classes = num_classes
        self.embed_dims = embed_dims
        self.pretrain_model = pretrain_model
        self.dropout = nn.Dropout(dropout_rate, inplace=True) if dropout_rate > 0 else nn.Identity()
        self.input_route = input_route
        self.output_route = output_route

        ######## network structure start
        scaling_cross = 1.0
        self.act = getattr(nn, activation)()
        # isolated layer 1
        self.layer1 = nn.ModuleDict({k:nn.Sequential() for k in input_route}) # no label, no model
        for k in input_route:
            for _ in range(stitch_mlp_layers):
                self.layer1[k].append(nn.Linear(embed_dims, embed_dims))
                self.layer1[k].append(self.act)
        # agg layer 2
        self.layer2 = nn.ParameterDict({
            ''.join(k):nn.Parameter(data=torch.ones(1), requires_grad=True) if k[0] == k[1] 
            else nn.Parameter(data=torch.rand(1)*scaling_cross, requires_grad=True)
         for k in itertools.product(output_route, input_route) })
        # isolated layer 3
        self.layer3 = nn.ModuleDict({k:nn.Sequential() for k in input_route}) # no label, no model
        for k in input_route:
            for _ in range(stitch_mlp_layers):
                self.layer3[k].append(nn.Linear(embed_dims, embed_dims))
                self.layer3[k].append(self.act)
        # agg layer 4
        self.layer4 = nn.ParameterDict({
            ''.join(k):nn.Parameter(data=torch.ones(1), requires_grad=True) if k[0] == k[1] 
            else nn.Parameter(data=torch.rand(1)*scaling_cross, requires_grad=True)
         for k in itertools.product(output_route, input_route) })
        # final isolated layer
        self.layer56 = nn.Sequential(self.dropout) 
        for k in input_route:
            for _ in range(final_mlp_layers):
                self.layer56.append(nn.Linear(embed_dims, embed_dims))
                self.layer56.append(self.act)
        self.layer56.append(nn.Linear(embed_dims, num_classes)) # final output
        self.layers = nn.ModuleList([self.layer1, self.layer2, self.layer3, self.layer4, self.layer56])
        ######## network structure end

        self.khop = khop
        self.pooling_act = nn.LeakyReLU() # non-linear after pooling
        self.mask_dicts = {}
        self.single_graph = False

    def apply_edges(self, edges):
        return {'h_edge': (edges.src['h'] + edges.dst['h']) / 2}

    def _cross_agg(self, g, feat, o_r, i_r):
        """Aggregate cross-level features (e.g. edge->node or node->edge) via graph message passing."""
        if o_r == 'n' and i_r == 'e':
            g.edata['_ch'] = feat
            g.update_all(fn.copy_e('_ch', '_cm'), fn.mean('_cm', '_cn'))
            return g.ndata['_cn']
        elif o_r == 'e' and i_r == 'n':
            g.ndata['_ch'] = feat
            g.apply_edges(lambda edges: {'_ce': (edges.src['_ch'] + edges.dst['_ch']) / 2})
            return g.edata['_ce']
        elif o_r == 'g' and i_r == 'n':
            g.ndata['_ch'] = feat
            return dgl.mean_nodes(g, '_ch')
        elif o_r == 'n' and i_r == 'g':
            return dgl.broadcast_nodes(g, feat)
        return None

    def _agg_layer(self, g, layer, models_last, inner_state):
        """Compute one aggregation layer, handling cross-level pairs via graph message passing."""
        new_inner_state = {}
        for o_r in self.output_route:
            terms = []
            for i_r in self.input_route:
                w = layer[''.join((o_r, i_r))]
                feat = models_last[i_r](inner_state[i_r])
                if o_r == i_r:
                    terms.append(w * feat)
                else:
                    cross = self._cross_agg(g, feat, o_r, i_r)
                    if cross is not None:
                        terms.append(w * cross)
            new_inner_state[o_r] = reduce(torch.Tensor.add, terms) if terms else inner_state[o_r]
        return new_inner_state

    def forward(self, g, h, sg_matrix, scen='train'):
        if not self.single_graph:
            # deactivate the BN and dropout for encoder
            self.pretrain_model.eval()
            with g.local_scope():
                inner_state = {}
                h = self.pretrain_model.embed(g, h)
                if 'g' in self.output_route:
                    g.ndata['h'] = h
                    inner_state['g'] = dgl.mean_nodes(g, 'h')
                    g.ndata.pop('h')
                if self.khop != 0:
                    h = SubgraphPooling(h, sg_matrix)
                if 'n' in self.output_route:
                    inner_state['n'] = h
                if 'e' in self.output_route:
                    g.ndata['h'] = h
                    g.apply_edges(self.apply_edges)
                    g.ndata.pop('h')
                    inner_state['e'] = g.edata['h_edge']

                for idx, layer in enumerate(self.layers):
                    if isinstance(layer, nn.ParameterDict):
                        models_last = self.layers[idx-1]
                        inner_state.update(self._agg_layer(g, layer, models_last, inner_state))
                    elif idx == 0 or idx == 2:
                        continue
                    else:
                        for o_r in self.output_route:
                            inner_state[o_r] = layer(inner_state[o_r])
                return inner_state
        else:
            self.pretrain_model.eval()
            # For single-graph, build full (unmasked) embeddings so that cross-level
            # aggregation can use the complete graph structure, then mask at the end.
            with g.local_scope():
                inner_state = {}
                h = self.pretrain_model.embed(g, h)
                if 'g' in self.output_route:
                    g.ndata['h'] = h
                    inner_state['g'] = dgl.mean_nodes(g, 'h')
                    g.ndata.pop('h')
                if self.khop != 0:
                    h = SubgraphPooling(h, sg_matrix)
                if 'n' in self.output_route:
                    inner_state['n'] = h
                if 'e' in self.output_route:
                    g.ndata['h'] = h
                    g.apply_edges(self.apply_edges)
                    g.ndata.pop('h')
                    inner_state['e'] = g.edata['h_edge']

                for idx, layer in enumerate(self.layers):
                    if isinstance(layer, nn.ParameterDict):
                        models_last = self.layers[idx-1]
                        inner_state.update(self._agg_layer(g, layer, models_last, inner_state))
                    elif idx == 0 or idx == 2:
                        continue
                    else:
                        for o_r in self.output_route:
                            inner_state[o_r] = layer(inner_state[o_r])

                # Apply node/edge masks after all layers so cross-level agg works on the full graph
                for k, masks in self.mask_dicts.items():
                    if k in inner_state and scen in masks:
                        inner_state[k] = inner_state[k][masks[scen], :]
                return inner_state
