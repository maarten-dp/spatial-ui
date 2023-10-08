from collections import defaultdict

from .primitives.element import Element


class TableRow(Element):
	def __init__(self, data=None):
		super().__init__()
		self.cells = []
		if data:
			[self.append(d) for d in data]

	def append(self, cell):
		self.cells.append(cell)
		self.add(cell)


class TableColumn:
	def __init__(self):
		self.cells = []

	def append(self, cell):
		self.cells.append(cell)


class TableCell(Element):
	def __init__(self, value, column_idx):
		super().__init__()
		self.value = value
		self.column_idx = column_idx
		self.add(str(value))


class TableHeader(TableCell):
	pass


class Table(Element):
	def __init__(self, data_connection):
		super().__init__()
		self.data_connection = data_connection
		self.rows = defaultdict(TableRow)
		self.columns = defaultdict(TableColumn)

		self.add(TableRow([TableHeader(h, idx) for idx, h in enumerate(self.data_connection.headers)]))
		for row_idx, raw_row in enumerate(self.data_connection.iter_rows()):
			for column_idx, raw_cell in enumerate(raw_row):
				cell = TableCell(raw_cell, column_idx)
				self.rows[row_idx].append(cell)
				self.columns[column_idx].append(cell)
			self.add(self.rows[row_idx])
