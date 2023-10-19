import sys
import json
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, 
                             QCheckBox, QPushButton, QDialog, 
                             QLineEdit, QFormLayout, QScrollArea,
                             QGroupBox, QLabel, QRadioButton, 
                             QGridLayout, QHBoxLayout, QButtonGroup, QTabWidget)

# Load resources from JSON files
with open("Resources/inorganic_resources.json", "r") as f:
    inorganic_resources_data = json.load(f)

with open("Resources/organic_resources.json", "r") as f:
    organic_resources = json.load(f)

inorganic_resources = list(inorganic_resources_data.keys())

def text_color_for_background(hex_color):
    # Convert hex color to RGB
    r = int(hex_color[1:3], 16) / 255.0
    g = int(hex_color[3:5], 16) / 255.0
    b = int(hex_color[5:7], 16) / 255.0
    
    # Calculate luminance
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    
    # Based on luminance, return either dark or light text color
    if luminance > 0.5:
        return "#000000"  # Black for bright backgrounds
    else:
        return "#FFFFFF"  # White for dark backgrounds


class PlanetTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # System Name Field
        self.system_name_le = QLineEdit()
        self.system_name_le.setPlaceholderText("Enter planet name")  # Changed placeholder text
        self.layout.addWidget(self.system_name_le)

        # Scroll Area for Planets
        self.scroll = QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll.setLayout(self.scroll_layout)
        self.scroll.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll)

        # Inorganic Resources
        resources_layout = QGridLayout()
        for idx, resource in enumerate(inorganic_resources):
            chk = QCheckBox(resource)
            resource_color = inorganic_resources_data[resource]["color"]  # Note the change from inorganic_resources to inorganic_resources_data
            text_color = text_color_for_background(resource_color)
            chk.setStyleSheet(f"QCheckBox {{ background-color: {resource_color}; color: {text_color}; }}")
            resources_layout.addWidget(chk, idx // 5, idx % 5)  # Assuming 5 columns


        # Organic Resources with buttons
        for idx, resource in enumerate(organic_resources, start=len(inorganic_resources)):
            btn = QPushButton(resource)
            btn.setFixedWidth(120)  # Set a fixed width to the button to prevent it from expanding too much.
            btn.clicked.connect(self.addOrganismDetails)
            resources_layout.addWidget(btn, idx // 5, idx % 5)

        self.layout.addLayout(resources_layout)
        
    def addOrganismDetails(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('Add Organism Details')
        dialog_layout = QFormLayout()

        # Organism Type (Flora or Fauna)
        type_group = QButtonGroup(dialog)
        flora_rb = QRadioButton("Flora")
        fauna_rb = QRadioButton("Fauna")
        type_group.addButton(flora_rb)
        type_group.addButton(fauna_rb)
        type_layout = QHBoxLayout()
        type_layout.addWidget(flora_rb)
        type_layout.addWidget(fauna_rb)
        dialog_layout.addRow("Type:", type_layout)

        # Organism Name
        name_le = QLineEdit()
        dialog_layout.addRow("Organism Name:", name_le)

        # Temperament
        temperament_group = QButtonGroup(dialog)
        temperament_layout = QHBoxLayout()
        temperaments = ["Skittish", "Fearless", "Wary", "Peaceful", "Defensive"]
        for temp in temperaments:
            rb = QRadioButton(temp)
            temperament_group.addButton(rb)
            temperament_layout.addWidget(rb)
        dialog_layout.addRow("Temperament:", temperament_layout)

        # Biomes (Listed as checkboxes)
        biome_layout = QHBoxLayout()
        biomes = ["Tropical Forest", "Deciduous Forest", "Mountains", "Savanna"]
        for biome in biomes:
            chk = QCheckBox(biome)
            biome_layout.addWidget(chk)
        dialog_layout.addRow("Biomes:", biome_layout)

        # Other details can be added similarly...

        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(dialog.accept)
        dialog_layout.addRow(ok_btn)

        dialog.setLayout(dialog_layout)
        dialog.exec_()  # This will block until the dialog is closed

        # Here you can store the collected data if needed.

        # Example:
        if name_le.text():
            organism_data = {
                'type': 'Flora' if flora_rb.isChecked() else 'Fauna',
                'name': name_le.text(),
                'temperament': [btn.text() for btn in temperament_group.buttons() if btn.isChecked()],
                'biomes': [chk.text() for chk in biome_layout.children() if isinstance(chk, QCheckBox) and chk.isChecked()]
            }
            print(organism_data)  # For demonstration purposes
        
    def get_selected_resources(self):
        # This method can be used to get the selected resources for the planet
        # For now, it's a placeholder. Implement based on your requirements.
        pass
 
class App(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Star System Data Entry')
        self.setGeometry(100, 100, 800, 600)
        
        # Main Layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # System Name Field
        self.system_name_le = QLineEdit()
        self.system_name_le.setPlaceholderText("Enter star system name")
        self.layout.addWidget(self.system_name_le)

        # Add Planet Button
        self.add_planet_btn = QPushButton("Add Planet")
        self.layout.addWidget(self.add_planet_btn)
        
        # Tab Widget for Planets
        self.planet_tabs = QTabWidget(self)
        self.layout.addWidget(self.planet_tabs)
        
        # Connect signals
        self.add_planet_btn.clicked.connect(self.addPlanet)
        
    
    def addPlanet(self):
        new_tab = PlanetTab(self)
        self.planet_tabs.addTab(new_tab, "New Planet")
        # Connect a signal to update resources when tab is changed
        self.planet_tabs.currentChanged.connect(self.update_resources)
        
    def update_resources(self):
        # This method will update the main window's resources based on 
        # the currently selected planet (tab).
        current_tab = self.planet_tabs.currentWidget()
        # Assuming `get_selected_resources` returns a list of resource names or similar
        selected_resources = current_tab.get_selected_resources()
        # Update the resources area based on selected_resources

    def onTraitButtonClicked(self):
        sender = self.sender()
        if sender.isChecked():
            sender.setStyleSheet("background-color: #b0e0e6")
        else:
            sender.setStyleSheet("")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec_())
