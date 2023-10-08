from .base import BaseDataReader


class SQLADataReader(BaseDataReader):
	def __init__(self, session, model, show_index=True):
		self.session = session
		self.model = model
		self.show_index = show_index
		self.index = self._extract_index()
		self._fields = self._extract_fields()

	def iter_rows(self):
		for instance in self.session.query(self.model).all():
			yield self._instance_to_row(instance)

	@property
	def fields(self):
		fields = self._fields.copy()
		if not self.show_index:
			fields.remove(self.index)
		return fields

	@property
	def headers(self):
		return [h.replace("_", " ").title() for h in self.fields]

	def _instance_to_row(self, instance):
		return [getattr(instance, column) for column in self.fields]

	def _extract_fields(self):
		fields = []
		for column in self.model.__table__.columns:
			fields.append(column.name)
		return fields

	def _extract_index(self):
		pk = [pk for pk in self.model.__table__.columns if pk.primary_key]
		return pk[0].name
