import sys
import json
import numpy as np
from scipy.stats import skewnorm
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit, QDoubleSpinBox, QTableWidget, QTableWidgetItem, QHBoxLayout, QHeaderView, QFileDialog

class AncestryTableWidget(QWidget):
  data_changed = Signal(list)

  def __init__(self, header_labels, data=None, parent=None):
    super().__init__(parent)
    self.header_labels = header_labels
    self.data = data or []

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
    self.table.setRowCount(len(self.data))
    for row_index, row_data in enumerate(self.data):
      for col_index, value in enumerate(row_data):
        item = QTableWidgetItem(str(value))
        self.table.setItem(row_index, col_index, item)

  def add_row(self):
    row_count = self.table.rowCount()
    self.table.insertRow(row_count)
    self.data.append(["" for _ in  self.header_labels])
    self.data_changed.emit(self.data)

  def remove_row(self):
    selected_rows = self.table.selectedItems()
    if selected_rows:
      row_to_remove = selected_rows[0].row()
      self.table.removeRow(row_to_remove)
      del self.data[row_to_remove]
      self.data_changed.emit(self.data)

  def get_data(self):
    table_data = []
    for row_index in range(self.table.rowCount()):
      row_data = []
      for col_index in range(self.table.columnCount()):
        item = self.table.item(row_index, col_index)
        value = item.text() if item else ""
        row_data.append(value)
      table_data.append(row_data)
    self.data = table_data
    return self.data

  def set_data(self, new_data):
    self.data = new_data
    self.populate_table()
    self.data_changed.emit(self.data)

class PopulationDemographicsApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.label = QLabel("Population Demographics Generator")
        layout.addWidget(self.label)

        layoutLoadSave = QHBoxLayout()

        self.loadButton = QPushButton("Load Population Data")
        self.loadButton.clicked.connect(self.load_from_file)
        layoutLoadSave.addWidget(self.loadButton)

        self.saveButton = QPushButton("Save Population Data")
        self.saveButton.clicked.connect(self.save_to_file)
        layoutLoadSave.addWidget(self.saveButton)

        layout.addLayout(layoutLoadSave)

        self.uncommonChanceLabel = QLabel("Uncommon Chance:")
        self.uncommonChanceSpin = QDoubleSpinBox()
        self.uncommonChanceSpin.setRange(0, 1)
        self.uncommonChanceSpin.setSingleStep(0.01)
        self.uncommonChanceSpin.setValue(0.25)
        layout.addWidget(self.uncommonChanceLabel)
        layout.addWidget(self.uncommonChanceSpin)

        self.rareChanceLabel = QLabel("Rare Chance:")
        self.rareChanceSpin = QDoubleSpinBox()
        self.rareChanceSpin.setRange(0, 1)
        self.rareChanceSpin.setSingleStep(0.01)
        self.rareChanceSpin.setValue(0.05)
        layout.addWidget(self.rareChanceLabel)
        layout.addWidget(self.rareChanceSpin)

        # Tables for editing ancestries and odds

        layoutAncTables = QHBoxLayout()

        self.commonTable = AncestryTableWidget(header_labels=["Common Ancestry and Heritage", "Odds"])
        layoutAncTables.addWidget(self.commonTable)

        self.uncommonTable = AncestryTableWidget(header_labels=["Uncommon Ancestry and Heritage", "Odds"])
        layoutAncTables.addWidget(self.uncommonTable)

        self.rareTable = AncestryTableWidget(header_labels=["Rare Ancestry and Heritage", "Odds"])

        self.default_data()
        self.commonTable.data_changed.connect(self.sync_data_from_tables())
        self.uncommonTable.data_changed.connect(self.sync_data_from_tables())
        self.rareTable.data_changed.connect(self.sync_data_from_tables())

        layoutAncTables.addWidget(self.rareTable)

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

    def normalize_probabilities(self):
        self.commonodds = self.normalize_list(self.commonodds)
        self.uncommonodds = self.normalize_list(self.uncommonodds)
        self.rareodds = self.normalize_list(self.rareodds)

    def normalize_list(self, odds_list):
        total = sum(odds_list)
        return [p / total for p in odds_list] if total > 0 else odds_list

    def refresh_tables_from_data(self):
      common_data = [[anc, str(int(odds))] for anc, odds in zip(self.commonancestry, self.commonodds)]
      self.commonTable.set_data(common_data)

      uncommon_data = [[anc, str(int(odds))] for anc, odds in zip(self.uncommonancestry, self.uncommonodds)]
      self.uncommonTable.set_data(uncommon_data)

      rare_data = [[anc, str(int(odds))] for anc, odds in zip(self.rareancestry, self.rareodds)]
      self.rareTable.set_data(rare_data)

    def generate_population(self):
      self.sync_data_from_tables()
      self.normalize_probabilities()

        # pull over script!
      vastmajority = False

      ndecimals = 0
      if ndecimals > 0:
        scale = 10**(ndecimals)
        width = 3+ndecimals
      else:
        scale = 1
        width = 2

      commonchance = 0.7
      uncommonchance = self.uncommonChanceSpin.value()
      rarechance = self.rareChanceSpin.value()

      ncmax = np.count_nonzero(self.commonodds)
      nucmax = np.count_nonzero(self.uncommonodds)
      nrmax = np.count_nonzero(self.rareodds)
      maxiterations = 0

      while(maxiterations<1):
        if(ncmax>1):
          nc = int(np.around(np.random.triangular(0,2,ncmax)))
          if(nc==1):
            nc = np.random.randint(0,3)
        elif(ncmax==1):
          nc = int(np.around(np.random.triangular(0,1,ncmax)))
        else:
          nc = ncmax

        nuc = min(nucmax, np.random.geometric(1-uncommonchance)-1)
        nr = min(nrmax, np.random.geometric(1-rarechance)-1)

        maxiterations = nc + nuc + nr

      uncommonscale = np.around(27.2343*np.tan(-1.4076*uncommonchance+0.703801),1)
      rarescale = np.around(27.2343*np.tan(-1.4076*rarechance+0.703801),1)
      common_dist = skewnorm.rvs(0, loc=0.5, scale=0.20, size = nc)
      common_choice = np.random.choice(self.commonancestry, nc, replace=False, p=self.commonodds)
      uncommon_dist = skewnorm.rvs(uncommonscale, loc=uncommonchance, scale=0.20, size = nuc)
      uncommon_choice = np.random.choice(self.uncommonancestry, nuc, replace=False, p=self.uncommonodds)
      rare_dist = skewnorm.rvs(rarescale, loc=rarechance, scale=0.20, size = nr)
      rare_choice = np.random.choice(self.rareancestry, nr, replace=False, p=self.rareodds)

      dist = np.append(common_dist, uncommon_dist)
      dist = np.append(dist, rare_dist)
      choice = np.append(common_choice, uncommon_choice)
      choice = np.append(choice, rare_choice)
      sort_idx = np.argsort(dist)[::-1]
      dist = dist[sort_idx]
      choice = choice[sort_idx]

      if(maxiterations>1):
        tol = 2 * scale # tolerance, when remainder is less than end simulation

        remainder = 100 * scale

        if(vastmajority):
          mode = 75
          rng = int(scale * np.random.triangular(61, mode, 90))
        else:
          mode = 25 * scale
          rng = int(scale * np.random.triangular(1, mode, 50))
        # population demographic
        popdemo = np.array([rng], dtype='int')
        remainder -= rng

        iterations = 1
        while(remainder >= tol and iterations < maxiterations):
          rng = int(np.random.triangular(1 * scale,remainder//2,remainder))

          popdemo = np.append(popdemo, rng)
          remainder -= rng
          iterations += 1

        popdemo = np.sort(popdemo)[::-1]
        other_cap = min((ncmax+nucmax+nrmax)//3, np.random.randint(7,15))
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


        output_text = 'Generated population: %d common, %d uncommon, and %d rare ancestries\n' % (nc, nuc, nr)
        choice = np.append(choice,'other')
        for val, anc in zip(popdemo, choice):
          output_text += f'{val:{width}}' + '%: ' + anc + '\n'

      else:
        output_text = 'Generated population: %d common, %d uncommon, and %d rare ancestries\n' % (nc, nuc, nr)
        output_text += f'99%: {choice[0]}\n'
        output_text += ' 1%: other'

      self.resultText.setText(output_text)

    def sync_data_from_tables(self):
      self.commonancestry, self.commonodds = self.get_table_data(self.commonTable)
      self.uncommonancestry, self.uncommonodds = self.get_table_data(self.uncommonTable)
      self.rareancestry, self.rareodds = self.get_table_data(self.rareTable)
      #self.normalize_probabilities()

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

      return ancestries, odds

    def default_data(self):
      self.commonancestry = ['dwarf', 'elf', 'gnome', 'goblin', 'halfling',
                             'human', 'leshy', 'orc', 'auivarian (half-elf)', 'dromaar (half-orc)']
      self.commonodds = [1, 1, 1, 1, 1,
                         1, 1, 1, 1, 1]

      self.uncommonancestry = ['athamaru', 'azarketi', 'catfolk', 'centaur', 'changeling',
                               'geniekin', 'dhampir', 'dragonblood', 'duskwalker', 'fetchling',
                               'hobgoblin', 'kholo', 'kitsune', 'kobold', 'lizardfolk',
                               'merfolk', 'minotaur', 'mixed ancestry', 'nagaji', 'nephilim',
                               'ratfolk', 'samsaran', 'tanuki', 'tengu', 'tripkee',
                               'vanara', 'wayang']
      self.uncommonodds = [1, 1, 1, 1, 1,
                           1, 1, 1, 1, 1,
                           1, 1, 1, 1, 1,
                           1, 1, 1, 1, 1,
                           1, 1, 1, 1, 1,
                           1, 1]

      self.rareancestry = ['anadi', 'android', 'automaton', 'awakened animal', 'beastkin',
                           'conrasu', 'fleshwarp', 'ghoran', 'goloma', 'kashrishi',
                           'poppet', 'reflection', 'sarangay', 'shisk', 'shoony',
                           'skeleton (undead)', 'sprite', 'strix', 'surki', 'vishkanya',
                           'yaksha', 'yaoguai']
      self.rareodds = [1, 1, 1, 1, 1,
                       1, 1, 1, 1, 1,
                       1, 1, 1, 1, 1,
                       1, 1, 1, 1, 1,
                       1, 1]

      self.refresh_tables_from_data()

    def load_from_file(self):
      filepath, _ = QFileDialog.getOpenFileName(self)

      if not filepath:
        return

      try:
        with open(filepath, 'r') as f:
          data = json.load(f)

        self.commonancestry = list(data.get('common', {}).keys())
        self.commonodds = list(data.get('common', {}).values())

        self.uncommonancestry = list(data.get('uncommon', {}).keys())
        self.uncommonodds = list(data.get('uncommon', {}).values())

        self.rareancestry = list(data.get('rare', {}).keys())
        self.rareodds = list(data.get('rare', {}).values())

        self.refresh_tables_from_data()
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

      data = {
          "common": dict(zip(self.commonancestry, self.commonodds)),
          "uncommon": dict(zip(self.uncommonancestry, self.uncommonodds)),
          "rare": dict(zip(self.rareancestry, self.rareodds))
          }

      try:
        with open(filepath, 'w') as f:
          json.dump(data, f, indent=4)
        self.resultText.setText("Population data saved successfully!")

      except Exception as e:
        self.resultText.setText(f"Error saving file: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PopulationDemographicsApp()
    window.show()
    sys.exit(app.exec())

