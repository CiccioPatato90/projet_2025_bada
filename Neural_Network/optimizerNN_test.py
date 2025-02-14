import torch
import torch.nn as nn
import torch.optim as optim
from pyBADA.bada4 import Bada4Aircraft, Parser as Bada4Parser, PTD
from utils.XML_Parser import XMLParser
from Input_Coefficient_NN import Input_Coefficient_NN
import pandas as pd
from sklearn.preprocessing import StandardScaler
import torch.nn.functional as F
import numpy as np




xml_parser = XMLParser("../reference_dummy_extracted/Dummy-TWIN-plus/Dummy-TWIN-plus.xml")

# Chargement des données BADA
badaVersion = "DUMMY"
allData = Bada4Parser.parseAll(badaVersion=badaVersion, filePath="../reference_dummy_extracted")

# Instance de l'avion
AC = Bada4Aircraft(badaVersion=badaVersion, acName="Dummy-TWIN-plus", allData=allData)
ptd = PTD(AC)

# Définition du modèle
class FuelEfficiencyNN(nn.Module):
    def __init__(self, input_size, output_size):
        super(FuelEfficiencyNN, self).__init__()
        self.fc1 = nn.Linear(input_size, 64)
        self.fc2 = nn.Linear(64, 64)
        self.fc3 = nn.Linear(64, output_size)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.fc3(x)  # Pas d'activation finale (les coefficients peuvent être positifs ou négatifs)
        return x


# Fonction de calcul de la consommation de carburant avec PyBADA
def fuel_consumption_model(predicted_coeffs, inputs):
    masses = inputs[:, 0].tolist()
    altitudes = inputs[:, 1].tolist()
    delta_temp = inputs[:, 2].tolist()

    fuel_flow_preds = []
    for i in range(len(masses)):
        xml_parser.modify_tag_NN("CD_clean/d", predicted_coeffs[:, 0].tolist())
        xml_parser.modify_tag_NN("CT/a",predicted_coeffs[:, 1].tolist())
        xml_parser.modify_tag_NN("CL_clean/bf",predicted_coeffs[:, 2].tolist())
        xml_parser.modify_tag_NN("CF/f",predicted_coeffs[:, 3].tolist())


        ptd_data = ptd.PTD_cruise(masses[0], [altitudes[i]], delta_temp[i])
        #print(ptd_data[11][0])
        fuel_flow_preds.append((ptd_data[11][0])*60)  # Index 12 correspond à la consommation de carburant (ff_complet)
    return torch.tensor(fuel_flow_preds, dtype=torch.float32)


# Fonction de perte basée sur l'erreur de consommation de carburant
def loss_function(predicted_coeffs, inputs, fuel_flow_real):
    fuel_flow_pred = fuel_consumption_model(predicted_coeffs, inputs)
    #print("prediction",fuel_flow_pred,"actual",fuel_flow_real)
    return F.mse_loss(fuel_flow_pred, fuel_flow_real)


# Hyperparamètres
input_size = 3  # Mass, Altitude, ISA
output_size = 4  # CD_clean/d, CT/a, CL_clean/bf, CF/f
learning_rate = 0.001
num_epochs = 1000

# Création du modèle et de l'optimiseur
model = FuelEfficiencyNN(input_size, output_size)
optimizer = optim.Adam(model.parameters(), lr=learning_rate)

# Chargement des données
data = pd.read_csv("../Data/combined_results.csv")

# Normalisation des entrées
scaler = StandardScaler()
dummy_inputs = scaler.fit_transform(data[["Mass", "Altitude", "ISA"]].values)
dummy_inputs = torch.tensor(dummy_inputs, dtype=torch.float32)


tags = ["CD_clean/d", "CT/a", "CL_clean/bf", "CF/f"]

coef = Input_Coefficient_NN(xml_parser,tags)
dummy_targets = coef.create()
dummy_targets = torch.tensor(dummy_targets, dtype=torch.float32)
'''coeff_scaler = StandardScaler()
dummy_targets = torch.tensor(coeff_scaler.fit_transform(dummy_targets), dtype=torch.float32)'''

dummy_fuel_flow_real = data["WFE"].values
dummy_fuel_flow_real = torch.tensor(dummy_fuel_flow_real, dtype=torch.float32)
'''fuel_flow_scaler = StandardScaler()
dummy_fuel_flow_real = torch.tensor(fuel_flow_scaler.fit_transform(dummy_fuel_flow_real.reshape(-1, 1)).flatten(), dtype=torch.float32)'''

dummy_fuel_flow_real = dummy_fuel_flow_real.clone().detach().requires_grad_(True)


# Boucle d'entraînement
def train_model(model, optimizer, inputs, targets, fuel_flow_real, num_epochs=1000):
    for epoch in range(num_epochs):
        optimizer.zero_grad()
        predictions = model(inputs)
        loss = loss_function(predictions, inputs, fuel_flow_real)
        loss.backward()
        optimizer.step()

        if epoch % 100 == 0:
            print(f"Epoch [{epoch}/{num_epochs}], Loss: {loss.item():.4f}")


# Entraînement du modèle
train_model(model, optimizer, dummy_inputs, dummy_targets, dummy_fuel_flow_real, num_epochs)
