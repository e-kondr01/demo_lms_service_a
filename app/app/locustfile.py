from random import choice, randint

from locust import FastHttpUser, between, task
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.models import Assessment, Institution, Unit
from app.models.foreign import ServiceBInstitution, ServiceCUnit

engine = create_engine("postgresql://postgres:postgres@localhost:5432/service_a")
session_factory = sessionmaker(engine, expire_on_commit=False)

with session_factory() as session:
    service_a_unit_ids = session.execute(select(Unit.id)).scalars().all()
    service_a_institution_ids = session.execute(select(Institution.id)).scalars().all()
    service_a_assessment_grades = (
        session.execute(select(Assessment.grade).distinct()).scalars().all()
    )
    service_b_institution_ids = (
        session.execute(select(ServiceBInstitution.id)).scalars().all()
    )
    service_c_unit_names = (
        session.execute(select(ServiceCUnit.name).distinct()).scalars().all()
    )
# TODO: добавить вариант None без фильтра


class AssessmentUser(FastHttpUser):
    host = "http://127.0.0.1:8000"
    # TODO
    wait_time = between(0.5, 1)


class SharedDBUser(AssessmentUser):
    @task
    def get_assessments(self):
        # Менять в сценарии с изменением размера страницы
        size = 20

        url = f"/api/assessments/shared-db?size={size}"

        max_page_number = int(275000 / size)
        page_number = randint(1, max_page_number)
        url += f"&page={page_number}"

        unit_id = choice(service_a_unit_ids)
        if unit_id:
            url += f"&unit_id={unit_id}"

        institution_id = choice(service_a_institution_ids)
        if institution_id:
            url += f"&institution_id={institution_id}"

        self.client.get(url)


class CyclicCompositionAssessmentUser(AssessmentUser):
    @task
    def get_assessments(self):
        size = 800
        url = f"/api/assessments/cyclic-api-composition?size={size}"
        unit_id = choice(service_a_unit_ids)
        if unit_id:
            url += f"&unit_id={unit_id}"
        institution_id = choice(service_a_institution_ids)
        if institution_id:
            url += f"&institution_id={institution_id}"
        self.client.get(url)


class PaginatedCompositionAssessmentUser(AssessmentUser):
    @task
    def get_assessments(self):
        size = 20
        url = f"/api/assessments/paginated-api-composition?size={size}"
        max_page_number = int(3550 / size)
        page_number = randint(1, max_page_number)
        url += f"&page={page_number}"
        unit_id = choice(service_a_unit_ids)
        if unit_id:
            url += f"&unit_id={unit_id}"
        institution_id = choice(service_a_institution_ids)
        if institution_id:
            url += f"&institution_id={institution_id}"
        self.client.get(url)
