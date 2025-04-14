import sys
import json
import numpy as np
from scipy.stats import skewnorm, poisson
from PySide6.QtCore import Signal, QAbstractTableModel
from PySide6.QtWidgets import QApplication, QCheckBox, QWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit, QDoubleSpinBox, QTableWidget, QTableWidgetItem, QHBoxLayout, QHeaderView, QFileDialog

class AncestryChanceWidget(QWidget):
  value_changed = Signal(float)

  def __init__(self, rarity_labels, default_value=1.0, parent=None):
    super().__init__(parent)
    self.layout = QHBoxLayout()
    self.setLayout(self.layout)

    self.label = QLabel(rarity_labels +' chance')
    self.spin = QDoubleSpinBox()
    self.spin.setRange(0.0, 0.99)
    self.spin.setSingleStep(0.01)
    self.spin.setDecimals(2)
    self.spin.setValue(default_value)
    self.spin.valueChanged.connect(self.value_changed)

    self.layout.addWidget(self.label)
    self.layout.addWidget(self.spin)

  def emit_value_changed(self):
    self.value_changed.emit(self.value())

  def value(self):
    return self.spin.value()

  def setValue(self, value):
    self.spin.setValue(value)

class AncestryTableWidget(QWidget):
  data_changed = Signal(list)

  def __init__(self, header_labels, data=None, parent=None):
    super().__init__(parent)
    self.header_labels = header_labels
    self._data = data or []

    self.init_ui()
    self.populate_table()
    self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

  def init_ui(self):
    self.layout = QVBoxLayout(self)

    self.table = QTableWidget(0, len(self.header_labels))
    self.table.setHorizontalHeaderLabels(self.header_labels)

    self.button_layout = QHBoxLayout()
    self.add_button = QPushButton("Add Ancestry")
    self.remove_button = QPushButton("Remove Ancestry")

    self.button_layout.addWidget(self.add_button)
    self.button_layout.addWidget(self.remove_button)

    self.add_button.clicked.connect(self.add_row)
    self.remove_button.clicked.connect(self.remove_row)

    self.layout.addWidget(self.table)
    self.layout.addLayout(self.button_layout)

    self.setLayout(self.layout)

  def populate_table(self):
    self.table.setRowCount(len(self._data))
    for row_index, row_data in enumerate(self._data):
      for col_index, value in enumerate(row_data):
        item = QTableWidgetItem(str(value))
        self.table.setItem(row_index, col_index, item)

  def add_row(self):
    row_count = self.table.rowCount()
    self.table.insertRow(row_count)
    self._data.append(["", 1])
    #self.populate_table()
    for col in range(len(self.header_labels)):
      item = QTableWidgetItem(str(self._data[-1][col]))
      self.table.setItem(row_count, col, item)

  def remove_row(self):
    selected_rows = self.table.selectedItems()
    if selected_rows:
      row_to_remove = selected_rows[0].row()
      self.table.removeRow(row_to_remove)
      del self._data[row_to_remove]
      self.data_changed.emit(self._data)

  def set_data(self, new_data):
    self._data = new_data
    self.populate_table()
    self.data_changed.emit(self._data)

class PopulationDemographicsApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.default_data()
        layout = QVBoxLayout()

        top_layout = QHBoxLayout()
        self.label = QLabel("Population Demographics Generator")
        top_layout.addWidget(self.label)
        self.vastMajority = QCheckBox("Vast Majority?")
        top_layout.addWidget(self.vastMajority)
        self.ndecimalslabel = QLabel('Number of Decimals')
        self.ndecimals = QDoubleSpinBox()
        self.ndecimals.setRange(0, 4)
        self.ndecimals.setSingleStep(1)
        self.ndecimals.setDecimals(0)
        self.ndecimals.setValue(0)
        top_layout.addWidget(self.ndecimalslabel)
        top_layout.addWidget(self.ndecimals)
        layout.addLayout(top_layout)

        layoutLoadSave = QHBoxLayout()

        self.loadButton = QPushButton("Load Population Data")
        self.loadButton.clicked.connect(self.load_from_file)
        layoutLoadSave.addWidget(self.loadButton)

        self.saveButton = QPushButton("Save Population Data")
        self.saveButton.clicked.connect(self.save_to_file)
        layoutLoadSave.addWidget(self.saveButton)

        layout.addLayout(layoutLoadSave)

        # create the chance widgets
        chance_layout = QHBoxLayout()
        chance_values = [0.75,0.25,0.05]
        for index, table_name in enumerate(self.data.keys()):
          model = AncestryChanceWidget(table_name, chance_values[index])
          model.setObjectName(table_name+'Chance')
          chance_layout.addWidget(model)

        # add chances to the main layout
        layout.addLayout(chance_layout)

        # Tables for editing ancestries and odds
        layoutAncTables = QHBoxLayout()
        for table_name, table_rows in self.data.items():
          headers = [table_name + ' Ancestry & Heritages', 'Odds']
          model = AncestryTableWidget(headers, list(self.data[table_name].items()))
          model.setObjectName(table_name+'Table')
          layoutAncTables.addWidget(model)

        # add ancestry tables to the main layout
        layout.addLayout(layoutAncTables)

        # Generate Button
        self.generateButton = QPushButton("Generate Population")
        self.generateButton.clicked.connect(self.generate_population)
        layout.addWidget(self.generateButton)

        self.resultText = QTextEdit()
        self.resultText.setReadOnly(True)
        layout.addWidget(self.resultText)

        self.setLayout(layout)
        self.setWindowTitle("Population Generator")

    def normalize_list(self, odds_list):
        total = sum(odds_list)
        return [p / total for p in odds_list] if total > 0 else odds_list

    def refresh_tables_from_data(self, new_data):
      tables = self.get_all_tables()
      for table_name, table_data in new_data.items():
        if table_name in tables:
          table_rows = [[k, str(v)] for k, v in table_data.items()]
          tables[table_name].set_data(table_rows)

    def sync_data_from_tables(self):
      tables = self.get_all_tables()
      for table_name in tables.keys():
        self.data[table_name] = self.get_table_data(tables[table_name])

    def get_all_chances(self):
      chances = {}
      for table_name in self.data.keys():
        chance = self.findChild(AncestryChanceWidget, f'{table_name}Chance').value()
        chances[table_name] = chance
      return chances

    def get_all_tables(self):
      tables = {}
      for table_name in self.data.keys():
        table = self.findChild(AncestryTableWidget, table_name+'Table')
        if table:
          tables[table_name] = table
      return tables

    def get_table_data(self, table):
      ancestries = []
      odds = []
      for row in range(table.table.rowCount()):
        name_item = table.table.item(row,0)
        ancestry = name_item.text() if name_item else ""
        odds_item = table.table.item(row,1)
        try:
          odd = int(float(odds_item.text())) if odds_item and odds_item and odds_item.text() else 1
        except ValueError:
          odd = 1

        ancestries.append(ancestry)
        odds.append(odd)

      return dict(zip(ancestries, odds))

    def generate_population(self):
      self.sync_data_from_tables()

      # pull over script
      #vastmajority = False

      ndecimals = int(self.ndecimals.value())
      if ndecimals > 0:
        scale = 10**(ndecimals)
        width = 3+ndecimals
      else:
        scale = 1
        width = 2

      chances = self.get_all_chances()
      chance_sum = 0
      for chance in chances.values():
        chance_sum += chance
        # the following shouldn't happen since the max value is 0.99
        if chance == 1:
          self.resultText.setText('No chance can be 1')
          return

      nmax = {}
      for rarity, ancestries in self.data.items():
        nmax[rarity] = np.count_nonzero(list(ancestries.values()))

      maxiterations = 0
      n = {}
      #nrarity = np.size(list(self.data.keys()))
      if(chance_sum > 0):
        while(maxiterations<1):
          for j, (rarity, chance) in enumerate(chances.items()):
            #n[rarity] = min(nmax[rarity], np.random.geometric(1-chance)-1)
            n[rarity] = min(nmax[rarity], poisson.rvs(0.25+2**chance))

          maxiterations = np.sum(list(n.values()))

      else:
        self.resultText.setText('At least one chance must be non-zero.')
        return

      # convert x_chance to a y_scale for skewnorm
      # y_scale = -27.2343 * tan( 1.4076 * (x_chance - 0.5) )
      # loc = x_chance
      choice = np.array([])
      dist = np.array([])
      for rarity, chance in chances.items():
        skew_scale = np.around(27.2343*np.tan(-1.4076*(chance - 0.5)))
        sum_odds = np.sum(list(self.data[rarity].values()))
        choice = np.append(choice, np.random.choice(list(self.data[rarity].keys()), n[rarity], replace=False, p=list(self.data[rarity].values())/sum_odds))
        dist = np.append(dist, skewnorm.rvs(skew_scale, loc=chance, scale=0.20, size=n[rarity]))

      sort_idx = np.argsort(dist)[::-1]
      dist = dist[sort_idx]
      choice = choice[sort_idx]

      if(maxiterations>1):
        tol = 2 * scale # tolerance, when remainder is less than end simulation
        remainder = 100 * scale

        if(self.vastMajority.isChecked()):
          mode = 75
          rng = int(scale * np.random.triangular(61, mode, 90))
          rng = int(scale * np.random.randint(60,91))
        else:
          mode = 35
          rng = int(scale * np.random.triangular(11, mode, 60))
          rng = int(scale * np.random.randint(10, 61))
        # population demographic
        popdemo = np.array([rng], dtype='int')
        remainder -= rng

        iterations = 1
        while(remainder >= tol and iterations < maxiterations):
          rng = int(np.random.triangular(1 * scale,remainder//2,remainder))
          rng = int(np.random.randint(1 * scale,remainder+1))

          popdemo = np.append(popdemo, rng)
          remainder -= rng
          iterations += 1

        popdemo = np.sort(popdemo)[::-1]
        nsum = sum(list(nmax.values()))
        other_cap = min(nsum//3, np.random.randint(7,15))
        other_cap *= scale
        other_diff = remainder - other_cap

        if(other_diff < 0):
          if(iterations < maxiterations):
            diff = maxiterations-iterations
            for i in range(diff):
              idx = np.argmax(popdemo)
              shift = np.random.randint(1,scale*(diff-i)+1)
              popdemo[idx] -= shift
              popdemo = np.append(popdemo, shift)
            popdemo = np.sort(popdemo)[::-1]
            popdemo = np.append(popdemo,remainder)
          else:
            popdemo = np.sort(popdemo)[::-1]
            popdemo = np.append(popdemo,remainder)
        else:
          popdiff1 = np.random.randint(0,other_diff+1)
          popdiff2 = other_diff - popdiff1
          popdemo[0] += max(popdiff1,popdiff2)
          popdemo[1] += min(popdiff1,popdiff2)
          popdemo = np.append(popdemo, other_cap)

        if ndecimals > 0:
          popdemo = np.round(popdemo / scale, ndecimals)


        output_text = 'Generated population: '
        nrange = np.size(list(n.values()))
        for j, (rarity, val) in enumerate(n.items()):
          if j < nrange-1:
            output_text += f'{val} {rarity}, '
          else:
            output_text += f'and {val} {rarity}\n'
        choice = np.append(choice,'other')
        for val, anc in zip(popdemo, choice):
          output_text += f'{val:{width}}' + '%: ' + anc + '\n'

      else:
        output_text = 'Generated population: '
        nrange = np.size(list(n.values()))
        for j, (rarity, val) in enumerate(n.items()):
          if j < nrange-1:
            output_text += f'{val} {rarity}, '
          else:
            output_text += f'and {val} {rarity}\n'
        output_text += f'99%: {choice[0]}\n'
        output_text += ' 1%: other'

      self.resultText.setText(output_text)

    def default_data(self):
      self.data = {
        "Common": {
          "dwarf": 1,
          "elf": 1,
          "gnome": 1,
          "goblin": 1,
          "halfling": 1,
          "human": 1,
          "leshy": 1,
          "orc": 1,
          "auivarian (half-elf)": 1,
          "dromaar (half-orc)": 1
        },

        "Uncommon": {
          "athamaru": 1,
          "azarketi": 1,
          "catfolk": 1,
          "centaur": 1,
          "changeling": 1,
          "geniekin": 1,
          "dhampir": 1,
          "dragonblood": 1,
          "duskwalker": 1,
          "fetchling": 1,
          "hobgoblin": 1,
          "kholo": 1,
          "kitsune": 1,
          "kobold": 1,
          "lizardfolk": 1,
          "merfolk": 1,
          "minotaur": 1,
          "mixed ancestry": 1,
          "nagaji": 1,
          "nephilim": 1,
          "ratfolk": 1,
          "samsaran": 1,
          "tanuki": 1,
          "tengu": 1,
          "tripkee": 1,
          "vanara": 1,
          "wayang": 1
        },

        "Rare": {
          "anadi": 1,
          "android": 1,
          "automaton": 1,
          "awakened animal": 1,
          "beastkin": 1,
          "conrasu": 1,
          "fleshwarp": 1,
          "ghoran": 1,
          "goloma": 1,
          "kashrishi": 1,
          "poppet": 1,
          "reflection": 1,
          "sarangay": 1,
          "shisk": 1,
          "shoony": 1,
          "skeleton (undead)": 1,
          "sprite": 1,
          "strix": 1,
          "surki": 1,
          "vishkanya": 1,
          "yaksha": 1,
          "yaoguai": 1
        }
      }

    def load_from_file(self):
      filepath, _ = QFileDialog.getOpenFileName(self)

      if not filepath:
        return

      try:
        with open(filepath, 'r') as f:
          data = json.load(f)

        self.refresh_tables_from_data(data)
        self.resultText.setText("Population data loaded successfully!")

      except Exception as e:
        self.resultText.setText(f"Error loading file: {str(e)}")

    def save_to_file(self):
      # might need sync_data_from_tables() instead
      self.sync_data_from_tables()
      filepath, _ = QFileDialog.getSaveFileName(self)

      if not filepath:
        return

      if not filepath.lower().endswith('.json'):
        filepath += '.json'

      try:
        with open(filepath, 'w') as f:
          json.dump(self.data, f, indent=2)
        self.resultText.setText("Population data saved successfully!")

      except Exception as e:
        self.resultText.setText(f"Error saving file: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PopulationDemographicsApp()
    window.show()
    sys.exit(app.exec())

