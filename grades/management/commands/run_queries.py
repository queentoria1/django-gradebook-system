from django.core.management.base import BaseCommand
from django.db.models import Avg, Window
from django.db.models.functions import RowNumber
from grades.models import Course, Score, Student

class Command(BaseCommand):
    help = 'Executes and prints the 3 required Week 2 ORM project report queries'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n=================================================='))
        self.stdout.write(self.style.SUCCESS('      WEEK 2 PROJECT: ORM QUERY RESULTS CHECK      '))
        self.stdout.write(self.style.SUCCESS('=================================================='))

        # ----------------------------------------------------
        # QUERY 1: Who are the top 3 scorers in each course?
        # ----------------------------------------------------
        self.stdout.write(self.style.MIGRATE_HEADING('\n📋 REPORT 1: Top 3 Scorers per Course'))
        
        ranked_scores = Score.objects.annotate(
            rank=Window(
                expression=RowNumber(),
                partition_by=['course_id'],
                order_by='-score'
            )
        )
        
        for course in Course.objects.all():
            self.stdout.write(f"\nCourse: {course.code} - {course.name}")
            course_ranks = [s for s in ranked_scores if s.course_id == course.id and s.rank <= 3]
            for s_record in course_ranks:
                self.stdout.write(f"  - Rank #{s_record.rank}: {s_record.student} | Score: {s_record.score}%")

        # ----------------------------------------------------
        # QUERY 2: Which students are below the pass mark of 50?
        # ----------------------------------------------------
        self.stdout.write(self.style.MIGRATE_HEADING('\n⚠️ REPORT 2: Students Below Pass Mark (< 50%)'))
        
        failing_records = Score.objects.filter(score__lt=50.0).select_related('student', 'course')
        if failing_records.exists():
            for record in failing_records:
                self.stdout.write(f"  - {record.student} | Course: {record.course.name} | Score: {record.score}%")
        else:
            self.stdout.write("  🎉 Exceptional! No students are currently tracking below 50%.")

        # ----------------------------------------------------
        # QUERY 3: Average score for each course (Highest to Lowest)
        # ----------------------------------------------------
        self.stdout.write(self.style.MIGRATE_HEADING('\n📊 REPORT 3: Course Performance Averages (Sorted)'))
        
        course_performance = Course.objects.annotate(
            average_score=Avg('scores__score')
        ).order_by('-average_score')
        
        for course in course_performance:
            avg = f"{course.average_score:.2f}%" if course.average_score else "0.00%"
            self.stdout.write(f"  - {course.code} | {course.name}: Average Score = {avg}")
            
        self.stdout.write(self.style.SUCCESS('\n==================================================\n'))
