import asyncio
from datetime import datetime
from random import randint

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db import async_session_factory
from app.models import Assessment, AssessmentFDWTwoServices, Institution, Student, Unit


async def generate_institutions(session: AsyncSession):
    institution_names = ("ИТМО", "ТюмГУ", "Политех", "ФТМИ")
    for name in institution_names:
        institution = Institution(name=name)
        session.add(institution)
    await session.commit()


async def generate_units(session: AsyncSession):
    unit_names = ("Первый", "Второй", "Третий", "Четвёртый", "Пятый")
    for name in unit_names:
        unit = Unit(name=name)
        session.add(unit)
        await session.commit()


async def generate_students(session: AsyncSession):
    institution = (
        await session.execute(select(Institution).filter_by(name="ИТМО"))
    ).scalar_one()
    for i in range(200):
        student = Student(name=f"Студент ИТМО {i+1}", institution_id=institution.id)
        session.add(student)

    institution = (
        await session.execute(select(Institution).filter_by(name="ТюмГУ"))
    ).scalar_one()
    for i in range(100):
        student = Student(name=f"Студент ТюмГУ {i+1}", institution_id=institution.id)
        session.add(student)

    institution = (
        await session.execute(select(Institution).filter_by(name="Политех"))
    ).scalar_one()
    for i in range(180):
        student = Student(name=f"Студент Политеха {i+1}", institution_id=institution.id)
        session.add(student)

    institution = (
        await session.execute(select(Institution).filter_by(name="ФТМИ"))
    ).scalar_one()
    for i in range(230):
        student = Student(name=f"Студент ФТМИ {i+1}", institution_id=institution.id)
        session.add(student)

    await session.commit()


async def generate_assessments(session: AsyncSession):
    students = (await session.execute(select(Student))).scalars().all()
    units = (
        (await session.execute(select(Unit).order_by(Unit.created_at))).scalars().all()
    )
    students_assessments = {student.id: 0 for student in students}
    assessments_to_create = []

    while len(assessments_to_create) != len(students) * len(units):
        student_index = randint(0, len(students) - 1)
        student = students[student_index]

        if students_assessments[student.id] != 5:
            unit_index = students_assessments[student.id]
            unit = units[unit_index]
            assessment = Assessment(
                unit_id=unit.id, student_id=student.id, created_at=datetime.now()
            )
            assessments_to_create.append(assessment)
            students_assessments[student.id] += 1

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
    students_assessments = {student_id: 0 for student_id in student_ids}
    assessments_to_create = []

    while len(assessments_to_create) != len(student_ids) * len(units):
        student_index = randint(0, len(student_ids) - 1)
        student_id = student_ids[student_index]

        if students_assessments[student_id] != 5:
            unit_index = students_assessments[student_id]
            unit = units[unit_index]
            assessment = AssessmentFDWTwoServices(
                unit_id=unit.id, student_id=student_id, created_at=datetime.now()
            )
            assessments_to_create.append(assessment)
            students_assessments[student_id] += 1

    session.add_all(assessments_to_create)
    await session.commit()


async def main():
    async with async_session_factory() as session:
        # await generate_institutions(session)
        # await generate_units(session)
        # await generate_students(session)
        # await generate_assessments(session)
        await generate_assessments_fdw_two_services(session)


asyncio.run(main())
