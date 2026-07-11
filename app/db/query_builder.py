from typing import Any, Dict, Iterable, List

from pypika import PostgreSQLQuery, Table
from pypika.dialects import PostgreSQLQueryBuilder
from pypika.utils import builder
from pypika.terms import Field, Term


class ExtendedQueryBuilder(PostgreSQLQueryBuilder):
    @builder
    def setmany(self, field_value_map: Dict[Field, Any]) -> None:
        for field, value in field_value_map.items():
            # the code below was copied directly from the original set method
            field = Field(field) if not isinstance(field, Field) else field
            if not isinstance(value, Term):
                value = self.wrap_constant(value, wrapper_cls=self._wrapper_cls)
            self._updates.append((field, value))


class PGQuery(PostgreSQLQuery):
    @classmethod
    def _builder(cls, **kwargs) -> ExtendedQueryBuilder:
        return ExtendedQueryBuilder(**kwargs)


def prefix_fields_with_table(table: Table, field_names: Iterable[str]) -> List[Field]:
    # adds the table name as a prefix to each field name, e.g. "cart_items.id" instead of just "id"
    prefixed_fields = []
    for field_name in field_names:
        field = getattr(table, field_name)
        prefixed_fields.append(field.as_(f"{table.get_table_name()}.{field_name}"))
    return prefixed_fields
