from django.core.management.base import BaseCommand

from resources.models import Course


COURSE_GROUPS = {
    "School of Engineering & Technology": [
        "B.Tech. Aerospace Engineering",
        "B.Tech. Aerospace Engineering (Specialisation in Unmanned Aerial Vehicles)",
        "B.Tech. Aerospace Engineering (Specialisation in Artificial Intelligence and Machine Learning)",
        "B.Tech. Aerospace Engineering (Specialisation in Aircraft Maintenance)",
        "B.Tech. Biomedical Engineering",
        "B.Tech. Biomedical Engineering (Specialisation in Artificial Intelligence and Machine Learning)",
        "B.Tech. Biotechnology",
        "B.Tech. Biotechnology (Specialisation in Artificial Intelligence)",
        "B.Tech. Biotechnology (Specialisation in Genome Engineering and Technology)",
        "B.Tech. Civil Engineering",
        "B.Tech. Civil Engineering (Specialisation in Building Information Modelling and Digital Twin)",
        "B.Tech. Civil Engineering (Specialisation in Geospatial Technology)",
        "B.Tech. Electrical and Electronics Engineering",
        "B.Tech. Electrical and Electronics Engineering (Specialisation in Artificial Intelligence and Machine Learning)",
        "B.Tech. Electronics and Communication Engineering",
        "B.Tech. Electronics and Communication Engineering (Specialisation in Artificial Intelligence and Machine Learning)",
        "B.Tech. Food Processing and Engineering",
        "B.Tech. Food Processing and Engineering (Specialisation in Internet of Things)",
        "B.Tech. Mechanical Engineering",
        "B.Tech. Mechanical Engineering (Specialisation in Artificial Intelligence and Machine Learning)",
        "B.Tech. Robotics and Automation",
        "B.Tech. Robotics and Automation (Specialisation in Artificial Intelligence and Data Science)",
        "B.Tech. Robotics and Automation (Specialisation in Artificial Intelligence and Machine Learning)",
    ],
    "School of Computer Science & Technology": [
        "B.Tech. Artificial Intelligence and Data Science",
        "B.Tech. Computer Science and Engineering",
        "B.Tech. Computer Science & Engineering (Specialisation in Artificial Intelligence and Machine Learning)",
        "B.Tech. Computer Science and Engineering (Specialisation in Cyber Security)",
        "B.Tech. Computer Science and Engineering (Specialisation in Quantum Computing)",
        "B.Tech. Computer Science and Engineering (Artificial Intelligence)",
        "B.Tech. Computer Science & Engineering (Artificial Intelligence and Machine Learning)",
        "B.Tech. Computer Science and Engineering (Cyber Security)",
    ],
    "School of Agriculture": [
        "B.Sc. (Hons.) Agriculture",
    ],
    "School of Arts & Science": [
        "B.Sc. Artificial Intelligence and Data Science",
        "B.Com. (Specialisation in Professional Accounting and Financial Technology)",
        "B.Sc. Energy Science and Technology",
        "B.Sc. Forensic Science",
        "B.Sc. Information Security and Digital Forensics",
        "B.Sc. (Hons.) Psychology",
        "B.Sc. Semiconductor Technology",
    ],
    "School of Media": [
        "B.Sc. Media Production and Digital Marketing",
    ],
    "School of Health Science": [
        "B.Sc. Medical Laboratory Technology",
        "B.Sc. Radiography and Imaging Technology",
        "B.Sc. Operation Theatre and Anesthesia Technology",
    ],
}


class Command(BaseCommand):
    help = "Seed college courses grouped by school."

    def handle(self, *args, **options):
        created = 0
        existing = 0
        serial = 1

        for school, course_names in COURSE_GROUPS.items():
            for name in course_names:
                code = f"C{serial:03d}"
                _, was_created = Course.objects.get_or_create(
                    code=code,
                    defaults={
                        "name": name.replace("★", "").strip(),
                        "description": f"School: {school}",
                    },
                )
                if was_created:
                    created += 1
                else:
                    existing += 1
                serial += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Course seeding complete. Created: {created}, Existing: {existing}"
            )
        )
