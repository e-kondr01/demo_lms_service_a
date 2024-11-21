import asyncio
from datetime import datetime
from random import randint
from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db import async_session_factory
from app.models import (
    Assessment,
    AssessmentFDWThreeServices,
    AssessmentFDWTwoServices,
    Institution,
    Student,
    Unit,
)

institution_names = (
    "ИТМО",
    "ТюмГУ",
    "Политех",
    "МГУ",
    "МФТИ",
    "СПбГУ",
    "МИФИ",
    "МГУТ им. Баумана",
    "ВШЭ",
    "МГИМО",
)


async def generate_institutions(session: AsyncSession):
    for name in institution_names:
        institution = Institution(name=name)
        session.add(institution)
    await session.commit()


async def generate_units(session: AsyncSession):
    for i in range(1, 101):
        name = f"Задание {i}"
        unit = Unit(name=name)
        session.add(unit)
    await session.commit()


async def generate_students(session: AsyncSession):
    for index, name in enumerate(institution_names):
        institution = (
            await session.execute(select(Institution).filter_by(name=name))
        ).scalar_one()
        for i in range(1, (index + 1) * 100 + 1):
            student = Student(
                name=f"Студент {institution.name} {i+1}", institution_id=institution.id
            )
            session.add(student)

    await session.commit()


async def generate_assessments(session: AsyncSession):
    students = (await session.execute(select(Student))).scalars().all()
    units = (
        (await session.execute(select(Unit).order_by(Unit.created_at))).scalars().all()
    )
    students_assessments: dict[UUID, set[int]] = {
        student.id: set() for student in students
    }
    assessments_to_create: list[Assessment] = []

    while len(assessments_to_create) != len(students) * len(units) * 0.5:
        student_index = randint(0, len(students) - 1)
        student = students[student_index]

        if len(students_assessments[student.id]) != len(units):
            unit_index = randint(0, len(units) - 1)
            if unit_index in students_assessments[student.id]:
                continue

            unit = units[unit_index]

            grade = randint(1, 5)
            assessment = Assessment(
                unit_id=unit.id,
                student_id=student.id,
                created_at=datetime.now(),
                grade=grade,
            )
            assessments_to_create.append(assessment)
            students_assessments[student.id].add(unit_index)

    session.add_all(assessments_to_create)
    await session.commit()


async def generate_assessments_fdw_two_services(session: AsyncSession):
    # sorry, hardcode for ports
    engine = create_async_engine(
        "postgresql+asyncpg://postgres:postgres@192.168.0.114:5433/service_b",
        echo=False,
        connect_args={"server_settings": {"jit": "off"}},
    )

    async_session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session_factory() as service_b_session:
        student_ids = (
            (await service_b_session.execute(text("SELECT id FROM servicebstudent;")))
            .scalars()
            .all()
        )

    units = (
        (await session.execute(select(Unit).order_by(Unit.created_at))).scalars().all()
    )

    students_assessments: dict[UUID, set[int]] = {
        student_id: set() for student_id in student_ids
    }
    assessments_to_create: list[AssessmentFDWTwoServices] = []

    while len(assessments_to_create) != len(student_ids) * len(units) * 0.5:
        student_index = randint(0, len(student_ids) - 1)
        student_id = student_ids[student_index]

        if len(students_assessments[student_id]) != len(units):
            unit_index = randint(0, len(units) - 1)
            if unit_index in students_assessments[student_id]:
                continue

            unit = units[unit_index]
            grade = randint(1, 5)
            assessment = AssessmentFDWTwoServices(
                unit_id=unit.id,
                student_id=student_id,
                created_at=datetime.now(),
                grade=grade,
            )
            assessments_to_create.append(assessment)
            students_assessments[student_id].add(unit_index)

    session.add_all(assessments_to_create)
    await session.commit()


async def generate_assessments_fdw_three_services(session: AsyncSession):
    engine = create_async_engine(
        "postgresql+asyncpg://postgres:postgres@192.168.0.114:5433/service_b",
        echo=False,
        connect_args={"server_settings": {"jit": "off"}},
    )

    async_session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session_factory() as service_b_session:
        student_ids = (
            (await service_b_session.execute(text("SELECT id FROM servicebstudent;")))
            .scalars()
            .all()
        )

    # We do a little bit of hiding
    engine = create_async_engine(
        "",
        echo=False,
        connect_args={"server_settings": {"jit": "off"}},
    )

    async_session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session_factory() as service_c_session:
        unit_ids = (
            (
                await service_c_session.execute(
                    text("SELECT id FROM servicecunit ORDER BY created_at;")
                )
            )
            .scalars()
            .all()
        )

    students_assessments: dict[UUID, set[int]] = {
        student_id: set() for student_id in student_ids
    }
    assessments_to_create: list[AssessmentFDWThreeServices] = []

    while len(assessments_to_create) != len(student_ids) * len(unit_ids) * 0.5:
        student_index = randint(0, len(student_ids) - 1)
        student_id = student_ids[student_index]

        if len(students_assessments[student_id]) != len(unit_ids):
            unit_index = randint(0, len(unit_ids) - 1)
            if unit_index in students_assessments[student_id]:
                continue

            unit_id = unit_ids[unit_index]
            grade = randint(1, 5)
            assessment = AssessmentFDWThreeServices(
                unit_id=unit_id,
                student_id=student_id,
                created_at=datetime.now(),
                grade=grade,
            )
            assessments_to_create.append(assessment)
            students_assessments[student_id].add(unit_index)

    session.add_all(assessments_to_create)
    await session.commit()


async def main():
    async with async_session_factory() as session:
        # await generate_institutions(session)
        # await generate_units(session)
        # await generate_students(session)
        await generate_assessments(session)
        await generate_assessments_fdw_two_services(session)
        await generate_assessments_fdw_three_services(session)


asyncio.run(main())
