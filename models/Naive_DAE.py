"""Implementation of a Deep Autoencoder"""
import torch
import torch.nn as nn
import torch.nn.functional as F




class DAE(nn.Module):
    """A Deep Autoencoder that takes a list of RBMs as input"""

    def __init__(self, models):
        """Create a deep autoencoder based on a list of RBM models

        Parameters
        ----------
        models: list[RBM]
            a list of RBM models to use for autoencoding
        """
        super(DAE, self).__init__()

        # extract weights from each model
        encoders = []
        encoder_biases = []
        decoders = []
        decoder_biases = []
        for model in models:
            encoders.append(nn.Parameter(model.W.clone()))
            encoder_biases.append(nn.Parameter(model.h_bias.clone()))
            decoders.append(nn.Parameter(model.W.clone()))
            decoder_biases.append(nn.Parameter(model.v_bias.clone()))
        
        
        # build encoders and decoders
        self.encoders = nn.ParameterList(encoders)
        self.encoder_biases = nn.ParameterList(encoder_biases)
        self.decoders = nn.ParameterList(reversed(decoders))
        self.decoder_biases = nn.ParameterList(reversed(decoder_biases))

    def forward(self, v):
        """Forward step

        Parameters
        ----------
        v: Tensor
            input tensor

        Returns
        -------
        Tensor
            a reconstruction of v from the autoencoder

        """
        # encode
        p_h = self.encode(v)

        # decode
        p_v = self.decode(p_h)

        return p_v

    def encode(self, v):  # for visualization, encode without sigmoid
        """Encode input

        Parameters
        ----------
        v: Tensor
            visible input tensor

        Returns
        -------
        Tensor
            the activations of the last layer

        """
        p_v = v
        activation = v
        for i in range(len(self.encoders)):
            W = self.encoders[i]
            h_bias = self.encoder_biases[i]
            activation = torch.mm(p_v, W) + h_bias
            p_v = activation

        # for the last layer, we want to return the activation directly rather than the sigmoid
        return activation

    def decode(self, h):
        """Encode hidden layer

        Parameters
        ----------
        h: Tensor
            activations from last hidden layer

        Returns
        -------
        Tensor
            reconstruction of original input based on h

        """
        p_h = h
        for i in range(len(self.encoders)):
            W = self.decoders[i]
            v_bias = self.decoder_biases[i]
            activation = torch.mm(p_h, W.t()) + v_bias
            p_h = activation
        return p_h


class Naive_DAE(nn.Module):
    """A Naive implementation of the DAE to be trained without RBMs"""

    def __init__(self, layers,with_loc=False):
        """Initialize the DAE

        Parameters
        ----------
        layers: list[int]
            the number of dimensions in each layer of the DAE

        """
        super(Naive_DAE, self).__init__()

        self.layers = layers
        if not with_loc:
            encoders = []
            decoders = []
            
            prev_layer = layers[0]
            for layer in layers[1:]:
                encoders.append(
                    nn.Linear(in_features=prev_layer, out_features=layer))
                encoders.append(
                    nn.ReLU())

                decoders.append(
                    nn.Linear(in_features=layer, out_features=prev_layer))
                decoders.append(
                    nn.ReLU())

                prev_layer = layer
            self.encoders = nn.ModuleList(encoders)
            self.decoders = nn.ModuleList(reversed(decoders))
            self.decoders = nn.ModuleList(reversed([nn.ReLU()]+decoders))
        else:
            encoders = []
            decoders = []
            prev_layer = layers[0]
            i = 0
            for layer in layers[1:]:
                if i == 0: 
                    decoders.append(
                    nn.Linear(in_features=layer, out_features=48))
                    decoders.append(
                        nn.ReLU()) 
                else:
                    decoders.append(
                    nn.Linear(in_features=layer, out_features=prev_layer))
                    decoders.append(
                    nn.ReLU())
                
                encoders.append(
                    nn.Linear(in_features=prev_layer, out_features=layer))
                encoders.append(
                    nn.ReLU())

                prev_layer = layer
                i=i+1
            
            self.encoders = nn.ModuleList(encoders)
            self.decoders = nn.ModuleList(reversed(decoders))
    def forward(self, x):
        """Forward step
        
        Parameters
        ----------
        x: Tensor
            input tensor
        
        Returns
        -------
        Tensor
            a reconstructed version of x

        """
        x_encoded = self.encode(x)
        x_reconstructed = self.decode(x_encoded)
        return x_reconstructed

    def encode(self, x):
        """Encode the input x
        
        Parameters
        ----------
        x: Tensor
            input to encode
        
        Returns
        -------
        Tensor
            encoded input

        """
        for i, enc in enumerate(self.encoders):
            if i == len(self.encoders) - 1:
                x = enc(x)
            else:
                x = enc(x)
        return x
    
    def decode(self, x):
        """Decode the representation x
        
        Parameters
        ----------
        x: Tensor
            input to decode
        
        Returns
        -------
        Tensor
            decoded input

        """
        for dec in self.decoders:
            x = dec(x)
        return x
class Conv_DAE(nn.Module):
    """A Naive implementation of the DAE to be trained without RBMs"""

    def __init__(self, layers,with_loc=False):
        """Initialize the DAE

        Parameters
        ----------
        layers: list[int]
            the number of dimensions in each layer of the DAE

        """
        super(Conv_DAE, self).__init__()

        self.layers = layers
        if not with_loc:
            encoders = []
            decoders = []
            encoders.append(nn.Conv1d(in_channels = 1, out_channels = 1,kernel_size = 5,padding = 2))
            prev_layer = layers[0]
            for layer in layers[1:]:
                encoders.append(
                    nn.Linear(in_features=prev_layer, out_features=layer))
                encoders.append(
                    nn.ReLU())

                decoders.append(
                    nn.Linear(in_features=layer, out_features=prev_layer))
                decoders.append(
                    nn.ReLU())

                prev_layer = layer
            self.encoders = nn.ModuleList(encoders)
            self.decoders = nn.ModuleList(reversed(decoders))
        else:
            encoders = []
            decoders = []
            prev_layer = layers[0]
            i = 0
            for layer in layers[1:]:
                if i == 0: 
                    decoders.append(
                    nn.Linear(in_features=layer, out_features=48))
                    decoders.append(
                        nn.ReLU()) 
                else:
                    decoders.append(
                    nn.Linear(in_features=layer, out_features=prev_layer))
                    decoders.append(
                    nn.ReLU())
                
                encoders.append(
                    nn.Linear(in_features=prev_layer, out_features=layer))
                encoders.append(
                    nn.ReLU())

                prev_layer = layer
                i=i+1
            
            self.encoders = nn.ModuleList(encoders)
            self.decoders = nn.ModuleList(reversed(decoders))
    def forward(self, x):
        """Forward step
        
        Parameters
        ----------
        x: Tensor
            input tensor
        
        Returns
        -------
        Tensor
            a reconstructed version of x

        """
        x_encoded = self.encode(x)
        x_reconstructed = self.decode(x_encoded)
        return x_reconstructed

    def encode(self, x):
        """Encode the input x
        
        Parameters
        ----------
        x: Tensor
            input to encode
        
        Returns
        -------
        Tensor
            encoded input

        """
        for i, enc in enumerate(self.encoders):
            if i == len(self.encoders) - 1:
                x = enc(x)
            else:
                x = enc(x)
        return x
    
    def decode(self, x):
        """Decode the representation x
        
        Parameters
        ----------
        x: Tensor
            input to decode
        
        Returns
        -------
        Tensor
            decoded input

        """
        for dec in self.decoders:
            x = dec(x)
        return x
class Dropout_DAE(nn.Module):
    """A Naive implementation of the DAE to be trained without RBMs"""

    def __init__(self, layers,with_loc=False):
        """Initialize the DAE

        Parameters
        ----------
        layers: list[int]
            the number of dimensions in each layer of the DAE

        """
        super(Dropout_DAE, self).__init__()

        self.layers = layers
        if not with_loc:
            encoders = []
            decoders = []
            
            prev_layer = layers[0]
            for layer in layers[1:]:
                encoders.append(
                    nn.Linear(in_features=prev_layer, out_features=layer))
                encoders.append(
                    nn.ReLU())
                encoders.append(nn.Dropout(p=0.1))
                    

                decoders.append(
                    nn.Linear(in_features=layer, out_features=prev_layer))
                decoders.append(
                    nn.ReLU())
                decoders.append(nn.Dropout(p=0.1))

                prev_layer = layer
            
            encoders = encoders[0:-1]
            decoders = decoders[0:-1]
            print(encoders)
            print(decoders)
            self.encoders = nn.ModuleList(encoders)
            self.decoders = nn.ModuleList(reversed(decoders))
            
        else:
            encoders = []
            decoders = []
            prev_layer = layers[0]
            i = 0
            for layer in layers[1:]:
                if i == 0: 
                    decoders.append(
                    nn.Linear(in_features=layer, out_features=48))
                    decoders.append(
                        nn.ReLU()) 
                else:
                    decoders.append(
                    nn.Linear(in_features=layer, out_features=prev_layer))
                    decoders.append(
                    nn.ReLU())
                
                encoders.append(
                    nn.Linear(in_features=prev_layer, out_features=layer))
                encoders.append(
                    nn.ReLU())

                prev_layer = layer
                i=i+1
            encoders = encoders[0:-1]
            decodes = decoders[1:]
            self.encoders = nn.ModuleList(encoders)
            self.decoders = nn.ModuleList(reversed(decoders))
    def forward(self, x):
        """Forward step
        
        Parameters
        ----------
        x: Tensor
            input tensor
        
        Returns
        -------
        Tensor
            a reconstructed version of x

        """
        x_encoded = self.encode(x)
        x_reconstructed = self.decode(x_encoded)
        return x_reconstructed

    def encode(self, x):
        """Encode the input x
        
        Parameters
        ----------
        x: Tensor
            input to encode
        
        Returns
        -------
        Tensor
            encoded input

        """
        for i, enc in enumerate(self.encoders):
            if i == len(self.encoders) - 1:
                x = enc(x)
            else:
                x = enc(x)
        return x
    
    def decode(self, x):
        """Decode the representation x
        
        Parameters
        ----------
        x: Tensor
            input to decode
        
        Returns
        -------
        Tensor
            decoded input

        """
        for dec in self.decoders:
            x = dec(x)
        return x