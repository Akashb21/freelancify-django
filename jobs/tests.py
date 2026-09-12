from django.test import TestCase
from django.contrib.auth import get_user_model
from jobs.models import Category, Job, Proposal

User = get_user_model()

class JobModelTest(TestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(username='client1', role='CLIENT')
        self.freelancer_user = User.objects.create_user(username='free1', role='FREELANCER')
        self.category = Category.objects.create(name='Web Development', slug='web-dev')

    def test_create_job_and_proposal(self):
        job = Job.objects.create(
            client=self.client_user,
            title='Build Django App',
            description='Project description',
            category=self.category,
            budget_min=500.00,
            budget_max=1000.00
        )
        self.assertEqual(job.title, 'Build Django App')
        self.assertEqual(job.proposal_count(), 0)

        proposal = Proposal.objects.create(
            job=job,
            freelancer=self.freelancer_user,
            bid_amount=750.00,
            cover_letter='I can build this fast.'
        )
        self.assertEqual(job.proposal_count(), 1)
        self.assertEqual(proposal.bid_amount, 750.00)
