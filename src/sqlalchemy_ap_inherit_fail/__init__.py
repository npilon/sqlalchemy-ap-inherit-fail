from sqlalchemy import create_engine
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relation, scoped_session, sessionmaker
from sqlalchemy.types import Integer
from sqlalchemy.types import Text

Base = declarative_base()


class Related(Base):
    __tablename__ = "related"

    id = Column(Integer, primary_key=True)
    name = Column(Text)


class SingleTableToRelated(Base):
    __tablename__ = "single_table_to_related"

    related_id = Column(
        ForeignKey("related.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
        index=True,
    )

    single_table_id = Column(
        ForeignKey("single_table.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
        index=True,
    )


class RelatedMixin:
    @declared_attr.cascading
    def related_names(cls):
        return association_proxy("relateds", "name")

    @declared_attr.cascading
    def has_related_names(cls):
        @hybrid_method
        def _has_related_names(self, names):
            return any(name in names for name in self.related_names)

        @_has_related_names.expression
        def _has_related_names(cls, names):
            return cls.related_names.in_(names)

        return _has_related_names

    @declared_attr.cascading
    def relevant(cls):
        @hybrid_property
        def _relevant(self):
            return self.has_related_names(["foo", "bar"])

        @_relevant.expression
        def _relevant(cls):
            return cls.has_related_names(["foo", "bar"])

        return _relevant


class Parent(RelatedMixin, Base):
    __tablename__ = "single_table"

    __mapper_args__ = {
        "polymorphic_on": "kind",
        "polymorphic_identity": "parent",
    }

    id = Column(Integer, primary_key=True)
    kind = Column(Text)

    relateds = relation(Related, secondary=SingleTableToRelated.__table__)


class Child(Parent):
    __tablename__ = "single_table"

    __mapper_args__ = {
        "polymorphic_identity": "child",
    }


def main():
    engine = create_engine("sqlite:///inherit_fail.db")

    Session = scoped_session(sessionmaker(bind=engine))

    Base.metadata.create_all(engine)

    rs = {}

    for name in ["foo", "bar", "baz"]:
        r = Related(name=name)
        Session.add(r)
        rs[name] = r

    p = Parent()
    p.relateds.append(rs["foo"])
    p.relateds.append(rs["baz"])
    Session.add(p)

    c = Child()
    c.relateds.append(rs["foo"])
    c.relateds.append(rs["bar"])
    Session.add(c)

    Session.commit()

    print(Session.query(Parent).filter(Parent.has_related_names(["foo"])).all())
    print(Session.query(Child).filter(Child.has_related_names(["foo"])).all())
    print(Session.query(Parent).filter(Parent.has_related_names(["bar"])).all())
    print(Session.query(Parent).filter(Parent.has_related_names(["baz"])).all())
