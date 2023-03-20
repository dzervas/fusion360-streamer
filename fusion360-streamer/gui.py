from .application import Application
from .constants import WINDOWS_OSID, OSX_OSID
from PyQt5.QtWidgets import QWidget, QPushButton, QProgressBar, QLabel, QComboBox, QVBoxLayout, QHBoxLayout, QCheckBox, QFileDialog, QLineEdit
from PyQt5.QtCore import QRect


class Gui(QWidget):
	def __init__(self):
		super().__init__()
		self.setGeometry(QRect(20, 20, 900, 700))
		self.setWindowTitle("Fusion 360 Streamer")

		# Create progress bar and label
		self.progress_bar = QProgressBar()
		progress_label = QLabel("Progress:")
		hboxProgress = QHBoxLayout()
		hboxProgress.addWidget(progress_label)
		hboxProgress.addWidget(self.progress_bar)

		# Platform dropdown
		self.platformCombo = QComboBox()
		self.platformCombo.addItems(["Windows", "Mac"])

		# Version VBox dropdown
		# versionCombo = QComboBox()
		# versionCombo.addItems(["Option 1", "Option 2", "Option 3"])
		# refreshBtn = QPushButton("Refresh", self)
		# refreshBtn.clicked.connect(self.refresh_clicked)
		# vboxVersion = QHBoxLayout()
		# vboxVersion.addWidget(versionCombo)
		# vboxVersion.addWidget(refreshBtn)

		# Output directory selection
		hboxOutput = QHBoxLayout()
		outputLbl = QLabel("Output Directory:")
		self.outputEdit = QLineEdit()
		outputBtn = QPushButton("Browse")
		outputBtn.clicked.connect(self.select_output_dir)
		self.recurseCheck = QCheckBox("Recurse into sub applications", self)
		hboxOutput.addWidget(outputLbl)
		hboxOutput.addWidget(self.outputEdit)
		hboxOutput.addWidget(outputBtn)
		hboxOutput.addWidget(self.recurseCheck)

		# Download/Extract VBox
		downloadBtn = QPushButton("Download Packages", self)
		downloadBtn.clicked.connect(self.download_clicked)
		extractBtn = QPushButton("Extract Packages", self)
		extractBtn.clicked.connect(self.extract_clicked)
		exitBtn = QPushButton("Exit", self)
		exitBtn.clicked.connect(self.exit_clicked)
		hboxDl = QHBoxLayout()
		hboxDl.addWidget(downloadBtn)
		hboxDl.addWidget(extractBtn)
		hboxDl.addWidget(exitBtn)

		# Main VBox
		vbox = QVBoxLayout()
		vbox.addWidget(self.platformCombo)
		# TODO: Add version selection via archive
		# vbox.addLayout(vboxVersion)
		# TODO: Add progress bar
		# vbox.addLayout(hboxProgress)
		vbox.addLayout(hboxOutput)
		vbox.addLayout(hboxDl)

		self.setLayout(vbox)

	# Button click functions
	def refresh_clicked(self):
		self.progress_bar.setValue(25)

	def select_output_dir(self):
		folder = QFileDialog.getExistingDirectory(self, 'Select Folder')
		self.outputEdit.setText(folder)
		print(f'Selected output folder: {folder}')

	def download_clicked(self):
		app = Application(os_id=WINDOWS_OSID if self.platformCombo.currentText() == "Windows" else OSX_OSID)
		app.download(output_dir=self.outputEdit.text(), recurse=self.recurseCheck.isChecked())

	def extract_clicked(self):
		app = Application(os_id=WINDOWS_OSID if self.platformCombo.currentText() == "Windows" else OSX_OSID)
		app.extract(output_dir=self.outputEdit.text(), recurse=self.recurseCheck.isChecked())

	def exit_clicked(self):
		print("Bye!")
		exit(0)
