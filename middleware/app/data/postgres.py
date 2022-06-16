#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Authors: Gonçalo Leal (goncalolealsilva@ua.pt), Vasco Regal (vascoregal24@ua.pt)
# Date: 02-04-2022

# Description:
# All database functions

from sqlalchemy import false, update, select

from app.data.db.conn import session, engine, Base


class PostgresManager:
    def __init__(self):
        Base.metadata.create_all(bind=engine)
        self._postgres = session

    # Guarda uma Base (super class dos models)
    def save_one(self, entity: Base) -> Base:
        self._postgres.add(entity)
        self._postgres.commit()
        return entity

    # Guarda uma lista de Bases (super class dos models)
    def save_all(self, entities):
        [self._postgres.add(entity) for entity in entities]
        self._postgres.commit()
        return entities

    # Guarda uma lista de Bases (super class dos models)
    def flush(self) -> None:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    def get_all(self, entity, skip: int = 0, has_limit: bool = false, limit: int = 100):
        if has_limit:
            return self._postgres.query(entity).offset(skip).limit(limit).all()
        else:
            return self._postgres.query(entity).all()

    def get_count(self, entity):
        return self._postgres.query(entity).count()

    def get_by_pk(self, entity, primary_key):
        return self._postgres.query(entity).filter_by(id=primary_key).first()

    def delete_by_pk(self, entity, primary_key):
        instance = self.get_by_pk(entity, primary_key)
        if instance:
            self._postgres.delete(instance)
            self._postgres.commit()

        return instance

    def update_one(self, entity, updated):
        instance = self.get_by_pk(entity, updated.id)
        if instance:
            self._postgres.execute(
                update(entity).
                where(entity.id == updated.id).
                values(**(dict(updated)))
            )

            self._postgres.commit()

        return instance

    # Get a list of all IDs from an entity
    def get_all_ids(self, entity):
        statement = select(entity.id)
        return [id[0] for id in self._postgres.execute(statement).all()]

    def get_collector_type_by_type(self, entity, t):
        return self._postgres.query(entity).filter_by(type=t).first()

    def get_by_name(self, entity, n):
        return self._postgres.query(entity).filter_by(name=n).first()

    def get_all_in(self, statement, column, list):
        return self._postgres.query(statement).filter(column.in_(list)).all()

    def execute(self, command):
        return self._postgres.execute(command)

    def commit(self):
        self._postgres.commit()

    def get_all_join(self, entity1, entity2):
        return self._postgres.query(entity1).join(entity2)

postgres_manager = PostgresManager()