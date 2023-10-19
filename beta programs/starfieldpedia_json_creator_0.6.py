import sys
import json
from functools import partial
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, 
                             QCheckBox, QPushButton, QDialog, 
                             QLineEdit, QFormLayout, QScrollArea,
                             QGroupBox, QLabel, QRadioButton, 
                             QGridLayout, QHBoxLayout, QButtonGroup, QTabWidget,
                             QTextEdit, QComboBox, QTableWidget, QTableWidgetItem)

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
    
class OrganismDetailsDialog(QDialog):
    def __init__(self, resource=None, parent=None):
        super().__init__(parent)
        self.resource = resource
        self.setWindowTitle('Add Organism Details')

        
        layout = QFormLayout(self)
        
        # Type RadioButtons
        self.type_group = QButtonGroup(self)
        self.flora_rb = QRadioButton("Flora", self)
        self.fauna_rb = QRadioButton("Fauna", self)
        self.type_group.addButton(self.flora_rb)
        self.type_group.addButton(self.fauna_rb)
        type_layout = QHBoxLayout()
        type_layout.addWidget(self.flora_rb)
        type_layout.addWidget(self.fauna_rb)
        layout.addRow("Type:", type_layout)
        
        # Signal to handle disabling of Temperament
        self.flora_rb.toggled.connect(self.handleTypeSelection)

        # Name LineEdit
        self.name_le = QLineEdit(self)
        layout.addRow("Name:", self.name_le)

        # Temperament RadioButtons
        self.temperament_group = QButtonGroup(self)
        self.temperaments = ['Peaceful', 'Wary', 'Defensive', 'Territorial', 'Fearless']
        temp_layout = QHBoxLayout()
        for temp in self.temperaments:
            rb = QRadioButton(temp, self)
            self.temperament_group.addButton(rb)
            temp_layout.addWidget(rb)
        layout.addRow("Temperament:", temp_layout)

        # Biomes CheckBoxes
        self.biomes = [
            "Coniferous Forest", "Craters", "Deciduous Forest", "Frozen Craters", "Frozen Crevasses",
            "Frozen Dunes", "Frozen Hills", "Frozen Mountains", "Frozen Plains", "Frozen Volcanic",
            "Hills", "Mountains", "Ocean", "Plateau", "Rocky Desert", "Sandy Desert", "Savanna",
            "Swamp", "Tropical Forest", "Volcanic", "Wetlands Frozen", "Wetlands"
        ]
        self.biome_cbs = {biome: QCheckBox(biome, self) for biome in self.biomes}
        biomes_layout = QGridLayout()
        for idx, (biome, cb) in enumerate(self.biome_cbs.items()):
            biomes_layout.addWidget(cb, idx // 3, idx % 3)  # Display in 3 columns
        layout.addRow("Biomes:", biomes_layout)

        # Outpost CheckBox
        self.outpost_cb = QCheckBox("True", self)
        layout.addRow("Outpost?", self.outpost_cb)

        # OK Button
        btn_ok = QPushButton("OK", self)
        btn_ok.setObjectName("OK")  # Set the object name
        btn_ok.clicked.connect(self.accept)
        layout.addWidget(btn_ok)

        self.setLayout(layout)
        
        # Add this line to call the validateInput method whenever the text changes
        self.name_le.textChanged.connect(self.validateInput)
        
        # Initialize the OK button's enabled state
        self.validateInput()

    def handleTypeSelection(self, checked):
        """Handle the Flora/Fauna selection to enable/disable Temperament."""
        if checked:  # If Flora is selected
            for btn in self.temperament_group.buttons():
                btn.setEnabled(False)
                btn.setChecked(False)  # Uncheck any previously selected radio button
        else:  # If Fauna is selected
            for btn in self.temperament_group.buttons():
                btn.setEnabled(True)

        self.validateInput()  # validate the input after each selection

    def validateInput(self):
        """Check if the necessary fields are filled to enable OK button."""
        is_name_filled = bool(self.name_le.text().strip())
        is_temperament_checked = any(btn.isChecked() for btn in self.temperament_group.buttons()) or self.flora_rb.isChecked()
        self.findChild(QPushButton, "OK").setEnabled(is_name_filled and is_temperament_checked)

    def get_data(self):
        """Retrieve data from the dialog's widgets."""
        temperament = [btn.text() for btn in self.temperament_group.buttons() if btn.isChecked()]
        biomes = [biome for biome, cb in self.biome_cbs.items() if cb.isChecked()]
        return {
            'type': 'Flora' if self.flora_rb.isChecked() else 'Fauna',
            'name': self.name_le.text(),
            'temperament': temperament,
            'biomes': biomes,
            'outpost': self.outpost_cb.isChecked(),
            'resource': self.resource if hasattr(self, 'resource') else None
        }
    
    
class OrganismDisplayWidget(QWidget):
    def __init__(self, organism_data, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        
        # Create a QLabel to display the organism data in a formatted manner
        data_str = json.dumps(organism_data, indent=4)
        label = QLabel(data_str, self)
        layout.addWidget(label)
        
        # Add a Delete button to remove the organism
        btn_delete = QPushButton("X", self)
        btn_delete.clicked.connect(self.deleteSelf)
        layout.addWidget(btn_delete)
        
        self.setLayout(layout)

    def deleteSelf(self):
        """Remove this widget from the parent's layout."""
        if self.parent():
            self.parent().layout().removeWidget(self)
        self.deleteLater()

class PlanetTab(QWidget):
    
    TRAITS = [
        "Active Faulting", "Aeriform Life","Amphibious Foothold", "Boiled Seas", "Bolide Bombardment",
        "Charred Ecosystem","Continual Conductor","Coralline Landmass","Crystalline Crust","Diseased Biosphere",
        "Ecological Consortium","Emerging Tectonics","Energetic Rifting","Extinction Event","Frozen Ecosystem",
        "Gaseous Font","Global Glacial Recession","Gravitational Anomoly","Pelted Fields","Primed For Life",
        "Primordial Network", "Prismatic Plumes","Psychotropic Biota","Sentient Microbial Colonies",
        "Slushy Subsurface Seas","Solar Storm Seasons","Sonorous Lithosphere"
        ]
        
    def __init__(self, planet_tabs, parent=None):
        super().__init__(parent)
        self.planet_tabs = planet_tabs  # Store the QTabWidget reference
        
        


        # Create a layout first
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # Planet Delete Button
        self.delete_planet_btn = QPushButton("Delete Planet")
        self.delete_planet_btn.clicked.connect(self.deletePlanet)
        self.layout.addWidget(self.delete_planet_btn)
        self.delete_planet_btn.setStyleSheet("QPushButton { background-color: red; color: white; width: 100px; }")

        # System Name Field
        self.system_name_le = QLineEdit()
        self.system_name_le.setPlaceholderText("Enter planet name")
        self.layout.addWidget(self.system_name_le)
        ###################
        
        # Add the notes field
        self.notes_label = QLabel("Planet Notes:", self)
        self.layout.addWidget(self.notes_label)
        self.notes_te = QTextEdit(self)
        self.notes_te.setPlaceholderText("Enter any notes pertaining to this planet...")
        self.layout.addWidget(self.notes_te)    
        # End Notes Field #
        
        # Add the Gravity field
        self.gravity_label = QLabel("Gravity", self)
        self.layout.addWidget(self.gravity_label)      
        self.gravity_te = QLineEdit(self)
        self.gravity_te.setPlaceholderText("Enter gravity...")
        self.layout.addWidget(self.gravity_te)    
        # End Gravity Field #

        
        # Create a label for "Atmosphere"
        atmosphere_label = QLabel("Atmosphere", self)
        
        # Adding label to the layout
        self.layout.addWidget(atmosphere_label)
        
        # Atmopshere Radio Buttons
        self.atmosphere_group = QButtonGroup(self)
        self.atmospheres = ['NONE','Thin O2', 'Thin CO2', 'Moderate O2', 'Moderate CO2', 'EXTR O2']
        temp_layout = QHBoxLayout()
        for temp in self.atmospheres:
            rb = QRadioButton(temp, self)
            self.atmosphere_group.addButton(rb)
            temp_layout.addWidget(rb)
        
        # Adding the radio buttons layout to the main layout
        self.layout.addLayout(temp_layout)
        #####################################
        
        # Create a label for "Magnetosphere"
        magnetosphere_label = QLabel("Magnetosphere", self)
        
        # Adding label to the layout
        self.layout.addWidget(magnetosphere_label)
        
        # Atmopshere Radio Buttons
        self.magnetosphere_group = QButtonGroup(self)
        self.magnestospheres = ['NONE','Weak', 'Moderate','Strong']
        temp_layout = QHBoxLayout()
        for temp in self.magnestospheres:
            mb = QRadioButton(temp, self)
            self.magnetosphere_group.addButton(mb)
            temp_layout.addWidget(mb)
        
        # Adding the radio buttons layout to the main layout
        self.layout.addLayout(temp_layout)
        #####################################
        
        # Add the traits checkboxes
        self.traits_label = QLabel("Planet Traits:", self)
        self.layout.addWidget(self.traits_label)

        self.traits_groupbox = QGroupBox("Select Traits", self)
        self.traits_layout = QGridLayout()
        self.checkboxes = []

        for idx, trait in enumerate(PlanetTab.TRAITS):
            checkbox = QCheckBox(trait, self)
            self.traits_layout.addWidget(checkbox, idx // 5, idx % 5)  # 5 columns
            self.checkboxes.append(checkbox)

        self.traits_groupbox.setLayout(self.traits_layout)
        self.layout.addWidget(self.traits_groupbox)
        
        # End Traits #

        # Resources grid layout to hold both inorganic and organic resources
        resources_layout = QGridLayout()
        
        for idx, resource in enumerate(organic_resources, start=len(inorganic_resources)):
            btn = QPushButton(resource)
            btn.setFixedWidth(120)
            btn.clicked.connect(partial(self.addOrganismDetails, resource_name=resource))
            resources_layout.addWidget(btn, idx // 5, idx % 5)


        # Inorganic Resources - Add checkboxes for inorganic resources
        for idx, resource in enumerate(inorganic_resources):
            chk = QCheckBox(resource)
            resource_color = inorganic_resources_data[resource]["color"]
            text_color = text_color_for_background(resource_color)
            chk.setStyleSheet(f"QCheckBox {{ background-color: {resource_color}; color: {text_color}; }}")
            resources_layout.addWidget(chk, idx // 5, idx % 5)  # 5 columns

        self.layout.addLayout(resources_layout)

        # Organism Details Table
        self.organism_details_table = QTableWidget(0, 7, self)
        self.organism_details_table.setHorizontalHeaderLabels(['Resource', 'Type', 'Name', 'Temperament', 'Biomes', 'Outpost', 'Actions'])
        self.layout.addWidget(self.organism_details_table)

        # Create and configure the dialog to enter organism details
        self.organism_dialog = self.createOrganismDetailsDialog()
        
    def get_selected_traits(self):
        """
        Return a list of selected traits.
        """
        return [cb.text() for cb in self.checkboxes if cb.isChecked()]
        
    def appendOrganismDetails(self, organism_data):
        """Function to display the added organism details in the table"""
        row_position = self.organism_details_table.rowCount()
        self.organism_details_table.insertRow(row_position)
    
        self.organism_details_table.setItem(row_position, 0, QTableWidgetItem(organism_data['resource']))
        self.organism_details_table.setItem(row_position, 1, QTableWidgetItem(organism_data['type']))
        self.organism_details_table.setItem(row_position, 2, QTableWidgetItem(organism_data['name']))
        temperament_text = ', '.join(organism_data['temperament'])  # convert list to string
        self.organism_details_table.setItem(row_position, 3, QTableWidgetItem(temperament_text))
        biomes_text = ', '.join(organism_data['biomes'])  # convert list to string
        self.organism_details_table.setItem(row_position, 4, QTableWidgetItem(biomes_text))
        outpost_text = 'Yes' if organism_data['outpost'] else 'No'
        self.organism_details_table.setItem(row_position, 5, QTableWidgetItem(outpost_text))

        # Add a delete button in the last column
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(lambda: self.deleteOrganism(row_position))
        self.organism_details_table.setCellWidget(row_position, 6, delete_btn)
        
    def deleteOrganism(self, row):
        """Function to remove an organism from the table"""
        self.organism_details_table.removeRow(row)
        
    def createOrganismDetailsDialog(self):
        """Function to create and configure a dialog to enter organism details"""
        return OrganismDetailsDialog()  # No need to set the resource here.

        
    def addOrganismDetails(self, resource_name):
        """Function to show the dialog and get the organism details from the user"""
        dialog = OrganismDetailsDialog(resource=resource_name, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            organism_data = dialog.get_data()
            self.appendOrganismDetails(organism_data)

            
    def deletePlanet(self):
        """Function to remove its own tab from the QTabWidget"""
        index = self.planet_tabs.indexOf(self)
        if index != -1:
            self.planet_tabs.removeTab(index)
            
    def get_data(self):
        """Collect data from the PlanetTab's widgets and return as a dictionary."""
        planet_data = {
            "name": self.system_name_le.text(),
            "type": "",  # Placeholder, since I didn't see a 'type' field in your GUI
            "gravity": 1.00,  # Placeholder, since I didn't see a 'gravity' field in your GUI
            "temperature": "",  # Placeholder, since I didn't see a 'temperature' field in your GUI
            "atmosphere": self.atmosphere_group.checkedButton().text() if self.atmosphere_group.checkedButton() else "NONE",
            "magnetosphere": self.magnetosphere_group.checkedButton().text() if self.magnetosphere_group.checkedButton() else "NONE",
            "traits": self.get_selected_traits(),
            "resources": {resource.text(): True for resource in inorganic_resources if resource.isChecked()},
            "fauna": [],
            "flora": []
        }

        for row in range(self.organism_details_table.rowCount()):
            organism_data = {
                "name": self.organism_details_table.item(row, 2).text(),
                "Temperament": self.organism_details_table.item(row, 3).text(),
                "biomes": self.organism_details_table.item(row, 4).text().split(', '),
                "outpost": self.organism_details_table.item(row, 5).text() == "Yes",
                "resources": {
                    self.organism_details_table.item(row, 0).text(): True
                }
            }

            if self.organism_details_table.item(row, 1).text() == "Fauna":
                planet_data["fauna"].append(organism_data)
            else:
                planet_data["flora"].append(organism_data)

        return planet_data
 
class App(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Star System Data Entry')
        self.setGeometry(100, 100, 800, 600)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.system_name_le = QLineEdit()
        self.system_name_le.setPlaceholderText("Enter star system name")
        self.layout.addWidget(self.system_name_le)

        self.add_planet_btn = QPushButton("Add Planet")
        self.add_planet_btn.clicked.connect(self.addPlanet)
        self.layout.addWidget(self.add_planet_btn)

        self.planet_tabs = QTabWidget(self)
        self.layout.addWidget(self.planet_tabs)

    def addPlanet(self):
        """Function to add a new tab for planet data entry"""
        new_tab = PlanetTab(self.planet_tabs)  # Pass the QTabWidget to PlanetTab
        self.planet_tabs.addTab(new_tab, "New Planet")




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec_())
