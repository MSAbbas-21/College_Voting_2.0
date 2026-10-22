from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import CustomUser
from elections.models import Election
from candidates.models import Candidate
from voting.models import VoterParticipation, Vote


class Command(BaseCommand):
    help = "Seed database with realistic demo accounts, elections, candidates, and votes for evaluation."

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE("Seeding database with demo college voting data..."))

        # 1. Create Superuser / Administrator
        admin_user, created = CustomUser.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@apexcollege.edu',
                'first_name': 'Chief Election',
                'last_name': 'Officer',
                'role': 'admin',
                'approval_status': 'approved',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        admin_user.set_password('Admin@12345')
        admin_user.save()
        if created:
            self.stdout.write(self.style.SUCCESS("Created Admin: admin / Admin@12345"))

        # 2. Create Students
        students_data = [
            {
                'username': 'CS2023001',
                'student_id': 'CS2023001',
                'first_name': 'Jordan',
                'last_name': 'Hayes',
                'email': 'jordan.hayes@apexcollege.edu',
                'department': 'CSE',
                'year_of_study': '3',
                'role': 'student',
                'approval_status': 'approved',
                'approved_by': admin_user,
                'approval_date': timezone.now(),
            },
            {
                'username': 'CS2023002',
                'student_id': 'CS2023002',
                'first_name': 'Priya',
                'last_name': 'Sharma',
                'email': 'priya.sharma@apexcollege.edu',
                'department': 'CSE',
                'year_of_study': '3',
                'role': 'student',
                'approval_status': 'approved',
                'approved_by': admin_user,
                'approval_date': timezone.now(),
            },
            {
                'username': 'EC2023015',
                'student_id': 'EC2023015',
                'first_name': 'Marcus',
                'last_name': 'Vance',
                'email': 'marcus.vance@apexcollege.edu',
                'department': 'ECE',
                'year_of_study': '2',
                'role': 'student',
                'approval_status': 'approved',
                'approved_by': admin_user,
                'approval_date': timezone.now(),
            },
            {
                'username': 'ME2023022',
                'student_id': 'ME2023022',
                'first_name': 'Elena',
                'last_name': 'Rostova',
                'email': 'elena.rostova@apexcollege.edu',
                'department': 'ME',
                'year_of_study': '4',
                'role': 'student',
                'approval_status': 'approved',
                'approved_by': admin_user,
                'approval_date': timezone.now(),
            },
            {
                'username': 'IT2024099',
                'student_id': 'IT2024099',
                'first_name': 'Liam',
                'last_name': 'Chen',
                'email': 'liam.chen@apexcollege.edu',
                'department': 'IT',
                'year_of_study': '1',
                'role': 'student',
                'approval_status': 'pending',
            },
            {
                'username': 'CE2024005',
                'student_id': 'CE2024005',
                'first_name': 'David',
                'last_name': 'Kim',
                'email': 'david.kim@apexcollege.edu',
                'department': 'CE',
                'year_of_study': '1',
                'role': 'student',
                'approval_status': 'rejected',
                'rejection_reason': 'Student roll number not found in active semester enrollment registry.',
            },
        ]

        created_students = {}
        for s_info in students_data:
            s_user, s_created = CustomUser.objects.get_or_create(
                username=s_info['username'],
                defaults=s_info
            )
            s_user.set_password('Student@12345')
            s_user.save()
            created_students[s_user.username] = s_user

        self.stdout.write(self.style.SUCCESS("Created 6 sample student accounts (Approved, Pending, Rejected)"))

        # 3. Create Elections
        now = timezone.now()

        # Election 1: Live & Active
        el_live, _ = Election.objects.get_or_create(
            title="Student Council Presidential Election 2026",
            defaults={
                'description': "Annual campus-wide election to elect the President of the Student Government Association for the 2026-2027 academic session. All approved students across all departments are eligible to cast one secret ballot.",
                'start_date': now - timedelta(days=1),
                'end_date': now + timedelta(days=3),
                'status': 'active',
                'is_published': False,
                'created_by': admin_user,
            }
        )

        # Candidates for Live Election
        c1, _ = Candidate.objects.get_or_create(
            election=el_live,
            student_id="CS2022010",
            defaults={
                'name': "Maya Lin",
                'department': "Computer Science & Engineering",
                'position': "President",
                'manifesto': "1. 24/7 Library & Maker-space access.\n2. Transparent student union budgeting.\n3. Expanded campus mental health resources and annual technical symposium.",
            }
        )

        c2, _ = Candidate.objects.get_or_create(
            election=el_live,
            student_id="ME2022045",
            defaults={
                'name': "Arthur Pendelton",
                'department': "Mechanical Engineering",
                'position': "President",
                'manifesto': "1. Upgrade laboratory equipment and workshop tooling.\n2. Better cafeteria meal choices and subsidized campus shuttle passes.\n3. Increased university funding for inter-college sports teams.",
            }
        )

        c3, _ = Candidate.objects.get_or_create(
            election=el_live,
            student_id="MBA2022003",
            defaults={
                'name': "Sarah Al-Mansoor",
                'department': "Management Studies (MBA)",
                'position': "President",
                'manifesto': "1. Direct student representation on the university academic board.\n2. Strong industry networking and career internship fairs.\n3. Eco-friendly campus sustainability initiative.",
            }
        )

        # Cast 1 initial vote from student CS2023002 in live election
        if not VoterParticipation.objects.filter(student=created_students['CS2023002'], election=el_live).exists():
            receipt = VoterParticipation.generate_receipt()
            VoterParticipation.objects.create(
                student=created_students['CS2023002'],
                election=el_live,
                receipt_code=receipt
            )
            Vote.objects.create(election=el_live, candidate=c1)

        # Election 2: Concluded with Published Certified Results
        el_concluded, _ = Election.objects.get_or_create(
            title="Department General Secretary Election 2026",
            defaults={
                'description': "Election to elect the General Secretary for Engineering and Applied Sciences. Voting has closed and certified results have been published by the Election Commission.",
                'start_date': now - timedelta(days=10),
                'end_date': now - timedelta(days=2),
                'status': 'closed',
                'is_published': True,
                'created_by': admin_user,
            }
        )

        cg1, _ = Candidate.objects.get_or_create(
            election=el_concluded,
            student_id="CS2022088",
            defaults={
                'name': "Rohan Gupta",
                'department': "Computer Science & Engineering",
                'position': "General Secretary",
                'manifesto': "Committed to seamless grievance redressal, faster club budget clearances, and modern digital event management across departments.",
            }
        )

        cg2, _ = Candidate.objects.get_or_create(
            election=el_concluded,
            student_id="IT2022014",
            defaults={
                'name': "Sophia Ramirez",
                'department': "Information Technology",
                'position': "General Secretary",
                'manifesto': "Bridging academia and practical projects. Focused on hackathons, tech workshops, and student mentorship programs.",
            }
        )

        # Populate votes for concluded election: 3 votes for Rohan, 1 vote for Sophia
        voters_concluded = [
            (created_students['CS2023001'], cg1),
            (created_students['CS2023002'], cg1),
            (created_students['EC2023015'], cg1),
            (created_students['ME2023022'], cg2),
        ]
        for v_student, v_cand in voters_concluded:
            if not VoterParticipation.objects.filter(student=v_student, election=el_concluded).exists():
                r_code = VoterParticipation.generate_receipt()
                VoterParticipation.objects.create(
                    student=v_student,
                    election=el_concluded,
                    receipt_code=r_code
                )
                Vote.objects.create(election=el_concluded, candidate=v_cand)

        # Election 3: Scheduled / Upcoming
        el_upcoming, _ = Election.objects.get_or_create(
            title="Annual Sports Committee Head Election 2026",
            defaults={
                'description': "Upcoming campus sports committee elections. Nominations have closed; campaigning is active. Polling begins in 3 days.",
                'start_date': now + timedelta(days=3),
                'end_date': now + timedelta(days=7),
                'status': 'active',
                'is_published': False,
                'created_by': admin_user,
            }
        )

        Candidate.objects.get_or_create(
            election=el_upcoming,
            student_id="ME2023091",
            defaults={
                'name': "Kevin Brooks",
                'department': "Mechanical Engineering",
                'position': "Sports Secretary",
                'manifesto': "Upgrade fitness center equipment, organize inter-college football leagues, and secure sports scholarship quotas.",
            }
        )

        Candidate.objects.get_or_create(
            election=el_upcoming,
            student_id="CE2023041",
            defaults={
                'name': "Nadia Patel",
                'department': "Civil Engineering",
                'position': "Sports Secretary",
                'manifesto': "Equal funding for men's and women's intramural teams, nighttime field lighting, and annual athletics meet.",
            }
        )

        self.stdout.write(self.style.SUCCESS("Created 3 elections (Active, Concluded with published results, and Upcoming)."))
        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully!"))
