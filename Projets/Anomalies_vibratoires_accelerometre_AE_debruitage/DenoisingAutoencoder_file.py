import torch
import torch.nn as nn
import torch.optim as optim
from fastdist import fastdist

import random
import numpy as np


class DenoisingAutoencoder(nn.Module):
    def __init__(self):
        super().__init__()

        self.encoder = nn.Sequential(
            nn.Conv1d(1, 16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool1d(2),
            nn.Conv1d(16, 8, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool1d(2)
        )

        self.decoder = nn.Sequential(
            nn.ConvTranspose1d(8, 16, kernel_size=2, stride=2),
            nn.ReLU(),
            nn.ConvTranspose1d(16, 1, kernel_size=2, stride=2)
        )

    def forward(self, x):
        x = self.encoder(x)
        x = self.decoder(x)
        return x


class AnomalyDetector:
    def __init__(self, window_size):
        self.window_size = window_size
        self.model = DenoisingAutoencoder()
        self.mean_data, self.std_data = None, None

    def add_noise(self, data, noise_interval=(18, 30)):
        noisy_data = data.copy()
        for i in range(0, len(data), self.window_size):
            num_anomalies = random.randint(10, 20)
            anomaly_indices = random.sample(range(i, i + self.window_size), num_anomalies)
            for j in anomaly_indices:
                noisy_data[j] = random.randint(*noise_interval)
        return noisy_data

    def normalize_data(self, data, noisy_data):
        self.mean_data, self.std_data = np.mean(data), np.std(data)
        data = (data - self.mean_data) / self.std_data
        noisy_data = (noisy_data - self.mean_data) / self.std_data
        return data, noisy_data

    def create_window_sequences(self, data, noisy_data):
        X = [noisy_data[i:i + self.window_size] for i in range(len(noisy_data) - self.window_size + 1)]
        y = [data[i:i + self.window_size] for i in range(len(data) - self.window_size + 1)]
        return np.array(X), np.array(y)

    def fit(self, X, y, n_epochs=100, batch_size=4, learning_rate=1e-3):
        criterion = nn.MSELoss()
        optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)

        X = torch.tensor(X, dtype=torch.float32).unsqueeze(1)
        y = torch.tensor(y, dtype=torch.float32).unsqueeze(1)

        for epoch in range(n_epochs):
            epoch_loss = 0
            for i in range(0, len(X), batch_size):
                batch_data = X[i:i + batch_size]
                batch_noisy_data = y[i:i + batch_size]
                outputs = self.model(batch_noisy_data)
                loss = criterion(outputs, batch_data)
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                epoch_loss += loss.item()

            epoch_loss /= len(X) // batch_size
            print(f"Epoch [{epoch + 1}/{n_epochs}], Loss: {epoch_loss:.4f}")

    def predict(self, input_data):
        input_data = torch.tensor(input_data, dtype=torch.float32).unsqueeze(0).unsqueeze(1)
        output_data = self.model(input_data).squeeze().detach().numpy()
        return output_data

    @staticmethod
    def detect_shock(input_data, output_data, threshold=140):
        distance = fastdist.euclidean(input_data, output_data)
        # print(f"Distance: {distance:.2f}")
        return distance > threshold

    def save_model(self, path="model.pt"):
        torch.save(self.model.state_dict(), path)

    def load_model(self, path="model.pt"):
        self.model.load_state_dict(torch.load(path))


if __name__ == '__main__':
    # ================================== #
    #               Main                 #
    # ================================== #

    window_size = 200
    Real_time = False  # Set to True to use the model in real time
    detector = AnomalyDetector(window_size)
    data = np.loadtxt('Raw_data_5000.txt')
    noisy_data = detector.add_noise(data)

    data, noisy_data = detector.normalize_data(data, noisy_data)
    X, y = detector.create_window_sequences(data, noisy_data)

    detector.fit(X, y)

    detector.save_model()
