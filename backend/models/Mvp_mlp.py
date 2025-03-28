import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random


class Mvp_mlp(nn.Module):
    """
    PyTorch neural network for MVP prediction.
    
    Multi-layer perceptron with:
    - Configurable hidden layers
    - Dropout for regularization
    - ReLU activation
    - Adam optimizer
    - MSE loss
    
    Attributes:
        model (nn.Sequential): Neural network layers
        epochs (int): Training epochs
        learning_rate (float): Learning rate for optimizer
    """

    def __init__(self, input_size, hidden_layers, dropout, epochs, learning_rate, activation=nn.ReLU):
        """
        Args:
            input_size (int): Number of input features
            hidden_layers (list): Sizes of hidden layers
            dropout (float): Dropout probability
            epochs (int): Number of training epochs
            learning_rate (float): Learning rate
            activation: Activation function class
        """
        super(Mvp_mlp, self).__init__()
        layers = []
        prev_size = input_size
        self.epochs = epochs
        self.learning_rate = learning_rate
        torch.manual_seed(42)
        np.random.seed(42)
        random.seed(42)

        for layer_size in hidden_layers:
            layers.append(nn.Linear(prev_size, layer_size))
            layers.append(activation())
            layers.append(nn.Dropout(dropout))
            prev_size = layer_size

        layers.append(nn.Linear(prev_size, 1))
        self.model = nn.Sequential(*layers)

    def forward(self, x):
        return self.model(x)

    def fit(self, X, y):
        criterion = nn.MSELoss()
        optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)

        X, y = torch.tensor(X.values, dtype=torch.float32), torch.tensor(y.values, dtype=torch.float32).view(-1, 1)

        for epoch in range(self.epochs):
            self.train()
            optimizer.zero_grad()
            y_pred = self.forward(X)
            loss = criterion(y_pred, y)
            loss.backward()
            optimizer.step()

    def predict(self, X):
        self.eval()
        X = torch.tensor(X.values, dtype=torch.float32)
        with torch.no_grad():
            y_pred = self.forward(X)
            return y_pred.squeeze().numpy()


def set_random_seed(seed=42):
    # Set the random seed for reproducibility
    random.seed(seed)  # Python random
    np.random.seed(seed)  # NumPy random
    torch.manual_seed(seed)  # PyTorch random
    torch.cuda.manual_seed_all(seed)  # For all GPUs (if using CUDA)
    torch.backends.cudnn.deterministic = True  # Ensures deterministic results (some operations are non-deterministic on GPUs)
    torch.backends.cudnn.benchmark = False  # Disables auto-tuner to ensure reproducibility
