#INFO: agregados al ORM ej expresiones para queries
#VER: https://docs.djangoproject.com/en/3.0/howto/custom-lookups/

from django.db.models import Lookup
from django.db.models.fields import Field

@Field.register_lookup
class Like(Lookup):
	lookup_name = 'like'

	def as_sql(self, compiler, connection):
		lhs, lhs_params = self.process_lhs(compiler, connection)
		rhs, rhs_params = self.process_rhs(compiler, connection)
		params = lhs_params + rhs_params
		return '%s LIKE %s' % (lhs, rhs), params


